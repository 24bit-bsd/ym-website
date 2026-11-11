#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live-Editor – Texte direkt auf der Seite ändern (nur lokal, keine Abhängigkeiten).

    python3 editor.py            # startet auf http://127.0.0.1:8777 und öffnet den Browser
    python3 editor.py --port 9000 --no-open

Ablauf: Text anklicken → bearbeiten → „Speichern“ schreibt in content/<sprache>/*.json und baut neu.
„Veröffentlichen“ prüft (check.py), committet nur content/ und pusht → GitHub baut Staging.
Der Server lauscht ausschließlich auf 127.0.0.1; Schreibzugriffe brauchen ein zufälliges Token (nur diese Seite kennt es).
"""
import argparse
import importlib
import json
import secrets
import subprocess
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import build
import check

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
OUT = ROOT / "edit"
LOCK = threading.Lock()
TOKEN = secrets.token_urlsafe(24)
PORT = 8777


SOURCES = [CONTENT, ROOT / "static", ROOT / "editor" / "assets", ROOT / "build.py"]
BUILT_AT = 0.0


def newest_source():
    """Jüngste Änderungszeit aller Quellen (Inhalte, Statisches, Editor-Dateien, build.py)."""
    t = 0.0
    for src in SOURCES:
        files = [src] if src.is_file() else [f for f in src.rglob("*") if f.is_file()]
        for f in files:
            t = max(t, f.stat().st_mtime)
    return t


def rebuild():
    global BUILT_AT
    mt = newest_source()
    if (ROOT / "build.py").stat().st_mtime > BUILT_AT:
        importlib.reload(build)  # build.py wurde geändert -> neuen Code laden
    build.EDIT_TOKEN = TOKEN
    build.build(check=False, edit=True)
    BUILT_AT = mt


def rebuild_if_stale():
    """Beim Seitenaufruf neu bauen, wenn sich Dateien auf der Platte geändert haben (z. B. durch Claude oder Git)."""
    with LOCK:
        if newest_source() > BUILT_AT:
            rebuild()


def content_file(rel):
    """Sicher auf content/<lang>/<name>.json auflösen (keine Pfadtricks)."""
    p = (CONTENT / rel).resolve()
    if CONTENT.resolve() not in p.parents or p.suffix != ".json" or not p.is_file():
        raise ValueError(f"Ungültige Datei: {rel}")
    return p


def resolve(data, path):
    """Container + letzten Schlüssel für einen JSON-Pfad (Liste aus Schlüsseln/Indizes)."""
    cur = data
    for k in path[:-1]:
        cur = cur[k]
    return cur, path[-1]


def get_value(rel, path):
    data = json.loads(content_file(rel).read_text(encoding="utf-8"))
    cont, key = resolve(data, path)
    v = cont[key]
    return v if isinstance(v, str) else None


def counterparts(rel, path):
    lang, name = rel.split("/", 1)
    out = []
    for l in build_langs():
        if l == lang:
            continue
        other = f"{l}/{name}"
        try:
            v = get_value(other, path)
        except (ValueError, KeyError, IndexError, TypeError):
            v = None
        if v is not None:
            out.append({"lang": l, "file": other, "value": v})
    return out


def build_langs():
    return json.loads((CONTENT / "config.json").read_text(encoding="utf-8"))["languages"]


def set_value(rel, path, value):
    p = content_file(rel)
    data = json.loads(p.read_text(encoding="utf-8"))
    cont, key = resolve(data, path)
    if not isinstance(cont[key], str):
        raise ValueError("Nur Textfelder sind editierbar")
    cont[key] = value
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git(*args, raw=False):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    out = r.stdout + r.stderr
    return r.returncode, (out if raw else out.strip())


def status():
    _, out = git("status", "--porcelain", "--", "content", raw=True)
    files = [{"status": ln[:2].strip(), "file": ln[3:]} for ln in out.splitlines() if ln.strip()]
    _, branch = git("rev-parse", "--abbrev-ref", "HEAD")
    return {"changed": files, "branch": branch}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(OUT), **kw)

    # -- Schutz: nur 127.0.0.1/localhost mit dem richtigen Port als Host
    def host_ok(self):
        return self.headers.get("Host", "") in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authed(self):
        return self.host_ok() and secrets.compare_digest(self.headers.get("X-Editor-Token", ""), TOKEN)

    def log_message(self, fmt, *args):
        if "/__" in str(args[0] if args else ""):
            super().log_message(fmt, *args)

    def do_GET(self):
        if not self.host_ok():
            return self.json({"ok": False, "error": "Host nicht erlaubt"}, 403)
        u = urlparse(self.path)
        if u.path.startswith("/__api/"):
            if not self.authed():
                return self.json({"ok": False, "error": "Nicht autorisiert"}, 403)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            try:
                if u.path == "/__api/get":
                    rel, path = q["file"], json.loads(q["path"])
                    return self.json({"ok": True, "value": get_value(rel, path), "others": counterparts(rel, path)})
                if u.path == "/__api/status":
                    return self.json({"ok": True, **status()})
            except Exception as e:  # noqa: BLE001
                return self.json({"ok": False, "error": str(e)}, 400)
            return self.json({"ok": False, "error": "Unbekannt"}, 404)
        if u.path.endswith("/") or u.path.endswith(".html"):
            try:
                rebuild_if_stale()
            except Exception as ex:  # noqa: BLE001
                print("Rebuild fehlgeschlagen:", ex)
        return super().do_GET()

    def do_POST(self):
        if not self.authed():
            return self.json({"ok": False, "error": "Nicht autorisiert"}, 403)
        n = int(self.headers.get("Content-Length", 0))
        if n > 200_000:
            return self.json({"ok": False, "error": "Zu groß"}, 413)
        body = json.loads(self.rfile.read(n) or b"{}")
        path = urlparse(self.path).path
        try:
            with LOCK:
                if path == "/__api/save":
                    for ch in body["changes"]:
                        set_value(ch["file"], ch["path"], str(ch["value"]))
                    rebuild()
                    errors, hints = check.run_checks(verbose=False)
                    return self.json({"ok": True, "errors": errors, "hints": hints})
                if path == "/__api/publish":
                    errors, _ = check.run_checks(verbose=False)
                    if errors:
                        return self.json({"ok": False, "error": "Die Inhaltsprüfung meldet Fehler – bitte zuerst beheben.", "errors": errors})
                    st = status()
                    if not st["changed"]:
                        return self.json({"ok": False, "error": "Keine Änderungen an den Inhalten."})
                    msg = (body.get("message") or "Inhalte aktualisiert (Live-Editor)").strip()[:200]
                    for cmd in (["add", "--", "content"], ["commit", "-m", msg, "--", "content"], ["push"]):
                        code, out = git(*cmd)
                        if code != 0:
                            return self.json({"ok": False, "error": f"git {cmd[0]} fehlgeschlagen:\n{out}"})
                    return self.json({"ok": True, "message": "Veröffentlicht: GitHub baut jetzt Staging (ca. 1 Minute)."})
                if path == "/__api/discard":
                    code, out = git("checkout", "--", "content")
                    if code != 0:
                        return self.json({"ok": False, "error": out})
                    rebuild()
                    return self.json({"ok": True})
        except Exception as e:  # noqa: BLE001
            return self.json({"ok": False, "error": f"{type(e).__name__}: {e}"}, 400)
        return self.json({"ok": False, "error": "Unbekannt"}, 404)


def main():
    global PORT
    ap = argparse.ArgumentParser(description="Live-Editor")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args()
    PORT = a.port
    errors, _ = check.run_checks(verbose=False)
    if errors:
        print("Hinweis: Die Inhaltsprüfung meldet aktuell Fehler (python3 check.py zeigt Details).")
    rebuild()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Live-Editor läuft: {url}   (beenden mit Strg+C)")
    if not a.no_open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nBeendet.")


if __name__ == "__main__":
    main()
