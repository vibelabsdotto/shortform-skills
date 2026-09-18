# VibeLabs Shortform Skills

Public shortform stack: strategy + ops + pull. Built for organic TikTok/Shorts testing.

## Skills

### 1. creative-shortform-process
The organic creative loop: Problem → Content → Testing → Winner → Variation → Distribution.
- Demand-Check before every angle
- 20 angles per problem, 10 hooks × 3 formats = 30 posts per batch
- Hook templates (Type A–E) in `references/hook-templates.md`
- App is the solution, comes late. Problem is the topic.

Use for: "Was posten wir diese Woche?", hook ideas, funnel diagnosis, winner analysis.

### 2. shortform-operations
The ops layer: where strategy lives in the workspace.
- `brands/<brand>/<format>/` — one account = one asset format
- `angles.md` (status lifecycle) + `batches/YYYY-MM-DD-batchNN-<slug>/batch.md` (6 parts) + `performance.md` (append-only, 48h)
- Batch size: 10 hooks × 1 account format = 10 posts
- `scripts/slide_overlay.py` — Pillow text overlay + ffmpeg concat pipeline

Use for: content plans, angle batches, tracking.

### 3. tiktok-pull
TikTok video + Photo Mode downloader. Proven path only.
- `curl_cffi (edge fingerprint) + session cookies → universal-data → best rendition → MP4 + meta.jsonl`
- No yt-dlp for TikTok (fingerprint-walled, verified 2026-08-30)
- `scripts/tiktok_pull.py` — `video <URL>` / `batch urls.txt` modes

Setup: export session cookies from logged-in Chrome → `~/.cache/tiktok-scrape/cookies.txt`, set `TT_OUT` to your pulls dir.

```
PULL=~/.hermes/skills/tiktok-pull/scripts/tiktok_pull.py
TT_OUT=./pulls python3 $PULL video "https://www.tiktok.com/@user/video/ID"
```

## Structure

```
skills/
├── creative-shortform-process/SKILL.md + references/
├── shortform-operations/SKILL.md + scripts/
└── tiktok-pull/SKILL.md + scripts/
```

Adapt paths (`TT_OUT`, skill install dir) to your setup. Internal VibeLabs paths stripped for public use.
