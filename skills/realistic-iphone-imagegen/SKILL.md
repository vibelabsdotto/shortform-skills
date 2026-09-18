---
name: realistic-iphone-imagegen
description: Use when Max wants realistic casual iPhone-style photos.
---

# Realistic iPhone ImageGen — Snapshot-Prompt-Baukasten

## Zweck
Bilder, die wie spontane Handy-Fotos wirken — für JEDE Art von Motiv
(People, Food, Produkte, Orte, Szenen). Akzeptanzkriterium: „Würde jemand
das unkommentiert auf Instagram posten?" — Max bewertet das Bild selbst.

Kein Editorial/Shooting-Look: kein 85mm-Bokeh-Vokabular, kein „magazine
style", keine Qualitäts-Buzzwords („8K, ultra-realistic, masterpiece" =
AI-Look-Trigger, nie verwenden).

## Kernprinzip: Snapshot- statt Editorial-Vokabular
| Editorial (nie nutzen) | Snapshot (nutzen) |
|---|---|
| 85mm f/2, Bokeh, Rim Light | „smartphone", „front camera", „through the mirror" |
| „editorial, magazine style" | „unedited, straight out of camera", „amateur" |
| Film grain, muted tones | „visible digital noise", „slight motion blur", „washed-out colors" |
| Dramatisches Licht, „sharp focus on the eyes" | „plain overhead fluorescent", „harsh flat light, unflattering shadows", „slight overexposure near windows" |
| Komponiert, Low-Angle | „slightly tilted", „off-center", „part cut off at the frame edge" |

## Baukasten — JSON-PROMPT-PFLICHT
**Jeder Bild-Prompt wird IMMER als JSON-Objekt erstellt. Fest vorgegeben,
keine Ausnahme — nie ein fließender Text als Prompt.** Nur die Werte
innerhalb des JSONs variieren je nach Motiv. Felder je nach Motiv wählen,
weglassen, was nicht passt:
- **style** — Genre („casual candid smartphone photo") + post_processing („unedited, straight out of camera", „natural smartphone image processing", "ordinary colors")
- **subject** — Beschreibung mit Markern statt Adjektiven (Alter, Kleidung, Zustand), Pose/Aktion
- **environment** — Ort, Hintergrund, Props
- **camera** — Aufnahmegerät/-situation: Spiegel-Selfie? POV des Essers? Foto von wem, aus welcher Haltung?
- **composition** — Framing (angeschnitten, off-center, tilted), Fokus/Bewegungsunschärfe, Orientation
- **lighting** — Quelle + Qualität, immer real/ungünstig, nie schöngerechnet
- **texture** — Oberflächen + noise/grain
- **constraints** — wenige, knappe Verbote („no studio lighting")

Beispiel-JSONs (nur als Illustration — jedes neue Motiv bekommt eigene
Werte): `references/examples.json`

Prompt-Erstellung in 2 Schritten: (1) Motiv in die JSON-Felder
übersetzen, (2) das komplette JSON als Prompt an das Modell übergeben.

## Eiserne Regeln (motivübergreifend)
1. **Lichtquelle IMMER nennen** — mit Richtung und Qualität, und das
   unvorteilhafte Licht explizit fordern („harsh flat light,
   unflattering shadows"). Ohne diese Zeile poliert das Modell ins
   Studio-Look.
2. **Imperfektion explizit fordern** — motion blur, digital noise,
   washed-out colors, Anschnitte am Frame-Rand. Das Modell „poliert"
   von selbst; alles nicht Geforderte fällt in den Standard-Look.
3. **Hintergrund-Personen nur weit weg + unscharf** („far in the
   background, faces indistinct"), sonst Blob-Artefakte.
4. **Markenprodukte**: Brand-Name allein → falsches generisches Logo.
   Formel: konkretes Modell („iPhone 15 Pro in black, back facing the
   mirror") + präziser Logo-Deskriptor („glossy chrome Apple logo
   silhouette etched directly onto the glass, catching the light like
   polished metal, with no circle or ring around it") + Halte-Hand
   minimieren („only two fingertips wrap around the lower edge").

## Referenz
Voll-Research (Modell-Landschaft, Iterations-Historie, alle Quellen):
(internal research archive, not public)
