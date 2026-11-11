---
name: kundenwebsite-mit-claude-code
description: Geführter Aufbau einer Kundenwebsite mit Claude Code auf Basis des Website-Templates (statisch, mehrsprachig, Live-Editor, Staging/Produktion, SEO/GEO, globaler Header/Footer). Nutzen, wenn eine neue Website, ein Relaunch oder ein Nachbau einer bestehenden Website gebaut, das Projekt eingerichtet (GitHub, Mac, Hosting/FTP, Subdomain, Deployment) oder abgesichert und übergeben werden soll. Führt Schritt für Schritt und in Rückfragen durch alle Einrichtungsschritte.
---

# Kundenwebsite mit Claude Code (wie ein OnePage.io, nur ohne Verwaltungs-Frontend)

Das Template (`website-template`, Repo in der GitHub-Organisation) liefert: Seitengenerator, Live-Editor, globale Bereiche (Header/Menü/Footer), Mehrsprachigkeit, Staging + Produktion, SEO/GEO-Ausgaben, Sicherheitshärtung. Dieser Skill führt durch alles, was darum herum nötig ist. Referenzprojekt mit allen Erkenntnissen: `24bit-bsd/website`.

## Wie du führst (gilt für jeden Schritt)
- **Ein Schritt nach dem anderen.** Sage in 1–2 Sätzen, was jetzt passiert und warum; gib die konkrete Aktion (Klickpfad oder Befehl); warte auf „fertig“/Rückmeldung, bevor du weitergehst. Keine Wand aus 15 Schritten.
- **Erst nachsehen, dann fragen.** Prüfe Zustand selbst (`git remote -v`, `ls`, `python3 build.py`, `curl -I`), statt den Menschen raten zu lassen. Tue alles, was du selbst kannst (Dateien, Git, Build), und sage nur die Dinge an, die nur die Person tun kann (Konten, Klicks in GitHub/Hoster, Passwörter).
- **Zugangsdaten nie im Chat.** Passwörter, SFTP-Zugänge und Schlüssel gibst du nie aus und lässt sie dir nicht schicken. Sie werden direkt in GitHub (Environment-Secrets) oder im Hoster-Panel eingetragen. Hilfe dabei: Klickpfade nennen, Eingabefelder erklären.
- **Fortschritt festhalten.** Pflege `docs/SETUP.md` im Projekt (Checkliste, abgehakt). Beim Start einer Sitzung zuerst dort nachlesen, damit die Einrichtung über mehrere Sitzungen weitergeht.
- **Erklären in einfacher Sprache**, Fachbegriffe beim ersten Mal kurz erläutern (Repository, Branch, Staging, Secret …). Frage zu Beginn nach dem Vorwissen (Technik-affin oder nicht) und passe die Tiefe an.
- Nicht committen, pushen, taggen oder live setzen ohne ausdrückliche Aufforderung. Produktion ist immer ein eigener, bestätigter Schritt.

## Schritt 0: Die Weiche (zuerst klären, mit AskUserQuestion)
1. **Neuaufbau** mit geführtem Briefing (neue Positionierung/Texte, evtl. neues Design) → weiter mit `references/briefing.md`.
2. **Nachbau einer bestehenden Website** (URL + wichtigste Assets: Logo, Farben/CI, Schriften, Bilder) → weiter mit `references/nachbau.md`.
3. Zusätzlich klären: Projektname/Kunde, Sprachen, Hosting vorhanden (welcher Anbieter?), Domain, wer pflegt später Inhalte, gibt es schon ein GitHub-Konto?

## Phasen (jede Phase endet mit Abhaken in `docs/SETUP.md`)
**A. Einrichtung** (`references/einrichtung.md`): GitHub-Konto + Zwei-Faktor → Repo aus Template erzeugen → auf den Mac klonen → lokal bauen/testen → Deploy-Key für Git-Push → Projekt-`CLAUDE.md` ausfüllen.
**B. Inhalt**: Briefing (Neuaufbau) oder Nachbau-Analyse → Seitenstruktur freigeben lassen → Inhalte in `content/` (alle Sprachen).
**C. Design/CI**: **Design-Inspirationen erfragen** (2–3 Vorbilder, was gefällt, No-Gos), auswerten, zwei Richtungen als Prototyp zeigen und freigeben lassen. Dann Farben, Logo, Schriften über `theme` in `content/config.json`, CSS und Layout **maßgeblich** anpassen: Jede Website muss anders aussehen (mindestens 5 von 8 Gestaltungsdimensionen). Ohne `design.status: "individuell"` bricht der Produktions-Build ab. Feinschliff im Browser (Desktop 1440, mobil 390). Details `references/design.md`.
**D. Funktionen prüfen** (`references/features.md`): Live-Editor, globale Bereiche (Header/Menü/Footer), Mehrsprachigkeit, Formular, SEO/GEO. Jede gewünschte Funktion ist im Template vorhanden; hier nur konfigurieren und testen.
**E. Hosting + Deployment** (`references/hosting-deployment.md`): FTP/SFTP-Zugang klären und testen → Staging-Subdomain anlegen → GitHub-Environments `staging` und `production` mit Secrets/Variablen → erster Staging-Deploy → Domain/SSL.
**F. Qualität + Sicherheit** (`references/qualitaet-seo.md`, `references/sicherheit.md`): vollständig durchgehen, Formular auf Staging real testen, Rechtstexte durch Kunden/Juristen prüfen lassen.
**G. Live-Gang**: Tag `live-…` oder Workflow „production“ nach ausdrücklicher Bestätigung; danach Nachkontrolle (Header, Formular, Sitemap, Search Console).
**H. Übergabe** (`references/uebergabe.md`): Zugriff für Kunden, Onboarding-Anleitung, Zuständigkeiten, Pflegeprozess.

## Immer mit abgebildet (Anforderungen an jedes Projekt)
Frontend-Editor (`python3 editor.py`) · Environments Produktion und Staging auf eigener Subdomain · Optimierung für SEO und GEO · Mehrsprachigkeit (beliebig viele Sprachen) · globale Abschnitte für Header/Menü und Footer · Sicherheitshärtung. Wenn der Kunde etwas davon nicht braucht, bewusst abwählen und in `CLAUDE.md` vermerken.

## Arbeitsregeln
- Empfehlen statt nur aufzählen; bei „Wie könnte das aussehen?“ einen Prototyp bauen und beurteilen.
- Nach jeder sichtbaren Änderung selbst prüfen: Build, Konsole, Screenshot Desktop/mobil, Überlauf.
- Alle Sprachen und Struktur parallel pflegen (`check.py` bricht bei Abweichungen ab).
- Kundentexte, Preise, Zahlen und Lebensläufe nie erfinden; Platzhalter klar markieren.
- Urheberrecht: Bilder/Texte/Schriften nur übernehmen, wenn der Kunde die Rechte hat; im Zweifel nachfragen.
- Bleibendes Wissen in die Projekt-`CLAUDE.md`/README, nicht im Chat lassen. Pro Thema eine neue Sitzung.
- Der Live-Editor committet Inhalte auf `main`; vor jedem Push `git pull --rebase`.

## Weitere Dateien
`references/einrichtung.md` · `references/briefing.md` · `references/nachbau.md` · `references/features.md` · `references/hosting-deployment.md` · `references/uebergabe.md` · `references/architektur.md` · `references/design.md` · `references/qualitaet-seo.md` · `references/sicherheit.md` · `references/stolpersteine.md`
