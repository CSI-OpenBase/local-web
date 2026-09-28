#!/usr/bin/env python3
"""Export the OpenBase video archive used to connect works in CSI Core."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from admin_app.csi_work_links import (  # noqa: E402
    build_csi_work_archive,
    build_csi_work_archive_rows,
)
from admin_app.local_config import load_local_settings  # noqa: E402
from admin_app.local_store import LocalStore  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="output XLSX file")
    return parser


def _write_bytes_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            Path(temporary_name).unlink()
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_local_settings()
    settings.ensure_directories()
    store = LocalStore(settings.database_path)
    videos = store.list_videos(limit=100_000)
    content = build_csi_work_archive(videos)
    count = len(build_csi_work_archive_rows(videos))
    timestamp = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d-%H%M%S")
    output = (args.output or settings.exports_dir / f"作品档案-{timestamp}.xlsx").resolve()
    _write_bytes_atomic(output, content)
    print(f"Exported {count} work identities: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
