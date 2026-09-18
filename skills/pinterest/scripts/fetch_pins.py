#!/usr/bin/env python3
"""
Pinterest pin fetcher — credential-free.

Takes pin image URLs (as scraped from a Pinterest search page) and downloads the
usable high-res images to a target directory, filtering out the small square
avatars Pinterest injects into the same URL space.

Why this exists instead of scripts/pinterest_api.py search:
  Pinterest renders the search grid client-side, so the upstream script's regexes
  over raw HTML return [] . The browser is the only working discovery path; this
  script owns the download + filtering half.

Verified behaviour (2026-09-17):
  - /originals/<path> keeps the TRUE extension and worked 16/16
  - requesting the wrong extension on a larger size returns 403, not a fallback
  - thumbnails are served as .jpg even when the asset is a .png
  - filter by real pixel dimensions, never file size (avatars are 256x256)

Usage:
  python3 fetch_pins.py --pins pins.json --out ~/.hermes/tmp/pinterest

Input JSON: either
  {"pins": [{"url": "https://i.pinimg.com/originals/ab/cd/ef/<hash>.jpg"}, ...]}
or a bare list of URL strings.
"""
import argparse, json, os, subprocess, sys, urllib.request

UA = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36'
}
MIN_EDGE = 400  # drop anything smaller on its short edge (avatars are 256x256)


def pixel_dims(path):
    """Real pixel dimensions via macOS sips. Falls back to (0, 0)."""
    try:
        r = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', path],
                           capture_output=True, text=True)
        w = h = 0
        for line in r.stdout.splitlines():
            if 'pixelWidth' in line:
                w = int(line.split(':')[1])
            elif 'pixelHeight' in line:
                h = int(line.split(':')[1])
        return w, h
    except Exception:
        return 0, 0


def load_urls(path):
    data = json.load(open(path))
    if isinstance(data, dict):
        data = data.get('pins', [])
    urls = []
    for item in data:
        if isinstance(item, str):
            urls.append(item)
        elif isinstance(item, dict) and item.get('url'):
            urls.append(item['url'])
    return urls


def candidates(url):
    """Same asset, in the order most likely to yield a usable image.

    /originals/ keeps the true extension, so try it first; then the other
    extension on the same size, then 736x. A 403 usually means wrong extension.
    """
    base, ext = os.path.splitext(url)
    other = '.png' if ext.lower() in ('.jpg', '.jpeg') else '.jpg'
    yield url
    yield base + other
    for size in ('736x', '564x'):
        for e in (ext, other):
            yield url.replace('/originals/', '/' + size + '/').rsplit('.', 1)[0] + e


def main():
    ap = argparse.ArgumentParser(description='Download Pinterest pins, filter junk.')
    ap.add_argument('--pins', required=True, help='JSON file of pin URLs')
    ap.add_argument('--out', required=True, help='Output directory')
    ap.add_argument('--limit', type=int, default=0, help='Max pins (0 = all)')
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    urls = load_urls(args.pins)
    if args.limit:
        urls = urls[:args.limit]

    results = []
    for url in urls:
        stem = os.path.basename(url).rsplit('.', 1)[0][:12]
        dest = None
        for cand in candidates(url):
            ext = os.path.splitext(cand)[1] or '.jpg'
            path = os.path.join(args.out, 'pin_%s%s' % (stem, ext))
            try:
                req = urllib.request.Request(cand, headers=UA)
                with urllib.request.urlopen(req, timeout=25) as r:
                    body = r.read()
                if len(body) < 2000:
                    continue
                with open(path, 'wb') as f:
                    f.write(body)
                dest = path
                break
            except Exception:
                continue

        if not dest:
            results.append({'url': url, 'status': 'FAIL', 'file': None})
            continue

        w, h = pixel_dims(dest)
        # dimension filter, NOT file size — avatars are small but plausible-looking
        if 0 < min(w, h) < MIN_EDGE:
            os.remove(dest)
            results.append({'url': url, 'status': 'JUNK', 'w': w, 'h': h, 'file': None})
        else:
            results.append({'url': url, 'status': 'OK', 'w': w, 'h': h,
                            'kb': round(os.path.getsize(dest) / 1024), 'file': dest})

    ok = [r for r in results if r['status'] == 'OK']
    junk = [r for r in results if r['status'] == 'JUNK']
    fail = [r for r in results if r['status'] == 'FAIL']

    json.dump(results, open(os.path.join(args.out, 'manifest.json'), 'w'), indent=2)
    print('total %d  usable %d  junk %d  failed %d' % (len(results), len(ok), len(junk), len(fail)))
    for r in sorted(ok, key=lambda x: -x.get('kb', 0)):
        print('  OK    %sx%-6s %6s KB  %s' % (r['w'], r['h'], r['kb'], os.path.basename(r['file'])))
    for r in junk:
        print('  JUNK  %sx%s (below %dpx short edge)' % (r.get('w'), r.get('h'), MIN_EDGE))
    for r in fail:
        print('  FAIL  %s' % r['url'][:90])

    # emit MEDIA lines for the Desktop chat
    if ok:
        print()
        print('--- MEDIA lines ---')
        for r in ok:
            print('MEDIA:' + r['file'])

    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
