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

# GitHub image URL host patterns we want to self-host.
GH_HOST_RE = r'https://(?:user-images\.githubusercontent\.com|github\.com/user-attachments|raw\.githubusercontent\.com|private-user-images\.githubusercontent\.com)[^"\'\s)]+'

# Standard markdown embed: ![alt](url)
GH_IMG_MD_RE = re.compile(rf'!\[([^\]]*)\]\(({GH_HOST_RE})\)')

# HTML <img> tag with src pointing at a GitHub host — GitHub now inserts
# these instead of markdown when you drag/paste an image into the issue.
GH_IMG_HTML_RE = re.compile(r'<img\b[^>]*/?>', re.IGNORECASE)


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


def _try_dl(url: str, dest_dir: Path) -> str | None:
    try:
        local = _download(url, dest_dir)
        print(f'  ↳ downloaded {url} → {local}')
        return local
    except Exception as e:
        print(f'  ↳ WARN: could not fetch {url}: {e}', file=sys.stderr)
        return None


def rewrite_images(body: str, date_str: str) -> str:
    """Replace GitHub-hosted image URLs in the body with local paths.

    Handles both markdown embeds (![alt](url)) and HTML <img src=...> tags
    (GitHub inserts <img> when you drag/paste an image into an issue).
    Both formats are normalised to markdown pointing at a local asset.

    Falls back to the original text if download fails."""
    dest_dir = IMG_DIR_BASE / date_str

    def md_repl(m: re.Match) -> str:
        alt, url = m.group(1), m.group(2)
        local = _try_dl(url, dest_dir)
        return f'![{alt}]({local})' if local else m.group(0)

    def html_repl(m: re.Match) -> str:
        tag = m.group(0)
        src_m = re.search(r'\bsrc=["\']([^"\']+)["\']', tag)
        if not src_m:
            return tag
        url = src_m.group(1)
        # Only self-host GitHub-hosted URLs; leave external images alone
        if not re.search(r'(user-attachments|githubusercontent)', url):
            return tag
        alt_m = re.search(r'\balt=["\']([^"\']*)["\']', tag)
        alt = alt_m.group(1) if alt_m else ''
        local = _try_dl(url, dest_dir)
        return f'![{alt}]({local})' if local else tag

    body = GH_IMG_MD_RE.sub(md_repl, body)
    body = GH_IMG_HTML_RE.sub(html_repl, body)
    return body


def main() -> int:
    body = os.environ.get("ISSUE_BODY", "").strip()
    title = os.environ.get("ISSUE_TITLE", "").strip()
    created_at = os.environ["ISSUE_CREATED_AT"]
    issue_number = os.environ.get("ISSUE_NUMBER", "").strip()

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

    # Idempotency backstop: tag each entry with an invisible marker keyed by
    # issue number. If the workflow ever fires more than once for the same
    # issue (e.g. GitHub emitting duplicate events), the second run sees the
    # marker already present and skips — so an issue can never be published
    # twice. The marker is an HTML comment, invisible in the rendered page.
    marker = f"<!-- issue:{issue_number} -->" if issue_number else ""
    entry = f"\n{marker}\n\n## {time_str}\n\n{content}\n"

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        if marker and marker in existing:
            print(f"Issue #{issue_number} already published in {target} — skipping.")
            return 0
        target.write_text(existing.rstrip() + "\n" + entry, encoding="utf-8")
        print(f"Appended to {target}")
    else:
        frontmatter = f"---\ndate: {date_str}\n---\n"
        target.write_text(frontmatter + entry, encoding="utf-8")
        print(f"Created {target}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
