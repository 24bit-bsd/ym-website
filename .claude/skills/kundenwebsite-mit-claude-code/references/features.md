# Die immer enthaltenen Funktionen (Phase D)

Jedes Kundenprojekt bringt diese Funktionen mit. Hier: wo sie konfiguriert werden und wie man sie testet.

## 1. Frontend-Editor (Texte direkt auf der Seite ändern)
- Start: `python3 editor.py` (oder Doppelklick auf `Editor starten.command`); läuft nur lokal auf `http://127.0.0.1:8777`.
- Text anklicken, ändern, speichern (⌘↵); die andere Sprache steht daneben. „Veröffentlichen“ prüft (`check.py`), committet **nur `content/`** und pusht auf `main` (löst Staging aus).
- Nur Texte, die mit `T()`/`rich()` ausgegeben werden, sind editierbar. Neue Renderer immer so schreiben.
- Hinweis: Der Editor committet selbst; vor eigenen Pushes `git pull --rebase`. Bei mehreren Personen gleichzeitig kann der Push abbrechen: nicht erzwingen.
- Schulung des Kunden: 10 Minuten Demo, Anleitung `docs/onboarding.html`.

## 2. Environments: Produktion und Staging/Test
- Zwei getrennte Ziele über GitHub-Environments `staging` und `production` (Secrets/Variablen je Umgebung). Staging liegt auf einer **eigenen Subdomain** (`staging_url` in der config), ist `noindex` und `robots.txt` Disallow.
- Auslöser: Push auf `main` → Staging; Tag `live-…` oder manueller Lauf → Produktion. Details `hosting-deployment.md`.
- Feature-Schalter, die nur auf Staging sichtbar sein sollen (z. B. `team_profiles`: `staging`|`on`|`off`).

## 3. SEO und GEO
Je Seite `title`/`description`; Sitemap (hreflang), `robots.txt` (inkl. KI-Crawler-Regeln), `llms.txt`, JSON-LD (Organization, WebSite, WebPage, Service, Breadcrumb), Open-Graph, kanonische URLs. Gesteuert über `content/config.json` → `seo` (Organisationstyp, Land, Gründungsjahr, Einzugsgebiet, Themen, `same_as`, Person, `service_pages`, `llms`). Checkliste `qualitaet-seo.md`. Share-Bild `static/assets/img/og-image.png` (1200×630) je Kunde neu erzeugen (`design/og-image.html` + Chrome headless).

## 4. Mehrsprachigkeit
- Sprachen in `content/config.json`: `languages`, `default_language`, `language_names`. Standardsprache liegt im Root, weitere unter `/<sprache>/`.
- Je Sprache ein Ordner `content/<lang>/` mit denselben Dateien (Seiten + `site.json`); `check.py` prüft, dass Struktur und Listenlängen übereinstimmen. Slugs je Sprache lokalisiert (`slug`).
- **Neue Sprache hinzufügen:** Ordner `content/<lang>/` aus einer vorhandenen Sprache kopieren, `locale` in `site.json` anpassen, Texte übersetzen, Slugs anpassen, Sprache in der config eintragen, `python3 build.py`. hreflang, Sitemap, Sprach-Dropdown und Formular-Texte ergeben sich automatisch. Für das Sprach-Dropdown gibt es Flaggen für de, en, fr, it, es, nl, pl, pt; weitere in `FLAGS` in `build.py`.
- Sprachregeln (verbotene Schreibweisen, Menü-Schreibweise, Begriffspaare) in `content/glossary.json`.

## 5. Globale Abschnitte: Header/Menü und Footer
- Alles in `content/<lang>/site.json`: `nav` (Hauptmenü, optional `mega` mit Spalten), `cta` (Header-Button), `ui` (Beschriftungen), `footer` (Bereiche, Rechtliches, Copyright), `form` (Formular-Texte, Themen), `tagline`. Einmal pflegen, wirkt auf allen Seiten.
- Sekundärmenü pro Seite: `subnav` in der Seiten-JSON (Anker-Links).
- Logo und Marke: `logo_image`, `brand.name`; Kontaktdaten, Social-Links in der config (erscheinen im Footer/Kontaktseite).
- Design des Headers/Footers (Layout, Mega-Menü, Mobile-Menü) im CSS je Kunde anpassen (`design.md`).

## 6. Kontaktformular
`api/contact.php` + `api/token.php` (Spam-Schutz, Rate-Limit), Empfänger/Absender/Themen aus der config (`mail`, `form_from`, `form.topics`). Auf Staging real testen. Details `sicherheit.md`.

## Abnahme dieser Phase
Editor startet und speichert; Staging-Deploy läuft; alle Sprachen bauen fehlerfrei; Menü/Footer korrekt; Formular-Mail kommt an; Sitemap/`robots.txt`/`llms.txt` im Produktions-Build vorhanden.
