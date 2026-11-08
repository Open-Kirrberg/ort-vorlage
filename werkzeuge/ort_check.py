"""Prüft die Inhalte eines Ort-Repositorys (läuft in CI bei jedem Pull Request und vor jedem Build).

    uv run --project werkzeuge python werkzeuge/ort_check.py .                    # alles prüfen
    uv run --project werkzeuge python werkzeuge/ort_check.py . --exif-entfernen   # EXIF aus Bildern löschen (lokal)

Geprüft wird (Plan „Orte skalieren“ §7, ADR 0054, Regeln R4, R5, R7):
- `ort.toml` gegen `schemas/ort.schema.json` (`sle-ort-v1`),
- `inhalte/orte/*.geojson` gegen `schemas/orte.schema.json`, eindeutige ids, Bild-Verweise vorhanden,
- `inhalte/geschichten/*.md`: Kopf (Front Matter) gegen `schemas/geschichte.schema.json`, Textlänge,
- `aktionen/*.yml` gegen `schemas/aktion.schema.json`,
- `inhalte/bilder/*`: Format, ≤ 2 MB, längste Seite ≤ 2560 px, **keine EXIF-/GPS-Daten**, Bildangaben `<bild>.yml`,
- Lizenzfeld vorhanden und erlaubt (ADR 0054) – das erledigen die Schemas,
- Datenschutz (R7): keine E-Mail-Adressen, Telefonnummern, Hausadressen, Kfz-Kennzeichen,
- Bodendenkmäler (R4): keine Hinweise zum Graben oder Sondeln; neue Funde (`kategorie: fund`) nur mit grober Lage
  (höchstens 2 Nachkommastellen ≈ 1 km), keine genauen Koordinaten in Texten,
- Kampfmittel (R5, ADR 0010): keine Bombentrichter, Blindgänger, Munition.

Die CI filtert nur Routinefälle; eine Ortspatin oder ein Ortspate prüft jeden Pull Request trotzdem selbst.
Ausgabe: GitHub-Annotationen (`::error file=…::…`); Exit 1 bei Fehlern.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from PIL import Image

SCHEMAS = Path(__file__).resolve().parent / "schemas"
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_BYTES = 2 * 1024 * 1024
MAX_IMAGE_EDGE = 2560
MAX_STORY_CHARS = 20_000
FIND_MAX_DECIMALS = 2

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"(?<![\d.,])(?:\+49|0049|0)[\s/-]?\(?\d{2,5}\)?[\s/-]?\d{3,}(?:[\s-]?\d+)*(?![\d.,])")
ADDRESS = re.compile(r"\b[\wäöüß.-]*(?:straße|strasse|str\.|gasse|weg|platz|allee|ring)\s+\d{1,4}\s?[a-z]?\b",
                     re.IGNORECASE)
PLATE = re.compile(r"\b[A-ZÄÖÜ]{1,3}[- ][A-Z]{1,2}[ -]?\d{1,4}[EH]?\b")
PRIVATE_WORDS = re.compile(r"\b(kennzeichen|briefkasten|klingelschild|hausnummer|privatgrundstück|innenhof)\b",
                           re.IGNORECASE)
DIGGING = re.compile(r"\b(metalldetektor\w*|detektor\w*|sondengänger\w*|sondeln|sondel\w*|schatzsuche\w*|"
                     r"ausgraben|ausgegraben|nachgraben|buddeln)\b", re.IGNORECASE)
UXO = re.compile(r"\b(bombentrichter\w*|trichterfeld\w*|blindgänger\w*|kampfmittel\w*|munition\w*|fliegerbombe\w*|"
                 r"granate\w*|crater\w*)\b", re.IGNORECASE)
COORD_TEXT = re.compile(r"\b(?:4[89]\.\d{3,}\s*[,;/ ]\s*[67]\.\d{3,}|[67]\.\d{3,}\s*[,;/ ]\s*4[89]\.\d{3,}|"
                        r"3\d{5}(?:\.\d+)?\s*[,;/ ]\s*54\d{5})\b")
README = "README.md"


@dataclass
class Report:
    errors: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[tuple[str, str]] = field(default_factory=list)

    def err(self, f: Path | str, msg: str) -> None:
        self.errors.append((str(f), msg))

    def warn(self, f: Path | str, msg: str) -> None:
        self.warnings.append((str(f), msg))


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((SCHEMAS / name).read_text(encoding="utf-8")))


# ------------------------------------------------------------------------------------------------ text rules
def text_problems(text: str) -> tuple[list[str], list[str]]:
    """(errors, warnings) of the privacy / heritage / UXO heuristics for one text. Pure."""
    errors, warnings = [], []
    if EMAIL.search(text):
        errors.append("enthält eine E-Mail-Adresse (R7: nur GitHub-Name oder ein gewählter Name)")
    if PHONE.search(text):
        errors.append("enthält eine Telefonnummer (R7)")
    if ADDRESS.search(text):
        errors.append("enthält eine Hausadresse mit Hausnummer (R7)")
    if PLATE.search(text):
        warnings.append("sieht nach einem Kfz-Kennzeichen aus (R7) – bitte prüfen")
    if PRIVATE_WORDS.search(text):
        warnings.append("erwähnt Privates (Kennzeichen, Briefkasten, Hof …) – bitte prüfen (R7)")
    if DIGGING.search(text):
        errors.append("enthält Hinweise zum Graben oder Sondeln – Schauen, nicht graben (R4, Denkmalschutzgesetz)")
    if UXO.search(text):
        errors.append("nennt Kampfmittel/Bombentrichter – solche Hinweise werden nie veröffentlicht (R5, ADR 0010)")
    if COORD_TEXT.search(text):
        errors.append("enthält genaue Koordinaten im Text – Orte gehören als Punkt nach inhalte/orte/ (R4)")
    return errors, warnings


def decimals(x: float) -> int:
    s = repr(float(x))
    return len(s.split(".")[1].rstrip("0")) if "." in s and "e" not in s else 0


def check_text(rep: Report, f: Path, text: str) -> None:
    e, w = text_problems(text)
    for m in e:
        rep.err(f, m)
    for m in w:
        rep.warn(f, m)


def schema_errors(rep: Report, f: Path, v: Draft202012Validator, doc: Any) -> bool:
    errs = sorted(v.iter_errors(doc), key=lambda e: list(e.absolute_path))
    for e in errs[:20]:
        where = "/".join(str(p) for p in e.absolute_path) or "(oben)"
        rep.err(f, f"Schema: {where}: {e.message}")
    return not errs


# ------------------------------------------------------------------------------------------------ files
def check_ort_toml(rep: Report, root: Path) -> None:
    f = root / "ort.toml"
    if not f.exists():
        rep.err(f, "ort.toml fehlt")
        return
    try:
        doc = tomllib.loads(f.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        rep.err(f, f"kein gültiges TOML: {e}")
        return
    schema_errors(rep, f, validator("ort.schema.json"), doc)


def check_orte(rep: Report, root: Path, ids: set[str]) -> None:
    v = validator("orte.schema.json")
    for f in sorted((root / "inhalte" / "orte").glob("*")):
        if f.name == README:
            continue
        if f.suffix != ".geojson":
            rep.err(f, "in inhalte/orte/ sind nur .geojson-Dateien erlaubt")
            continue
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            rep.err(f, f"kein gültiges JSON: {e}")
            continue
        if not schema_errors(rep, f, v, doc):
            continue
        for feat in doc["features"]:
            p = feat["properties"]
            if p["id"] in ids:
                rep.err(f, f"id {p['id']!r} kommt mehrfach vor")
            ids.add(p["id"])
            check_text(rep, f, " ".join(str(p.get(k, "")) for k in ("name", "beschreibung", "quelle", "autor")))
            if p["kategorie"] == "fund":
                lon, lat = feat["geometry"]["coordinates"]
                if decimals(lon) > FIND_MAX_DECIMALS or decimals(lat) > FIND_MAX_DECIMALS:
                    rep.err(f, f"{p['id']}: neue Funde nur mit grober Lage (höchstens {FIND_MAX_DECIMALS} "
                               "Nachkommastellen ≈ 1 km) – die genaue Stelle bitte nur der Denkmalpflege melden (R4)")
            if p.get("bild") and not (root / "inhalte" / p["bild"]).exists():
                rep.err(f, f"{p['id']}: Bild inhalte/{p['bild']} fehlt")


def split_front_matter(text: str) -> tuple[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    return text[4:end], text[end + 5:]


def check_geschichten(rep: Report, root: Path) -> None:
    v = validator("geschichte.schema.json")
    for f in sorted((root / "inhalte" / "geschichten").glob("*")):
        if f.name == README:
            continue
        if f.suffix != ".md":
            rep.err(f, "in inhalte/geschichten/ sind nur .md-Dateien erlaubt")
            continue
        text = f.read_text(encoding="utf-8")
        parts = split_front_matter(text)
        if parts is None:
            rep.err(f, "Kopf fehlt: die Datei muss mit '---', den Angaben (titel, autor, lizenz, datum) und '---' beginnen")
            continue
        try:
            head = yaml.safe_load(parts[0]) or {}
        except yaml.YAMLError as e:
            rep.err(f, f"Kopf ist kein gültiges YAML: {e}")
            continue
        if isinstance(head, dict) and hasattr(head.get("datum"), "isoformat"):
            head["datum"] = head["datum"].isoformat()
        if not schema_errors(rep, f, v, head):
            continue
        if len(parts[1]) > MAX_STORY_CHARS:
            rep.err(f, f"Text länger als {MAX_STORY_CHARS} Zeichen")
        check_text(rep, f, parts[1] + " " + " ".join(str(x) for x in head.get("quellen", [])) + " " + head["titel"])
        for b in head.get("bilder", []):
            if not (root / "inhalte" / b).exists():
                rep.err(f, f"Bild inhalte/{b} fehlt")


def check_aktionen(rep: Report, root: Path) -> None:
    v = validator("aktion.schema.json")
    for f in sorted((root / "aktionen").glob("*")):
        if f.name == README:
            continue
        if f.suffix not in (".yml", ".yaml"):
            rep.err(f, "in aktionen/ sind nur .yml-Dateien erlaubt")
            continue
        try:
            doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            rep.err(f, f"kein gültiges YAML: {e}")
            continue
        if isinstance(doc, dict) and hasattr(doc.get("datum"), "isoformat"):
            doc["datum"] = doc["datum"].isoformat()
        if not schema_errors(rep, f, v, doc):
            continue
        check_text(rep, f, " ".join(str(doc.get(k, "")) for k in ("titel", "beschreibung", "quelle", "autor"))
                   + " " + " ".join(doc.get("partner", [])))


def image_exif(im: Image.Image) -> bool:
    if im.getexif():
        return True
    info = im.info or {}
    return any(k in info for k in ("exif", "xmp", "XML:com.adobe.xmp"))


def strip_exif(f: Path) -> None:
    """Re-encode the pixels only (a fresh image carries no EXIF, XMP or text chunks)."""
    with Image.open(f) as im:
        im.load()
        clean = Image.frombytes(im.mode, im.size, im.tobytes())
        if im.mode == "P" and im.getpalette():
            clean.putpalette(im.getpalette())
    kw = {"quality": 90} if f.suffix.lower() in (".jpg", ".jpeg", ".webp") else {}
    clean.save(f, **kw)


def check_bilder(rep: Report, root: Path, fix_exif: bool) -> None:
    v = validator("bild.schema.json")
    d = root / "inhalte" / "bilder"
    for f in sorted(d.glob("*")):
        if f.name == README or f.suffix in (".yml", ".yaml"):
            continue
        if f.suffix.lower() not in IMAGE_EXT:
            rep.err(f, "nur .jpg, .png oder .webp erlaubt")
            continue
        if f.stat().st_size > MAX_IMAGE_BYTES:
            rep.err(f, f"{f.stat().st_size / 1e6:.1f} MB – höchstens 2 MB")
        try:
            with Image.open(f) as im:
                im.verify()
            with Image.open(f) as im:
                if max(im.size) > MAX_IMAGE_EDGE:
                    rep.err(f, f"{im.size[0]}×{im.size[1]} px – längste Seite höchstens {MAX_IMAGE_EDGE} px")
                has_meta = image_exif(im)
        except Exception as e:   # noqa: BLE001 - any decoder error means: not a usable image
            rep.err(f, f"kein lesbares Bild ({e})")
            continue
        if has_meta and fix_exif:
            strip_exif(f)
            rep.warn(f, "EXIF/XMP-Daten entfernt")
        elif has_meta:
            rep.err(f, "enthält EXIF/XMP-Daten (Kamera, Zeit, evtl. GPS) – lokal entfernen mit "
                       "`uv run --project werkzeuge python werkzeuge/ort_check.py . --exif-entfernen`")
        side = f.with_name(f.name + ".yml")
        if not side.exists():
            rep.err(f, f"Bildangaben {side.name} fehlen (titel, autor, lizenz, eigenes_foto: true)")
            continue
        meta = yaml.safe_load(side.read_text(encoding="utf-8"))
        if isinstance(meta, dict) and hasattr(meta.get("datum"), "isoformat"):
            meta["datum"] = meta["datum"].isoformat()
        if schema_errors(rep, side, v, meta):
            check_text(rep, side, f"{meta['titel']} {meta['autor']}")
    for side in sorted(d.glob("*.yml")):
        if not side.with_suffix("").exists():
            rep.err(side, "Bildangaben ohne Bild")


def check_layout(rep: Report, root: Path) -> None:
    """Nothing unexpected under inhalte/ (only orte/, geschichten/, bilder/ and READMEs); no symlinks anywhere."""
    base = root / "inhalte"
    for p in sorted(base.rglob("*")) if base.exists() else []:
        if p.is_symlink():
            rep.err(p, "symbolische Links sind nicht erlaubt")
        rel = p.relative_to(base).parts
        if p.is_file() and p.name != README and rel[0] not in ("orte", "geschichten", "bilder"):
            rep.err(p, "unerwartete Datei: Inhalte gehören nach inhalte/orte, inhalte/geschichten oder inhalte/bilder")
        if p.is_file() and len(rel) > 2:
            rep.err(p, "keine Unterordner in inhalte/<art>/")


def check_repo(root: Path, fix_exif: bool = False) -> Report:
    rep = Report()
    check_ort_toml(rep, root)
    check_layout(rep, root)
    check_orte(rep, root, set())
    check_geschichten(rep, root)
    check_aktionen(rep, root)
    check_bilder(rep, root, fix_exif)
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path, nargs="?", default=Path("."))
    ap.add_argument("--exif-entfernen", action="store_true", help="EXIF/XMP aus Bildern löschen (nur lokal)")
    a = ap.parse_args(argv)
    rep = check_repo(a.root.resolve(), a.exif_entfernen)
    for f, m in rep.warnings:
        print(f"::warning file={Path(f).relative_to(a.root.resolve()) if Path(f).is_absolute() else f}::{m}")
    for f, m in rep.errors:
        print(f"::error file={Path(f).relative_to(a.root.resolve()) if Path(f).is_absolute() else f}::{m}")
    print(f"{len(rep.errors)} Fehler, {len(rep.warnings)} Hinweise")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
