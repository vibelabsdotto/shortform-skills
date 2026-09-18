---
name: bg-removal
description: Use when removing backgrounds from images locally with AI (transparent PNG cutouts, freestellen, product shots, logos, portraits). Global rembg + BiRefNet install on Max's Mac.
version: 1.0.0
author: VibeLabs
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [images, background-removal, rembg, birefnet, onnx, transparent, cutout, local-ai]
    related_skills: [artifact-routing]
---

# Local Background Removal (rembg + BiRefNet)

100% lokale AI-Hintergrundentfernung auf Max's Mac. Kein API-Key, keine Cloud, keine Uploads.
Setup läuft global: `rembg` ist im PATH (via `~/.local/bin/rembg`), das beste Modell (`birefnet-general`, ~973 MB) liegt fertig in `~/.u2net/`.

## Wann nutzen

- Hintergrund aus Bildern entfernen → transparentes PNG (Logos, Produktfotos, Porträts, Fotos für Web/Marketing)
- Batch: ganzen Ordner freistellen
- Maske (nur Alpha/Silhouette) oder Ersatz-Hintergrundfarbe erzeugen

## Grundbefehle

```bash
# Einzelnes Bild (Standard: bestes Modell)
rembg i -m birefnet-general input.png output.png

# Ordner-Batch (session reuse → schneller)
rembg p -m birefnet-general input_dir/ output_dir/

# Nur Maske (weiß=Objekt, schwarz=Hintergrund)
rembg i -m birefnet-general -om input.png mask.png

# Auf Farbhintergrund statt Transparenz legen (R,G,B,A)
rembg i -m birefnet-general -bgc "255,255,255,255" input.png output.png
```

## Modelle (Qualität → Geschwindigkeit)

| Modell | Qualität | Größe | Wann |
|---|---|---|---|
| `birefnet-general` | **exzellent** (Haare, Glas, komplexe Kanten) | 973 MB | **Default — immer zuerst nehmen** |
| `birefnet-general-lite` | gut | ~250 MB | Schneller, wenn Zeit kritisch |
| `birefnet-portrait` | sehr gut (Menschen) | ~1 GB | Porträts, wenn general schlecht schneidet |
| `isnet-general-use` | gut | groß | schneller Kompromiss |
| `u2net` | mittel — schneidet Details (Hände, Glas) ab | 176 MB | **nur als Notnagel** (rembg-Default, nicht nutzen!) |

**Lizenz-Hinweis (kommerziell relevant):** `birefnet-*` = MIT (frei, auch kommerziell).
`bria-rmbg` (RMBG-2.0) = CC BY-NC 4.0 → **nicht** in Produkten verwenden.

## HTTP-Server (für Agents/Apps)

```bash
rembg s --host 127.0.0.1 --port 7000 --log_level info
# POST -F file=@input.jpg http://127.0.0.1:7000/api/remove -o output.png
# GET  "http://127.0.0.1:7000/api/remove?url=..."  (SSRF-Schutz: blockt private IPs)
# Docs/Swagger: http://127.0.0.1:7000/api  |  Gradio-UI: http://127.0.0.1:7000/
```

## Performance (Apple Silicon, CPU-only)

- Kaltstart (erster Lauf): ~15–17 s pro Bild (inkl. Modell-Load)
- Warm: ~8–10 s pro Bild (birefnet-general)
- Kleinere Modelle deutlich schneller; NVIDIA-GPU via `rembg[gpu]` möglich
- Alpha Matting (`-a`) verbessert Haare/Fell, kostet RAM (8 GB+ bei Riesenbildern) — nur bei Bedarf

## Setup-Fakten (nicht ändern, nur falls Reparatur nötig)

- venv: `~/.hermes/tools/bg-removal/.venv` (Python 3.11)
- Launcher: `~/.hermes/tools/bg-removal/bin/rembg` → Symlink `~/.local/bin/rembg`
- Modelle: `~/.u2net/` (Env `U2NET_HOME` überschreibbar)
- Install: `pip install "rembg[cpu,cli]"` — **`[cpu]`-Extra ist Pflicht** (ohne onnxruntime startet rembg nicht)

## Pitfalls

1. `rembg` ohne `[cpu]` installiert → "No onnxruntime backend found" → `pip install "rembg[cpu,cli]"` ins venv
2. Globaler Launcher scheitert nacheinander mit fehlenden Modulen wie `PIL` oder `packaging` → der dokumentierte Tool-venv ist unvollständig; nicht einzelne Transitiv-Abhängigkeiten nachinstallieren, sondern mit `~/.hermes/tools/bg-removal/.venv/bin/python -m pip install --upgrade "rembg[cpu,cli]"` den vollständigen Runtime-Satz reparieren und denselben `~/.local/bin/rembg`-Befehl erneut ausführen.
3. `u2net` als Default ist alt → bei Qualitätsproblemen IMMER `-m birefnet-general` setzen
3. Riesenbilder (>2000px) können RAM-Loops geben → vorher verkleinern oder `-m birefnet-general-lite`
4. Output ist PNG mit Alpha — für JPG/Web muss erst auf Farbfläche gelegt werden (`-bgc`)
5. Nach jedem Lauf Ergebnis **visuell verifizieren** (vision_analyze): Objekt vollständig? Kanten sauber? Bei Logo/Fotos mit weißem Hintergrund prüfen, dass der weiße Rand weg ist

## Verify

```bash
ls -la output.png            # Datei existiert, > 0 Bytes
# + vision_analyze auf output.png: Hintergrund transparent? Objekt vollständig?
```
