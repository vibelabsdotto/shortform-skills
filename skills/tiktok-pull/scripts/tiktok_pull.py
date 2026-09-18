#!/usr/bin/env python3
"""
TikTok Pull — authentifizierter Video/Metadaten-Loader für VibeLabs.

Bewiesener Pfad (2026-08-30):
  curl_cffi(edge-Fingerprint) + Shared-Chrome-Session-Cookies
  → universal-data parsen → beste Rendition, ERSTE UrlList-URL → MP4 + JSONL.

Cookie-Refresh (wenn 'sessionid fehlt'):
  im Shared-Chrome (CDP 9224) TikTok einmal laden, dann Storage.getCookies
  via browser_exec neu exportieren → ~/.cache/tiktok-scrape/cookies.txt

Profil-Pull (2 Schritte, da item_list-API signiert ist — X-Bogus):
  1) browser_exec(session='tiktok-session'):
     goto_url("https://www.tiktok.com/@HANDLE"); wait_for_load(); sleep 3;
     2x js("window.scrollBy(0, 2400)"); dann Video-hrefs aus dem Grid lesen
     (JS-Snippet siehe SKILL.md 'Profile Pulls').
  2) URLs in eine Datei (eine pro Zeile) und:
     python3 tiktok_pull.py batch urls.txt

Usage:
  python3 tiktok_pull.py video <URL> [URL ...]
  python3 tiktok_pull.py batch <urls.txt>
"""
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "/opt/homebrew/Cellar/yt-dlp/2026.7.4/libexec/lib/python3.14/site-packages")
import curl_cffi.requests as cr

TARGET = "edge"  # verifiziert; Alternativen: safari17_2_ios, firefox, safari18_4_ios
COOKIES = Path.home() / ".cache/tiktok-scrape/cookies.txt"
UA_LANG = {"Accept-Language": "en-US,en;q=0.9"}


def load_jar():
    jar = {}
    for line in COOKIES.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        p = line.split("\t")
        if len(p) == 7:
            jar[p[5]] = p[6]
    if "sessionid" not in jar:
        sys.exit("FEHLER: sessionid fehlt in cookies.txt → Re-Export nötig (siehe SKILL.md).")
    return jar


def fetch_scope(url, jar):
    r = cr.get(url, timeout=25, impersonate=TARGET, cookies=jar, headers=UA_LANG)
    if r.status_code != 200:
        sys.exit(f"HTTP {r.status_code} für {url}")
    i = r.text.find("__UNIVERSAL_DATA_FOR_REHYDRATION__")
    if i == -1:
        if "Maintenance" in r.text:
            sys.exit(f"BLOCKIERT (Fingerprint-Wall) für {url} → anderen TARGET probieren.")
        sys.exit(f"Keine Universal-Daten für {url} (Challenge/Rate-Limit?).")
    s = r.text.find(">", i) + 1
    e = r.text.find("</script>", s)
    return json.loads(r.text[s:e])["__DEFAULT_SCOPE__"]


def known_ids(outdir):
    meta = outdir / "meta.jsonl"
    if not meta.exists():
        return set()
    return {json.loads(l).get("id") for l in meta.read_text().splitlines() if l.strip()}


def pull_video(url, jar, outdir, skip_if_done=True):
    vid_id = url.rstrip("/").rsplit("/", 1)[-1]
    if skip_if_done and vid_id in known_ids(outdir):
        print(f"  ✓ {vid_id} bereits im Archiv — skip")
        return None
    scope = fetch_scope(url, jar)
    detail = scope["webapp.video-detail"]
    if detail.get("statusCode") != 0:
        print(f"  - {vid_id} SKIP (statusCode {detail.get('statusCode')})")
        return {"id": vid_id, "skipped": True}
    item = detail["itemInfo"]["itemStruct"]

    rends = item["video"].get("bitrateInfo", [])
    best = max(rends, key=lambda x: x.get("Bitrate", 0)) if rends else None
    urls = (best or {}).get("PlayAddr", {}).get("UrlList") or [item["video"].get("playAddr")]
    # WICHTIG: ERSTE URL der Liste — die letzte liefert HTML statt MP4.
    vr = cr.get(urls[0], timeout=120, impersonate=TARGET, cookies=jar,
                headers={"Referer": "https://www.tiktok.com/", **UA_LANG})
    if b"ftyp" not in vr.content[4:8]:
        print(f"  - {vid_id} SKIP (kein MP4, {len(vr.content)} B)")
        return {"id": vid_id, "skipped": True, "reason": "no-mp4"}

    f = outdir / f"{item['author']['uniqueId']}_{vid_id}.mp4"
    f.write_bytes(vr.content)

    rec = {
        "id": vid_id,
        "url": url,
        "author": "@" + item["author"]["uniqueId"],
        "desc": item.get("desc", ""),
        "created": item.get("createTime"),
        "file": str(f),
        "bytes": len(vr.content),
        "bitrate": best["Bitrate"] if best else None,
        "duration": item["video"].get("duration"),
        "stats": {k: item.get("stats", {}).get(k) for k in
                  ("playCount", "diggCount", "commentCount", "shareCount", "collectCount")},
    }
    with (outdir / "meta.jsonl").open("a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    st = rec["stats"]
    print(f"  ↓ {vid_id} {len(vr.content):>11,} B | {st['playCount']:,} plays | {st['diggCount']:,} likes | {rec['desc'][:36]}")
    return rec


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    mode = args[0]
    out = Path(os.environ.get("TT_OUT", "pulls"))
    out.mkdir(parents=True, exist_ok=True)
    jar = load_jar()

    if mode == "video":
        for u in args[1:]:
            pull_video(u, jar, out)
            time.sleep(2.5)
    elif mode == "batch":
        urls = [l.strip() for l in Path(args[1]).read_text().splitlines() if l.strip().startswith("http")]
        print(f"{len(urls)} URLs → {out}")
        for n, u in enumerate(urls):
            print(f"[{n+1}/{len(urls)}]")
            pull_video(u, jar, out)
            time.sleep(2.5)
    else:
        sys.exit(f"Unbekannter Modus: {mode}\n{__doc__}")
    print(f"fertig → {out.resolve()}")


if __name__ == "__main__":
    main()