# Eigene Fotos

- Formate `.jpg`, `.png`, `.webp`; höchstens **2 MB** und **2560 Pixel** an der längsten Seite.
- **Ohne EXIF-Daten** (Kamera, Aufnahmezeit, oft der GPS-Standort). Entfernen im Codespace:
  `uv run --project werkzeuge python werkzeuge/ort_check.py . --exif-entfernen`.
- **Keine Menschen, keine Autokennzeichen, Briefkästen, privaten Türen oder Höfe.**
- Nur **eigene** Fotos.
- Zu jedem Foto eine Datei `<foto>.yml` daneben (Schema: [`bild.schema.json`](../../werkzeuge/schemas/bild.schema.json)):

```yaml
# linde.jpg.yml
titel: Die alte Linde im Herbst
autor: dein-github-name
lizenz: CC-BY-4.0        # oder CC-BY-SA-4.0
eigenes_foto: true
datum: 2026-11-08        # optional
```
