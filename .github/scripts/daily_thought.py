#!/usr/bin/env python3
"""Convert a GitHub issue into a daily thought entry.

Reads issue metadata from env vars (set by workflow), then either creates a
new _daily/YYYY-MM-DD.md file or appends to an existing one. Timestamp
is in JST (user's local time). Any images pasted into the issue (GitHub
user-attachments CDN URLs) are downloaded and rewritten to point at local
assets so the daily entry stays self-contained if GitHub ever moves URLs."""

import hashlib
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

JST = timezone(timedelta(hours=9))
DAILY_DIR = Path("_daily")
IMG_DIR_BASE = Path("assets/images/daily")

# Match ![alt](url) where url is a GitHub-hosted image (either legacy
# user-images CDN, the newer user-attachments URL, or a raw.githubusercontent
# pointer that a user might paste in).
GH_IMG_RE = re.compile(
    r'!\[([^\]]*)\]\('
    r'(https://(?:user-images\.githubusercontent\.com'
    r'|github\.com/user-attachments'
    r'|raw\.githubusercontent\.com)[^)\s]+)'
    r'\)'
)


def _guess_ext(url: str) -> str:
    """Return a safe file extension based on the URL."""
    last = url.split('?', 1)[0].rsplit('/', 1)[-1]
    m = re.search(r'\.([A-Za-z0-9]{2,5})$', last)
    ext = (m.group(1).lower() if m else 'png')
    if ext not in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'avif'}:
        ext = 'png'
    return ext


def _download(url: str, dest_dir: Path) -> str:
    """Download url into dest_dir under a deterministic filename (SHA1 of
    URL). Return the site-absolute path suitable for `![](...)`."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    fname = hashlib.sha1(url.encode()).hexdigest()[:12] + '.' + _guess_ext(url)
    target = dest_dir / fname
    if not target.exists():
        req = urllib.request.Request(url, headers={'User-Agent': 'daily-thought-bot'})
        with urllib.request.urlopen(req, timeout=20) as resp:
            target.write_bytes(resp.read())
    # Site-absolute path (Jekyll will resolve /assets/... at build time)
    return '/' + target.as_posix()


def rewrite_images(body: str, date_str: str) -> str:
    """Replace any GitHub-hosted image URLs in the body with local paths.

    If download fails, the original URL is kept so the entry still renders."""
    dest_dir = IMG_DIR_BASE / date_str

    def _repl(m: re.Match) -> str:
        alt, url = m.group(1), m.group(2)
        try:
            local = _download(url, dest_dir)
            print(f'  ↳ downloaded {url} → {local}')
            return f'![{alt}]({local})'
        except Exception as e:
            print(f'  ↳ WARN: could not fetch {url}: {e}', file=sys.stderr)
            return m.group(0)

    return GH_IMG_RE.sub(_repl, body)


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

    # Rewrite any embedded GitHub-hosted images to local paths so the
    # daily entry is self-contained.
    body = rewrite_images(body, date_str)

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
