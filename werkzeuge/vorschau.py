"""Baut eine statische Vorschau der Inhalte (vorschau/index.html): Karte mit den Punkten aus inhalte/orte/,
Liste der Geschichten und Aktionen. Nur für die lokale Vorschau; veröffentlicht wird sie nicht.

    uv run --project werkzeuge python werkzeuge/vorschau.py . vorschau
"""
from __future__ import annotations

import html
import json
import shutil
import sys
import tomllib
from pathlib import Path

import yaml

from ort_check import split_front_matter

LEAFLET = "https://unpkg.com/leaflet@1.9.4/dist"


def build(root: Path, out: Path) -> Path:
    e = html.escape
    ort = tomllib.loads((root / "ort.toml").read_text(encoding="utf-8"))
    feats = []
    for f in sorted((root / "inhalte" / "orte").glob("*.geojson")):
        try:
            feats += json.loads(f.read_text(encoding="utf-8")).get("features", [])
        except json.JSONDecodeError:
            pass
    stories = []
    for f in sorted((root / "inhalte" / "geschichten").glob("*.md")):
        parts = split_front_matter(f.read_text(encoding="utf-8"))
        head = (yaml.safe_load(parts[0]) if parts else None) or {}
        stories.append(f"<li><strong>{e(str(head.get('titel', f.name)))}</strong> – {e(str(head.get('autor', '?')))}, "
                       f"{e(str(head.get('lizenz', 'Lizenz fehlt')))}</li>")
    actions = []
    for f in sorted((root / "aktionen").glob("*.yml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        actions.append(f"<li>{e(str(d.get('datum', '')))}: <strong>{e(str(d.get('titel', f.name)))}</strong> "
                       f"({e(str(d.get('art', '')))})</li>")
    out.mkdir(parents=True, exist_ok=True)
    if (root / "inhalte" / "bilder").exists():
        shutil.copytree(root / "inhalte" / "bilder", out / "bilder", dirs_exist_ok=True)
    data = json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False).replace("</", "<\\/")
    page = f"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Vorschau {e(ort.get('name_de', ''))}</title>
<link rel="stylesheet" href="{LEAFLET}/leaflet.css">
<style>body{{margin:0;font:15px/1.4 system-ui,sans-serif}}#map{{height:60vh}}main{{padding:0 1rem 2rem}}</style>
</head><body><div id="map"></div><main>
<h1>Vorschau: {e(ort.get('name_de', ''))}</h1>
<p>{len(feats)} Punkte · {len(stories)} Geschichten · {len(actions)} Aktionen. Schauen, nicht graben.</p>
<h2>Geschichten</h2><ul>{''.join(stories) or '<li>noch keine</li>'}</ul>
<h2>Aktionen</h2><ul>{''.join(actions) or '<li>noch keine</li>'}</ul></main>
<script src="{LEAFLET}/leaflet.js"></script><script>
const data = {data};
const map = L.map('map');
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{maxZoom: 19,
  attribution: '&copy; OpenStreetMap-Mitwirkende'}}).addTo(map);
const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}})[c]);
const layer = L.geoJSON(data, {{onEachFeature: (f, l) => {{ const p = f.properties || {{}};
  l.bindPopup(`<strong>${{esc(p.name)}}</strong><br>${{esc(p.kategorie)}}<br>${{esc(p.beschreibung)}}<br><small>${{esc(p.autor)}}, ${{esc(p.lizenz)}}</small>`
    + (p.bild ? `<br><img src="${{esc(p.bild)}}" style="max-width:200px">` : '')); }}}}).addTo(map);
if (data.features.length) map.fitBounds(layer.getBounds().pad(0.3), {{maxZoom: 16}}); else map.setView([49.32, 7.34], 11);
</script></body></html>
"""
    (out / "index.html").write_text(page, encoding="utf-8")
    return out / "index.html"


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    print(build(root, Path(sys.argv[2] if len(sys.argv) > 2 else root / "vorschau").resolve()))
