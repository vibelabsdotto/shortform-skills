---
name: shortform-operations
description: "Use for VibeLabs content plans, angle batches, tracking."
version: 1.0.0
author: Echo / VibeLabs
license: Proprietary
metadata:
  hermes:
    tags: [shortform, operations, content-plan, batches, performance, vibelabs]
    related_skills: [creative-shortform-process, tiktok-pull, body-transformation-images]
---

# Shortform Operations (VibeLabs)

Die Operations-Schicht für VibeLabs-Shortform: Dateisystem, Content-Plans,
Batches, Performance-Zahlen. Das strategische Wissen (Hook-Gesetze,
Demand-Check, Loop-Prozedur, Angle-Methodik) liegt im Skill
`vibelabs/creative-shortform-process` — dieser Skill definiert, WO und WIE
das Wissen im Workspace gelebt wird.

Verbindliche Begriffs-Definitionen: `Glossary.md` im Projekt-Root von
`shortform-content`. Bei neuen Begriffen dort ergänzen, nicht im Chat neu
erfinden.

## Die Ebenen

| Ebene | Ort | Zweck |
|---|---|---|
| Strategie/Wissen | Skill `vibelabs/creative-shortform-process` | Hook-Gesetze, Demand-Check, Loop, Variation-Mathematik |
| Operation | `brands/<brand>/<format>/` | Content-Plan, Batches, Performance |
| Begriffe | `Glossary.md` (Projekt-Root) | Verbindliche Definitionen |
| Reasoning-Archiv | `.hermes/plans/` | Brainstormings/Konzepte — additive Updates only |
| Auswertungen | `.hermes/reports/` | Mechanismus-Analysen, Reports (AGENTS-Regel 8) |

## Format-Ordner = Account = ein Asset-Format

- Unter `brands/<brand>/` liegen **Format-Ordner**: `ugc/`, `mascot/`,
  `motivation/`, `food/` … Jeder ist ein Account (oder wird einer) mit
  eigenem Raum für Persona, Posts und Content-Plan.
- **Ein Account = ein Asset-Format** (Projekt-Konvention, bewusste
  Abweichung vom Skill-Standard 10×3):
  - @jona.bulks (UBulk/UGC) = **Photo-Mode Slideshow** (1–8 Bilder,
    Single-Image-Post als bewusste Variante innerhalb des Formats)
- Format-Erweiterung (z.B. Video auf dem Account) = bewusste Entscheidung:
  im Format-Ordner + Glossary dokumentieren, NICHT als Batch-Default
  zurückholen.
- **Batch-Größe: 10 Hooks × 1 Account-Format = 10 Posts** zu EINEM Angle.

## Content-Plan-System (pro live Format-Ordner)

```text
brands/<brand>/<format>/
├── angles.md        # Angles + Territories + Beispiel-Hook + Demand-Probe + Status
├── batches/         # YYYY-MM-DD-batchNN-<angle-slug>/batch.md
├── performance.md   # Append-only Metriken-Journal
├── persona/         # Persona-Assets (falls Persona-Account)
└── posts/           # Asset-Ordner pro Post
```

- `angles.md`: Angles werden nie gelöscht. Status-Lebenszyklus:
  `Idee → Probe ok / Probe fehl → Batch läuft → Winner / Pausiert`.
- `performance.md`: eine Zeile pro Post, 48h nach Post ausgefüllt,
  append-only; Korrekturen als neue Zeile mit `Korrektur: ja`.
- `batches/`: pro Charge ein Ordner mit `batch.md`.
- Ein Format geht live → Content-Plan-System nach diesem Muster kopieren.

## Batch-Anatomie (batch.md, 6 Teile)

1. **Header-Tabelle:** Batch-ID, Angle, Territory, Demand-Probe-Status,
   Status, Account, Asset-Format, Phase
2. **10 Hooks** mit Typ-Etikett (A–E) + mindestens 2 Third-Person-Varianten
   + visuelle Richtung je Hook
3. **Post-Matrix** (10 Zeilen): Post-ID, Hook, Status, Post-Ordner, Perf-Zeile
4. **Produktions-Brief** für das Account-Format (Struktur, Gerüst, Look)
5. **Post-Checkliste:** Slide-1-Regel · Slide-Level-Hooks · Typ dokumentiert ·
   **Hook-Body-Value: der Body muss den Fix liefern, nicht die Diagnose
   durchziehen** · Claim-Grenzen · Phase-Check · 48h-Perf-Zeile
6. **Learnings** (append-only; Winner-Analyse nach `.hermes/reports/`)

## Der Operations-Loop

1. Angle in `angles.md` wählen → Demand-Probe (Skill: Demand-Check) →
   `Probe ok`
2. Batch-Ordner + `batch.md` anlegen → Status `Batch läuft`
3. Posts produzieren → Assets in `posts/`, Post-Ordner in der Matrix
   verlinken (Referenz-Kette Pflicht, AGENTS-Regel 7)
4. Live → nach 48h Zeile in `performance.md`
5. Winner → Mechanismus-Analyse in `.hermes/reports/` → Learning in
   `batch.md` + `angles.md` → Folge-Batch auf demselben Mechanismus
6. Status überall aktuell halten (AGENTS-Regel 9)

## Lessons

- **Hook diagnostiziert, Body liefert den Fix.** Max-Regel 2026-09-17:
  ein Post, der nur das Problem durchzieht ("das reicht nicht"), bietet
  keinen Value — der Viewer muss nach dem Post WISSEN, was er anders
  machen soll (Tipps, Fixes, dense swaps). Diagnose max. 2 Slides, dann
  Fix. "Wen juckt's, dass DU es geschafft hast" — die eigene Story ist
  Receipt, nicht Content.
- **Story-Logik vor Hook-Text prüfen:** Jede Slide muss der Story folgen
  (Hypothese → Befund → Fix → Ergebnis). Eine Slide, die eine andere
  Erzählung aufmacht (Buddy-Vergleich ohne Auflösung), bricht den Post —
  auch wenn der Hook gut ist.
- **Pipeline-Werkzeuge (2026-09-17, Max-Go):** `scripts/slide_overlay.py`
  (Pillow-Text-Overlay als Derivat, Master bleibt neutral) + ffmpeg
  concat (je Slide 2,2 s, 1080×1920, yuv420p) bauen komplette
  Slideshow-MP4s vollautomatisch. Eingebaut nach Max' Wunsch nach einer
  Code-Overlay-CLI; AI-Text-Rendering bleibt aus (Tippfehler, Ad-Look).
- Pinterest-Pins sind Referenz, nie Post-Asset: grob die Hälfte der
  Pins enthält Logos/eingebrannten Text/falsche Szene (HelloFresh-Ad-Fall),
  fremde Personen brechen die Persona, Rechte bleiben Drittwerke.
  Auto-Filter (Dimension + Varianz) fängt Flat-Texturen, NICHT Ads —
  dafür braucht es Vision-Checks. Pins → Referenz für eigene Generierung.
- Die 30er-Trias (10×3) aus dem Strategie-Skill NICHT als Default in Batches
  zurückholen — Projekt-Konvention ist 10 × Account-Format; die Abweichung
  ist dokumentiert (Glossary: Asset-Format/Batch), nicht vergessen.
- Plan-Archiv (`.hermes/plans/`) ist Reasoning-Historie: nur additive
  Updates, nie etwas löschen (Max-Anweisung).
- Performance-Daten sind append-only — nie Zahlen überschreiben.
- Beispiel-Hooks in `angles.md` sind Richtungs-Anker, nicht finale Hooks —
  die 10 Batch-Hooks entstehen erst in der Charge.
- Post-Assets leben in `posts/` (oder dem persona-/mascot-Raum) — `batches/`
  enthält nur Planung und Verweise.
- Neues Format geht live → Content-Plan-System kopieren, bevor der erste
  Post produziert wird, nicht danach.

## Verhältnis zu bestehenden Skills

- `vibelabs/creative-shortform-process` — Strategie: Hook-Gesetze,
  Demand-Check, Loop-Prozedur, Hook-Templates. Hier gilt die Projekt-
  Abweichung (10 × Account-Format statt 10×3).
- `vibelabs/tiktok-pull` — Referenz-Downloads (nur auf Max' Link).
- `vibelabs/body-transformation-images` — Persona-Bild-Produktion.
- `vibelabs/app-ad-creative-mining` — Paid-Seite, gleiche Logik, anderer Kanal.

## Verification

- Jede Batch hat eine `batch.md` mit allen 6 Teilen, bevor produziert wird.
- Jeder gepostete Post hat eine `performance.md`-Zeile innerhalb von 48h.
- `angles.md`-Status spiegelt die Realität (kein `Batch läuft` ohne
  batch.md, kein `Winner` ohne Mechanismus-Analyse).
- Keine Angle-/Plan-Datei wurde verkürzt oder gelöscht — nur additive
  Status-Änderungen.
- **Value-Check je Post:** Nach dem Diagnose-Moment kommt mindestens ein
  konkreter Fix (Tipps, Swaps, Mengen) — kein Post endet auf reiner
  Diagnose.
