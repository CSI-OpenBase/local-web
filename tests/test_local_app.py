from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from admin_app.local_app import create_local_app
from admin_app.local_config import LocalSettings
from admin_app.local_store import LocalStore


class FakeRunner:
    def __init__(self, store: LocalStore) -> None:
        self.store = store
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def start(self) -> None:
        return None

    def submit(self, kind: str, **payload: Any) -> dict[str, Any]:
        self.calls.append((kind, payload))
        return self.store.create_job(
            kind, video_id=payload.get("video_id"), payload=payload
        )


def settings(
    tmp_path: Path, token: str = "", instance_nonce: str = ""
) -> LocalSettings:
    return LocalSettings(
        data_home=tmp_path,
        session_home=tmp_path / ".sessions",
        desktop_token=token,
        instance_nonce=instance_nonce,
    )


def csrf(client: TestClient) -> str:
    response = client.get("/")
    marker = 'name="csrf_token" value="'
    return response.text.split(marker, 1)[1].split('"', 1)[0]


def test_local_home_and_manual_authorization_job(tmp_path: Path) -> None:
    local_settings = settings(tmp_path)
    store = LocalStore(local_settings.database_path)
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert "本地归档" in response.text
        token = csrf(client)
        response = client.post(
            "/actions/authorize", data={"csrf_token": token}, follow_redirects=False
        )
        assert response.status_code == 303
    assert runner.calls == [("authorize", {})]


def test_export_requires_authorization(tmp_path: Path) -> None:
    local_settings = settings(tmp_path)
    store = LocalStore(local_settings.database_path)
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        response = client.post(
            "/actions/export",
            data={"csrf_token": csrf(client)},
            follow_redirects=False,
        )
        assert response.status_code == 303
    assert runner.calls == []


def test_complete_export_requires_a_profile_sync(tmp_path: Path) -> None:
    local_settings = settings(tmp_path)
    store = LocalStore(local_settings.database_path)
    store.set_meta("creator_identity", {"handle": "creator-handle"})
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        response = client.post(
            "/actions/export",
            data={"csrf_token": csrf(client)},
            follow_redirects=False,
        )
        assert response.status_code == 303
    assert runner.calls == []


def test_complete_export_rejects_an_incomplete_profile_archive(
    tmp_path: Path,
) -> None:
    local_settings = settings(tmp_path)
    store = LocalStore(local_settings.database_path)
    store.set_meta("creator_identity", {"handle": "creator-handle"})
    store.set_meta(
        "last_video_sync",
        {"finished_at": "2026-09-07T12:00:00Z", "complete": False},
    )
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        response = client.post(
            "/actions/export",
            data={"csrf_token": csrf(client)},
            follow_redirects=False,
        )
        assert response.status_code == 303
    assert runner.calls == []


def test_sync_route_always_targets_the_signed_in_profile(tmp_path: Path) -> None:
    local_settings = settings(tmp_path)
    store = LocalStore(local_settings.database_path)
    store.set_meta("creator_identity", {"handle": "creator-handle"})
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        response = client.post(
            "/actions/sync-videos",
            data={
                "csrf_token": csrf(client),
                "profile_url": "https://www.douyin.com/user/someone-else",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
    assert runner.calls == [("sync_videos", {})]


def test_desktop_token_guards_ui_and_identifies_health_instance(tmp_path: Path) -> None:
    local_settings = settings(
        tmp_path, token="desktop-secret", instance_nonce="instance-123"
    )
    store = LocalStore(local_settings.database_path)
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        assert client.get("/health").status_code == 401
        assert client.get("/").status_code == 401
        response = client.get(
            "/health", headers={"X-CSI-Desktop-Token": "desktop-secret"}
        )
        assert response.status_code == 200
        assert response.json()["instance_nonce"] == "instance-123"
        assert client.get("/").status_code == 200


def test_desktop_token_replaces_a_stale_cookie_after_restart(tmp_path: Path) -> None:
    local_settings = settings(tmp_path, token="new-desktop-secret")
    store = LocalStore(local_settings.database_path)
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        client.cookies.set(
            "csi_desktop",
            "old-desktop-secret",
            domain="testserver.local",
            path="/",
        )
        response = client.get(
            "/", headers={"X-CSI-Desktop-Token": "new-desktop-secret"}
        )
        assert response.status_code == 200
        assert client.cookies.get(
            "csi_desktop", domain="testserver.local", path="/"
        ) == "new-desktop-secret"
        assert client.get("/static/local.css").status_code == 200


def test_shutdown_requires_desktop_token_and_invokes_callback(tmp_path: Path) -> None:
    stopped: list[bool] = []
    local_settings = settings(tmp_path, token="desktop-secret")
    store = LocalStore(local_settings.database_path)
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(
            local_settings,
            store=store,
            runner=runner,
            shutdown_callback=lambda: stopped.append(True),
        )
    ) as client:
        assert client.post("/api/shutdown").status_code == 401
        response = client.post(
            "/api/shutdown",
            headers={"X-CSI-Desktop-Token": "desktop-secret"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "status": "stopping",
            "force_required": False,
        }
    assert stopped == [True]


def test_shutdown_is_not_exposed_in_source_mode(tmp_path: Path) -> None:
    local_settings = settings(tmp_path)
    store = LocalStore(local_settings.database_path)
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        assert client.post("/api/shutdown").status_code == 404


def test_shutdown_waits_for_desktop_to_force_cleanup_of_active_browser_job(
    tmp_path: Path, monkeypatch
) -> None:
    stopped: list[bool] = []

    class ActiveRunner:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            self.close_calls = 0

        def start(self) -> None:
            return None

        def close(self) -> bool:
            self.close_calls += 1
            return False

    import admin_app.local_jobs as jobs_module

    monkeypatch.setattr(jobs_module, "LocalJobRunner", ActiveRunner)
    local_settings = settings(
        tmp_path, token="desktop-secret", instance_nonce="instance-123"
    )
    with TestClient(
        create_local_app(
            local_settings,
            shutdown_callback=lambda: stopped.append(True),
        )
    ) as client:
        response = client.post(
            "/api/shutdown",
            headers={"X-CSI-Desktop-Token": "desktop-secret"},
        )
        assert response.status_code == 200
        assert response.json() == {
            "status": "stopping",
            "force_required": True,
        }
        assert stopped == []


def test_comment_route_only_creates_explicit_immediate_job(tmp_path: Path) -> None:
    local_settings = settings(tmp_path)
    store = LocalStore(local_settings.database_path)
    store.upsert_videos(
        [
            {
                "video_id": "7680023068660346011",
                "title": "视频",
                "video_url": "https://www.douyin.com/video/7680023068660346011",
                "manifest_path": "works/videos/douyin/7680023068660346011/manifest.json",
                "first_seen_at": "2026-09-07T00:00:00Z",
                "last_seen_at": "2026-09-07T00:00:00Z",
            }
        ]
    )
    runner = FakeRunner(store)
    with TestClient(
        create_local_app(local_settings, store=store, runner=runner)
    ) as client:
        response = client.post(
            "/videos/7680023068660346011/comments",
            data={"csrf_token": csrf(client)},
            follow_redirects=False,
        )
        assert response.status_code == 303
    assert runner.calls == [
        ("comments", {"video_id": "7680023068660346011"})
    ]
