# Geschichten (`*.md`)

Eine Markdown-Datei je Geschichte. Sie beginnt mit einem Kopf zwischen zwei Zeilen `---`.
Schema: [`werkzeuge/schemas/geschichte.schema.json`](../../werkzeuge/schemas/geschichte.schema.json).

Beispiel (`die-alte-linde.md`):

```markdown
---
titel: Die alte Linde am Dorfplatz
autor: dein-github-name
lizenz: CC-BY-4.0
datum: 2026-11-08
ort: linde-dorfplatz          # optional: id eines Punkts aus inhalte/orte/
quellen:
  - Ortschronik, 1985, S. 42
bilder:
  - bilder/linde.jpg
---
Die Linde wurde der Überlieferung nach 1815 gepflanzt …
```

- `lizenz`: `CC-BY-4.0` oder `CC-BY-SA-4.0`. Nur eigene Texte oder Texte, deren Urheber zugestimmt haben.
- Bis 20 000 Zeichen. Keine genauen Koordinaten im Text – Orte gehören als Punkt nach `inhalte/orte/`.
- Keine Hinweise zum Graben oder Sondeln, keine Kampfmittel, keine Adressen oder Namen von Privatleuten.
