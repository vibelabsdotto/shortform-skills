---
name: tiktok-pull
description: "Use when downloading TikTok videos or Photo Mode posts."
version: 1.2.0
author: Echo / VibeLabs
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [tiktok, download, scraping, curl_cffi, cookies, vibelabs]
    related_skills: [browser-automation, media-workflows]
---

# TikTok Pull (VibeLabs)

## When to Use

Load this skill whenever a task needs TikTok videos or Photo Mode posts stored
locally: single URLs, batches, or a profile's recent posts. Covers
authenticated public pulls on macOS with shared-Chrome cookies. Not for
transcripts/analysis or Instagram/YouTube downloads.

## Script Location (non-negotiable)

There is exactly ONE copy of the puller, and it lives inside this skill:

```text
~/.hermes/skills/vibelabs/tiktok-pull/scripts/tiktok_pull.py
```

**The project NEVER holds a copy of this script.** No
`shortform-content/tiktok_pull.py`, no `scripts/` helper dir, no vendored fork.
A copy in the project rots out of sync with this skill and is wrong by
definition. Do not create one, do not restore one, do not "just symlink it".

- Invoke it **by absolute path** from anywhere:
  `python3 ~/.hermes/skills/vibelabs/tiktok-pull/scripts/tiktok_pull.py …`
- Output goes **into the project**, always:
  `TT_OUT=~/VibeLabs/shortform-content/pulls`
  (the default `./pulls` is relative — never rely on it, always pin `TT_OUT`.)
- **Always state the absolute path of both** (script and output dir) when
  reporting a pull to Max. Say where the script ran from and where the files
  landed. No "irgendwo im Projekt" — absolute paths, every time.

## The One Rule

**Do NOT use yt-dlp for TikTok.** Verified 2026-08-30: TikTok serves yt-dlp's
fingerprint (all curl_cffi targets, with or without cookies) a fake
"Site Maintenance" page. Direct curl_cffi requests with the same fingerprints
work fine — yt-dlp's extractor path is what's flagged. Don't re-litigate this;
use the proven path.

## Proven Path

```text
curl_cffi(edge-fingerprint) + Shared-Chrome session cookies
  → parse __UNIVERSAL_DATA_FOR_REHYDRATION__ from video page HTML
  → pick best rendition from video.bitrateInfo
  → download PlayAddr.UrlList[0]  (FIRST url — see Pitfalls)
  → MP4 + meta.jsonl (stats, desc, duration)
```

- Working fingerprint targets: `edge` (default), `firefox`, `safari17_2_ios`,
  `safari18_4_ios`. Blocked: `chrome`, desktop `safari`.
- Canonical (and only) script: `scripts/tiktok_pull.py` inside this skill.
  See "Script Location" above — the project holds no copy.

## Cookie Setup (do this first, refresh when expired)

Cookies come from the shared Chrome (CDP port 9224, see browser-automation
skill). The account `@echo66024` is logged in there. Export via browser_exec:

```python
# browser_exec(session="tiktok-session") — requires TikTok loaded once in that Chrome
data = cdp('Storage.getCookies', **{})
tt = [c for c in data.get('cookies', []) if 'tiktok' in c.get('domain', '')]
lines = ["# Netscape HTTP Cookie File"]
for c in tt:
    dom = c.get('domain', ''); flag = "TRUE" if dom.startswith('.') else "FALSE"
    exp = int(c.get('expires', 2147483647)) if c.get('expires', -1) > 0 else 2147483647
    lines.append(f"{dom}\t{flag}\t{c.get('path','/')}\t{'TRUE' if c.get('secure') else 'FALSE'}\t{exp}\t{c['name']}\t{c['value']}")
import os
d = os.path.expanduser("~/.cache/tiktok-scrape"); os.makedirs(d, mode=0o700, exist_ok=True)
p = os.path.join(d, "cookies.txt")
open(p, "w").write("\n".join(lines) + "\n"); os.chmod(p, 0o600)
print(len(tt), "cookies →", p)
```

Verify login first: `browser_exec` → `new_tab("https://www.tiktok.com/@echo66024")`,
check `document.querySelector('[data-e2e="nav-login"]')` is absent.

**Expiry symptom:** script exits "sessionid fehlt" or page returns no
universal-data → re-export. Cookie file contains a live session; keep it at
0600, never paste values into chat or reports.

## Commands

```bash
# Project root stays clean — the script is reached by absolute path, files land in pulls/:
PULL=~/.hermes/skills/vibelabs/tiktok-pull/scripts/tiktok_pull.py
TT_OUT=~/VibeLabs/shortform-content/pulls python3 $PULL video "https://www.tiktok.com/@user/video/ID"
TT_OUT=~/VibeLabs/shortform-content/pulls python3 $PULL batch urls.txt   # one URL per line, auto-dedupes via meta.jsonl
```

Each pull: fetch video page → metadata (plays, likes, comments, shares,
saves, desc, duration) + best-rendition MP4 → `meta.jsonl` appended. 2.5s
sleep between pulls (session health).

Records in `meta.jsonl` store **absolute** paths, so a pull is reproducible
from the archive alone. If a record points at a directory that no longer
exists, the files were moved after the pull — reconcile the record, don't
re-pull.

## Photo Mode Pulls

The `tiktok_pull.py` video path does **not** support `/photo/` URLs: static HTTP
usually omits `webapp.video-detail` and raises `KeyError`. Do not retry it.
Use the logged-in shared browser and extract rendered Photo Mode images:

```python
# browser_exec(session="tiktok-session")
goto_url("https://www.tiktok.com/@HANDLE/photo/ID")
wait_for_load()
import time; time.sleep(3)
imgs = js("""
[...document.images]
  .map(i => ({src:i.src, alt:i.alt||'', w:i.naturalWidth||0, h:i.naturalHeight||0}))
  .filter(i => i.src.includes('photomode-image') && i.w >= 500 && i.h >= 500)
""")
seen = set(); slides = []
for image in imgs:
    key = image['src'].split('~tplv-photomode')[0]
    if key not in seen:
        seen.add(key); slides.append(image)
print(len(slides), "ordered slides")
```

Download each signed `src` with a browser user agent and
`Referer: https://www.tiktok.com/`. Keep DOM order, use zero-padded slide
filenames, and store a `meta.json` record with canonical URL, title, alt text,
slide count, and local paths. For batches, keep at least 2.5 seconds between
page navigations.

**Photo Mode verification:** every source URL has a record; downloaded file
count equals the sum of declared slide counts; each image decodes; dedupe uses
the URL before `~tplv-photomode`, not the full signed query string. Inspect a
contact sheet before analysis because DOM pages may repeat each slide.

- Prefer the nearest `.swiper-slide` element's `data-swiper-slide-index` when present to verify or sort original slide order. TikTok may render three copies of every slide, including `swiper-slide-duplicate` elements. URL dedupe alone proves uniqueness, not sequence.
- Scope engagement extraction to the requested post. Rendered pages can include a second autoplay post and recommendation counters. `data-e2e="favorite-count"` is the saves counter; `like-count`, `comment-count`, and `share-count` are separate. Save the first post's exact labels with its source URL. Never treat saves/likes as a view-based save rate or infer installs from engagement.
- Persist each batch before navigating onward, then aggregate unique post IDs and decoded-image counts in code. Keep originals uncropped; create separate contact sheets for review.

## Profile Pulls (2-step)

TikTok's `api/post/item_list` is X-Bogus-signed — unsigned calls return HTTP
200 with an EMPTY body. Do not fight the signature. Instead:

1. **Harvest URLs from the rendered grid** in the shared Chrome
   (browser_exec, session `tiktok-session`):

```python
goto_url("https://www.tiktok.com/@HANDLE"); wait_for_load()
import time; time.sleep(3)
for _ in range(2): js("window.scrollBy(0, 2400)"); time.sleep(2)
urls = js("""
(() => { const o = new Set();
  for (const a of document.querySelectorAll('a[href*="/video/"]'))
    if (/\\/video\\/\\d+/.test(a.href))
      { const u = new URL(a.href, location.origin); o.add(u.origin + u.pathname); }
  return [...o].slice(0, 12); })()
""")
print(urls)
```

2. Write URLs to a file and run `batch`.

This yields the ~9–15 newest posts per profile (first grid page + scroll).
Deeper paging would need the signed API — only go there if a task truly
requires it.

## Pitfalls (all verified the hard way)

- **`UrlList[0]`, never the last entry.** The LAST URL of the list returns
  HTML instead of MP4. Always take the first. Validate by checking
  `content[4:8] == b"ftyp"`.
- **curl_cffi pinning.** Brew yt-dlp tolerates curl_cffi `0.10.x–0.15.x`
  only; `0.16+` marks targets "unavailable", and brew upgrades reinstall
  `0.16.x`. Fix:
  `PY=/opt/homebrew/Cellar/yt-dlp/<version>/libexec/bin/python; $PY -m pip install -q "curl_cffi==0.15.*"`
- **Rate-limit wall.** Several pulls within minutes can trigger the
  challenge wall even on good fingerprints (fake "Maintenance" page).
  Wait it out (minutes), keep the 2.5s spacing, prefer metadata-only reads
  when no download is needed.
- **Cookie-based blocks are fingerprint-based, not auth-based.** Adding
  cookies does NOT fix yt-dlp; only the direct curl_cffi path with cookies
  works.
- **Script dependency path.** The script inserts brew's yt-dlp venv
  site-packages via `sys.path.insert`. If brew's yt-dlp version folder
  changes, update that path — or install curl_cffi elsewhere and drop it.
- **ffprobe verify** every MP4 before delivering (`duration`, `codec_name`).
  The magic-byte check (`ftyp`) catches all HTML-bait responses.
- **Never copy the script into the working project.** Verified the hard way:
  on 2026-09-03 `shortform-content/tiktok_pull.py` was created as a copy of
  this skill's script and silently drifted for two weeks. Run it by absolute
  path instead; the skill is the single source of truth.

## Risk Note

Session cookies = account `@echo66024` at the front. It's a fresh 0-follower
account; keep volumes low (batch ≤ ~15, daily cron modest, 2.5s+ spacing).
At serious volume, move to a dedicated burner before the shared profile.