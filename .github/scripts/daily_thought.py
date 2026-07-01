#!/usr/bin/env python3
"""Convert a GitHub issue into a daily thought entry.

Reads issue metadata from env vars (set by workflow), then either creates a
new _daily/YYYY-MM-DD.md file or appends to an existing one. Timestamp
is in JST (user's local time)."""

import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
DAILY_DIR = Path("_daily")


def main() -> int:
    body = os.environ.get("ISSUE_BODY", "").strip()
    title = os.environ.get("ISSUE_TITLE", "").strip()
    created_at = os.environ["ISSUE_CREATED_AT"]

    if not body:
        print("Empty body — skipping.")
        return 0

    # Normalise GitHub's line endings and strip stray zero-width chars
    body = body.replace("\r\n", "\n").strip()

    # Convert issue creation time (UTC ISO) to JST
    dt_utc = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    dt_jst = dt_utc.astimezone(JST)
    date_str = dt_jst.strftime("%Y-%m-%d")
    time_str = dt_jst.strftime("%H:%M")

    # If the title is meaningful (not just a placeholder like "Daily"), use it
    # as a bold heading before the body. Otherwise, just body.
    is_placeholder_title = (
        not title
        or title.lower() in {"daily", "thought", "todo", "note"}
        or re.match(r"^\d{4}-\d{2}-\d{2}", title)
    )
    if is_placeholder_title:
        content = body
    else:
        content = f"**{title}**\n\n{body}"

    DAILY_DIR.mkdir(exist_ok=True)
    target = DAILY_DIR / f"{date_str}.md"

    entry = f"\n## {time_str}\n\n{content}\n"

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        target.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
        print(f"Appended to {target}")
    else:
        frontmatter = f"---\ndate: {date_str}\n---\n"
        target.write_text(frontmatter + entry, encoding="utf-8")
        print(f"Created {target}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
