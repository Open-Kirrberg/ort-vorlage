"""Tests für ort_check.py: jede Regel einmal erlaubt, einmal abgelehnt."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ort_check as oc  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
ORT = """schema = "sle-ort-v1"
id = "musterdorf"
name_de = "Musterdorf"
ags = "10045999"
state = "SL"
maintainers = ["ortspate"]

[options]
relict_candidates = false
pointclouds = []
"""


def point(pid="aussicht-1", kat="aussicht", lon=7.3412, lat=49.3301, **extra):
    props = {"id": pid, "name": "Aussicht am Waldrand", "kategorie": kat, "autor": "ortspate",
             "lizenz": "CC0-1.0", "datum": "2026-11-08", **extra}
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "ort.toml").write_text(ORT)
    for d in ("inhalte/orte", "inhalte/geschichten", "inhalte/bilder", "aktionen"):
        (tmp_path / d).mkdir(parents=True)
    return tmp_path


def write_points(repo, *feats, name="punkte.geojson"):
    (repo / "inhalte" / "orte" / name).write_text(json.dumps({"type": "FeatureCollection", "features": list(feats)}))


def msgs(rep):
    return " | ".join(m for _, m in rep.errors)


def test_empty_template_passes(repo):
    rep = oc.check_repo(repo)
    assert rep.errors == [], rep.errors


def test_template_repo_itself_passes():
    """The checked-out template (or a place repo created from it) passes its own check."""
    rep = oc.check_repo(REPO)
    assert rep.errors == [], rep.errors


def test_ort_toml_schema(repo):
    (repo / "ort.toml").write_text(ORT.replace('ags = "10045999"', "ags = 10045999").replace('"ortspate"', '"a@b.de"'))
    m = msgs(oc.check_repo(repo))
    assert "ags" in m and "maintainers" in m


def test_points_valid_and_licence_required(repo):
    write_points(repo, point())
    assert oc.check_repo(repo).errors == []
    p = point()
    del p["properties"]["lizenz"]
    write_points(repo, p)
    assert "lizenz" in msgs(oc.check_repo(repo))
    write_points(repo, point(lizenz="CC-BY-NC-4.0"))
    assert "lizenz" in msgs(oc.check_repo(repo))


def test_points_duplicate_ids_and_outside(repo):
    write_points(repo, point(), point())
    assert "mehrfach" in msgs(oc.check_repo(repo))
    write_points(repo, point(lon=13.4, lat=52.5))
    assert "coordinates" in msgs(oc.check_repo(repo))


def test_new_find_needs_coarse_location(repo):
    write_points(repo, point(pid="fund-1", kat="fund", lon=7.3412, lat=49.3301))
    assert "grober Lage" in msgs(oc.check_repo(repo))
    write_points(repo, point(pid="fund-1", kat="fund", lon=7.34, lat=49.33))
    assert oc.check_repo(repo).errors == []


@pytest.mark.parametrize("text, frag", [
    ("Schreib mir: max@example.org", "E-Mail"),
    ("Ruf an: 06841 123456", "Telefon"),
    ("Treffpunkt Hauptstraße 12", "Hausadresse"),
    ("Mit dem Metalldetektor findet man hier viel", "Sondeln"),
    ("Hier liegt ein Bombentrichter", "Kampfmittel"),
    ("Genau bei 49.33012, 7.34121 im Wald", "Koordinaten"),
])
def test_text_rules_reject(text, frag):
    errors, _ = oc.text_problems(text)
    assert any(frag in e for e in errors), (text, errors)


@pytest.mark.parametrize("text", [
    "Der Grabhügel liegt am Waldrand; Wall und Graben sind gut zu sehen.",
    "Die Linde ist etwa 250 Jahre alt.",
    "Schauen, nicht graben: Funde bitte der Denkmalpflege melden.",
    "Erbaut 1778 bis 1788.",
])
def test_text_rules_allow(text):
    assert oc.text_problems(text)[0] == []


def test_plate_is_a_warning():
    errors, warnings = oc.text_problems("Auto HOM-AB 123 parkt dort")
    assert errors == [] and warnings


def test_story_front_matter(repo):
    f = repo / "inhalte" / "geschichten" / "linde.md"
    f.write_text("---\ntitel: Die alte Linde\nautor: ortspate\nlizenz: CC-BY-4.0\ndatum: 2026-11-08\n---\nText.\n")
    assert oc.check_repo(repo).errors == []
    f.write_text("---\ntitel: Die alte Linde\nautor: ortspate\ndatum: 2026-11-08\n---\nText.\n")
    assert "lizenz" in msgs(oc.check_repo(repo))
    f.write_text("Kein Kopf\n")
    assert "Kopf fehlt" in msgs(oc.check_repo(repo))


def test_action_yaml(repo):
    f = repo / "aktionen" / "2026-pflanzung.yml"
    f.write_text("titel: Obstbäume am Spielplatz\nart: pflanzung\ndatum: 2026-11-08\nbaeume: 12\n"
                 "partner: [Obst- und Gartenbauverein]\nautor: ortspate\nlizenz: CC0-1.0\n")
    assert oc.check_repo(repo).errors == []
    f.write_text("titel: X\nart: party\ndatum: 2026-11-08\nautor: o\nlizenz: CC0-1.0\n")
    m = msgs(oc.check_repo(repo))
    assert "art" in m


def _img(path, size=(64, 48), exif=False):
    im = Image.new("RGB", size, (90, 140, 60))
    kw = {}
    if exif:
        ex = Image.Exif()
        ex[0x010F] = "KameraHersteller"   # Make
        kw["exif"] = ex.tobytes()
    im.save(path, **kw)


def test_image_rules(repo):
    d = repo / "inhalte" / "bilder"
    _img(d / "linde.jpg")
    assert "Bildangaben" in msgs(oc.check_repo(repo))
    (d / "linde.jpg.yml").write_text("titel: Linde\nautor: ortspate\nlizenz: CC-BY-4.0\neigenes_foto: true\n")
    assert oc.check_repo(repo).errors == []
    _img(d / "linde.jpg", exif=True)
    assert "EXIF" in msgs(oc.check_repo(repo))
    rep = oc.check_repo(repo, fix_exif=True)
    assert rep.errors == [] and oc.check_repo(repo).errors == []
    _img(d / "linde.jpg", size=(3000, 100))
    assert "längste Seite" in msgs(oc.check_repo(repo))
    (d / "linde.jpg.yml").write_text("titel: Linde\nautor: ortspate\nlizenz: CC-BY-4.0\neigenes_foto: false\n")
    _img(d / "linde.jpg")
    assert "eigenes_foto" in msgs(oc.check_repo(repo))


def test_unexpected_files(repo):
    (repo / "inhalte" / "notiz.txt").write_text("x")
    (repo / "aktionen" / "a.json").write_text("{}")
    m = msgs(oc.check_repo(repo))
    assert "unerwartete Datei" in m and "nur .yml" in m


def test_examples_from_readme_pass(repo):
    """The example files in the template READMEs (fenced blocks marked as examples) are valid."""
    src = REPO / "inhalte" / "orte" / "README.md"
    if not src.exists():
        pytest.skip("template README missing")
    text = src.read_text(encoding="utf-8")
    block = text.split("```json", 1)[1].split("```", 1)[0]
    (repo / "inhalte" / "orte" / "beispiel.geojson").write_text(block)
    assert oc.check_repo(repo).errors == []
    shutil.rmtree(repo / "inhalte" / "orte")
