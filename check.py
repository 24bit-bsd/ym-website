#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inhaltsprüfung (wird von build.py automatisch aufgerufen, geht auch einzeln: python3 check.py)

Prüft anhand von content/glossary.json:
  1. Struktur: DE und EN haben je Datei dieselben Schlüssel und gleich lange Listen (nichts vergessen)
  2. Verbotene Schreibweisen je Sprache (z. B. „Digitalization“, britisches Englisch)
  3. EN-Menüpunkte in Title Case (Navigation, Mega-Menü, Sekundärmenü, Footer-Links)
  4. Hinweise: Glossar-Begriffspaare (DE-Begriff im Text, EN-Entsprechung fehlt)

Fehler (1–3) brechen den Build ab, Hinweise (4) werden nur ausgegeben.
"""
import json
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"

# Schlüssel, deren Werte keine Fließtexte sind (Links, IDs, Pfade …)
SKIP_KEYS = {"href", "slug", "id", "type", "variant", "theme", "style", "image", "logo", "output", "locale", "n", "value", "name",
             "form_action", "domain", "date", "updated", "kind", "parent", "logo_image", "logo_icon", "booking_url", "linkedin_url", "mail", "user"}


SAFE_URL = re.compile(r"^(page:|https://|http://|mailto:|tel:|#|/|\?)")
DESIGN_BASIS = ROOT / "design" / "template-basis.json"
DESIGN_DIMENSIONS = ["farbe", "schrift", "formensprache", "hero", "raster", "bildstil", "signatur", "bewegung"]
URL_KEYS = {"href", "booking_url", "linkedin_url", "map_url", "form_action"}


def bad_links(o, where, out):
    """Alle Link-Felder: nur page:, https://, http://, mailto:, tel:, #, / erlaubt (kein javascript:/data:)."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k in URL_KEYS and isinstance(v, str) and v.strip() and not SAFE_URL.match(v.strip()):
                out.append(f"[Sicherheit] {where} {k}: unerlaubte Link-Adresse {v!r}")
            else:
                bad_links(v, f"{where}.{k}", out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            bad_links(v, f"{where}[{i}]", out)


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def walk(o, path=""):
    """Liefert (pfad, text) für alle Strings, ohne technische Schlüssel."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k in SKIP_KEYS or k.startswith("_"):
                continue
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")
    elif isinstance(o, str):
        yield path, o


def page_files(lang_dir):
    """Alle Inhaltsdateien einer Sprache als (relativer Name, Pfad): Seiten (*.json) und Beiträge (posts/*.json)."""
    out = [(f.name, f) for f in sorted(lang_dir.glob("*.json"))]
    out += [(f"posts/{f.name}", f) for f in sorted((lang_dir / "posts").glob("*.json"))]
    return out


def design_fingerprint():
    cfg = load(CONTENT / "config.json")
    return {
        "css": hashlib.sha256((ROOT / "static/assets/css/style.css").read_bytes()).hexdigest(),
        "theme": hashlib.sha256(json.dumps(cfg.get("theme", {}), sort_keys=True).encode()).hexdigest(),
    }


def check_design(cfg, production, errors, hints):
    """Design-Check: jede Kundenwebsite muss gestalterisch eigenständig sein (siehe references/design.md)."""
    d = cfg.get("design", {})
    status = d.get("status", "template")
    if status == "template":
        if "example.com" in cfg.get("domain", ""):  # das Template selbst: Basis-Fingerabdruck muss aktuell sein
            base = load(DESIGN_BASIS) if DESIGN_BASIS.exists() else None
            if base != design_fingerprint():
                errors.append("[Design] Template-Basis (style.css/theme) hat sich geändert: `python3 check.py --design-baseline` ausführen und design/template-basis.json committen")
            return
        hints.append("[Design] design.status steht noch auf 'template', obwohl das Projekt angepasst ist: auf 'offen' setzen")
        status = "offen"
    if status == "offen":
        msg = "[Design] Design ist noch nicht individualisiert (design.status = offen): Staging ist möglich, Produktion erst nach Design-Phase (references/design.md)"
        (errors if production else hints).append(msg)
    elif status == "individuell":
        if len(str(d.get("concept", "")).strip()) < 40:
            errors.append("[Design] design.concept: Designkonzept in Worten fehlt (mind. 40 Zeichen)")
        dims = {x for x in d.get("dimensions", []) if x in DESIGN_DIMENSIONS}
        if len(dims) < 5:
            errors.append(f"[Design] design.dimensions: mindestens 5 von {len(DESIGN_DIMENSIONS)} Gestaltungsdimensionen müssen individuell angepasst sein ({', '.join(DESIGN_DIMENSIONS)}); eingetragen: {len(dims)}")
        if not str(d.get("signature", "")).strip():
            errors.append("[Design] design.signature: das Signatur-Element der Seite fehlt")
        base = load(DESIGN_BASIS) if DESIGN_BASIS.exists() else None
        fp = design_fingerprint()
        if base and fp["css"] == base["css"] and fp["theme"] == base["theme"]:
            errors.append("[Design] style.css und theme sind unverändert gegenüber dem Template: Design wurde nicht angepasst")
    else:
        errors.append(f"[Design] design.status: unbekannter Wert {status!r} (template | offen | individuell)")


def structure_diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a.keys() - b.keys():
            out.append(f"{path}.{k}: fehlt in der Zweitsprache")
        for k in b.keys() - a.keys():
            out.append(f"{path}.{k}: fehlt in der Standardsprache")
        for k in a.keys() & b.keys():
            out += structure_diff(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: Standardsprache hat {len(a)} Einträge, Zweitsprache {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            out += structure_diff(x, y, f"{path}[{i}]")
    elif type(a) is not type(b):
        out.append(f"{path}: Typ unterschiedlich")
    return out


def title_case(s, small, keep):
    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        core = re.sub(r"^[(\[]+", "", w)
        pre = w[: len(w) - len(core)]
        if core in ("&", "/", "|") or core in keep or (core.isupper() and len(core) > 1):
            out.append(w)
        elif i not in (0, len(words) - 1) and core.lower() in small:
            out.append(pre + core.lower())
        else:
            out.append(pre + core[:1].upper() + core[1:])
    return " ".join(out)


def menu_strings(lang_dir):
    """Alle Menütexte einer Sprache: (pfad, text)."""
    site = load(lang_dir / "site.json")
    for i, n in enumerate(site.get("nav", [])):
        yield f"site.json nav[{i}].label", n["label"]
        for ci, c in enumerate(n.get("mega", {}).get("cols", [])):
            if c.get("title"):
                yield f"site.json nav[{i}].mega.cols[{ci}].title", c["title"]
            for li, l in enumerate(c.get("links", []) + c.get("strong", [])):
                yield f"site.json nav[{i}].mega.cols[{ci}] link[{li}]", l["label"]
    ft = site.get("footer", {})
    for i, a in enumerate(ft.get("areas", [])):
        yield f"site.json footer.areas[{i}]", a["label"]
    for k in ("areasTitle", "imprint", "privacy"):
        if ft.get(k):
            yield f"site.json footer.{k}", ft[k]
    if site.get("cta", {}).get("label"):
        yield "site.json cta.label", site["cta"]["label"]
    for f in sorted(lang_dir.glob("*.json")):
        sn = load(f).get("subnav")
        if sn:
            yield f"{f.name} subnav.title", sn["title"]
            for i, l in enumerate(sn["links"]):
                yield f"{f.name} subnav.links[{i}]", l["label"]


def run_checks(verbose=True, production=False):
    gl = load(CONTENT / "glossary.json")
    cfg = load(CONTENT / "config.json")
    langs = cfg["languages"]
    default = cfg["default_language"]
    errors, hints = [], []

    # 0. Sicherheit: nur erlaubte Link-Arten
    bad_links(load(CONTENT / "config.json"), "config.json", errors)
    for f in sorted(list(CONTENT.glob("*/*.json")) + list(CONTENT.glob("*/posts/*.json"))):
        bad_links(load(f), f.relative_to(CONTENT).as_posix(), errors)

    # 1. Struktur Standardsprache <-> jede weitere Sprache
    exempt = set(gl.get("structureExempt", []))
    others = [l for l in langs if l != default]
    for lang in others:
        for name, f in page_files(CONTENT / default):
            if name in exempt:
                continue
            other = CONTENT / lang / name
            if not other.exists():
                # Beiträge dürfen in einzelnen Sprachen fehlen (Hinweis), Seiten nicht (Fehler)
                (hints if name.startswith("posts/") else errors).append(f"[Struktur] {name}: Datei fehlt in {lang}/")
                continue
            for d in structure_diff(load(f), load(other), f"{lang}/{name}"):
                errors.append(f"[Struktur] {d}")
        for name, f in page_files(CONTENT / lang):
            if name not in exempt and not (CONTENT / default / name).exists():
                (hints if name.startswith("posts/") else errors).append(f"[Struktur] {lang}/{name}: Datei fehlt in {default}/")

    # 2. Verbotene Schreibweisen
    for lang in langs:
        rules = [(re.compile(r["pattern"], re.I), r) for r in gl.get(lang, {}).get("forbidden", [])]
        for name, f in page_files(CONTENT / lang):
            for path, text in walk(load(f)):
                for rx, r in rules:
                    m = rx.search(text)
                    if m:
                        errors.append(f"[Schreibweise] {lang}/{name} {path}: „{m.group(0)}“ → {r['use']}")

    # 3. Title Case in englischen Menüs
    en = gl.get("en", {})
    if en.get("menuTitleCase") and (CONTENT / "en").exists():
        small, keep = set(en.get("smallWords", [])), set(en.get("keepCase", []))
        for path, text in menu_strings(CONTENT / "en"):
            exp = title_case(text, small, keep)
            if exp != text:
                errors.append(f"[Menü] en/{path}: „{text}“ → „{exp}“")

    # 4. Begriffspaare Standardsprache -> Zweitsprache (Hinweis, nur Deutsch/Englisch)
    pairs = gl.get("terms", [])
    if default == "de" and (CONTENT / "en").exists():
        for f in sorted((CONTENT / default).glob("*.json")):
            other = CONTENT / "en" / f.name
            if f.name in exempt or not other.exists():
                continue
            en_map = dict(walk(load(other)))
            for path, text in walk(load(f)):
                for t in pairs:
                    if t["de"].lower() in text.lower() and path in en_map and not re.search(t.get("enPattern", re.escape(t["en"])), en_map[path], re.I):
                        hints.append(f"[Glossar] {f.name} {path}: DE „{t['de']}“ – EN enthält nicht „{t['en']}“")

    # 5. SEO-Längen (Hinweis): Titel ~18–62, Beschreibung ~70–160 Zeichen
    for lang in langs:
        for name, f in page_files(CONTENT / lang):
            if name in ("site.json", "notfound.json"):
                continue
            d = load(f)
            t, desc = d.get("title", ""), d.get("description", "")
            if not 18 <= len(t) <= 62:
                hints.append(f"[SEO] {lang}/{name} title: {len(t)} Zeichen (Ziel 18–62): „{t}“")
            if not 70 <= len(desc) <= 160:
                hints.append(f"[SEO] {lang}/{name} description: {len(desc)} Zeichen (Ziel 70–160)")

    # 6. Design: jede Kundenwebsite braucht ein eigenes Design (Produktion bleibt gesperrt, bis es individualisiert ist)
    check_design(cfg, production, errors, hints)

    if verbose:
        for h in hints:
            print("Hinweis:", h)
        for e in errors:
            print("FEHLER: ", e)
        print(f"Prüfung: {len(errors)} Fehler, {len(hints)} Hinweise")
    return errors, hints


if __name__ == "__main__":
    if "--design-baseline" in sys.argv:
        DESIGN_BASIS.parent.mkdir(exist_ok=True)
        DESIGN_BASIS.write_text(json.dumps(design_fingerprint(), indent=2) + "\n", encoding="utf-8")
        print("design/template-basis.json aktualisiert (nur im Template-Repo, nach Änderungen an style.css oder theme)")
        sys.exit(0)
    errs, _ = run_checks(production="--production" in sys.argv)
    sys.exit(1 if errs else 0)
