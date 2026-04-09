#!/usr/bin/env python3
"""Initialize a Tech Radar episode workspace under podcast_studio/."""

import argparse
import datetime
import json
import re
from pathlib import Path


def slugify(text: str, max_len: int = 48) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return value[:max_len].strip("_") or "episode"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a podcast_studio episode workspace")
    parser.add_argument("--request", required=True, help="Original user request text")
    parser.add_argument("--topic", required=True, help="Normalized episode topic")
    parser.add_argument("--episode", required=True, type=int, help="Episode number")
    parser.add_argument("--language", default="vi", choices=["vi", "en"], help="Target audio language")
    parser.add_argument("--length", default="standard", choices=["standard", "deep-dive"], help="Episode length mode")
    parser.add_argument("--workspace-root", default="podcast_studio", help="Workspace root directory")
    parser.add_argument("--slug", default="", help="Optional custom slug")
    parser.add_argument("--guest-name", default="Minh", help="Default guest name")
    parser.add_argument("--guest-role", default="", help="Default guest role")
    parser.add_argument("--guest-gender", default="male", choices=["male", "female"], help="Default guest gender")
    return parser.parse_args()


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def write_status_markdown(workspace: Path, status_data: dict) -> None:
    lines = [f"# {workspace.name} Status", ""]
    for phase in ("initialized", "research", "outline", "script_en", "script_vi", "audio_render"):
        info = status_data.get("phases", {}).get(phase, {})
        marker = "x" if info.get("status") == "completed" else " "
        lines.append(f"- [{marker}] {phase}")
    lines.append("")
    lines.append(f"Current phase: `{status_data.get('current_phase', '')}`")
    lines.append(f"Updated: `{status_data.get('updated_at', '')}`")
    (workspace / "STATUS.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    args = parse_args()
    root = Path(args.workspace_root).expanduser().resolve()
    slug = args.slug or slugify(args.topic)
    workspace = root / f"ep{args.episode:02d}_{slug}"

    for directory in (
        workspace,
        workspace / "research",
        workspace / "research" / "raw",
        workspace / "logs",
        workspace / "cache",
        workspace / "cache" / "segments",
        workspace / "exports",
    ):
        directory.mkdir(parents=True, exist_ok=True)

    today = datetime.date.today().isoformat()
    now = datetime.datetime.now().isoformat(timespec="seconds")

    request_data = {
        "original_request": args.request,
        "normalized_topic": args.topic,
        "episode": args.episode,
        "language": args.language,
        "length": args.length,
        "created_at": now,
        "assumptions": [],
        "overrides": {
            "slug": slug,
        },
    }
    write_json(workspace / "request.json", request_data)

    episode_data = {
        "topic": args.topic,
        "episode": args.episode,
        "date": today,
        "language": args.language,
        "length": args.length,
        "voice_style": {
            "region": "",
            "pace": "",
            "energy": "",
            "style": [],
        },
        "guests": [
            {
                "name": args.guest_name,
                "role": args.guest_role,
                "gender": args.guest_gender,
                "voice_profile": "auto",
            }
        ],
    }
    write_json(workspace / "episode.json", episode_data)

    status_data = {
        "workspace": str(workspace),
        "current_phase": "initialized",
        "updated_at": now,
        "phases": {
            "initialized": {
                "status": "completed",
                "updated_at": now,
            },
            "research": {
                "status": "pending",
                "updated_at": now,
            },
            "outline": {
                "status": "pending",
                "updated_at": now,
            },
            "script_en": {
                "status": "pending",
                "updated_at": now,
            },
            "script_vi": {
                "status": "pending",
                "updated_at": now,
            },
            "audio_render": {
                "status": "pending",
                "updated_at": now,
            },
        },
    }
    write_json(workspace / "status.json", status_data)
    write_status_markdown(workspace, status_data)

    workspace_manifest = {
        "workspace": str(workspace),
        "episode": workspace.name,
        "request": str(workspace / "request.json"),
        "episode_config": str(workspace / "episode.json"),
        "status": str(workspace / "status.json"),
        "research": {
            "dir": str(workspace / "research"),
            "raw_dir": str(workspace / "research" / "raw"),
            "merged": str(workspace / "research" / "research.json"),
        },
        "logs_dir": str(workspace / "logs"),
        "cache": {
            "segments_dir": str(workspace / "cache" / "segments"),
        },
        "exports_dir": str(workspace / "exports"),
        "updated_at": now,
    }
    write_json(workspace / "workspace_manifest.json", workspace_manifest)

    print(str(workspace))


if __name__ == "__main__":
    main()
