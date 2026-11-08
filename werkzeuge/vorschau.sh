#!/usr/bin/env bash
# Vorschau der Inhalte: prüft alles, baut vorschau/index.html (Karte mit Punkten, Geschichten, Aktionen)
# und startet einen kleinen Webserver auf Port 8000 (im Codespace: „Open in Browser“).
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --project werkzeuge --frozen python werkzeuge/ort_check.py . || echo "⚠️  Die Prüfung meldet Fehler (siehe oben) – die Vorschau zeigt trotzdem alles."
uv run --project werkzeuge --frozen python werkzeuge/vorschau.py . vorschau
echo "Vorschau: http://localhost:8000/  (Strg+C beendet)"
cd vorschau && python3 -m http.server 8000 --bind 127.0.0.1
