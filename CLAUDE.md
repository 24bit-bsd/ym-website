# <Kunde> – Website-Projekt

> **Wenn dieses Repo `website-template` selbst ist** (nicht ein Kundenprojekt): zuerst `docs/TEMPLATE-WARTUNG.md` lesen. Dort stehen die Regeln und die Testliste für Änderungen am Template.

> Vorlage: Beim Einrichten ausfüllen (Skill `kundenwebsite-mit-claude-code`, Datei `docs/SETUP.md`). Platzhalter in `<…>` ersetzen.

Statischer Site-Generator (Python 3, keine Abhängigkeiten) für `<domain>`. Sprachen: `<…>`. Hosting: `<Hoster>` (Apache + PHP). Repo: `<org>/<kunde>-website` (privat).

## Befehle
- `python3 build.py` → dist/ (Produktion, indexierbar, sitemap/robots/llms.txt); `--noindex` Staging; `--preview` lokale Vorschau; `python3 check.py` Prüfung (läuft bei jedem Build)
- `python3 editor.py` → Live-Editor (127.0.0.1:8777): Texte anklicken und ändern, „Veröffentlichen“ = Prüfung + Commit nur `content/` + Push. Neue Textausgaben im Renderer mit `T(...)`/`rich(...)`.
- Deployment: Push auf `main` → GitHub Action baut mit `--noindex` und lädt auf **Staging** (`<staging-url>`). Produktion nur manuell: Tag `live-…` pushen oder Actions → Run workflow → `production`. Zugangsdaten als Environment-Secrets (`DEPLOY_*`), Zielordner/Protokoll als Environment-Variablen. Ohne bezahlten GitHub-Plan keine technische Freigabe: ein Tag geht sofort live; nur `<Verantwortliche Person>` startet Produktion, Claude nur auf ausdrückliche Anweisung.

## Struktur
- `content/config.json` Marke, Domain, Staging-URL, Kontakt, Sprachen, `theme` (Design-Variablen), `seo`, `redirects`
- `content/<lang>/*.json` eine Datei je Seite, `site.json` = Navigation, UI, Footer, Formular; `content/glossary.json` Sprachregeln
- Sektionstypen und Renderer: siehe Skill `references/architektur.md`; `static/` wird 1:1 nach dist/ kopiert

## Regeln
- Design ist individuell für diesen Kunden (Tokens in `theme`, Layout/CSS anpassen); Designkonzept: `<kurz beschreiben>`. Pflicht: Block `design` in `content/config.json` (Status `offen` → `individuell`, mind. 5 von 8 Dimensionen angepasst); ohne ihn bricht der Produktions-Build ab (Skill `references/design.md`)
- Alle Sprachen parallel pflegen; Slugs je Sprache lokalisiert; Sprachregeln im Glossar
- Link-Felder nur `page:`, `https://`, `http://`, `mailto:`, `tel:`, `#`, `/`; keine Inline-Skripte (CSP); Formular braucht JavaScript (signierter Zeitstempel)
- Keine Fremdskripte/-schriften ohne bewusste CSP- und Datenschutz-Entscheidung
- `dist/`, `preview/`, `edit/` sind generiert, nicht von Hand editieren
- Nach Änderungen: bauen, mobil (390) und Desktop (1440) auf Überlauf prüfen; nicht committen/pushen/taggen ohne Aufforderung

## Offen
`<Liste aus docs/SETUP.md>`
