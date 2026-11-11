# Template pflegen (nur relevant, wenn dieses Repo `website-template` selbst ist)

Dieses Repo ist die Vorlage für alle Kundenwebsites. Änderungen hier wirken auf **alle künftigen** Projekte. Deshalb gelten andere Regeln als in einem Kundenprojekt. In Kunden-Repos ist diese Datei unwichtig und kann gelöscht werden.

## Sitzungen trennen
- **Template-Werkstatt** (diese Sitzung, Ordner `~/Websites/website-template`): Generator, Bausteine, Sicherheit, Skill, Anleitungen.
- **Kundenprojekte** je eigener Ordner/Sitzung; **24bit-Website** (`~/Websites/24bit-website`) ist das Referenzprojekt, nicht Teil des Templates.
- Wissen aus Projekten kommt gebündelt hierher: Erkenntnisse werden **im Chat dieser Template-Werkstatt** gesammelt und in Auftrag gegeben („Erkenntnis: …“). Sie werden hier abgearbeitet und in Code, Beispielinhalte, Skill und diese Datei übertragen. Eine Arbeit auf GitHub (Issues) ist dafür nicht nötig.

## Regeln für Änderungen
1. **Kein Kundenbezug im Template:** keine Namen, Domains, Adressen, Fotos, Texte, Preise, Zugangsdaten von 24bit oder Kunden. Beispiele sind „Muster GmbH“, `example.com`, Platzhalter-Bilder.
2. **Design bleibt neutral:** `style.css` ist eine schlichte Basis. Gestalterische Besonderheiten eines Kunden gehören ins Kundenprojekt, höchstens als Beispiel in `references/design.md`. Nach jeder Änderung an `style.css` oder `theme`: `python3 check.py --design-baseline` ausführen und `design/template-basis.json` mitcommitten (sonst meldet `check.py` im Template einen Fehler).
3. **Alles konfigurierbar statt hartcodiert:** Marke, Texte, Hosts, Mail, SEO-Daten kommen aus `content/config.json` bzw. `content/<lang>/site.json`. Neue Einstellungen dort dokumentieren (`references/architektur.md`).
4. **Mehrsprachig denken:** Keine Annahmen über „de“ und „en“ im Code; neue Texte in allen Beispielsprachen.
5. **Sicherheit zuerst:** Neue Link-Ausgaben mit `safe_url()`, keine Inline-Skripte (CSP), Texte über `T()`/`rich()`. Keine Fremdressourcen.
6. **Skill und Template zusammen pflegen:** Ändert sich ein Ablauf oder eine Datei, die Anleitungen unter `.claude/skills/kundenwebsite-mit-claude-code/` im selben Commit anpassen. Danach den Skill nach `~/.claude/skills/` kopieren: `rm -rf ~/.claude/skills/kundenwebsite-mit-claude-code && cp -R .claude/skills/kundenwebsite-mit-claude-code ~/.claude/skills/`.
7. **Nicht committen/pushen ohne Aufforderung**; Commits ohne Kundendaten, mit aussagekräftiger Nachricht.

## Testliste vor jedem Push (alles muss grün sein)
- [ ] `python3 check.py` ohne Fehler
- [ ] `python3 build.py`, `python3 build.py --noindex`, `python3 build.py --preview` laufen durch
- [ ] Produktions-Build erzeugt `sitemap.xml`, `robots.txt`, `llms.txt`, `assets/css/theme.css`, `api/config.php`; `.htaccess` enthält keine Platzhalter-Markierung (`{{GENERATED_REDIRECTS}}`)
- [ ] Design-Check: `design.status` testweise auf `offen` → Produktions-Build bricht ab, Staging-Build geht; auf `individuell` ohne Anpassungen → Fehler; danach zurück auf `template`
- [ ] Neue Bausteine (Cases-Slider, Prozess, Preise, News, Beitragsseite) und Nach-oben-Button: Desktop (1440) und mobil (390) ohne Überlauf, Button erscheint erst nach etwa einer Bildschirmhöhe, Slider-Pfeile blättern
- [ ] Dritte Sprache testen: Ordner `content/en` nach `content/fr` kopieren, in der Config eintragen, bauen (hreflang, Sprach-Dropdown), danach **nicht** übernehmen
- [ ] Startseite und eine Unterseite im Browser prüfen: Desktop (1440) und mobil (390), kein horizontaler Überlauf, keine Konsolenfehler, Bilder laden
- [ ] CSP-Test: Seite mit CSP-Header ausliefern (Anleitung `references/sicherheit.md`), keine Verstöße
- [ ] Link-Prüfung: ein `javascript:`-Link in einer JSON-Datei bricht den Build ab (danach zurücksetzen)
- [ ] Keine Kundenreste: `grep -rIn -i "24bit\|mica\|rosenheim" . --exclude-dir=.git --exclude-dir=dist --exclude-dir=preview` findet nur bewusste Verweise im Skill (Referenzprojekt)
- [ ] Platzhalter vorhanden und klar markiert (`Muster`, `example.com`, `Platzhalter`, `20XX`)
- [ ] Skill-Dateien und `README.md` zeigen den aktuellen Stand; Skill nach `~/.claude/skills/` kopiert

## Nach dem Push
Kurz in einem Kundenprojekt prüfen, dass „Use this template“ den neuen Stand liefert. Größere Änderungen am Verhalten (Workflow-Variablen, Config-Schlüssel) in `README.md` unter „Template pflegen“ und im Skill vermerken, damit bestehende Kundenprojekte wissen, was sie nachziehen müssen (`git remote add template …`, `git diff HEAD template/main -- <datei>`).

## Offene Ideen
- Weitere neutrale Bausteine (Zitate/Referenzen, Prozess-Schritte, Preistabelle, Blog/News), nur mit Beispielinhalten. FAQ ist umgesetzt.
- SSH-Schlüssel statt Passwort im Deploy-Workflow; Basic-Auth für Staging optional.
- Hoster-Hinweise im Skill (`hosting-deployment.md`) um geprüfte Erfahrungen ergänzen (z. B. DomainFactory), sobald ein Kunde dort liegt.
- Eigenes kleines Verwaltungs-Frontend (Idee: „eigenes OnePage.io“): Konzeptentwurf in `docs/KONZEPT-KUNDENPFLEGE.md`, Bedarf bei Kunden erst validieren.
