# Aktionen (`*.yml`)

Pflanz-, Entsiegelungs- und Pflegeaktionen im Ort – eine Datei je Aktion. Später speisen sie im Explorer
„So kommt <Ort> nach oben“. Schema: [`werkzeuge/schemas/aktion.schema.json`](../werkzeuge/schemas/aktion.schema.json).

```yaml
# 2026-11-obstbaeume-spielplatz.yml
titel: Zwölf Obstbäume am Spielplatz
art: pflanzung              # pflanzung | entsiegelung | pflege | sonstiges
datum: 2026-11-08
baeume: 12                  # optional
flaeche_m2: 400             # optional
lage: { lon: 7.3412, lat: 49.3301 }   # optional, ein öffentlicher Ort
partner:                    # optional: Vereine, Schulen, Gemeinde – keine Privatpersonen
  - Obst- und Gartenbauverein
beschreibung: Hochstämme alter Sorten, gepflanzt mit der Grundschule.
autor: dein-github-name
lizenz: CC0-1.0             # oder CC-BY-4.0 / CC-BY-SA-4.0
```

Die Rangliste „Orte im Vergleich“ rechnet der Orte-Katalog zentral aus amtlichen Daten; Aktionen hier
verändern keine Ranglisten-Zahl.
