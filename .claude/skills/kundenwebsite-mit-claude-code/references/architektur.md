# Architektur des Templates

**Stack:** Python-3-Generator ohne Abhängigkeiten, statische Ausgabe, Apache + PHP-Formular (Shared Hosting). Keine Frameworks, keine Build-Tools außer Python. Gründe: nichts zu patchen, nichts, was ausfällt, jede Person kann es lokal bauen.

## Ordner
- `content/config.json` Marke, Firma, Domain, `staging_url`, Sprachen, Kontakt, Mail, Logo, `theme` (Design-Variablen), `seo` (strukturierte Daten, llms.txt), `redirects`, `intro` (Ladeanimation an/aus), `team_profiles`
- `content/<lang>/*.json` eine Datei je Seite; `site.json` = Navigation, UI-Texte, Footer, Formulartexte
- `content/glossary.json` Sprachregeln (verbotene Schreibweisen, Menü-Schreibweise, Begriffspaare)
- `build.py` Renderer je Sektionstyp (`RENDERERS`), JSON-LD, Sitemap/robots/llms.txt, `theme.css`, `api/config.php`, `.htaccess`-Weiterleitungen, Editor-Build (`--edit`)
- `check.py` Inhaltsprüfung (Struktur aller Sprachen, Glossar, Menü-Schreibweise, Link-Sicherheit); bricht den Build ab
- `editor.py` + `editor/assets/` lokaler Live-Editor (127.0.0.1, Token, Host-Prüfung)
- `static/` wird 1:1 nach `dist/`: `assets/css/style.css` (neutrale Basis), `assets/js/` (`init.js`, `main.js`), `assets/img/`, `api/*.php`, `.htaccess`
- `.github/workflows/deploy.yml` Prüfen → Bauen → Hochladen → Auslieferung prüfen; `.github/dependabot.yml`
- `docs/` Onboarding und `SETUP.md` (Checkliste), `design/og-image.html` (Share-Bild-Vorlage)
- `.claude/skills/kundenwebsite-mit-claude-code/` dieser Skill

## Sektionstypen (Seite = Liste von `sections` mit `type`)
hero (Wechselwörter `rotator`, Buttons, optional `sub` für zweizeilige Buttons), rings, grid (Varianten `cards`, `numbered`, `services`), logos, about (Text + Team-Kacheln + Profil-Fenster), text (Absätze, Liste, Fazit-Kasten `after`), features, chips, projects, toolgroups, offers, cases (Referenz-Cases als Slider), process (Prozess-Schritte), pricing (Pläne mit Empfohlen-Badge), news (Beitragsliste), article (Beitragsseite), faq (Fragen `items[].q`/`a`, aufklappbar ohne JavaScript; erzeugt automatisch FAQPage-Daten, abschaltbar mit `"schema": false`), cta, contact, legal, notfound. Pflichtangaben siehe Beispiele in `content/de/*.json`.
**Neue Sektion** = Renderer in `build.py` (`r_<name>` + Eintrag in `RENDERERS`) + CSS + Beispiel in allen Sprachen. Texte immer mit `T()`/`rich()` ausgeben (escaped und im Editor editierbar), Links mit `ctx.link_attrs()`/`safe_url()`.

### Neue Bausteine im Detail
- **cases** (Slider): `items[]` mit `client`, `title`, `text`, `results[]` (`value`, `label`), `image` (optional, sonst neutrale Platzhalterfläche), `cta` (Link). Scroll-Snap, ohne JavaScript scrollbar; Pfeile per `main.js`. UI-Texte `ui.slider.{label,prev,next}`.
- **process**: `items[]` mit `title`, `text`, `meta` (z. B. „Woche 1“); `variant`: `steps` (nebeneinander) oder `timeline` (untereinander); optional `buttons`.
- **pricing**: `items[]` mit `name`, `subtitle`, `from`, `price`, `period`, `note`, `features[]`, `cta`, `featured` (true = hervorgehoben mit Badge, Text aus `badge` oder `ui.recommended`); optional `footnote`. Keine erfundenen Preise: Platzhalter (`000 €`) lassen, bis der Kunde freigibt.
- **news / Blog**: Beiträge liegen je Sprache unter `content/<lang>/posts/<id>.json` (ID global eindeutig, `slug` z. B. `blog/mein-beitrag`, `parent: "blog"` für die Brotkrumen). Der Beitrag besteht aus einer `article`-Sektion (`title`, `teaser`, `category`, `author`, `date` (ISO), optional `updated`, `image`, `body[]`, `back`) plus beliebigen weiteren Sektionen (z. B. `cta`). `body` kennt Absätze (Text), `{"h": …}`, `{"list": […]}`, `{"quote": …, "by": …}`. Die Sektion `news` (z. B. auf der Startseite mit `limit: 3` oder auf `blog.json` ohne Limit; `category` filtert, `variant`: `cards` | `list`, `cta` verlinkt auf alle Beiträge) zieht die neuesten Beiträge der Sprache automatisch. Beiträge dürfen in einzelnen Sprachen fehlen (Hinweis statt Fehler). Sitemap, hreflang, `llms.txt` und JSON-LD (`BlogPosting`) entstehen automatisch. UI-Texte: `ui.months`, `ui.dateFormat` (`{D}` Tag, `{d}` Tag zweistellig, `{m}` Monat zweistellig, `{M}` Monatsname, `{Y}` Jahr), `ui.readMore`, `ui.noPosts`.
- **Nach-oben-Button**: auf allen Seiten, rund und neutral, Akzentfarbe nur beim Hover; erscheint nach etwa einer Bildschirmhöhe (mindestens 400 px). Text `ui.toTop`. Aussehen in `style.css` (`.to-top`).
- **Design-Check**: Block `design` in `content/config.json` (`status`, `concept`, `inspirations`, `dimensions`, `signature`), geprüft in `check.py`; Fingerabdruck der Vorlage in `design/template-basis.json` (nur im Template-Repo mit `python3 check.py --design-baseline` erneuern). Siehe `design.md`.

## Textauszeichnung (`rich()`)
`**fett**`, `[[Wort]]` Hervorhebung (Marker), `{{Wort}}` Farbverlauf, `\n` Zeilenumbruch, `{year}`. Links in Inhalten: `page:<id>[?query][#anchor]`.

## Was aus der config erzeugt wird (nicht von Hand ändern)
`assets/css/theme.css` (aus `theme`), `api/config.php` (Empfänger, Absender, Themen, erlaubte Hosts, Meldungen), Weiterleitungen und Domain-Regel in `.htaccess` (aus `domain`, `redirects`), `sitemap.xml`, `robots.txt`, `llms.txt` (nur Produktionsbuild).

## Befehle
`python3 build.py` (Produktion), `--noindex` (Staging), `--preview` (relative Links, Formular aus), `--no-check`, `python3 check.py`, `python3 editor.py`. Lokal ohne PHP: einfacher Python-HTTP-Server auf `dist/` (Formular nur auf Staging testbar).

## Feature-Schalter
`intro` (Ladeanimation), `team_profiles` (`staging`|`on`|`off`). Neue Schalter in `content/config.json`, Auswertung im Renderer.
