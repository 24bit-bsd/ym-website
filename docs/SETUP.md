# Einrichtung und Projektstand

Checkliste für dieses Kundenprojekt. Claude liest sie zu Beginn jeder Sitzung und hakt ab (Skill `kundenwebsite-mit-claude-code`). Passwörter und Schlüssel gehören **nie** in diese Datei.

**Kunde:** Yoga Momente (Susanne Müller) / Momente Macher GbR  **Domain:** www.momente.yoga  **Staging:** website.momente.yoga  **Hoster:** IONOS  **Verantwortlich für Live-Gänge:** …

## 0. Weiche
- [x] Nachbau einer bestehenden Seite (`docs/NACHBAU.md`)
- [x] Sprachen: de, en  Standardsprache: de

## A. Einrichtung
- [ ] Mac vorbereitet (Git, Python 3, Chrome), Arbeitsordner außerhalb von Synology/iCloud/Dropbox
- [ ] GitHub-Konto mit Zwei-Faktor
- [ ] Repo aus Template erzeugt (privat) und auf den Mac geklont
- [x] Lokaler Arbeitsordner `~/Websites/ym-website` (aus Template, frisches `git init`, noch kein GitHub-Repo, kein Commit)
- [ ] `python3 build.py --preview` läuft ohne Fehler
- [ ] Deploy-Key angelegt (`~/.ssh/id_ed25519_ym_website`, lokal gebunden), auf GitHub eingetragen, `git push` ohne Passwort möglich
- [ ] `CLAUDE.md` und `content/config.json` (Marke, Domain, Staging-URL, Kontakt, Sprachen) ausgefüllt

## B. Inhalt
- [ ] Sitemap/Seitenstruktur freigegeben
- [ ] Texte in allen Sprachen (keine Platzhalter mehr: `grep -rn "Muster\|example.com\|Platzhalter\|20XX" content static`)
- [ ] Impressum und Datenschutz an den Kunden angepasst und rechtlich geprüft

## C. Design
- [x] `design.status` in `content/config.json` auf `offen` gesetzt (Produktions-Build gesperrt bis zur Design-Phase)
- [ ] Design-Inspirationen eingeholt (2–3 Vorbilder, No-Gos, Adjektive) und ausgewertet
- [ ] Designkonzept freigegeben (zwei Richtungen gezeigt)
- [ ] Mindestens 5 von 8 Gestaltungsdimensionen individuell angepasst; `design`-Block ausgefüllt, `status: individuell`
- [ ] Theme-Tokens, Schrift (lokal), Logo, Favicon, Share-Bild (1200×630)
- [ ] Layout individuell umgesetzt; Mobil (390) und Desktop (1440) geprüft

## D. Funktionen
- [ ] Live-Editor getestet (Text ändern, veröffentlichen)
- [ ] Header/Menü/Footer, Mehrsprachigkeit, Sprach-Dropdown geprüft
- [ ] SEO/GEO: Titel/Beschreibung je Seite, `seo`-Block in der config, Sitemap/robots/llms.txt im Produktions-Build

## E. Hosting und Deployment
- [ ] FTP/SFTP-Zugang vom Hoster, Verbindung mit Client getestet, Remote-Pfade notiert
- [ ] Staging-Subdomain angelegt (Zielordner, SSL)
- [ ] GitHub-Environments `staging` und `production`: Secrets (`DEPLOY_HOST/USER/PASSWORD/PORT`) und Variablen (`DEPLOY_REMOTE_DIR`, `DEPLOY_PROTOCOL`)
- [ ] Erster Staging-Deploy grün, Seite auf der Subdomain geprüft
- [ ] Formular-Test auf Staging (Mail kommt an)

## F. Qualität und Sicherheit
- [ ] Prüfliste in `sicherheit.md` und `qualitaet-seo.md` abgearbeitet (2FA, CSP/HSTS getestet, Actions gepinnt)
- [ ] Kunde hat Staging abgenommen

## G. Live-Gang
- [ ] Produktion eingerichtet, Tag `live-…` gesetzt (nur nach ausdrücklicher Bestätigung)
- [ ] Domain umgelegt, SSL aktiv, Weiterleitungen alter URLs geprüft
- [ ] Nachkontrolle: Header, Formular, Sitemap, Search Console/Bing

## H. Übergabe
- [ ] Zugriff/Eigentum geklärt, Onboarding-PDF übergeben, Schulung erledigt, Verantwortliche benannt
