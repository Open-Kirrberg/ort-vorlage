# Besondere Orte (`*.geojson`)

Eine oder mehrere GeoJSON-Dateien mit Punkten. Koordinaten in WGS84, **erst Länge (≈ 7.3), dann Breite (≈ 49.3)**.
Schema: [`werkzeuge/schemas/orte.schema.json`](../../werkzeuge/schemas/orte.schema.json).

Beispiel (`aussicht-am-hang.geojson`):

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [7.3412, 49.3301] },
      "properties": {
        "id": "aussicht-am-hang",
        "name": "Aussicht am Hang",
        "kategorie": "aussicht",
        "beschreibung": "Bank am Waldrand mit Blick über das Tal.",
        "autor": "dein-github-name",
        "lizenz": "CC0-1.0",
        "datum": "2026-11-08"
      }
    }
  ]
}
```

| Feld | Pflicht | Inhalt |
|---|---|---|
| `id` | ja | eindeutig im Repository, klein, mit Bindestrichen |
| `name` | ja | 2–80 Zeichen |
| `kategorie` | ja | `aussicht`, `natur`, `baum`, `wasser`, `denkmal`, `geschichte`, `weg`, `spielplatz`, `fund`, `sonstiges` |
| `beschreibung` | nein | bis 1000 Zeichen |
| `quelle` | nein | Quelle des Wissens (Buch, Webseite), bis 300 Zeichen |
| `autor` | ja | GitHub-Name oder selbst gewählter Name |
| `lizenz` | ja | `CC0-1.0` (eigene Angaben) oder `ODbL-1.0` (aus OpenStreetMap übernommen) |
| `datum` | ja | `JJJJ-MM-TT` |
| `bild` | nein | `bilder/<datei>.jpg` (das Foto liegt in `inhalte/bilder/`) |
| `hoehe_m` | nein | z. B. geschätzte Baumhöhe |

**`kategorie: fund`** (eine neue archäologische Beobachtung): nur mit **grober Lage**, höchstens zwei
Nachkommastellen (≈ 1 km), z. B. `[7.34, 49.33]`. Die genaue Stelle bitte nur der Denkmalpflege melden.
Bekannte, öffentlich ausgeschilderte Denkmäler (`denkmal`) dürfen genau sein.
