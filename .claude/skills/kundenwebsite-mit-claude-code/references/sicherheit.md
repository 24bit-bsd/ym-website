# Sicherheit statischer Kundenwebsites

Statische Seite = kleine Angriffsfläche (keine DB, kein CMS, keine Plugins, keine Nutzerinhalte, keine Fremdskripte). Realistische Risiken: Konten/Pipeline, Formular, eingeschleuste Links/Skripte über Inhalte, fehlende Header. Von Anfang an umsetzen.

## Code-Injection / Inhalte
- Alle Texte beim Rendern maskieren (`esc()`), Formatierung erst danach (`rich()`); Editor-Ausgabe genauso.
- **Link-Prüfung:** Nur `page:`, `https://`, `http://`, `mailto:`, `tel:`, `#`, `/` erlauben. `check.py` (alle Link-Felder in `content/` und `config.json`) und `safe_url()` im Generator (Build-Abbruch bei `javascript:`/`data:`). Für jede neue Link-Ausgabe `safe_url()` verwenden.
- **Keine Inline-Skripte**, keine `on*`-Attribute: Init-Code als Datei (`init.js`) früh im `<head>`. Dann ist `script-src 'self'` möglich.
- Externe Ressourcen nur nach bewusster CSP-Anpassung (Skripte, Fonts, iframes, Bilder).

## HTTP-Header (`.htaccess`)
`Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'self'; base-uri 'self'; object-src 'none'` (style-attribute brauchen `'unsafe-inline'`), `Strict-Transport-Security: max-age=31536000` (nach funktionierendem HTTPS, ohne includeSubDomains/preload beginnen), `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (Kamera/Mikro/Standort aus), `Cross-Origin-Opener-Policy: same-origin`, `Options -Indexes`, versteckte Dateien und interne PHP-Helfer sperren (`<FilesMatch "^\.">`, `<Files "common.php">`).
**CSP lokal testen** (Header werden vom Apache gesetzt): kleinen Python-Server mit gleichem Header starten, Seiten laden, Browser-Konsole auf „violates the following Content Security Policy“ prüfen und einmal gezielt ein Inline-Skript einschleusen (muss blockiert werden).

## Kontaktformular (PHP)
- Honeypot-Feld, serverseitig **signierter Zeitstempel** (`api/token.php`, HMAC mit zufälligem Schlüssel im Temp-Verzeichnis, nicht im Repo), Mindest-/Höchstalter, `hash_equals`.
- Origin/Referer-Prüfung gegen Whitelist eigener Hosts; Rate-Limits je IP (z. B. 30 s und 5/Std.) und gesamt (z. B. 40/Std.).
- Eingaben: Länge begrenzen, Steuerzeichen entfernen, einzeilige Felder von Zeilenumbrüchen befreien (Header-Injection), E-Mail mit `FILTER_VALIDATE_EMAIL`, Thema/Sprache gegen Whitelist, Empfänger fest, Ausgabe mit `htmlspecialchars`.
- Pflicht-Einwilligung; nichts auf dem Server speichern außer anonymen Zählern.
- Folge: Formular braucht JavaScript (Token-Abruf); Fallback ist die E-Mail-Adresse. Auf **Staging mit echter Anfrage testen** (PHP ist lokal oft nicht installiert).
- Absenderadresse in eigener Domain; SPF/DKIM/DMARC einrichten.

## Pipeline, Konten, Hosting
- Zwei-Faktor für jedes Konto mit Schreibrechten (Authenticator/Passkey/Security Key, Recovery-Codes im Passwort-Manager). SMS vermeiden.
- Secrets (`DEPLOY_HOST/USER/PASSWORD/PORT`) nur als GitHub-Environment-Secrets, nie im Repo oder Chat. Deploy Key statt Passwort für Git; FTP/SFTP-Benutzer nur auf den Zielordner; getrennte Zugänge für Staging/Produktion, SSH-Schlüssel statt Passwort (Verbesserung; Template nutzt Passwort). Unverschlüsseltes FTP vermeiden (SFTP oder FTPS).
- GitHub Actions auf **Commit-Hashes pinnen** (`uses: owner/action@<sha> # vX.Y.Z`), `permissions: contents: read`, Dependabot (`github-actions`, monatlich).
- Workflow-Prüfungen: Produktions-Build ohne `noindex`, ausgelieferte Version gegen Build abgleichen, `--delete` nur mit exklusivem Zielordner und Plausibilitätsprüfung des Pfades.
- **Plan-Grenzen:** „Required reviewers“ für Environments, Branch-/Tag-Rulesets mit Pflichtprüfung sind bei privaten Repos erst im bezahlten GitHub-Plan verfügbar. Ohne sie geht jeder `live-*`-Tag sofort live: Schreibrechte eng halten, Regel „nur Inhaber:in startet Produktion“ dokumentieren (README, CLAUDE.md, Onboarding). Wenn möglich Team-Plan nutzen: Required reviewers, Tag-Ruleset `live-*`, Branch-Ruleset (Löschen/Force-Push sperren; PR-Pflicht nur, wenn der Live-Editor-Push über Bypass läuft).
- Lokaler Editor: nur 127.0.0.1, Token für Schreibzugriffe, Host-Header-Prüfung (DNS-Rebinding). Rechner mit Festplattenverschlüsselung und Bildschirmsperre (Deploy Key liegt lokal).
- Hoster: PHP-Version aktuell halten, Konto mit Zwei-Faktor, Domain-Transferschutz beim Registrar.
- Staging ist erreichbar, aber `noindex`; nur Inhalte kurz vor Veröffentlichung dort ablegen. Bei vertraulichen Entwürfen Basic-Auth davor schalten.

## Prüfliste vor Live
[ ] Link-Prüfung aktiv [ ] keine Inline-Skripte, CSP getestet [ ] HSTS erst nach stabilem HTTPS [ ] Formular auf Staging real getestet [ ] 2FA aller Beteiligten [ ] Actions gepinnt [ ] Secrets korrekt, Pfade geprüft [ ] Rollen/Plan-Grenzen dokumentiert [ ] SPF/DKIM/DMARC [ ] Rechtstexte.
