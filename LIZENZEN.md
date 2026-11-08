# Lizenzen

Dieses Repository enthält zwei Arten von Material mit **unterschiedlichen Lizenzen** (ADR 0054 des Saar LiDAR
Explorers):

| Was | Wo | Lizenz |
|---|---|---|
| Code, Workflows, Prüfskripte, Schemas, Skills, Devcontainer | `.github/`, `.devcontainer/`, `.claude/`, `werkzeuge/` | **MIT** (Datei [`LICENSE`](LICENSE)) |
| Texte (Geschichten, Beschreibungen) und eigene Fotos | `inhalte/geschichten/`, `inhalte/bilder/` | **CC BY 4.0** ([Lizenztext](https://creativecommons.org/licenses/by/4.0/legalcode.de)), je Beitrag wahlweise **CC BY-SA 4.0** ([Lizenztext](https://creativecommons.org/licenses/by-sa/4.0/legalcode.de)) |
| Datenbeiträge (Punkte, Aktionen) | `inhalte/orte/`, `aktionen/` | **CC0 1.0** ([Lizenztext](https://creativecommons.org/publicdomain/zero/1.0/legalcode.de)); aus OpenStreetMap abgeleitete Punkte **ODbL 1.0** ([Lizenztext](https://opendatacommons.org/licenses/odbl/1-0/)) |
| Dokumentation (README, CONTRIBUTING, diese Datei) | Wurzel | CC BY 4.0 |

- **Jeder Beitrag nennt seine Lizenz und seinen Urheber** (Feld `lizenz` und `autor`; bei Bildern in der Datei
  `<bild>.yml`). Als Urheber genügt der GitHub-Name oder ein selbst gewählter Name – mehr nicht.
- Andere Lizenzen (z. B. Zeitungsfotos, Archivscans, „CC BY-NC“) können nicht angenommen werden, außer eine
  Ortspatin oder ein Ortspate hat die Nutzung ausdrücklich geklärt und dokumentiert.
- Die CI lehnt Beiträge ohne erlaubtes Lizenzfeld ab (`werkzeuge/ort_check.py`).

## Daten, die beim Build entstehen

Die 3D-Daten werden **nicht** in diesem Repository gespeichert. GitHub Actions baut sie aus offenen amtlichen
Daten und veröffentlicht sie auf GitHub Pages; die vollständige Quellenliste steht dort in `ATTRIBUTION.txt`.
Je nach Ort sind das unter anderem:

- © GeoBasis-DE/LVGL-SL (2026), dl-de/by-2-0, Daten bearbeitet (Laserscanning DGM1/DOM1 2025, LoD2, DOP20)
- © GeoBasis-DE/LVermGeoRP (2026), dl-de/by-2-0, www.lvermgeo.rlp.de, Daten bearbeitet
- © OpenStreetMap-Mitwirkende, ODbL
- © BKG (2026) CC BY 4.0 (Daten verändert), Datenquellen: https://sgx.geodatenzentrum.de/web_public/gdz/datenquellen/datenquellen_vg25.pdf (VG25)

Lizenz der amtlichen Daten: [Datenlizenz Deutschland – Namensnennung – Version 2.0](https://www.govdata.de/dl-de/by-2-0).
