---
name: ort-pflegen
description: Pflege der Inhalte eines Ort-Repositorys des Saar LiDAR Explorers – einen Punkt, eine Geschichte, eine Aktion oder ein Foto hinzufügen, ein Issue (Riesenbaum melden, Aktion melden, Geschichte vorschlagen) in einen Pull Request verwandeln, Lizenz und Datenschutz prüfen, EXIF entfernen, die Vorschau starten. Nutzen, wenn jemand in diesem Repository „Punkt hinzufügen“, „Issue übernehmen“, „Lizenz prüfen“, „Vorschau“ oder Ähnliches sagt.
---

# Ort pflegen

Ein Ort-Repository (`ort-<id>`, aus `Open-Kirrberg/ort-vorlage`) enthält nur Steckbrief und Gemeinschafts-Inhalte;
die 3D-Daten baut GitHub Actions. Regeln: [CONTRIBUTING.md](../../../CONTRIBUTING.md), Lizenzen:
[LIZENZEN.md](../../../LIZENZEN.md). Antworte den Menschen auf Deutsch.

## Harte Regeln (nie verhandeln)

- **Schauen, nicht graben:** keine Hinweise zum Graben, Sondeln, Schatzsuchen. `kategorie: fund` nur mit grober
  Lage (höchstens 2 Nachkommastellen). Genaue Fundstellen gehören zur Denkmalpflege, nicht ins Repository.
- **Keine Kampfmittel** (Bombentrichter, Blindgänger, Munition) – nie, auch nicht „nur als Hinweis“.
- **Keine Personen, nichts Privates:** keine Menschen auf Fotos, keine Kennzeichen, Briefkästen, privaten Türen
  oder Höfe, keine Adressen, Telefonnummern, E-Mail-Adressen, Klarnamen von Privatleuten. Urheber = GitHub-Name
  oder selbst gewählter Name.
- **Lizenz:** Punkte/Aktionen `CC0-1.0` (OSM-Ableitung `ODbL-1.0`), Texte/Fotos `CC-BY-4.0` oder `CC-BY-SA-4.0`,
  nur eigene Fotos. Fehlt die Zustimmung im Issue, nachfragen statt raten.

## Einen Punkt hinzufügen

1. Datei in `inhalte/orte/` wählen oder neu anlegen (`<thema>.geojson`, Muster in `inhalte/orte/README.md`).
2. Feature anhängen: Koordinaten WGS84 **[Länge, Breite]**, `id` eindeutig (klein, Bindestriche), `kategorie` aus
   der Liste im Schema, `autor`, `lizenz`, `datum` (heute, `JJJJ-MM-TT`).
3. Prüfen (Schritt „Prüfen“).

## Ein Issue übernehmen

1. Issue lesen (`gh issue view <nr>`); Lizenz-Häkchen gesetzt? Urheber-Name ohne E-Mail? Sonst nachfragen.
2. In die passende Datei übertragen: Riesenbaum → Punkt `kategorie: baum` (+ `hoehe_m`); Aktion → `aktionen/<datum>-<kurz>.yml`;
   Geschichte → `inhalte/geschichten/<kurz>.md` mit Kopf; Fotos aus dem Issue herunterladen, EXIF entfernen,
   `<foto>.yml` schreiben (`eigenes_foto: true` nur, wenn das Issue das bestätigt).
3. Branch, Commit, Pull Request mit „Closes #<nr>“.

## Prüfen

```bash
uv run --project werkzeuge --frozen python werkzeuge/ort_check.py .                    # alle Regeln
uv run --project werkzeuge --frozen python werkzeuge/ort_check.py . --exif-entfernen   # EXIF aus Fotos löschen
```

Die Meldungen nennen Datei und Grund. Hinweise (`::warning`) sind kein Fehler, aber ansehen (z. B. mögliches
Kennzeichen). Fotos zusätzlich selbst ansehen – Gesichter und Kennzeichen erkennt die Prüfung nicht.

## Vorschau

```bash
werkzeuge/vorschau.sh      # prüft, baut vorschau/index.html und startet http://localhost:8000/
```

## Nicht hier

- `ort.toml` `relict_candidates` nur auf ausdrücklichen Wunsch der Ortspaten ändern (ADR 0053).
- Pipeline-Version (`.github/workflows/build.yml`): `uses: …@<ref>`, `pipeline_ref`, `pipeline_version` nur gemeinsam.
- Ranglisten-Zahlen werden zentral im Orte-Katalog berechnet; nichts hier kann sie ändern.
