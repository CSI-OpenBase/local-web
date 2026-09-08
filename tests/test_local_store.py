from __future__ import annotations

from pathlib import Path

import pytest

from admin_app.local_store import ActiveCommentJobError, LocalStore


def video_record(video_id: str = "7680023068660346011") -> dict[str, str]:
    return {
        "video_id": video_id,
        "platform": "douyin",
        "title": "归档测试视频",
        "video_url": f"https://www.douyin.com/video/{video_id}",
        "manifest_path": f"works/videos/douyin/{video_id}/manifest.json",
        "first_seen_at": "2026-09-07T10:00:00Z",
        "last_seen_at": "2026-09-07T10:00:00Z",
    }


def test_store_persists_metadata_and_video_index(tmp_path: Path) -> None:
    store = LocalStore(tmp_path / "openbase.sqlite3")
    store.set_meta("creator_identity", {"handle": "creator"})
    assert store.get_meta("creator_identity") == {"handle": "creator"}

    assert store.upsert_videos([video_record()]) == 1
    video = store.get_video("7680023068660346011")
    assert video is not None
    assert video["title"] == "归档测试视频"

    updated = video_record()
    updated["title"] = "更新标题"
    updated["last_seen_at"] = "2026-09-08T10:00:00Z"
    store.upsert_videos([updated])
    video = store.get_video("7680023068660346011")
    assert video is not None
    assert video["title"] == "更新标题"
    assert video["first_seen_at"] == "2026-09-07T10:00:00Z"
    assert video["last_seen_at"] == "2026-09-08T10:00:00Z"


def test_comment_job_is_immediate_and_deduplicated(tmp_path: Path) -> None:
    store = LocalStore(tmp_path / "openbase.sqlite3")
    store.upsert_videos([video_record()])
    first = store.create_job("comments", video_id="7680023068660346011")
    assert first["status"] == "queued"
    assert first["payload"] == {}

    with pytest.raises(ActiveCommentJobError):
        store.create_job("comments", video_id="7680023068660346011")

    store.update_job(first["id"], "succeeded", result={"count": 3})
    second = store.create_job("comments", video_id="7680023068660346011")
    assert second["id"] > first["id"]


@pytest.mark.parametrize("video_id", ["..", "../outside", "1234", "12345678/9"])
def test_store_rejects_video_ids_that_could_escape_paths(
    tmp_path: Path, video_id: str
) -> None:
    store = LocalStore(tmp_path / "openbase.sqlite3")
    with pytest.raises(ValueError):
        store.upsert_videos([video_record(video_id)])
    with pytest.raises(ValueError):
        store.create_job("comments", video_id=video_id)


def test_startup_marks_unfinished_work_interrupted_instead_of_resuming(
    tmp_path: Path,
) -> None:
    path = tmp_path / "openbase.sqlite3"
    store = LocalStore(path)
    job = store.create_job("export")
    store.update_job(job["id"], "running")

    restarted = LocalStore(path)
    assert restarted.get_job(job["id"])["status"] == "running"
    assert restarted.interrupt_active_jobs() == 1
    recovered = restarted.get_job(job["id"])
    assert recovered is not None
    assert recovered["status"] == "interrupted"
    assert restarted.active_job_count() == 0


def test_worker_cannot_overwrite_an_interrupted_job(tmp_path: Path) -> None:
    store = LocalStore(tmp_path / "openbase.sqlite3")
    job = store.create_job("export")
    store.update_job(job["id"], "running", expected_status="queued")
    store.interrupt_active_jobs()

    from admin_app.local_store import JobStateConflictError

    with pytest.raises(JobStateConflictError):
        store.update_job(
            job["id"], "succeeded", expected_status="running"
        )
    assert store.get_job(job["id"])["status"] == "interrupted"


def test_comment_export_updates_video_summary(tmp_path: Path) -> None:
    store = LocalStore(tmp_path / "openbase.sqlite3")
    store.upsert_videos([video_record()])
    store.record_comment_export(
        "7680023068660346011",
        count=27,
        exported_at="2026-09-07T12:00:00Z",
    )
    video = store.get_video("7680023068660346011")
    assert video is not None
    assert video["comment_count"] == 27
    assert video["last_comment_export_at"] == "2026-09-07T12:00:00Z"
