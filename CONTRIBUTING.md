# Mitmachen – Schritt für Schritt

Danke, dass du deinen Ort im Saar LiDAR Explorer zeigen willst! Diese Anleitung geht vom einfachsten Weg (ein
Formular ausfüllen) bis zur eigenen Vorschau. Du brauchst nur ein GitHub-Konto.

## Die drei Regeln vorab

1. **Schauen, nicht graben.** Keine Hinweise zum Graben, Sondeln oder Schatzsuchen. Neue archäologische
   Beobachtungen nur mit grober Lage (etwa 1 km) – die genaue Stelle bitte direkt der Denkmalpflege melden.
2. **Keine Kampfmittel.** Bombentrichter, Blindgänger oder Munition werden nie veröffentlicht.
3. **Keine Personen, nichts Privates.** Keine Menschen auf Fotos, keine Autokennzeichen, Briefkästen, privaten
   Türen oder Höfe, keine Adressen, Telefonnummern oder E-Mail-Adressen. Als Urheber genügt dein GitHub-Name
   oder ein selbst gewählter Name.

Jeder Beitrag braucht eine **Lizenz**: Texte und eigene Fotos CC BY 4.0 (oder CC BY-SA 4.0), Punkte und Aktionen
CC0 1.0 (aus OpenStreetMap abgeleitet: ODbL 1.0). Nur **eigene** Fotos. Mehr in [LIZENZEN.md](LIZENZEN.md).

## 1. Ohne Git: ein Formular ausfüllen

1. Oben auf **Issues → New issue** klicken.
2. Ein Formular wählen: *Riesenbaum melden*, *Fehler melden*, *Aktion melden* oder *Geschichte vorschlagen*.
3. Ausfüllen, Lizenz bestätigen, absenden. Fertig – eine Ortspatin oder ein Ortspate meldet sich im Issue.

## 2. Im Browser: eine Datei anlegen

Beispiel „neuer Aussichtspunkt“:

1. In den Ordner `inhalte/orte/` gehen, **Add file → Create new file**.
2. Name `aussicht-am-hang.geojson`, Inhalt wie das Beispiel in [`inhalte/orte/README.md`](inhalte/orte/README.md).
   Koordinaten: im Explorer an die Stelle fliegen; Längen- und Breitengrad stehen in der Adresszeile
   oder in jeder Karten-App. Reihenfolge in GeoJSON: **erst Länge (≈ 7.3), dann Breite (≈ 49.3)**.
3. **Commit changes → Create a new branch … → Propose changes → Create pull request.**
4. Die Prüfungen laufen (Häkchen oder rotes Kreuz im Pull Request). Bei einem Kreuz: „Details“ öffnen – die
   Meldung sagt auf Deutsch, was fehlt (z. B. „lizenz fehlt“). Datei korrigieren, die Prüfung läuft erneut.
5. Eine Ortspatin oder ein Ortspate prüft und übernimmt den Beitrag. Nach dem Übernehmen veröffentlicht
   GitHub Actions die Seite neu (Inhalte allein: wenige Minuten).

Geschichten (`inhalte/geschichten/*.md`), Aktionen (`aktionen/*.yml`) und Fotos (`inhalte/bilder/`) gehen genauso;
die Vorlagen stehen in den README-Dateien der Ordner.

**Fotos:** vor dem Hochladen die EXIF-Daten entfernen (Kamera, Zeit, oft der GPS-Standort). Die Prüfung lehnt
Fotos mit EXIF ab. In einem Codespace (Schritt 3) geht das mit
`uv run --project werkzeuge python werkzeuge/ort_check.py . --exif-entfernen`. Höchstens 2 MB und 2560 Pixel.
Zu jedem Foto gehört `<foto>.yml` mit Titel, Autor, Lizenz und `eigenes_foto: true`.

## 3. Vorschau im Codespace (ohne Installation)

1. **Code → Codespaces → Create codespace on main** (oder auf deinem Branch).
2. Warten, bis das Terminal bereit ist (die Umgebung installiert sich selbst).
3. `werkzeuge/vorschau.sh` eingeben. Es prüft alle Inhalte und öffnet eine Karte mit deinen Punkten,
   Geschichten und Aktionen (Port 8000, „Open in Browser“).

Die 3D-Ansicht im Explorer zeigt die Inhalte der Orte erst in einer späteren Ausbaustufe; bis dahin ist diese
Karte die Vorschau.

## 4. Für Ortspaten

- **Issue → Pull Request:** Angaben aus dem Formular in die passende Datei übertragen (oder den Skill
  `ort-pflegen` in Claude Code nutzen), Lizenz und Urheber übernehmen, im Pull Request „Closes #<nummer>“ schreiben.
- **Prüfen vor dem Übernehmen:** Fotos ansehen (Personen? Kennzeichen? private Höfe?), Texte lesen (Grabungs-
  oder Sondelhinweise? Adressen?), Lizenz eigener Fotos plausibel? Die CI fängt nur Routinefälle ab.
- **`CODEOWNERS`** (`.github/CODEOWNERS`): eure GitHub-Namen eintragen, dann bittet GitHub euch bei jedem Pull
  Request automatisch um eine Prüfung. Unter *Settings → Branches* „Require review from Code Owners“ einschalten.
- **Relikt-Kandidaten** (`relict_candidates` in `ort.toml`) erst einschalten, wenn ihr die Kandidaten angesehen
  habt und die Denkmalsituation kennt (ADR 0053). Das Einschalten ist ein eigener Pull Request.
- **Pipeline-Version anheben:** in `.github/workflows/build.yml` die Zeile `uses: …@<ref>` und die Eingaben
  `pipeline_ref` / `pipeline_version` gemeinsam ändern (sonst bricht der Build mit einer klaren Meldung ab).
  Ein solcher Pull Request baut die Daten neu.
- **Neu bauen** ohne Änderung: *Actions → Daten bauen und veröffentlichen → Run workflow*. Bitte nur, wenn es
  einen Grund gibt (die Daten kommen von öffentlichen Diensten).

## Neuen Ort anlegen

1. Prüfen, ob es den Ort schon gibt: im [Orte-Katalog](https://open-kirrberg.github.io/orte-katalog/) steht jede
   Gemeinde mit Status. „Ortspate gesucht“ heißt: Es gibt noch kein Repository.
2. Ein Mitglied von Open-Kirrberg legt mit **Use this template** das Repository `ort-<id>` an (z. B.
   `ort-kirkel`). Öffentlich.
3. `ort.toml` ausfüllen: `id`, `name_de`, `ags` und `state` genau wie im Katalog, `maintainers` = eure GitHub-Namen.
4. `.github/workflows/build.yml`: `place_id` auf dieselbe `id` setzen.
5. *Settings → Pages → Source: GitHub Actions*.
6. Im Repository `orte-katalog` in `orte.toml` den Ort eintragen (`status = "3d"`, `data_url =
   "https://open-kirrberg.github.io/ort-<id>/"`, `repo`, `maintainers`) – als Pull Request.
7. *Actions → Daten bauen und veröffentlichen → Run workflow*. Der erste Build lädt die amtlichen Daten
   (je nach Größe 20–60 Minuten); spätere Builds nutzen den Cache.
