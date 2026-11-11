# Übergabe und Unabhängigkeit des Kunden (Phase H)

Ziel: Der Kunde kann jederzeit selbst weiterarbeiten oder den Dienstleister wechseln.

## Eigentum und Zugänge klären
- **Domain, Hoster, E-Mail**: gehören dem Kunden; wir arbeiten mit eigenem Hosting-Benutzer (Rechte entziehbar).
- **GitHub-Repo**: entweder in der Organisation des Beraters mit **Zugriff für den Kunden** (Collaborator/Team, Zwei-Faktor Pflicht) oder per **Repository-Transfer** in das Konto/die Organisation des Kunden (Settings → Danger Zone → Transfer). Danach Secrets/Variablen prüfen (bleiben im Repo, Berechtigungen anpassen), Deploy-Keys neu setzen.
- **Secrets**: SFTP-Passwort kennt nur, wer es im Hoster-Panel vergibt; Rotation vereinbaren (nach Personalwechsel/Übergabe Passwort ändern und in GitHub aktualisieren).
- **Claude-Zugang**: jede Person arbeitet mit eigenem Zugang (kein geteilter Account).

## Dokumentation für den Kunden
`docs/onboarding.html` (Einrichtung Mac, GitHub, Editor, Spielregeln; als PDF mit Chrome headless `--print-to-pdf`), `README.md` (Befehle, Deployment), `CLAUDE.md` (Projektregeln für KI). Inhalt anpassen: Namen, Rollen, wer startet Produktion, Hinweis auf GitHub-Plan-Grenzen.

## Schulung (30–60 Min.)
Editor bedienen (Text ändern, veröffentlichen), Staging prüfen, Live-Gang nur durch die verantwortliche Person, was bei Fehlern zu tun ist (`git pull --rebase`, Actions-Log, wen anrufen). Optional: kurzer Screencast.

## Betrieb
Wartung (PHP-Version beim Hoster, Dependabot-PRs für Actions, Domain/Zertifikat-Ablauf), Backup (GitHub ist die Sicherung der Inhalte), Änderungswünsche (kleine: Editor, größere: Claude Code auf Branch → PR → Staging → Live), regelmäßig SEO/GEO-Check und Search Console.

## Abschluss-Checkliste
[ ] Zugriff und Eigentum geklärt [ ] 2FA bei allen Beteiligten [ ] Secrets rotiert/dokumentiert [ ] Onboarding-PDF übergeben [ ] Schulung erledigt [ ] Verantwortliche Person für Live-Gänge benannt [ ] Offene Punkte in README/`SETUP.md` abgehakt oder übergeben.
