#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Website-Template – statischer Seitengenerator (keine Abhängigkeiten, Python 3.8+)

  python3 build.py              -> dist/      Produktion (Inhalt gehört ins Webverzeichnis des Hosters)
  python3 build.py --noindex    -> dist/      Staging (noindex + robots.txt Disallow)
  python3 build.py --preview    -> preview/   lokale Vorschau (relative Links, noindex, Formular aus)

Inhalte:   content/<sprache>/<seite>.json   (Seiten)  und  content/<sprache>/site.json  (Navigation, Texte)
Technik:   content/config.json              (Marke, Domain, Kontakt, Design-Variablen, SEO-Daten, Redirects ...)
Statisch:  static/                          (CSS, JS, Bilder, PHP-Formular, .htaccess) wird 1:1 kopiert
"""
import argparse
import datetime
import hashlib
import html
import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"

# --------------------------------------------------------------------------- #
# Helfer
# --------------------------------------------------------------------------- #


EDIT = False  # True beim Live-Editor-Build (python3 editor.py): Texte werden mit ihrer Fundstelle in der JSON markiert
EDIT_TOKEN = ""
TAG_SKIP = {"href", "slug", "id", "type", "variant", "theme", "style", "image", "logo", "output", "locale", "value", "h", "cols", "level"}


SAFE_URL = re.compile(r"^(page:|https://|http://|mailto:|tel:|#|/|\?)")


def safe_url(u):
    """Nur erlaubte Link-Arten (https, http, mailto, tel, interne Seiten/Anker) – kein javascript:/data: o. Ä."""
    if not isinstance(u, str) or not SAFE_URL.match(u.strip()):
        raise ValueError(f"Unerlaubte Link-Adresse: {u!r} (erlaubt: page:, https://, http://, mailto:, tel:, #, /)")
    return u


class PStr(str):
    """String mit Herkunft (Datei + JSON-Pfad) – nur im Editor-Build relevant, sonst ein normaler str."""

    ed = None


def tag_strings(o, file, path=()):
    if isinstance(o, dict):
        return {k: (v if k in TAG_SKIP else tag_strings(v, file, path + (k,))) for k, v in o.items()}
    if isinstance(o, list):
        return [tag_strings(v, file, path + (i,)) for i, v in enumerate(o)]
    if isinstance(o, str):
        p = PStr(o)
        p.ed = (file, list(path))
        return p
    return o


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_content(path):
    """Inhaltsdatei laden; im Editor-Build mit Fundstellen-Markierung."""
    data = load(path)
    if EDIT:
        data = tag_strings(data, Path(path).relative_to(CONTENT).as_posix())
    return data


def esc(s):
    return html.escape(str(s), quote=True)


def mark(out, s):
    """Editor-Build: Textstelle klickbar machen (span mit Fundstelle). Sonst unverändert."""
    if EDIT and isinstance(s, PStr) and s.ed:
        return f'<span class="ed" data-ed="{esc(json.dumps(s.ed, ensure_ascii=False))}">{out}</span>'
    return out


def T(s):
    """Text im HTML-Textknoten (escaped, im Editor-Build editierbar)."""
    return mark(esc(s), s)


def rich(s):
    """Text -> HTML: escaped, **fett**, Zeilenumbruch \\n -> <br>."""
    orig = s
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s, flags=re.S)
    s = re.sub(r"\[\[(.+?)\]\]", r'<span class="hl">\1<i class="hl-box" aria-hidden="true"></i></span>', s, flags=re.S)
    s = re.sub(r"\{\{(.+?)\}\}", r'<span class="grad-text">\1</span>', s, flags=re.S)
    s = s.replace("{year}", f'<span data-year>{datetime.date.today().year}</span>')
    return mark(s.replace("\n", "<br>"), orig)


def plain(s):
    """Text ohne Auszeichnung (für strukturierte Daten): **fett**, [[…]], {{…}} entfernt, Absätze mit Leerzeichen."""
    s = re.sub(r"\*\*(.+?)\*\*|\[\[(.+?)\]\]|\{\{(.+?)\}\}", lambda m: m.group(1) or m.group(2) or m.group(3), str(s), flags=re.S)
    return re.sub(r"\s*\n\s*", " ", s.replace("{year}", str(datetime.date.today().year))).strip()


def paragraphs(s, cls=""):
    c = f' class="{cls}"' if cls else ""
    out = "".join(f"<p{c}>{rich(str(p))}</p>" for p in str(s).split("\n\n") if p.strip())
    if EDIT and isinstance(s, PStr) and s.ed:
        return f'<div class="ed ed-block" data-ed="{esc(json.dumps(s.ed, ensure_ascii=False))}">{out}</div>'
    return out


ICONS = {
    "mail": '<path d="M3 6.5A1.5 1.5 0 0 1 4.5 5h15A1.5 1.5 0 0 1 21 6.5v11a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "pin": '<path d="M12 21s7-6.2 7-11.5A7 7 0 0 0 5 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "cal": '<rect x="4" y="5" width="16" height="15" rx="2"/><path d="M4 10h16M9 3v4M15 3v4"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "x": '<path d="M7 7l10 10M17 7 7 17"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="9.5" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
    "arrow": '<path d="M4 12h15M13 6l6 6-6 6"/>',
    "bolt": '<path d="M13 2 4.5 13.5H11L10 22l8.5-11.5H12z"/>',
    "chart": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/>',
    "coins": '<ellipse cx="9" cy="7" rx="5.5" ry="3"/><path d="M3.5 7v5c0 1.7 2.5 3 5.5 3"/><path d="M3.5 12v5c0 1.7 2.5 3 5.5 3 1 0 2-.2 2.8-.5"/><ellipse cx="16" cy="13.5" rx="5.5" ry="3"/><path d="M10.5 13.5v4c0 1.7 2.5 3 5.5 3s5.5-1.3 5.5-3v-4"/>',
    "award": '<circle cx="12" cy="9" r="6"/><path d="m8.5 14 -1.5 8 5-3 5 3-1.5-8"/>',
    "smile": '<circle cx="12" cy="12" r="9"/><path d="M8 14.5c1 1.5 2.4 2.3 4 2.3s3-.8 4-2.3"/><path d="M9 9.5h.01M15 9.5h.01"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "chev": '<path d="m9 6 6 6-6 6"/>',
    "up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
    "down": '<path d="m6 9 6 6 6-6"/>',
    "linkedin": '<rect x="2" y="8.5" width="5" height="14" rx="0.5" ry="0.5"/><ellipse cx="4.48" cy="4" rx="2.48" ry="2.5"/><path d="M18.5,22.5h3A.5.5,0,0,0,22,22V13.6C22,9.83,19.87,8,16.89,8a4.21,4.21,0,0,0-3.17,1.27A.41.41,0,0,1,13,9a.5.5,0,0,0-.5-.5h-3A.5.5,0,0,0,9,9V22a.5.5,0,0,0,.5.5h3A.5.5,0,0,0,13,22V14.5a2.5,2.5,0,0,1,5,0V22A.5.5,0,0,0,18.5,22.5Z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.7 3.9 5.7 3.9 9s-1.3 6.3-3.9 9c-2.6-2.7-3.9-5.7-3.9-9S9.4 5.7 12 3z"/>',
}


def icon(name, cls="i"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'


# --------------------------------------------------------------------------- #
# Site-Modell
# --------------------------------------------------------------------------- #


class Site:
    def __init__(self, preview=False, noindex=False):
        self.cfg = load(CONTENT / "config.json")
        self.langs = self.cfg["languages"]
        self.default = self.cfg["default_language"]
        self.preview = preview
        self.noindex = noindex or preview
        self.text = {l: load_content(CONTENT / l / "site.json") for l in self.langs}
        self.pages = {}
        for l in self.langs:
            for f in sorted((CONTENT / l).glob("*.json")):
                if f.name == "site.json":
                    continue
                p = load_content(f)
                p.setdefault("id", f.stem)
                p["lang"] = l
                p["_file"] = f"{l}/{f.name}"
                self.pages[(l, p["id"])] = p
            for f in sorted((CONTENT / l / "posts").glob("*.json")):  # Blog-/News-Beiträge: content/<lang>/posts/*.json
                p = load_content(f)
                p.setdefault("id", f.stem)
                if (l, p["id"]) in self.pages:
                    raise SystemExit(f"Beitrag {l}/posts/{f.name}: ID '{p['id']}' ist schon vergeben (Seite oder Beitrag).")
                p["lang"], p["kind"], p["_file"] = l, "post", f"{l}/posts/{f.name}"
                self.pages[(l, p["id"])] = p
        self.version = self._asset_version()
        self.today = datetime.date.today()

    def _asset_version(self):
        h = hashlib.md5()
        for f in ("assets/css/style.css", "assets/js/main.js"):
            h.update((STATIC / f).read_bytes())
        h.update(json.dumps(self.cfg.get("theme", {}), sort_keys=True).encode())
        return h.hexdigest()[:8]

    def parts(self, lang, pid):
        p = self.pages[(lang, pid)]
        parts = [] if lang == self.default else [lang]
        if p.get("slug"):
            parts += p["slug"].split("/")
        return parts

    def abs_url(self, lang, pid):
        parts = self.parts(lang, pid)
        return self.cfg["domain"] + "/" + "/".join(parts) + ("/" if parts else "")

    def indexable_pages(self):
        return [p for (l, i), p in self.pages.items() if not p.get("output")]


class Ctx:
    """Kontext für eine Seite: Linkberechnung, Texte."""

    def __init__(self, site, page):
        self.site = site
        self.page = page
        self.lang = page["lang"]
        self.t = site.text[self.lang]
        self.cur = [] if page.get("output") else site.parts(self.lang, page["id"])

    # -- URLs
    def _rel(self, target_parts, filename=None):
        cur = "/".join(self.cur) or "."
        tgt = "/".join(target_parts) or "."
        rel = os.path.relpath(tgt, cur)
        if filename:
            return filename if rel == "." else f"{rel}/{filename}"
        return rel

    def page_url(self, lang, pid):
        if (lang, pid) not in self.site.pages:
            pid = "home"
        parts = self.site.parts(lang, pid)
        if self.site.preview:
            return self._rel(parts, "index.html")
        return "/" + "/".join(parts) + ("/" if parts else "")

    def asset(self, path, versioned=True):
        v = f"?v={self.site.version}" if versioned else ""
        if self.site.preview:
            return self._rel(path.split("/")[:-1], path.split("/")[-1]) + v
        return "/" + path + v

    def href(self, h):
        if not h.startswith("page:"):
            return safe_url(h)
        ref, anchor, query = h[5:], "", ""
        if "#" in ref:
            ref, anchor = ref.split("#", 1)
            anchor = "#" + anchor
        if "?" in ref:
            ref, query = ref.split("?", 1)
            query = "?" + query
        if (self.lang, ref) not in self.site.pages:
            raise KeyError(f"Unbekannte Seite '{ref}' in {self.lang} (Link '{h}')")
        return self.page_url(self.lang, ref) + query + anchor

    def link_attrs(self, h):
        url = self.href(h)
        ext = url.startswith("http") and not url.startswith(self.site.cfg["domain"])
        extra = ' target="_blank" rel="noopener noreferrer"' if ext else ""
        return f'href="{esc(url)}"{extra}'


# --------------------------------------------------------------------------- #
# Bausteine
# --------------------------------------------------------------------------- #


def btn(ctx, b):
    style = b.get("style", "primary")
    cls = {"primary": "btn btn-primary", "secondary": "btn btn-secondary", "link": "link-more"}[style]
    label = esc(b["label"])
    if b.get("sub"):  # zweizeiliger Button: Aktion + kurzer Nutzen
        label = f'<span class="btn-two"><span class="btn-main">{label}</span><span class="btn-sub">{esc(b["sub"])}</span></span>'
        cls += " btn--two"
    if style == "link":
        label += icon("chev", "i i-chev")
    emb = ""
    if b.get("embed"):  # Formular im Fenster (Dialog) öffnen; ohne JavaScript bleibt es ein normaler Link
        e = ctx.t["ui"]["embed"]
        emb = (f' data-embed="{esc(safe_url(b["href"]))}" data-embed-title="{esc(b.get("embedTitle", b["label"]))}"'
               f' data-embed-close="{esc(e["close"])}" data-embed-new="{esc(e["openNew"])}"')
    return f'<a class="{cls}" {ctx.link_attrs(b["href"])}{emb}>{label}</a>'


def buttons(ctx, items, cls="btn-row"):
    if not items:
        return ""
    return f'<div class="{cls}">' + "".join(btn(ctx, b) for b in items) + "</div>"


def chips(items, cls=""):
    out = []
    for it in items:
        if isinstance(it, dict):
            badge = f'<span class="badge">{T(it["badge"])}</span>' if it.get("badge") else ""
            hl = " chip--hl" if it.get("hl") else ""
            out.append(f'<li class="chip{hl}">{T(it["label"])}{badge}</li>')
        else:
            out.append(f'<li class="chip">{T(it)}</li>')
    return f'<ul class="chips {cls}">' + "".join(out) + "</ul>"


def list_html(items, style="ticks"):
    if style == "questions":
        return '<ul class="questions">' + "".join(f"<li>{rich(i)}</li>" for i in items) + "</ul>"
    ic = "bolt" if style == "pains" else "check"
    return f'<ul class="marks marks--{style}">' + "".join(
        f'<li>{icon(ic, "i i-mark")}<span>{rich(i)}</span></li>' for i in items
    ) + "</ul>"


def head(sec, center=False, small=False):
    out = ""
    if sec.get("eyebrow"):
        out += f'<p class="eyebrow">{rich(sec["eyebrow"])}</p>'
    if sec.get("title") and small:
        out += f'<p class="logos-title">{rich(sec["title"])}</p>'
    elif sec.get("title"):
        out += f'<h2 class="h2">{rich(sec["title"])}</h2>'
    if sec.get("lead"):
        out += f'<p class="lead">{rich(sec["lead"])}</p>'
    if not out:
        return ""
    wide = " sec-head--wide" if sec.get("wideHead") else ""
    return f'<header class="sec-head{" sec-head--center" if center else ""}{wide}" data-reveal>{out}</header>'


def wrap(sec, inner, extra=""):
    sid = f' id="{esc(sec["id"])}"' if sec.get("id") else ""
    theme = sec.get("theme", "light")
    return f'<section class="section theme-{theme} {extra}"{sid}><div class="wrap">{inner}</div></section>\n'


def mail_link(ctx, cls=""):
    """E-Mail wird nur als „name[at]domain“ angezeigt; mailto: entsteht erst per Klick (siehe main.js)."""
    m = ctx.site.cfg["mail"]
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="#" data-mu="{esc(m["user"])}" data-md="{esc(m["domain"])}">{esc(m["user"])}[at]{esc(m["domain"])}</a>'


# --------------------------------------------------------------------------- #
# Section-Renderer
# --------------------------------------------------------------------------- #


def rot_line(sec):
    rot = sec["rotator"]
    full = rot["prefix"] + " " + ", ".join(w.rstrip(".") for w in rot["words"]) + "."
    words = "".join(f'<span class="rot-w{" on" if i == 0 else ""}">{T(w)}</span>' for i, w in enumerate(rot["words"]))
    return (
        f'<p class="hero-line rot-line" data-reveal aria-label="{esc(full)}"><span aria-hidden="true">{esc(rot["prefix"])}</span>'
        f'<span class="rot" aria-hidden="true">{words}</span></p>'
    )


def r_hero(ctx, sec):
    home = sec.get("variant") == "home"
    out = ""
    if sec.get("eyebrow"):
        tag = f'<span class="badge-tag">{T(sec["tag"])}</span>' if sec.get("tag") else ""
        out += f'<p class="pill" data-reveal>{tag}{rich(sec["eyebrow"])}</p>'
    if home:
        sub_ = f' <span class="hero-sub">{rich(sec["subtitle"])}</span>' if sec.get("subtitle") else ""
        out += f'<h1 class="hero-title" data-reveal><span class="hero-brand">{T(sec["title"])}</span>{sub_}</h1>'
        if sec.get("tagline"):
            out += f'<p class="hero-line hero-tagline" data-reveal>{rich(sec["tagline"])}</p>'
        if sec.get("rotator"):
            out += rot_line(sec)
    else:
        out += f'<h1 class="hero-title hero-title--page" data-reveal>{rich(sec["title"])}</h1>'
        if sec.get("lead"):
            out += f'<p class="hero-lead" data-reveal>{rich(sec["lead"])}</p>'
        if sec.get("rotator"):
            out += rot_line(sec)
    out += buttons(ctx, sec.get("buttons"), "btn-row btn-row--center")
    cls = "hero hero--home" if home else "hero"
    style = ""
    if sec.get("image"):
        cls += " hero--photo"
        style = f' style="background-image:linear-gradient(var(--hero-shade),var(--hero-shade)),url({esc(ctx.asset(sec["image"], False))})"'
    return f'<section class="{cls}"{style}><div class="wrap">{out}</div></section>\n'


def r_rings(ctx, sec):
    alt = esc(sec.get("alt", ""))
    n = len(sec["items"])
    rings = "".join(
        f'<span class="ring ring-{i}" data-ring="{i}"></span>' for i in range(n - 1, -1, -1)
    )
    items = ""
    for i, it in enumerate(sec["items"]):
        items += (
            f'<li class="ring-item{" is-active" if i == 0 else ""}" data-ring="{i}" tabindex="0" data-reveal style="--i:{i}">'
            f'<span class="ring-bar"></span><p class="ring-title"><span class="ring-kicker">{T(it["label"])}:</span> {rich(it["title"])}</p>'
            f'<p class="ring-text">{rich(it["text"])}</p></li>'
        )
    inner = (
        head(sec, center=True)
        + f'<div class="rings-grid"><div class="rings" role="img" aria-label="{alt}" data-reveal>{rings}</div>'
        + f'<ul class="ring-list">{items}</ul></div>'
    )
    return wrap(sec, inner, "section--rings")


def r_services(ctx, sec):
    cards = ""
    for i, it in enumerate(sec["items"]):
        img = ""
        if it.get("image"):
            img = f'<div class="svc-media"><img src="{esc(ctx.asset(it["image"], False))}" alt="" loading="lazy" width="1000" height="1000"></div>'
        claim = f'<p class="svc-claim">{rich(it["claim"])}</p>' if it.get("claim") else ""
        more = f'<span class="link-more">{T(ctx.t["ui"]["more"])}{icon("chev", "i i-chev")}</span>'
        cards += (
            f'<li class="svc svc-{i}" data-reveal style="--i:{i}"><a class="svc-card" {ctx.link_attrs(it["href"])}>'
            f'<span class="svc-go" aria-hidden="true">{icon("arrow")}</span><h3 class="h3">{rich(it["title"])}</h3><p class="svc-text">{rich(it["text"])}</p>{claim}{more}{img}</a></li>'
        )
    return wrap(sec, head(sec, center=True) + f'<ul class="svc-grid">{cards}</ul>', "section--services")


def r_tiles(ctx, sec):
    """Foto-Kacheln: Bild, Titel und Kurztext über Verlauf, ganze Kachel ist ein Link."""
    lis = ""
    for i, it in enumerate(sec["items"]):
        img = f'<img src="{esc(ctx.asset(it["image"], False))}" alt="" loading="lazy" width="800" height="1000">' if it.get("image") else ""
        lis += (
            f'<li class="wt" data-reveal style="--i:{i}"><a class="wt-link" {ctx.link_attrs(it["href"])}>{img}'
            f'<span class="wt-body"><h3 class="h3">{rich(it["title"])}</h3><span class="wt-text">{rich(it.get("text", ""))}</span>'
            f'<span class="wt-go" aria-hidden="true">{icon("arrow")}</span></span></a></li>'
        )
    return wrap(sec, head(sec, center=True) + f'<ul class="wt-grid">{lis}</ul>', "section--tiles")


def r_grid(ctx, sec):
    if sec.get("variant") == "services":
        return r_services(ctx, sec)
    if sec.get("variant") == "tiles":
        return r_tiles(ctx, sec)
    variant = sec.get("variant", "cards")
    cols = sec.get("cols", 3)
    cards = ""
    for i, it in enumerate(sec["items"]):
        style = f' style="--i:{i}"'
        n = f'<span class="num">{T(it["n"])}</span>' if it.get("n") else ""
        title = f'<h3 class="h3">{rich(it["title"])}</h3>' if it.get("title") else ""
        if it.get("image"):
            n = f'<img class="card-img" src="{esc(ctx.asset(it["image"], False))}" alt="{esc(it.get("alt", ""))}" loading="lazy" width="320" height="320">' + n
        text = f'<div class="card-text">{paragraphs(it["text"])}</div>' if it.get("text") else ""
        cta = ""
        if it.get("href"):
            cta = f'<p class="card-cta"><span class="link-more">{T(it.get("cta", ctx.t["ui"]["more"]))}{icon("chev", "i i-chev")}</span></p>'
        if variant == "benefits":
            inner = f'<span class="benefit-icon">{icon(it.get("icon", "check"))}</span>{title}{text}'
        elif variant == "steps":
            inner = f'<span class="step-n">{T(it.get("n", i + 1))}</span>{title}{text}'
        else:
            inner = f"{n}{title}{text}{cta}"
        if it.get("href") and variant == "cards":
            cards += f'<li class="card card--link grid-item" data-reveal{style}><a class="card-hit" {ctx.link_attrs(it["href"])}>{inner}</a></li>'
        else:
            cards += f'<li class="card grid-item grid-item--{variant}" data-reveal{style}>{inner}</li>'
    closing = ""
    if sec.get("closing"):
        cl = sec["closing"]
        if "\n" in cl:
            lab, _, stmt = str(cl).partition("\n")
            closing = mark(f'<div class="closing closing--big" data-reveal><p class="closing-label">{esc(lab)}</p><p class="closing-text">{rich(stmt.strip())}</p></div>', cl)
        else:
            closing = f'<p class="closing" data-reveal>{rich(cl)}</p>'
    inner = head(sec, center=(variant == "numbered")) + f'<ul class="grid grid--{cols} grid--{variant}">{cards}</ul>' + closing
    return wrap(sec, inner)


def r_logos(ctx, sec):
    lis = ""
    for i, it in enumerate(sec["items"]):
        if it.get("logo"):
            body = f'<img src="{esc(ctx.asset(it["logo"], False))}" alt="{esc(it["name"])}" loading="lazy" style="--lh:{int(it.get("h", 32))}px">'
        else:
            body = f'<span class="logo-text">{T(it["name"])}</span>'
        lis += f'<li data-reveal style="--i:{i}">{body}</li>'
    inner = head(sec, center=True, small=True) + f'<ul class="logos">{lis}</ul>'
    return wrap(sec, inner, "section--logos")


PLACEHOLDER_PERSON = (
    '<svg class="team-ph" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<circle cx="12" cy="8.5" r="4"/><path d="M4 21c0-4.4 3.6-7.5 8-7.5s8 3.1 8 7.5"/></svg>'
)


def profiles_enabled(ctx):
    """Profil-Fenster der Team-Kacheln: Standard nur auf Staging/Vorschau (noindex), nicht auf Produktion.
    config.json `team_profiles`: "staging" (Standard) | "on" | "off"."""
    mode = ctx.site.cfg.get("team_profiles", "staging")
    return mode == "on" or (mode == "staging" and ctx.site.noindex)


def team_photo(ctx, p, big=False):
    if p.get("image"):
        return f'<img src="{esc(ctx.asset(p["image"], False))}" alt="{esc(p["name"])}" loading="lazy" width="800" height="800">'
    return PLACEHOLDER_PERSON


def team_profile(ctx, p, labels, idx):
    pr = p.get("profile") or {}
    tid = f"team-{idx}"
    body = f'<p class="team-intro">{rich(pr["intro"])}</p>' if pr.get("intro") else ""
    if pr.get("roles"):
        body += f'<h4 class="team-h">{T(labels["roles"])}</h4><ul class="chips">' + "".join(f'<li class="chip">{T(x)}</li>' for x in pr["roles"]) + "</ul>"
    if pr.get("skills"):
        body += f'<h4 class="team-h">{T(labels["skills"])}</h4><ul class="chips">' + "".join(f'<li class="chip">{T(x)}</li>' for x in pr["skills"]) + "</ul>"
    if pr.get("career"):
        body += f'<h4 class="team-h">{T(labels["career"])}</h4><ol class="career">' + "".join(
            f'<li><span class="career-period">{T(c["period"])}</span><span>{T(c["title"])}</span></li>' for c in pr["career"]
        ) + "</ol>"
    return (
        f'<dialog class="team-modal" id="{tid}" aria-labelledby="{tid}-name">'
        f'<div class="team-modal-box">'
        f'<button class="team-close" type="button" data-team-close aria-label="{esc(labels["close"])}">{icon("x")}</button>'
        f'<div class="team-modal-head"><div class="team-photo team-photo--lg">{team_photo(ctx, p, True)}</div>'
        f'<div><h3 class="team-name" id="{tid}-name">{T(p["name"])}</h3><p class="team-role">{T(p["role"])}</p></div></div>'
        f'<div class="team-modal-body">{body}</div></div></dialog>'
    )


def r_about(ctx, sec):
    labels = sec.get("profile_labels", {})
    use_modal = profiles_enabled(ctx)
    tiles, dialogs = "", ""
    for i, p in enumerate(sec.get("team", [])):
        inner = (
            f'<span class="team-photo">{team_photo(ctx, p)}</span>'
            f'<span class="team-name">{T(p["name"])}</span><span class="team-role">{T(p["role"])}</span>'
        )
        if use_modal and p.get("profile"):
            tiles += (
                f'<li data-reveal style="--i:{i}"><button class="team-tile" type="button" data-team-open="team-{i}" aria-haspopup="dialog">'
                f'{inner}<span class="team-more" aria-hidden="true">{icon("arrow")}</span></button></li>'
            )
            dialogs += team_profile(ctx, p, labels, i)
        else:
            tiles += f'<li data-reveal style="--i:{i}"><div class="team-tile">{inner}</div></li>'
    team = f'<ul class="team">{tiles}</ul>' if tiles else ""
    lead = f'<p class="about-claim">{rich(sec["lead"])}</p>' if sec.get("lead") else ""
    bullets = '<ul class="dots">' + "".join(f"<li>{rich(b)}</li>" for b in sec.get("bullets", [])) + "</ul>"
    ctas = ""
    for b in sec.get("buttons", []):
        ctas += f'<a class="bar-link" {ctx.link_attrs(b["href"])}><span>{T(b["label"])}</span>{icon("arrow")}</a>'
    head_html = (
        '<header class="sec-head sec-head--center" data-reveal>'
        f'<h2 class="h2">{rich(sec.get("eyebrow", ""))}</h2>'
        f'<p class="lead">{rich(sec["title"])}</p></header>'
    )
    panel = f'<div class="about-panel"><div class="about-text" data-reveal>{lead}{bullets}</div>{team}</div>'
    return wrap(sec, head_html + panel + f'<div class="bar-links" data-reveal>{ctas}</div>' + dialogs, "section--about")


def r_text(ctx, sec):
    body = ""
    for p in sec.get("paragraphs", []):
        body += paragraphs(p)
    qcards = ""
    if sec.get("list") and sec.get("listStyle") == "questions":
        qcards = '<ol class="qcards" data-reveal>' + "".join(
            f'<li class="qcard"><span class="qmark" aria-hidden="true">?</span><p class="qtext">{rich(q)}</p></li>' for q in sec["list"]
        ) + "</ol>"
    elif sec.get("list"):
        body += list_html(sec["list"], sec.get("listStyle", "ticks"))
    after = ""
    for p in sec.get("after", []):
        main, _, sub_ = str(p).partition("\n")
        callout = (
            f'<div class="callout" data-reveal><p class="callout-main">{rich(main)}</p>'
            + (f'<p class="callout-sub">{rich(sub_.strip())}</p>' if sub_.strip() else "")
            + "</div>"
        )
        after += mark(callout, p)
    return wrap(sec, head(sec) + (f'<div class="prose{" prose--wide" if sec.get("wideBody") else ""}" data-reveal>{body}</div>' if body else "") + qcards + after)


def mock_board(ctx, it):
    """Checkliste als Projekt-Grafik (wirkt wie ein Ausschnitt aus einem Projekt-Tool, nicht wie Fließtext)."""
    st = ctx.t["ui"]["mock"]
    items = it["checklist"]
    done = sum(1 for c in items if c.get("done"))
    first_open = next((i for i, c in enumerate(items) if not c.get("done")), None)
    rows = ""
    for i, c in enumerate(items):
        state = "done" if c.get("done") else ("active" if i == first_open else "todo")
        ic = icon("check", "i") if state == "done" else ""
        rows += (
            f'<li class="mock-row mock-row--{state}"><span class="mock-ic" aria-hidden="true">{ic}</span>'
            f'<span class="mock-text">{T(c["text"])}</span><span class="mock-state">{esc(st[state])}</span></li>'
        )
    pct = round(100 * (done + 0.5) / len(items)) if items else 0
    title = T(it["checklistTitle"]) if it.get("checklistTitle") else ""
    label = T(it["checklistLabel"]) if it.get("checklistLabel") else ""
    return (
        '<div class="mock-wrap" aria-hidden="false"><figure class="mock">'
        f'<div class="mock-bar"><span class="mock-win" aria-hidden="true"><i></i><i></i><i></i></span><span class="mock-title">{title}</span><span class="mock-badge">{label}</span></div>'
        f'<div class="mock-progress" aria-hidden="true"><span style="width:{pct}%"></span></div>'
        f'<ul class="mock-list">{rows}</ul></figure></div>'
    )


def r_features(ctx, sec):
    t = ctx.t["ui"]
    bento = sec.get("layout") == "bento"
    inner = head(sec)
    if sec.get("introChips"):
        inner += f'<div data-reveal>{chips(sec["introChips"], "chips--lg")}</div>'
    cards = ""
    for i, it in enumerate(sec["items"], 1):
        left = f'<span class="feat-n">{i:02d}</span><h3 class="h3 feat-title">{rich(it["title"])}</h3>'
        if it.get("subtitle"):
            left += f'<p class="feat-sub">{rich(it["subtitle"])}</p>'
        text = f'<div class="feat-text">{paragraphs(it["text"])}</div>' if it.get("text") else ""
        bullets = '<ul class="dots">' + "".join(f"<li>{rich(b)}</li>" for b in it["bullets"]) + "</ul>" if it.get("bullets") else ""
        chip_html = chips(it["chips"], "chips--block" if it.get("chipsStyle") == "block" else "") if it.get("chips") else ""
        checklist = mock_board(ctx, it) if it.get("checklist") else ""
        note = f'<div class="note">{paragraphs(it["note"])}</div>' if it.get("note") else ""
        benefit = (
            f'<p class="feat-benefit"><span class="feat-benefit-ic" aria-hidden="true">{icon("arrow")}</span>'
            f'<span><strong>{esc(t["benefit"])}:</strong> {T(it["benefit"])}</span></p>'
            if it.get("benefit") else ""
        )
        tools = ""
        if it.get("tools"):
            tools = f'<div class="tools"><span class="tools-label">{T(t["tools"])}</span>{chips(it["tools"], "chips--sm chips--tools")}</div>'
        if bento and it.get("wide"):
            # volle Breite: Zahl/Titel/Untertitel einspaltig, dann zweispaltig (Text | Fazit), dann einspaltig Prozessbeispiele und zuletzt die Tools
            fazit = ""
            if it.get("note"):
                fazit = f'<div class="note note--fazit"><span class="note-ic" aria-hidden="true">{icon("arrow")}</span><div>{paragraphs(it["note"])}</div></div>'
            cards += (
                f'<article class="card feat feat--wide" data-reveal><div class="feat-l">{left}</div>'
                f'<div class="feat-cols"><div class="feat-r">{text}{bullets}</div><div class="feat-r">{checklist}{fazit}</div></div>'
                f'<div class="feat-chips">{chip_html}</div>{tools}</article>'
            )
            continue
        right = text + bullets + chip_html + checklist + benefit + note + tools
        cards += f'<article class="card feat" data-reveal><div class="feat-l">{left}</div><div class="feat-r">{right}</div></article>'
    return wrap(sec, inner + f'<div class="feat-list{" feat-list--bento" if bento else ""}">{cards}</div>')


def r_chips(ctx, sec):
    return wrap(sec, head(sec) + f'<div data-reveal>{chips(sec["items"], "chips--lg")}</div>')


def r_projects(ctx, sec):
    cards = ""
    for i, it in enumerate(sec["items"]):
        kpi = f'<span class="tile-kpi">{T(it["kpi"])}</span>' if it.get("kpi") else ""
        tag = f'<span class="tile-tag">{T(it["tag"])}</span>' if it.get("tag") else ""
        cards += (
            f'<li class="project" data-reveal style="--i:{i}"><div class="tile tile--{i % 3}">{tag}{kpi}</div>'
            f'<h3 class="h3">{rich(it["title"])}</h3><p>{rich(it["text"])}</p></li>'
        )
    return wrap(sec, head(sec) + f'<ul class="projects projects--{len(sec["items"])}">{cards}</ul>', "")


def r_toolgroups(ctx, sec):
    groups = ""
    for i, g in enumerate(sec["groups"]):
        groups += f'<li class="card tool-group" data-reveal style="--i:{i}"><h3 class="h4">{esc(g["title"])}</h3>{chips(g["items"], "chips--sm")}</li>'
    comp = ""
    if sec.get("compliance"):
        c = sec["compliance"]
        comp = (
            f'<div class="card compliance" data-reveal><span class="compliance-icon">{icon("lock")}</span>'
            f'<div><h3 class="h4">{T(c["title"])}</h3>{list_html(c["items"], "ticks")}</div></div>'
        )
    return wrap(sec, head(sec) + f'<ul class="tool-groups">{groups}</ul>{comp}')


def r_offers(ctx, sec):
    cards = ""
    for i, it in enumerate(sec["items"]):
        feat = " offer--featured" if it.get("featured") else ""
        body = f'<h3 class="h3">{rich(it["title"])}</h3>'
        if it.get("subtitle"):
            body += f'<p class="offer-sub">{rich(it["subtitle"])}</p>'
        if it.get("text"):
            body += paragraphs(it["text"])
        if it.get("result"):
            body += f'<p class="offer-result">{rich(it["result"])}</p>'
        if it.get("ideal"):
            body += f'<p class="offer-ideal">{rich(it["ideal"])}</p>'
        if it.get("list"):
            body += f'<p class="offer-list-title">{T(it.get("listTitle", ""))}</p>' + list_html(it["list"], "ticks")
        cta = f'<div class="offer-cta">{btn(ctx, it["cta"])}</div>' if it.get("cta") else ""
        cards += f'<li class="card offer{feat}" data-reveal style="--i:{i}"><div class="offer-body">{body}</div>{cta}</li>'
    return wrap(sec, head(sec) + f'<ul class="offers">{cards}</ul>')


def r_faq(ctx, sec):
    """Häufige Fragen: aufklappbar mit <details> (ohne JavaScript); erzeugt zusätzlich FAQPage-Daten (siehe jsonld_graph)."""
    items = ""
    for i, it in enumerate(sec["items"]):
        items += (
            f'<details class="faq-item" data-reveal style="--i:{i}"><summary class="faq-q"><span>{rich(it["q"])}</span>'
            f'{icon("down", "i faq-chev")}</summary><div class="faq-a">{paragraphs(it["a"])}</div></details>'
        )
    return wrap(sec, head(sec) + f'<div class="faq">{items}</div>', "section--faq")


def fmt_date(ctx, iso):
    """ISO-Datum -> Anzeigeformat der Sprache (site.json -> ui.dateFormat mit {d} {D} {m} {M} {Y}, ui.months)."""
    try:
        d = datetime.date.fromisoformat(str(iso))
    except ValueError:
        return str(iso)
    ui = ctx.t["ui"]
    months = ui.get("months") or []
    return ui.get("dateFormat", "{Y}-{m}-{d}").format(
        Y=d.year, m=f"{d.month:02}", d=f"{d.day:02}", D=d.day, M=months[d.month - 1] if len(months) == 12 else f"{d.month:02}"
    )


def media_or_placeholder(ctx, it, cls, label=""):
    """Bild (optional) oder neutrale Platzhalterfläche mit Anfangsbuchstabe."""
    if it.get("image"):
        return f'<div class="{cls}"><img src="{esc(ctx.asset(it["image"], False))}" alt="{esc(it.get("alt", ""))}" loading="lazy" width="1200" height="750"></div>'
    letter = esc((str(label).strip() or "·")[:1].upper())
    return f'<div class="{cls} {cls}--ph" aria-hidden="true"><span>{letter}</span></div>'


def r_cases(ctx, sec):
    """Referenz-Cases als Slider (CSS scroll-snap, funktioniert ohne JavaScript; Pfeile kommen per JS dazu)."""
    ui = ctx.t["ui"]
    slides = ""
    for i, it in enumerate(sec["items"]):
        res = ""
        if it.get("results"):
            res = '<dl class="case-results">' + "".join(
                f'<div><dt>{T(r["label"])}</dt><dd>{T(r["value"])}</dd></div>' for r in it["results"]
            ) + "</dl>"
        cta = f'<p class="case-cta">{btn(ctx, dict(it["cta"], style="link"))}</p>' if it.get("cta") else ""
        slides += (
            f'<li class="slide card case" id="{esc(sec.get("id", "cases"))}-{i + 1}">'
            f'{media_or_placeholder(ctx, it, "case-media", it.get("client", it.get("title", "")))}'
            f'<div class="case-body">'
            + (f'<p class="case-client">{T(it["client"])}</p>' if it.get("client") else "")
            + f'<h3 class="h3 case-title">{rich(it["title"])}</h3>'
            + (f'<div class="card-text">{paragraphs(it["text"])}</div>' if it.get("text") else "")
            + res + cta + "</div></li>"
        )
    nav = (
        f'<div class="slider-nav" data-slider-nav>'
        f'<button type="button" class="slider-btn" data-slider-prev aria-label="{esc(ui["slider"]["prev"])}">{icon("chev", "i i-prev")}</button>'
        f'<button type="button" class="slider-btn" data-slider-next aria-label="{esc(ui["slider"]["next"])}">{icon("chev", "i")}</button></div>'
    )
    inner = (
        head(sec)
        + f'<div class="slider" data-slider data-reveal>{nav}'
        f'<ul class="slider-track" role="list" tabindex="0" aria-label="{esc(ui["slider"]["label"])}">{slides}</ul></div>'
    )
    return wrap(sec, inner, "section--cases")


def r_process(ctx, sec):
    """Prozess-Schritte. variant: steps (Standard, nebeneinander) | timeline (untereinander mit Linie)."""
    variant = sec.get("variant", "steps")
    items = ""
    for i, it in enumerate(sec["items"]):
        items += (
            f'<li class="proc-step" data-reveal style="--i:{i}"><span class="proc-n" aria-hidden="true">{i + 1:02d}</span>'
            f'<div class="proc-body"><h3 class="h3 proc-title">{rich(it["title"])}</h3>'
            + (f'<p class="proc-meta">{T(it["meta"])}</p>' if it.get("meta") else "")
            + (f'<div class="card-text">{paragraphs(it["text"])}</div>' if it.get("text") else "")
            + "</div></li>"
        )
    closing = f'<div class="proc-cta" data-reveal>{buttons(ctx, sec.get("buttons"))}</div>' if sec.get("buttons") else ""
    return wrap(sec, head(sec) + f'<ol class="process process--{esc(variant)}">{items}</ol>' + closing, "section--process")


def r_pricing(ctx, sec):
    """Preistabelle / Pläne. Ein Plan mit featured:true bekommt das Badge (Text aus `badge` oder ui.recommended)."""
    cards = ""
    for i, it in enumerate(sec["items"]):
        feat = bool(it.get("featured"))
        badge = ""
        if feat:
            badge = f'<span class="plan-badge">{T(it["badge"]) if it.get("badge") else esc(ctx.t["ui"]["recommended"])}</span>'
        price = (
            '<p class="plan-price">'
            + (f'<span class="plan-from">{T(it["from"])}</span>' if it.get("from") else "")
            + f'<span class="plan-amount">{T(it["price"])}</span>'
            + (f'<span class="plan-period">{T(it["period"])}</span>' if it.get("period") else "")
            + "</p>"
        )
        body = (
            f'<h3 class="h3 plan-name">{rich(it["name"])}</h3>'
            + (f'<p class="plan-sub">{rich(it["subtitle"])}</p>' if it.get("subtitle") else "")
            + price
            + (f'<p class="plan-note">{rich(it["note"])}</p>' if it.get("note") else "")
            + (list_html(it["features"], "ticks") if it.get("features") else "")
        )
        cta = f'<div class="plan-cta">{btn(ctx, it["cta"])}</div>' if it.get("cta") else ""
        cards += f'<li class="card plan{" plan--featured" if feat else ""}" data-reveal style="--i:{i}">{badge}<div class="plan-body">{body}</div>{cta}</li>'
    foot = f'<p class="plans-foot" data-reveal>{rich(sec["footnote"])}</p>' if sec.get("footnote") else ""
    return wrap(sec, head(sec) + f'<ul class="plans plans--{len(sec["items"])}">{cards}</ul>' + foot, "section--pricing")


def posts_for(ctx, limit=None, category=None):
    """Beiträge der aktuellen Sprache, neueste zuerst."""
    posts = [p for (l, _), p in ctx.site.pages.items() if l == ctx.lang and p.get("kind") == "post"]
    if category:
        posts = [p for p in posts if article_of(p).get("category") == category]
    posts.sort(key=lambda p: str(article_of(p).get("date", "")), reverse=True)
    return posts[:limit] if limit else posts


def article_of(page):
    return next((s for s in page["sections"] if s["type"] == "article"), {})


def r_news(ctx, sec):
    """Beitragsliste (Blog/News): zieht die Beiträge aus content/<lang>/posts/. limit = Anzahl; variant: cards | list."""
    variant = sec.get("variant", "cards")
    ui = ctx.t["ui"]
    cards = ""
    for i, p in enumerate(posts_for(ctx, sec.get("limit"), sec.get("category"))):
        a = article_of(p)
        meta = (
            (f'<span class="chip">{T(a["category"])}</span>' if a.get("category") else "")
            + f'<time datetime="{esc(a.get("date", ""))}">{esc(fmt_date(ctx, a.get("date", "")))}</time>'
        )
        teaser = a.get("teaser") or p.get("description", "")
        inner = (
            (media_or_placeholder(ctx, a, "news-media", a.get("title", "")) if variant == "cards" else "")
            + f'<div class="news-body"><p class="news-meta">{meta}</p><h3 class="h3 news-title">{rich(a["title"])}</h3>'
            f'<p class="news-teaser">{rich(teaser)}</p>'
            f'<p class="card-cta"><span class="link-more">{esc(ui["readMore"])}{icon("chev", "i i-chev")}</span></p></div>'
        )
        cards += f'<li class="card card--link news-item" data-reveal style="--i:{i}"><a class="news-hit" href="{esc(ctx.page_url(ctx.lang, p["id"]))}">{inner}</a></li>'
    if not cards:
        cards = f'<li class="news-empty">{esc(ui.get("noPosts", ""))}</li>'
    more = f'<div class="news-more" data-reveal>{btn(ctx, sec["cta"])}</div>' if sec.get("cta") else ""
    return wrap(sec, head(sec) + f'<ul class="news news--{esc(variant)}">{cards}</ul>' + more, "section--news")


def r_article(ctx, sec):
    """Beitragsseite. body: Liste aus Absatz-Text, {"h": …}, {"list": […]}, {"quote": …, "by": …}."""
    body = ""
    for b in sec.get("body", []):
        if isinstance(b, dict):
            if b.get("h"):
                body += f'<h2 class="article-h">{rich(b["h"])}</h2>'
            if b.get("list"):
                body += list_html(b["list"], "ticks")
            if b.get("quote"):
                body += f'<blockquote class="article-quote"><p>{rich(b["quote"])}</p>' + (f'<footer>{T(b["by"])}</footer>' if b.get("by") else "") + "</blockquote>"
        else:
            body += paragraphs(b)
    meta = (
        (f'<span class="chip">{T(sec["category"])}</span>' if sec.get("category") else "")
        + f'<time datetime="{esc(sec.get("date", ""))}">{esc(fmt_date(ctx, sec.get("date", "")))}</time>'
        + (f'<span class="article-author">{T(sec["author"])}</span>' if sec.get("author") else "")
    )
    img = media_or_placeholder(ctx, sec, "article-media", sec.get("title", "")) if sec.get("image") else ""
    back = f'<p class="article-back">{btn(ctx, dict(sec["back"], style="link"))}</p>' if sec.get("back") else ""
    return wrap(
        sec,
        f'<article class="article"><header class="article-head" data-reveal><p class="article-meta">{meta}</p>'
        f'<h1 class="h2 article-title">{rich(sec["title"])}</h1>'
        + (f'<p class="lead">{rich(sec["teaser"])}</p>' if sec.get("teaser") else "")
        + f"</header>{img}<div class=\"prose prose--article\" data-reveal>{body}</div>{back}</article>",
        "section--article",
    )


def r_cta(ctx, sec):
    out = ""
    if sec.get("eyebrow"):
        out += f'<p class="eyebrow">{rich(sec["eyebrow"])}</p>'
    out += f'<h2 class="h2">{rich(sec["title"])}</h2>'
    if sec.get("subtitle"):
        out += f'<p class="cta-sub">{rich(sec["subtitle"])}</p>'
    if sec.get("text"):
        out += f'<p class="lead">{rich(sec["text"])}</p>'
    if sec.get("person"):
        out += f'<p class="cta-person">{rich(sec["person"])}</p>'
    if sec.get("teaser"):
        out += f'<p class="cta-teaser">{rich(sec["teaser"])}</p>'
    out += buttons(ctx, sec.get("buttons"), "btn-row btn-row--center")
    return f'<section class="section theme-light section--cta"><div class="wrap"><div class="cta-panel" data-reveal>{out}</div></div></section>\n'


def tile(label, value, href=None, extra="", ext=False):
    go = '<span class="svc-go" aria-hidden="true">' + icon("arrow") + "</span>"
    inner = f'<span class="ctile-label">{T(label)}</span><span class="ctile-value">{value}</span>'
    if href is None:
        return f'<li><div class="ctile">{inner}</div></li>'
    tgt = ' target="_blank" rel="noopener noreferrer"' if ext else ""
    safe_url(href)
    return f'<li><a class="ctile ctile--link" href="{esc(href)}"{tgt}{extra}>{go}{inner}</a></li>'


def r_contact(ctx, sec):
    cfg = ctx.site.cfg
    f = ctx.t["form"]
    tel = re.sub(r"[^\d+]", "", cfg["phone"].replace("(0)", ""))
    m = cfg["mail"]
    tiles = tile(f["mail"], esc(m["user"]) + "[at]" + esc(m["domain"]), "#", f' data-mu="{esc(m["user"])}" data-md="{esc(m["domain"])}"')
    tiles += tile(f["phone"], esc(cfg["phone"]), f"tel:{tel}")
    tiles += tile(f["location"], f'{esc(cfg["street"])},<br>{esc(cfg["zip"])} {esc(cfg["city"])}', cfg.get("map_url") or None, ext=True)
    if cfg.get("booking_url"):
        tiles += tile(f["booking"], esc(f["bookingLink"]), cfg["booking_url"], ext=True)
    mp = ""
    if cfg.get("map_image"):
        mp = (
            f'<a class="map" href="{esc(safe_url(cfg.get("map_url") or "#"))}" target="_blank" rel="noopener noreferrer" aria-label="{esc(f["mapLabel"])}" data-reveal>'
            f'<img src="{esc(ctx.asset(cfg["map_image"], False))}" alt="" loading="lazy" width="1400" height="865">'
            f'<span class="map-chip">{esc(cfg["street"])}, {esc(cfg["city"])}{icon("arrow")}</span></a>'
        )
    opts = "".join(f'<option value="{esc(o["value"])}">{esc(o["label"])}</option>' for o in f["topics"])
    privacy = f'<a {ctx.link_attrs("page:privacy")}>{T(f["privacyLink"])}</a>'
    consent = esc(f["consent"]).replace("{privacy}", privacy)
    action = "#" if ctx.site.preview else cfg["form_action"]
    preview_attr = ' data-preview="1"' if ctx.site.preview else ""
    form = f"""
<form class="form" id="formular" method="post" action="{esc(action)}" novalidate{preview_attr}
  data-sending="{esc(f['sending'])}" data-ok="{esc(f['ok'])}" data-err="{esc(f['err'])}" data-invalid="{esc(f['invalid'])}" data-preview-msg="{esc(f['previewMsg'])}">
  <input type="hidden" name="lang" value="{ctx.lang}">
  <input type="hidden" name="ts" value="">
  <input type="hidden" name="sig" value="">
  <div class="hp" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
  <div class="field"><label for="f-name">{T(f['name'])} <span class="req" aria-hidden="true">*</span></label><input id="f-name" name="name" type="text" autocomplete="name" required maxlength="120"></div>
  <div class="field"><label for="f-email">{T(f['email'])} <span class="req" aria-hidden="true">*</span></label><input id="f-email" name="email" type="email" autocomplete="email" required maxlength="160"></div>
  <div class="field-row">
    <div class="field"><label for="f-company">{T(f['company'])}</label><input id="f-company" name="company" type="text" autocomplete="organization" maxlength="160"></div>
    <div class="field"><label for="f-phone">{T(f['phoneField'])}</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" maxlength="60"></div>
  </div>
  <div class="field"><label for="f-topic">{T(f['topic'])}</label><select id="f-topic" name="topic">{opts}</select></div>
  <div class="field"><label for="f-message">{T(f['message'])} <span class="req" aria-hidden="true">*</span></label><textarea id="f-message" name="message" rows="6" required maxlength="5000"></textarea></div>
  <div class="field field--check"><input id="f-consent" name="consent" type="checkbox" value="1" required><label for="f-consent">{consent} <span class="req" aria-hidden="true">*</span></label></div>
  <button class="btn btn-primary btn-block" type="submit">{T(f['submit'])}</button>
  <p class="form-status" role="status" aria-live="polite"></p>
</form>"""
    bento = f'<div class="bento"><ul class="tiles" data-reveal>{tiles}</ul>{mp}</div>'
    card = f'<div class="card contact-form" data-reveal><h2 class="h3 form-title">{esc(f["title"])}</h2>{form}</div>'
    return wrap(sec, bento + card)


def r_legal(ctx, sec):
    table = ""
    if sec.get("table"):
        table = '<dl class="kv">' + "".join(
            f"<div><dt>{rich(k)}</dt><dd>{rich(v)}</dd></div>" for k, v in sec["table"]
        ) + "</dl>"
    out = ""
    for b in sec.get("blocks", []):
        lvl = b.get("level", 2)
        if b.get("h"):
            out += f'<h{lvl + 1} class="legal-h{lvl}">{rich(b["h"])}</h{lvl + 1}>'
        for p in b.get("p", []):
            out += paragraphs(p)
        if b.get("list"):
            out += "<ul class=\"plain-list\">" + "".join(f"<li>{rich(i)}</li>" for i in b["list"]) + "</ul>"
    return wrap(sec, table + f'<div class="prose prose--legal">{out}</div>')


def r_notfound(ctx, sec):
    return wrap(sec, f'<div class="notfound" data-reveal><p class="num num--big">404</p>{head(sec)}{buttons(ctx, sec.get("buttons"), "btn-row btn-row--center")}</div>')


RENDERERS = {
    "hero": r_hero,
    "rings": r_rings,
    "grid": r_grid,
    "logos": r_logos,
    "about": r_about,
    "text": r_text,
    "features": r_features,
    "chips": r_chips,
    "projects": r_projects,
    "toolgroups": r_toolgroups,
    "offers": r_offers,
    "faq": r_faq,
    "cases": r_cases,
    "process": r_process,
    "pricing": r_pricing,
    "news": r_news,
    "article": r_article,
    "cta": r_cta,
    "contact": r_contact,
    "legal": r_legal,
    "notfound": r_notfound,
}

# --------------------------------------------------------------------------- #
# Seitenrahmen
# --------------------------------------------------------------------------- #


def brand(ctx, cls="brand"):
    cfg = ctx.site.cfg
    home = ctx.page_url(ctx.lang, "home")
    label = esc(ctx.t["ui"]["homeLabel"])
    if cfg.get("logo_image"):
        nm = esc(cfg.get("brand", {}).get("name", ""))
        if "brand--foot" in cls and cfg.get("logo_dark"):
            return f'<a class="{cls}" href="{esc(home)}" aria-label="{label}"><img class="brand-full" src="{esc(ctx.asset(cfg["logo_dark"], False))}" alt="{nm}" width="{cfg.get("logo_width", 800)}" height="{cfg.get("logo_height", 441)}"></a>'
        inner = f'<img class="brand-full" src="{esc(ctx.asset(cfg["logo_image"], False))}" alt="{nm}" width="{cfg.get("logo_width", 800)}" height="{cfg.get("logo_height", 441)}">'
        if "brand--foot" not in cls:
            if cfg.get("logo_dark"):
                inner += f'<img class="brand-dark" src="{esc(ctx.asset(cfg["logo_dark"], False))}" alt="" width="{cfg.get("logo_width", 800)}" height="{cfg.get("logo_height", 441)}" aria-hidden="true">'
            if cfg.get("logo_icon"):
                inner += f'<img class="brand-icon" src="{esc(ctx.asset(cfg["logo_icon"], False))}" alt="" width="64" height="64" aria-hidden="true">'
    else:
        inner = f'<span class="brand-bit">{esc(cfg.get("brand", {}).get("name", ""))}</span>'
    return f'<a class="{cls}" href="{esc(home)}" aria-label="{label}">{inner}</a>'


FLAGS = {
    "de": '<rect width="24" height="8" fill="#000"/><rect y="8" width="24" height="8" fill="#d00"/><rect y="16" width="24" height="8" fill="#ffce00"/>',
    "en": '<rect width="24" height="24" fill="#fff"/>'
    + "".join(f'<rect y="{y}" width="24" height="1.85" fill="#b22234"/>' for y in (0, 3.7, 7.4, 11.1, 14.8, 18.5, 22.15))
    + '<rect width="12" height="12.9" fill="#3c3b6e"/>'
    + "".join(f'<circle cx="{x}" cy="{y}" r="0.7" fill="#fff"/>' for x in (2.5, 6, 9.5) for y in (2.5, 6.3, 10))
    + "".join(f'<circle cx="{x}" cy="{y}" r="0.7" fill="#fff"/>' for x in (4.25, 7.75) for y in (4.4, 8.2)),
}


FLAGS.update({
    "fr": '<rect width="8" height="24" fill="#0055a4"/><rect x="8" width="8" height="24" fill="#fff"/><rect x="16" width="8" height="24" fill="#ef4135"/>',
    "it": '<rect width="8" height="24" fill="#009246"/><rect x="8" width="8" height="24" fill="#fff"/><rect x="16" width="8" height="24" fill="#ce2b37"/>',
    "es": '<rect width="24" height="24" fill="#aa151b"/><rect y="6" width="24" height="12" fill="#f1bf00"/>',
    "nl": '<rect width="24" height="8" fill="#ae1c28"/><rect y="8" width="24" height="8" fill="#fff"/><rect y="16" width="24" height="8" fill="#21468b"/>',
    "pl": '<rect width="24" height="12" fill="#fff"/><rect y="12" width="24" height="12" fill="#dc143c"/>',
    "pt": '<rect width="10" height="24" fill="#006600"/><rect x="10" width="14" height="24" fill="#ff0000"/>',
})


def flag(l):
    """Rundes Flaggen-Icon (inline SVG); leer, wenn für die Sprache keine Flagge hinterlegt ist."""
    if l not in FLAGS:
        return ""
    return (
        f'<svg class="flag" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
        f'<defs><clipPath id="flag-{l}"><circle cx="12" cy="12" r="12"/></clipPath></defs>'
        f'<g clip-path="url(#flag-{l})">{FLAGS[l]}</g></svg>'
    )


def lang_url(ctx, l):
    return ctx.page_url(l, ctx.page["id"]) if not ctx.page.get("output") else ctx.page_url(l, "home")


def lang_switch(ctx, cls="lang"):
    """Inline-Links (Footer, Mobile-Menü)."""
    out = f'<div class="{cls}" role="group" aria-label="{esc(ctx.t["ui"]["langLabel"])}">'
    for l in ctx.site.langs:
        cur = ' aria-current="true"' if l == ctx.lang else ""
        out += f'<a href="{esc(lang_url(ctx, l))}" hreflang="{l}" lang="{l}"{cur}>{l.upper()}</a>'
    return out + "</div>"


def lang_menu(ctx):
    """Dropdown mit Globus (Header)."""
    names = ctx.site.cfg.get("language_names", {})
    items = ""
    for l in ctx.site.langs:
        cur = ' aria-current="true"' if l == ctx.lang else ""
        mark = icon("check", "i i-check") if l == ctx.lang else ""
        items += f'<li><a href="{esc(lang_url(ctx, l))}" hreflang="{l}" lang="{l}"{cur}><span class="lang-name">{flag(l)}<span>{esc(names.get(l, l.upper()))}</span></span>{mark}</a></li>'
    return (
        f'<div class="lang-menu"><button class="lang-btn" type="button" aria-expanded="false" aria-controls="lang-list" aria-label="{esc(ctx.t["ui"]["langLabel"])}: {ctx.lang.upper()}">'
        f'{icon("globe", "i")}<span class="lang-code">{ctx.lang.upper()}</span>{icon("down", "i i-down")}</button>'
        f'<ul class="lang-list" id="lang-list" hidden>{items}</ul></div>'
    )


def mega_html(ctx, mega, mobile=False):
    cols = ""
    for col in mega["cols"]:
        if col.get("strong"):
            lis = "".join(
                f'<li><a class="mega-link mega-link--strong" href="{esc(ctx.href(l["href"]))}"><span>{T(l["label"])}</span></a></li>'
                for l in col["strong"]
            )
            cols += f'<div class="mega-col"><ul class="mega-list">{lis}</ul></div>'
            continue
        lis = ""
        for l in col["links"]:
            badge = f'<span class="mega-badge">{esc(l["badge"])}</span>' if l.get("badge") else ""
            cls = "mega-link mega-link--lead" if l.get("lead") else "mega-link"
            sep = ' class="mega-sep"' if l.get("sepAfter") else ""
            lis += f'<li{sep}><a class="{cls}" href="{esc(ctx.href(l["href"]))}"><span>{T(l["label"])}</span>{badge}</a></li>'
        cols += f'<div class="mega-col"><div class="mega-title">{T(col["title"])}</div><ul class="mega-list">{lis}</ul></div>'
    c = mega.get("cta")
    if c:
        txt = f'<span class="mega-cta-text">{T(c["text"])}</span>' if c.get("text") else ""
        cols += f'<div class="mega-cta">{txt}<a class="btn btn-primary btn-sm" href="{esc(ctx.href(c["href"]))}">{T(c["label"])}</a></div>'
    return cols


def loader_html(ctx):
    cfg = ctx.site.cfg
    logo = f'<img src="{esc(ctx.asset(cfg.get("logo_icon", "assets/img/logo-icon.png"), False))}" alt="" width="480" height="470">'
    return (
        f'<div class="intro-mark">{logo}<svg class="intro-ring" viewBox="0 0 100 100" aria-hidden="true">'
        '<circle class="intro-track" cx="50" cy="50" r="46"/><circle class="intro-arc" cx="50" cy="50" r="46"/></svg></div>'
    )


def header(ctx):
    t = ctx.t
    items, mobile = "", ""
    for i, n in enumerate(t["nav"]):
        pid = n["href"].split("#")[0][5:]
        cur = ' aria-current="page"' if pid == ctx.page["id"] else ""
        url = esc(ctx.href(n["href"]))
        mega = n.get("mega")
        if mega:
            mid = f"mega-{i}"
            items += (
                f'<li class="nav-slot has-mega"><a class="nav-item" href="{url}"{cur}>{T(n["label"])}</a>'
                f'<button class="nav-chev" type="button" aria-expanded="false" aria-controls="{mid}" aria-label="{esc(mega["label"])}: {esc(n["label"])}">{icon("down", "i")}</button>'
                f'<div class="mega-wrap" id="{mid}" hidden><div class="mega">{mega_html(ctx, mega)}</div></div></li>'
            )
            mobile += (
                f'<li class="m-item"><div class="m-row"><a href="{url}"{cur}>{T(n["label"])}</a>'
                f'<button class="m-chev" type="button" aria-expanded="false" aria-controls="m-{mid}" aria-label="{esc(mega["label"])}: {esc(n["label"])}">{icon("down", "i")}</button></div>'
                f'<div class="m-sub" id="m-{mid}"><div class="m-sub-in"><div class="mobile-mega">{mega_html(ctx, mega, True)}</div></div></div></li>'
            )
        else:
            items += f'<li class="nav-slot"><a class="nav-item" href="{url}"{cur}>{T(n["label"])}</a></li>'
            mobile += f'<li><a href="{url}"{cur}>{T(n["label"])}</a></li>'
    cta = t["cta"]
    return f"""<header class="site-header" data-header>
  <div class="bar">
    {brand(ctx)}
    <nav class="nav-desktop" aria-label="{esc(t['ui']['navLabel'])}"><ul>{items}</ul></nav>
    <div class="bar-right">
      {lang_menu(ctx)}
      <a class="btn btn-dark nav-cta" href="{esc(ctx.href(cta['href']))}">{esc(cta['label'])}</a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="{esc(t['ui']['menu'])}" data-label-open="{esc(t['ui']['menu'])}" data-label-close="{esc(t['ui']['menuClose'])}"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu">
  <nav aria-label="{esc(t['ui']['navLabel'])}"><ul class="mobile-links">{mobile}</ul></nav>
  <a class="btn btn-dark btn-block" href="{esc(ctx.href(cta['href']))}">{esc(cta['label'])}</a>
  {lang_switch(ctx, "lang lang--mobile")}
</div>"""


def subnav(ctx):
    sn = ctx.page.get("subnav")
    if not sn:
        return ""
    links = "".join(f'<li><a href="{esc(safe_url(l["href"]))}">{T(l["label"])}</a></li>' for l in sn["links"])
    return (
        f'<nav class="subnav" aria-label="{esc(sn["title"])}"><div class="subnav-in">'
        f'<span class="subnav-title">{T(sn["title"])}</span><ul>{links}</ul></div></nav>\n'
    )


def footer(ctx):
    """Globaler Footer – identisch auf allen Seiten (Texte aus site.json, Social aus config.json)."""
    t, cfg = ctx.t, ctx.site.cfg
    ft = t["footer"]
    areas = "".join(
        f'<li><a class="foot-link" href="{esc(ctx.href(a["href"]))}">{T(a["label"])}</a></li>' for a in ft["areas"]
    )
    li = ""
    if cfg.get("linkedin_url"):
        li = f'<a class="social" href="{esc(safe_url(cfg["linkedin_url"]))}" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">{icon("linkedin")}</a>'
    terms_ = f'<span aria-hidden="true">|</span><a href="{esc(ctx.href("page:terms"))}">{T(ft["terms"])}</a>' if ft.get("terms") else ""
    copyright_ = esc(ft["copyright"]).replace("{year}", f'<span data-year>{ctx.site.today.year}</span>')
    m = cfg["mail"]
    tel = re.sub(r"[^\d+]", "", cfg["phone"].replace("(0)", ""))
    mailto = f'<a href="#" data-mu="{esc(m["user"])}" data-md="{esc(m["domain"])}">{esc(m["user"])}[at]{esc(m["domain"])}</a>'
    legal = (f'<li><a href="{esc(ctx.href("page:imprint"))}">{T(ft["imprint"])}</a></li>'
             f'<li><a href="{esc(ctx.href("page:privacy"))}">{T(ft["privacy"])}</a></li>'
             + (f'<li><a href="{esc(ctx.href("page:terms"))}">{T(ft["terms"])}</a></li>' if ft.get("terms") else ""))
    wave = '<svg class="sf-wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true"><path d="M0 50 C200 0 420 90 720 46 S1230 4 1440 52 V0 H0 Z"/></svg>'
    return f"""<footer class="site-footer site-footer--yoga">
  {wave}
  <div class="sf-in">
    <div class="sf-lead">
      {brand(ctx, "brand brand--foot")}
      <p class="sf-claim">{T(t['tagline'])}</p>
      <a class="btn btn-primary" href="{esc(ctx.href(t['cta']['href']))}">{T(ft.get('ctaLabel', t['cta']['label']))}</a>
    </div>
    <div class="sf-cols">
      <nav class="sf-col" aria-label="{esc(ft['areasTitle'])}"><h2 class="sf-h">{esc(ft['areasTitle'])}</h2><ul>{areas}</ul></nav>
      <div class="sf-col"><h2 class="sf-h">{T(ft['contactTitle'])}</h2>
        <address class="sf-addr">{esc(cfg["street"])}<br>{esc(cfg["zip"])} {esc(cfg["city"])}<br><a href="tel:{tel}">{esc(cfg["phone"])}</a><br>{mailto}</address></div>
      <div class="sf-col"><h2 class="sf-h">{T(ft.get('socialTitle', ''))}</h2><ul>{legal}</ul></div>
    </div>
    <div class="sf-bottom"><p>{copyright_}</p>{lang_switch(ctx, "lang lang--foot")}</div>
  </div>
</footer>"""


def seo_cfg(site):
    return site.cfg.get("seo", {})


def lang_value(v, lang, default=""):
    """Wert, der je Sprache als {"de": ..., "en": ...} oder direkt angegeben sein kann."""
    if isinstance(v, dict):
        return v.get(lang) or next(iter(v.values()), default)
    return v if v is not None else default


def jsonld_graph(ctx):
    """Strukturierte Daten (schema.org) für Suchmaschinen und KI-Systeme; gesteuert über config.json -> seo."""
    site, page, cfg = ctx.site, ctx.page, ctx.site.cfg
    if page.get("output") or page.get("noindex"):
        return []
    seo, brand_name = seo_cfg(site), cfg.get("brand", {}).get("name", "")
    dom = cfg["domain"]
    org_id, person_id, site_id = f"{dom}/#organization", f"{dom}/#person", f"{dom}/#website"
    url = site.abs_url(ctx.lang, page["id"])
    home_url = site.abs_url(ctx.lang, "home")
    tel = re.sub(r"[^\d+]", "", cfg.get("phone", "").replace("(0)", ""))
    area = [{"@type": "Country", "name": n} for n in lang_value(seo.get("area_served"), ctx.lang, [])]
    graph = []
    if page["id"] == "home":
        org = {
            "@type": seo.get("org_types", ["Organization"]),
            "@id": org_id,
            "name": brand_name,
            "legalName": cfg.get("company", brand_name),
            "url": dom + "/",
            "logo": {"@type": "ImageObject", "url": f"{dom}/{cfg.get('logo_image', 'assets/img/logo.png')}"},
            "image": f"{dom}/assets/img/og-image.png",
            "description": page.get("description", ""),
            "address": {"@type": "PostalAddress", "streetAddress": cfg.get("street", ""), "postalCode": cfg.get("zip", ""), "addressLocality": cfg.get("city", ""), "addressCountry": seo.get("country_code", "DE")},
        }
        if tel:
            org["telephone"] = tel
        if seo.get("founding_year"):
            org["foundingDate"] = str(seo["founding_year"])
        if area:
            org["areaServed"] = area
        if seo.get("knows_about"):
            org["knowsAbout"] = lang_value(seo["knows_about"], ctx.lang, [])
        same = [u for u in seo.get("same_as", []) if u]
        if same:
            org["sameAs"] = same
        graph.append(org)
        person = seo.get("person")
        if person and person.get("name"):
            org["founder"] = {"@id": person_id}
            p = {"@type": "Person", "@id": person_id, "name": person["name"], "worksFor": {"@id": org_id}}
            if person.get("job_title"):
                p["jobTitle"] = lang_value(person["job_title"], ctx.lang)
            if person.get("image"):
                p["image"] = f"{dom}/{person['image']}"
            if person.get("same_as"):
                p["sameAs"] = person["same_as"]
            graph.append(p)
        graph.append({"@type": "WebSite", "@id": site_id, "url": dom + "/", "name": brand_name, "publisher": {"@id": org_id}, "inLanguage": site.langs})
    # Breadcrumb + Seite
    labels = {n["href"].split(":")[1].split("#")[0]: n["label"] for n in ctx.t["nav"]}
    name = labels.get(page["id"]) or page["title"].split(" | ")[0]
    if page["id"] != "home":
        crumbs = [{"@type": "ListItem", "position": 1, "name": brand_name, "item": home_url}]
        parent = page.get("parent")
        if parent and (ctx.lang, parent) in site.pages:
            crumbs.append({"@type": "ListItem", "position": 2, "name": site.pages[(ctx.lang, parent)]["title"].split(" | ")[0], "item": site.abs_url(ctx.lang, parent)})
        crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": name, "item": url})
        graph.append({"@type": "BreadcrumbList", "itemListElement": crumbs})
    ptype = "ContactPage" if page["id"] == "contact" else "WebPage"
    graph.append({"@type": ptype, "@id": url + "#webpage", "url": url, "name": page["title"], "description": page.get("description", ""), "inLanguage": ctx.lang, "isPartOf": {"@id": site_id}})
    if page["id"] in seo.get("service_pages", []):
        svc = {
            "@type": "Service",
            "@id": url + "#service",
            "name": name,
            "serviceType": name,
            "description": page.get("description", ""),
            "url": url,
            "provider": {"@id": org_id},
            "inLanguage": ctx.lang,
        }
        if area:
            svc["areaServed"] = area
        graph.append(svc)
    if page.get("kind") == "post":
        a = article_of(page)
        post = {
            "@type": "BlogPosting",
            "@id": url + "#article",
            "headline": plain(a.get("title", "")),
            "description": page.get("description", ""),
            "datePublished": str(a.get("date", "")),
            "dateModified": str(a.get("updated", a.get("date", ""))),
            "mainEntityOfPage": {"@id": url + "#webpage"},
            "author": {"@type": "Person", "name": a["author"]} if a.get("author") else {"@id": org_id},
            "publisher": {"@id": org_id},
            "inLanguage": ctx.lang,
        }
        if a.get("image"):
            post["image"] = f"{dom}/{a['image']}"
        graph.append(post)
    faq = [x for sec in page["sections"] if sec["type"] == "faq" and sec.get("schema", True) for x in sec["items"]]
    if faq:
        graph.append({
            "@type": "FAQPage",
            "@id": url + "#faq",
            "mainEntity": [
                {"@type": "Question", "name": plain(x["q"]), "acceptedAnswer": {"@type": "Answer", "text": plain(x["a"])}}
                for x in faq
            ],
        })
    return graph


def head_tags(ctx):
    site, page, cfg = ctx.site, ctx.page, ctx.site.cfg
    title = page["title"]
    desc = page.get("description", "")
    out = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        '<meta name="theme-color" content="#ffffff">',
        '<meta name="format-detection" content="telephone=no">',
    ]
    robots = "noindex, nofollow" if (site.noindex or page.get("noindex")) else "index, follow, max-image-preview:large"
    out.append(f'<meta name="robots" content="{robots}">')
    if not page.get("output"):
        canon = site.abs_url(ctx.lang, page["id"])
        out.append(f'<link rel="canonical" href="{esc(canon)}">')
        for l in site.langs:
            if (l, page["id"]) in site.pages:
                out.append(f'<link rel="alternate" hreflang="{l}" href="{esc(site.abs_url(l, page["id"]))}">')
        out.append(f'<link rel="alternate" hreflang="x-default" href="{esc(site.abs_url(site.default, page["id"]))}">')
        img = cfg["domain"] + "/assets/img/og-image.png"
        out += [
            f'<meta property="og:type" content="{"article" if page.get("kind") == "post" else "website"}">',
            f'<meta property="og:site_name" content="{esc(cfg.get("brand", {}).get("name", ""))}">',
            f'<meta property="og:title" content="{esc(title)}">',
            f'<meta property="og:description" content="{esc(desc)}">',
            f'<meta property="og:url" content="{esc(canon)}">',
            f'<meta property="og:locale" content="{esc(ctx.t["locale"])}">',
            f'<meta property="og:image" content="{esc(img)}">',
            f'<meta property="og:image:width" content="1200">',
            f'<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{esc(page.get("ogAlt", cfg.get("brand", {}).get("name", "") + " – " + ctx.t["tagline"]))}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{esc(title)}">',
            f'<meta name="twitter:description" content="{esc(desc)}">',
        ]
    out += [
        f'<link rel="icon" href="{esc(ctx.asset("assets/img/favicon.svg", False))}" type="image/svg+xml">',
        f'<link rel="apple-touch-icon" href="{esc(ctx.asset("assets/img/apple-touch-icon.png", False))}">',
        f'<link rel="stylesheet" href="{esc(ctx.asset("assets/css/style.css"))}">',
        f'<link rel="stylesheet" href="{esc(ctx.asset("assets/css/theme.css"))}">',
        f'<script src="{esc(ctx.asset("assets/js/init.js"))}"></script>',
    ]
    graph = jsonld_graph(ctx)
    if graph:
        out.append('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    return "\n".join(out)


def editor_tags(ctx):
    """Nur im Editor-Build: Werkzeugleiste + Bearbeitungslogik einbinden."""
    if not EDIT:
        return ""
    page = ctx.page
    others = [
        {"lang": l, "url": ctx.page_url(l, page["id"])}
        for l in ctx.site.langs
        if l != ctx.lang and (l, page["id"]) in ctx.site.pages
    ]
    cfg = {
        "token": EDIT_TOKEN,
        "lang": ctx.lang,
        "file": page.get("_file", f"{ctx.lang}/{page['id']}.json"),
        "page": page["id"],
        "others": others,
    }
    data = json.dumps(cfg, ensure_ascii=False).replace("</", "<\\/")
    return (
        '<link rel="stylesheet" href="/__ed/editor.css">\n'
        f"<script>window.__ED__={data};</script>\n"
        '<script src="/__ed/editor.js" defer></script>\n'
    )


def render_page(site, page):
    ctx = Ctx(site, page)
    body = ""
    for i, sec in enumerate(page["sections"]):
        body += RENDERERS[sec["type"]](ctx, sec)
        if i == 0 and page.get("subnav"):
            body += subnav(ctx)
    ui = ctx.t["ui"]
    return f"""<!doctype html>
<html lang="{ctx.lang}"{' data-intro="1"' if ctx.site.cfg.get("intro") else ""}>
<head>
{head_tags(ctx)}
</head>
<body class="page-{esc(page['id'])}{' has-hero' if page['sections'][0]['type'] == 'hero' else ''}{' has-photo' if page['sections'][0].get('image') and page['sections'][0]['type'] == 'hero' else ''}{' has-subnav' if page.get('subnav') else ''}">
{(f'<div class="intro-screen" id="intro" aria-hidden="true">{loader_html(ctx)}</div>' if ctx.site.cfg.get("intro") else "")}
<a class="skip" href="#main">{esc(ui['skip'])}</a>
{header(ctx)}
<main id="main">
{body}</main>
{footer(ctx)}
<button type="button" class="to-top" data-to-top aria-label="{esc(ui['toTop'])}">{icon("up")}</button>
<script src="{esc(ctx.asset('assets/js/main.js'))}" defer></script>
{editor_tags(ctx)}</body>
</html>
"""


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


AI_BOTS = [
    # Suche/Antworten (zitieren Quellen)
    "OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "Claude-User", "PerplexityBot",
    # Training (wer das nicht möchte, entfernt diese Zeilen)
    "GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended",
]


def robots_txt(dom):
    bots = "".join(f"User-agent: {b}\nAllow: /\nDisallow: /api/\n\n" for b in AI_BOTS)
    return (
        "User-agent: *\nAllow: /\nDisallow: /api/\n\n"
        "# KI-Crawler ausdrücklich erlaubt (GEO): Seiten sollen in KI-Antworten zitiert werden\n"
        + bots
        + f"Sitemap: {dom}/sitemap.xml\n"
    )


def llms_txt(site):
    """Kurzbeschreibung der Website für KI-Systeme (llms.txt, Markdown); Texte aus config.json -> seo.llms."""
    cfg, seo = site.cfg, seo_cfg(site)
    llms = seo.get("llms", {})
    order = llms.get("pages", ["home", "contact"])
    out = [f"# {cfg.get('company', cfg.get('brand', {}).get('name', ''))}", ""]
    summary = llms.get("summary")
    if summary:
        out += ["> " + lang_value(summary, site.default), ""]
    for lang in site.langs:
        title = lang_value(llms.get("section_title"), lang, "Pages (" + lang.upper() + ")")
        out += [f"## {title}", ""]
        for pid in order:
            if (lang, pid) in site.pages:
                p = site.pages[(lang, pid)]
                out.append(f"- [{p['title'].split(' | ')[0]}]({site.abs_url(lang, pid)}): {p.get('description', '')}")
        posts = sorted((p for (l, _), p in site.pages.items() if l == lang and p.get("kind") == "post"), key=lambda p: str(article_of(p).get("date", "")), reverse=True)[:10]
        for p in posts:
            out.append(f"- [{plain(article_of(p).get('title', p['title']))}]({site.abs_url(lang, p['id'])}): {p.get('description', '')}")
        out.append("")
    facts = [f"- Firma / company: {cfg.get('company', '')}, {cfg.get('street', '')}, {cfg.get('zip', '')} {cfg.get('city', '')}"]
    if cfg.get("phone"):
        facts.append(f"- Telefon / phone: {cfg['phone']}")
    facts.append(f"- Kontakt / contact: {site.abs_url(site.default, 'contact')}")
    facts += [f"- {x}" for x in llms.get("facts", [])]
    out += ["## Fakten / Facts", ""] + facts + ["", "## Rechtliches / Legal", ""]
    for pid in ("imprint", "privacy"):
        for lang in site.langs:
            if (lang, pid) in site.pages:
                p = site.pages[(lang, pid)]
                out.append(f"- [{p['title'].split(' | ')[0]}]({site.abs_url(lang, pid)})")
    return "\n".join(out) + "\n"


def write_generated(site, out):
    """Kundenspezifische Dateien, die aus config.json erzeugt werden: theme.css, api/config.php, .htaccess-Redirects."""
    cfg = site.cfg
    # Design-Variablen (Farben, Radius, Schrift) überschreiben die Standardwerte in style.css
    theme = cfg.get("theme", {})
    lines = ["/* automatisch aus content/config.json (theme) erzeugt – nicht von Hand ändern */", ":root {"]
    for k, v in theme.items():
        if re.fullmatch(r"[a-z0-9-]+", k) and re.fullmatch(r"[^;{}<>]+", str(v)):
            lines.append(f"  --{k}: {v};")
    lines.append("}")
    (out / "assets" / "css" / "theme.css").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # PHP-Konfiguration für das Formular (Empfänger, Absender, erlaubte Hosts, Themen)
    m = cfg["mail"]
    to = f"{m['user']}@{m['domain']}"
    sender = cfg.get("form_from") or to
    hosts = sorted({urlparse_host(cfg["domain"]), urlparse_host(cfg["domain"]).replace("www.", "", 1)} | ({urlparse_host(cfg["staging_url"])} if cfg.get("staging_url") else set()) | set(cfg.get("extra_hosts", [])))
    topics = {}
    for t in site.text[site.default]["form"]["topics"]:
        topics[t["value"]] = {l: next((x["label"] for x in site.text[l]["form"]["topics"] if x["value"] == t["value"]), t["label"]) for l in site.langs}
    php = "<?php\n// automatisch aus content/config.json erzeugt – nicht von Hand ändern\n"
    php += f"const CONTACT_TO = {php_str(to)};\nconst CONTACT_FROM = {php_str(sender)};\n"
    php += f"const SITE_NAME = {php_str(cfg.get('brand', {}).get('name', ''))};\n"
    php += "const ALLOWED_HOSTS = array(" + ", ".join(php_str(h) for h in hosts) + ");\n"
    php += f"const DEFAULT_LANG = {php_str(site.default)};\n"
    php += "const MSG = array(\n"
    for l in site.langs:
        f = site.text[l]["form"]
        php += f"    {php_str(l)} => array('ok' => {php_str(f['ok'])}, 'invalid' => {php_str(f['invalid'])}, 'slow' => {php_str(f.get('slow', f['err']))}, 'fail' => {php_str(f['err'])}, 'back' => {php_str(f.get('back', ''))}),\n"
    php += ");\n"
    php += "const TOPICS = array(\n"
    for k, labels in topics.items():
        php += f"    {php_str(k)} => array(" + ", ".join(f"{php_str(l)} => {php_str(v)}" for l, v in labels.items()) + "),\n"
    php += ");\n"
    (out / "api" / "config.php").write_text(php, encoding="utf-8")

    # .htaccess: Hauptdomain mit/ohne www + Weiterleitungen alter URLs
    ht = (out / ".htaccess").read_text(encoding="utf-8")
    host = urlparse_host(cfg["domain"])
    gen = ""
    if host.startswith("www."):
        bare = host[4:]
        gen += f"RewriteCond %{{HTTP_HOST}} ^{re.escape(bare)}$ [NC]\nRewriteRule ^ {cfg['domain']}%{{REQUEST_URI}} [L,R=301,NE]\n"
    for r in cfg.get("redirects", []):
        gen += f"RewriteRule {r['from']} {r['to']} [L,R=301,NE]\n"
    (out / ".htaccess").write_text(ht.replace("# {{GENERATED_REDIRECTS}}", gen.rstrip("\n")), encoding="utf-8")


def urlparse_host(u):
    return re.sub(r"^https?://", "", u).split("/")[0].lower()


def php_str(v):
    return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'") + "'"


def build(preview=False, noindex=False, check=True, edit=False):
    global EDIT
    EDIT = edit
    if edit:
        noindex = True
    if check:
        from check import run_checks

        errors, _ = run_checks(production=not (noindex or preview))
        if errors:
            raise SystemExit("Build abgebrochen: bitte die obigen Fehler beheben (oder mit --no-check überspringen).")
    site = Site(preview, noindex)
    out = ROOT / ("edit" if edit else "preview" if preview else "dist")
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(STATIC, out)
    if edit:
        shutil.copytree(ROOT / "editor" / "assets", out / "__ed")

    for (lang, pid), page in sorted(site.pages.items()):
        if page.get("output"):
            target = out / page["output"]
        else:
            target = out.joinpath(*site.parts(lang, pid)) / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_page(site, page), encoding="utf-8")

    write_generated(site, out)

    # sitemap + robots
    dom = site.cfg["domain"]
    urls = ""
    for (lang, pid), page in sorted(site.pages.items()):
        if page.get("output") or page.get("noindex"):
            continue
        alts = "".join(
            f'<xhtml:link rel="alternate" hreflang="{l}" href="{esc(site.abs_url(l, pid))}"/>'
            for l in site.langs
            if (l, pid) in site.pages
        )
        art = article_of(page)
        lastmod = str(art.get("updated", art.get("date", site.today.isoformat()))) if page.get("kind") == "post" else site.today.isoformat()
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{esc(site.abs_url(site.default, pid))}"/>'
        urls += f"<url><loc>{esc(site.abs_url(lang, pid))}</loc><lastmod>{esc(lastmod)}</lastmod>{alts}</url>\n"
    if not site.noindex:
        (out / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n",
            encoding="utf-8",
        )
        (out / "robots.txt").write_text(robots_txt(dom), encoding="utf-8")
        (out / "llms.txt").write_text(llms_txt(site), encoding="utf-8")
    else:
        (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")

    print(f"OK: {len(site.pages)} Seiten -> {out.relative_to(ROOT)}/  (Version {site.version}{', noindex' if site.noindex else ''})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Website bauen")
    ap.add_argument("--preview", action="store_true", help="lokale Vorschau mit relativen Links")
    ap.add_argument("--noindex", action="store_true", help="Staging: Suchmaschinen aussperren")
    ap.add_argument("--edit", action="store_true", help="Editor-Build -> edit/ (wird von editor.py benutzt)")
    ap.add_argument("--no-check", action="store_true", help="Inhaltsprüfung (check.py, Glossar) überspringen")
    a = ap.parse_args()
    build(a.preview, a.noindex, not a.no_check, a.edit)
