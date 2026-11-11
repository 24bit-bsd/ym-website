# Hosting, FTP/SFTP, Subdomain, Environments (Phase E)

Kunden bringen meist eigenes Hosting mit (IONOS, DomainFactory, Strato, all-inkl, …). Das Template deployt per GitHub Action auf zwei Ziele: **Staging** (eigene Subdomain, `noindex`) und **Produktion** (Hauptdomain). Voraussetzung beim Hoster: Apache mit `.htaccess`, optional PHP (Formular), SFTP/FTPS-Zugang.

## 1. Anforderungen klären (Fragen an den Kunden/Hoster)
Welcher Hoster und welcher Tarif? Gibt es **SFTP** (bevorzugt), sonst **FTPS** (FTP über TLS), nur im Notfall unverschlüsseltes FTP (Passwort im Klartext – möglichst vermeiden)? Ist PHP ≥ 7.2 aktiv (für `api/contact.php`)? Läuft Apache (`.htaccess`)? Kann man **Subdomains** mit eigenem Zielordner und **SSL-Zertifikat** anlegen? Wer hat Zugang zum Hoster-Panel und zur DNS-Verwaltung? Wo wird die Domain verwaltet (Registrar)?

## 2. Zugang einrichten und testen (vor GitHub!)
1. Im Hoster-Panel einen **eigenen FTP/SFTP-Benutzer** für die Website anlegen (nicht den Haupt-Account), Ziel-Verzeichnisse: ein Ordner für Produktion (z. B. `website`) und einer für Staging (z. B. `website-staging`).
2. Host, Port (SFTP meist 22, FTP/FTPS 21), Benutzer notieren. **Passwort nur im Panel/Passwortmanager, nie im Chat.**
3. **Verbindung testen** mit einem Client auf dem Mac (z. B. Cyberduck, FileZilla oder `sftp user@host`): einloggen, Ordner ansehen, Testdatei hochladen/löschen. Ziel: den **Pfad ab der Wurzel des Benutzers** herausfinden. Manche Hoster (z. B. IONOS) zeigen dem Benutzer einen Unterordner bereits als Wurzel `/`; dann ist der Pfad `/website-staging`, nicht der im Panel angezeigte Gesamtpfad. Falscher Pfad = Dateien landen in verschachtelten Ordnern und „verschwinden“.
4. Notiere: Protokoll (sftp/ftps/ftp), Host, Port, Benutzer, **Remote-Pfade** je Umgebung.

## 3. Staging-Subdomain
1. Subdomain anlegen, z. B. `staging.<kundendomain>` (oder `test.`/`website.`), **Zielordner = Staging-Ordner** aus Schritt 2.
2. **SSL-Zertifikat** für die Subdomain aktivieren (Hoster-Panel, meist kostenlos/automatisch); ohne SSL schlägt HSTS/`https`-Prüfung fehl.
3. DNS: Wenn die Domain beim Hoster verwaltet wird, legt das Panel den Eintrag an; sonst beim Registrar einen A-/CNAME-Eintrag nach Anweisung des Hosters setzen.
4. `content/config.json` → `staging_url` auf `https://staging.<kundendomain>` setzen.
5. Test: Eine Datei `test.html` hochladen und im Browser über die Subdomain öffnen.

## 4. GitHub-Environments
Im Repo: **Settings → Environments → New environment** zweimal: `staging` und `production`. Je Environment:
- **Secrets** („Add environment secret“): `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_PASSWORD`, optional `DEPLOY_PORT`.
- **Variables** („Add environment variable“): `DEPLOY_REMOTE_DIR` (z. B. `/website-staging` bzw. `/website`), optional `DEPLOY_PROTOCOL` (`sftp` ist Standard; `ftps` oder `ftp`).
- Production: bei bezahltem GitHub-Plan „Required reviewers“ aktivieren; ohne Plan geht ein `live-*`-Tag sofort live (organisatorisch regeln, siehe `sicherheit.md`).
Die Person trägt die Werte **selbst** ein; du erklärst die Felder und wartest. Passwörter nie anzeigen oder in Dateien schreiben.

## 5. Erster Staging-Deploy
Nach ausdrücklicher Bestätigung: Änderungen committen und `git push` auf `main` → Actions-Tab öffnen, Lauf „Build & Deploy“ beobachten. Schritte: Prüfen, Bauen, Hochladen, „Prüfen, ob der neue Stand ausgeliefert wird“. Bei Fehlern das Log lesen: häufig falscher `DEPLOY_REMOTE_DIR`, Passwortfehler, Subdomain zeigt nicht auf den Zielordner, SSL fehlt. Danach Staging im Browser prüfen (Seiten, Formular mit echter Test-Anfrage, `robots.txt` = Disallow).

## 6. Produktion und Domain
1. Hauptdomain bleibt bis zum Live-Gang auf der alten Seite. Produktion-Environment wie oben einrichten (anderer Zielordner).
2. **Erster Produktions-Deploy** per Tag: `git tag live-YYYY-MM-DD && git push origin live-YYYY-MM-DD` (nur nach Bestätigung durch die verantwortliche Person). Die Prüfung der Hauptdomain warnt am Anfang nur, solange die Domain noch nicht umgelegt ist.
3. **Domain umlegen**: im Hoster-Panel die Hauptdomain (und `www`) auf den Produktionsordner zeigen lassen, SSL aktivieren, `www`/ohne-`www`-Weiterleitung kommt aus der `.htaccess` (aus `domain` in der config).
4. Nachkontrolle: `curl -sI https://www.<domain>/` (Header: CSP, HSTS), Formular-Test, `sitemap.xml`, `robots.txt`, Weiterleitungen alter URLs (`redirects` in der config), Search Console/Bing.

## Hoster-Hinweise (prüfen, nicht annehmen)
- **IONOS**: SFTP verfügbar; Benutzer sieht oft einen Ordner als Wurzel (Pfad entsprechend kürzen); Subdomains unter „Domains & SSL“; Mail-Versand per `mail()` nur mit Absender in eigener Domain; PHP-Version im Panel wählbar.
- **DomainFactory und andere**: im Hoster-Panel/FAQ nachsehen, welche Protokolle der Tarif erlaubt (SFTP/FTPS/FTP), wie Subdomains auf Ordner zeigen und ob `mail()` erlaubt ist. Vor der Einrichtung des Workflows immer lokal mit Cyberduck/FileZilla testen.
- Bei reinem FTP: `DEPLOY_PROTOCOL=ftp` nur im Notfall; Kunden auf das Risiko hinweisen oder Hosterwechsel/SFTP-Upgrade vorschlagen.
