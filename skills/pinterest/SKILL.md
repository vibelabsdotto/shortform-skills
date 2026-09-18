---
name: pinterest
description: Use when finding Pinterest pins for visual inspiration.
version: 1.0.2
author: 0xs4m1337 (openclaw/skills)
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [pinterest, inspiration, moodboard, images, browser-automation, stock-imagery]
    related_skills: [creative-artifact-production, app-ad-creative-mining]
    source: "openclaw-skills-pinterest @ lobehub market v1.0.2"
    installed: "2026-09-17"
    payload_audit: "sha256 verified vs marketplace fileHashes; network scope limited to pinterest.com/i.pinimg.com"
---

# Pinterest Skill

Search and browse Pinterest pins — delivers actual images, not just links.
Also covered: high-res original retrieval, moodboard capture, and free
third-party imagery for slide backgrounds.

## Quick Search & Send Images

### Step 1: Search Pinterest
```
browser action=navigate url="https://www.pinterest.com/search/pins/?q=YOUR+SEARCH+TERMS"
browser action=snapshot
```

### Step 2: Get High-Res Image URLs
From the snapshot, find image URLs. Pinterest images follow this pattern:
- Thumbnail: `https://i.pinimg.com/236x/...`
- Medium: `https://i.pinimg.com/564x/...`
- **High-res: `https://i.pinimg.com/originals/...`**

To get high-res: replace `236x` or `564x` with `originals` in the URL.

### Step 3: Send Images to User
**Send actual image (not link!):**
```
message action=send media="https://i.pinimg.com/originals/xx/xx/image.jpg" message="Pin description here"
```

**Send multiple images:**
```
message action=send media="https://i.pinimg.com/originals/..." message="Option 1: Modern minimal"
message action=send media="https://i.pinimg.com/originals/..." message="Option 2: Cozy rustic"
```

## Detailed Pin Workflow

1. **Navigate** to Pinterest search
2. **Snapshot** to see results
3. **Click** on a pin for details (gets larger image)
4. **Screenshot** the pin detail page OR extract originals URL
5. **Send image** via message tool with `media=` parameter

### Getting Original Images
When on a pin detail page:
- Look for `<img>` with `src` containing `i.pinimg.com`
- Convert to originals: `https://i.pinimg.com/originals/{hash}.jpg`

## Example: "Find me minimalist desk setups"

```
# 1. Search
browser action=navigate url="https://www.pinterest.com/search/pins/?q=minimalist+desk+setup"
browser action=snapshot

# 2. Extract image URLs from snapshot (look for i.pinimg.com)
# 3. Convert to high-res originals

# 4. Send images
message action=send media="https://i.pinimg.com/originals/ab/cd/ef123.jpg" message="Clean white desk with plant 🌿"
message action=send media="https://i.pinimg.com/originals/gh/ij/kl456.jpg" message="Wooden desk, natural light ☀️"
```

## Alternative: Screenshot Method

If image URL extraction is tricky, screenshot the pin:
```
browser action=navigate url="https://www.pinterest.com/pin/123456/"
browser action=screenshot
# Then send the screenshot file
message action=send filePath="/path/to/screenshot.jpg" message="Here's the pin!"
```

## API Method (For User's Own Content)

Requires OAuth token setup — see `references/oauth-setup.md`

```bash
export PINTEREST_ACCESS_TOKEN="your_token"
python3 scripts/pinterest_api.py boards
python3 scripts/pinterest_api.py board-pins <board_id>
python3 scripts/pinterest_api.py pin <pin_id>
```

## Key Points

- ✅ **Always send images directly** using `media=` parameter
- ✅ Use `originals` URLs for high-res
- ❌ Don't just send links — send the actual image
- 💡 If URL doesn't work, screenshot the pin and send that

## References

- OAuth setup: `references/oauth-setup.md`
- API endpoints: `references/api-reference.md`

---

# Hermes Adaptation (Echo)

The instructions above are written for OpenClaw tool syntax. In Hermes the
capabilities are the same but the calls differ. Read this section first; the
workflow above still applies.

## Tool mapping

| Skill says | Hermes equivalent |
|---|---|
| `browser action=navigate url=...` | `browser_exec`: `new_tab("...")` then `wait_for_load()` |
| `browser action=snapshot` | `js('document.body.innerText')`, or `cdp('Accessibility.getFullAXTree')` |
| `browser action=screenshot` | `capture_screenshot()` (path returns into context) |
| `message action=send media=<url>` | `MEDIA:<absolute-path>` on its own line — local files only |
| `message action=send filePath=...` | same: `MEDIA:<absolute-path>` |

## Sending images: the important difference

Hermes renders **local** files via `MEDIA:`; remote URLs do not render in the
Desktop chat (remote `![alt](url)` does). So the "send the actual image" intent
becomes: **download the original to disk, then emit `MEDIA:/abs/path`.**

```bash
mkdir -p ~/.hermes/tmp/pinterest && curl -sL -o ~/.hermes/tmp/pinterest/pin1.jpg "<originals-url>"
file ~/.hermes/tmp/pinterest/pin1.jpg   # confirm it's really an image, not a block page
```

Never emit a `MEDIA:` line for a path that does not exist.

## Credential-free path (default)

No OAuth needed for search/inspiration. **The browser is the working path —
there is no reliable script fallback for search:**

`scripts/pinterest_api.py search` is effectively dead. Pinterest serves the
search grid client-side, so the script's regexes over raw HTML return `[]`
(confirmed 2026-09-17). Use the browser:

```python
new_tab("https://www.pinterest.com/search/pins/?q=home+gym+aesthetic")
wait_for_load()
# pin images are NOT in a[href="/pin/..."] for logged-out sessions.
# Scrape them out of the rendered HTML instead:
js(r"""(()=>{
  const h=document.documentElement.innerHTML;
  const re=/https:\/\/i\.pinimg\.com\/(236x|474x|564x|736x|originals)\/([a-zA-Z0-9]{2}\/[a-zA-Z0-9]{2}\/[a-zA-Z0-9]{2}\/[a-zA-Z0-9]+\.(?:jpg|png|webp))/g;
  ...
})()""")
```

Then **download to disk** and emit `MEDIA:` lines. `scripts/fetch_pins.py` does
the download + dimension filtering end to end — reuse it instead of rewriting.

## How Pinterest actually serves images (verified 2026-09-17)

Three rules the upstream docs get wrong. These decide whether you get a real
image, a 403, or a thumbnail pretending to be a photo:

1. **The `.jpg` suffix in a thumbnail URL is a lie.** Pinterest serves the
   *thumbnail* path with `.jpg` even when the stored asset is a **PNG**. The URL
   text and the real bytes disagree.
2. **Requesting the wrong extension on a larger size returns HTTP 403,** not a
   fallback. `<asset>.png` exists at `/originals/` but `/736x/<asset>.jpg` → 403.
   So a 403 on `736x` does **not** mean the pin is gone; it usually means try the
   other extension or go up to `/originals/`.
3. **`/originals/` is the one that works, and it keeps the true extension.** Pull
   `/originals/<path>` as-is from the page. It is the highest-yield size and, for
   these pins, succeeded 16/16 while `736x` failed 4/8.

## Pitfalls (verified in practice)

- **Filter by real pixel dimensions, never by file size.** Pinterest injects
  small square **avatars** into the same `i.pinimg.com` URL space (e.g.
  `256x256`, 43 KB PNG). They pass a naive "is it a real image" check and will
  land in your moodboard as a broken-looking thumbnail. Read actual dimensions
  (`sips -g pixelWidth -g pixelHeight` on macOS) and drop anything under ~400px
  on the short edge. In testing: 16 raw hits → **15 real photos, 1 avatar**.
- **`originals` can be multi-MB** (2.3 MB and 2500x3750 in testing). Correct for
  reference capture; resize before using as a slide background.
- **Logged-out Pinterest exposes no pin IDs.** There are zero
  `a[href*="/pin/"]` links and no `"id":"<pinid>"` near image URLs, so you
  cannot build a permalink without a logged-in session. Deliver the searched
  URL as the reference, or use the logged-in shared browser.
- **~16 pins per logged-out search page**, lazy-loaded. More requires scrolling.
- **Attribution.** Pins are third-party works. Fine for internal reference and
  moodboards; for anything published, prefer the user's own or licensed assets.
- **The API half needs credentials and consent.** `boards` / `board-pins` require
  `PINTEREST_ACCESS_TOKEN` from a Pinterest developer app. Do not set this up or
  use a token without explicit approval.
- **Pin metadata is a data source.** Titles/descriptions/reaction counts from
  pins are useful raw material for hook and angle research, not just images.
