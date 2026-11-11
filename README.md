# Website-Template

Statischer Website-Generator (Python 3, keine Abhängigkeiten) für mehrsprachige Unternehmenswebsites mit Live-Editor, Staging/Produktion, SEO/GEO und Sicherheitshärtung. Gedacht als Startpunkt für **Kundenprojekte, die mit Claude Code gebaut werden**: Struktur und Technik sind fertig, Design, Layout und Inhalte entstehen je Kunde neu.

## Neues Kundenprojekt starten
1. Auf GitHub: **„Use this template“** → neues privates Repo `<kunde>-website`.
2. Auf den Mac klonen (`~/Websites/<kunde>-website`), Ordner in der Claude-App (Tab „Code“) öffnen.
3. Claude bitten: **„Richte die Website nach dem Skill kundenwebsite-mit-claude-code ein.“** Der Skill führt Schritt für Schritt (Konten, GitHub, FTP/Hosting, Subdomain, Briefing oder Nachbau, Design, Deployment, Übergabe).

## Befehle
```bash
python3 build.py            # Produktion nach dist/
python3 build.py --noindex  # Staging
python3 build.py --preview  # lokale Vorschau
python3 check.py            # Inhaltsprüfung
python3 editor.py           # Live-Editor (http://127.0.0.1:8777)
```

## Was enthalten ist
Seitenbausteine (Hero, Text, Karten, Features, Angebote, FAQ, Referenz-Cases als Slider, Prozess-Schritte, Preise/Pläne, Blog/News, Team, Logos, CTA, Kontakt, Rechtliches, 404) · Nach-oben-Button · globale Bereiche Header/Menü/Footer · beliebig viele Sprachen mit hreflang · Live-Editor · Staging (Subdomain, noindex) und Produktion (GitHub Actions, FTP/SFTP/FTPS) · SEO/GEO (Sitemap, robots, llms.txt, JSON-LD, Open-Graph) · Kontaktformular mit Spam-Schutz · Sicherheit (CSP, HSTS, Link-Prüfung, gepinnte Actions) · neutrale Basis-Gestaltung über Design-Variablen (`theme` in `content/config.json`) · **Design-Check**: Jede Kundenwebsite muss individuell gestaltet werden, sonst bricht der Produktions-Build ab (`design`-Block in `content/config.json`).

## Ordner
`content/` Texte und Einstellungen · `static/` CSS, JS, Bilder, PHP, `.htaccess` · `build.py`, `check.py`, `editor.py` · `.github/workflows/deploy.yml` · `docs/` Checkliste und Onboarding · `.claude/skills/` der Skill für Claude Code. Details im Skill (`references/architektur.md`).

## Template pflegen (Regeln und Testliste: `docs/TEMPLATE-WARTUNG.md`)
Verbesserungen aus Kundenprojekten (neue Bausteine, Sicherheitsregeln, Skill-Erkenntnisse) hier einpflegen. Kunden-Repos übernehmen sie bei Bedarf selektiv (Dateien vergleichen und kopieren).
