---
name: pinterest
description: Use when finding Pinterest pins for visual reference.
version: 1.1.0
author: 0xs4m1337 (openclaw/skills)
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [pinterest, inspiration, moodboard, images, browser-automation]
    related_skills: [browser-automation, artifact-routing]
---

# Pinterest references

Use Pinterest exclusively for visual research, inspiration, and internal moodboards. Find references, inspect their composition, and deliver actual images with source links.

## When to use

- Find visual directions for photography, design, styling, or creative concepts.
- Collect reference images for a moodboard.
- Research visible pin titles and descriptions for creative angles.

## Prerequisites

Load `browser-automation` before browsing and `artifact-routing` before saving files. Use public Pinterest pages. The download helper requires Python 3 and macOS `sips` for dimension checks.

## Procedure

1. Search Pinterest in the browser with concrete visual terms. Open the first page with `new_tab`, then call `wait_for_load`. Example URL: `https://www.pinterest.com/search/pins/?q=minimalist+desk+setup`.
2. Inspect the rendered page with `js` or the accessibility tree. Collect image URLs from `img` elements and rendered page data containing `i.pinimg.com`. Pinterest renders search results client-side; raw HTML fetching is not a reliable search method.
3. Open useful pins for detail when available. Record the pin URL and any original source link. If a permalink is unavailable, record the search URL and label it as a search source. Never invent pin IDs.
4. Prefer observed `https://i.pinimg.com/originals/...` URLs with their exact extension. If only a thumbnail URL is available, try replacing its size segment with `originals`, then verify the download.
5. Save collected URLs in JSON, either a list of URL strings or `{"pins": [{"url": "<image-url>"}]}`. Deduplicate in code. For multi-image requests, keep batches on disk and verify the final count against the requested count.
6. Run the bundled downloader through `terminal`, resolving the script path from this skill's directory:
   ```
   python3 <skill-dir>/scripts/fetch_pins.py --pins <pins.json> --out <absolute-output-directory>
   ```
7. Inspect the manifest and actual image dimensions. Reject unreadable files and irrelevant avatars. Use `vision_analyze` to inspect downloaded images before describing or selecting them.
8. Deliver selected images using `MEDIA:/absolute/path/to/image` on separate lines, plus concise source links and what makes each reference useful. Preserve original dimensions and composition unless the user explicitly requests a crop or resize.

## Pitfalls

- Thumbnail extensions may differ from the original asset. A `.jpg` thumbnail can belong to a `.png` original. Try the alternative extension if an original request fails, but do not assume every 403 means an extension mismatch.
- Prefer observed originals over guessed larger thumbnail URLs. Label lower-resolution fallbacks honestly.
- Filter by real pixel dimensions, not file size. The helper removes images below 400 pixels on the short edge, but files with unknown dimensions require manual rejection.
- Public search results can omit pin links and load only a small initial batch. Scroll for more; do not mistake the first screen for the complete results.
- If Pinterest blocks public access, use `web_search` with `site:pinterest.com` to discover public references. Report inaccessible content instead of claiming it was inspected.
- If image retrieval fails but the pin is visible, a browser screenshot can serve as a clearly labeled reference capture. It is not the original image.
- Pins are third-party works. Reference collection does not grant publication rights. Use owned or licensed assets for published work.

## Verification

- Every delivered local file exists and decodes as an image with nonzero dimensions.
- References match the requested visual direction and retain their composition.
- Source links are observed URLs, with search sources distinguished from pin permalinks.
- Requested counts are checked against deduplicated, usable images. Report any shortfall.
