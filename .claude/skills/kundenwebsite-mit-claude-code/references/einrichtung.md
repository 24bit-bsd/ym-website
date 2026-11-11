# Einrichtung Schritt für Schritt (Phase A)

Führe im Dialog: **ein Schritt, Rückmeldung abwarten, dann weiter.** Prüfe vorher selbst, was schon erledigt ist (`git remote -v`, `ls ~/Websites`, `python3 --version`). Hake in `docs/SETUP.md` ab.

## Zwei Fälle
- **A1 – Template pflegen** (einmalig, nur Berater:in): Das Repo `website-template` selbst auf GitHub bringen und lokal klonen.
- **A2 – Neue Kundenwebsite**: aus dem Template ein eigenes Repo erzeugen und auf den Mac holen. Das ist der Normalfall.

## Vorbereitung auf dem Mac (einmalig je Rechner)
1. **Terminal öffnen** (Programme → Dienstprogramme → Terminal).
2. **Git und Python 3 installieren**: `xcode-select --install` (Dialog bestätigen). Prüfen mit `git --version` und `python3 --version` (Python ab 3.8).
3. **Browser**: Chrome empfohlen (für Bild-/Share-Bild-Erzeugung headless und zum Testen).
4. **Arbeitsordner anlegen**: `mkdir -p ~/Websites`. Projekte liegen **nicht** in Synology Drive, iCloud oder Dropbox (Git-Ordner `.git` wird dort beschädigt oder doppelt synchronisiert).
5. **Claude-App** (Tab „Code“) oder Claude Code im Terminal; Projektordner öffnen.

## GitHub
1. **Konto** auf github.com anlegen (falls nötig), **Zwei-Faktor** aktivieren (Authenticator-App oder Passkey; Recovery-Codes im Passwort-Manager sichern).
2. **Wo liegt das Repo?** Empfehlung: in der GitHub-Organisation des Beraters (z. B. `24bit-bsd`), privat, Name `<kunde>-website`. Der Kunde bekommt später Zugriff oder das Repo wird übertragen (siehe `uebergabe.md`).
3. **Repo aus Template erzeugen** (A2): auf der Seite des Template-Repos „Use this template“ → „Create a new repository“ → Owner wählen, Name `<kunde>-website`, **Private**, „Include all branches“ aus. Alternativ mit der GitHub-CLI: `gh repo create <org>/<kunde>-website --template <org>/website-template --private`.
4. **Template selbst veröffentlichen** (A1): neues privates Repo `website-template` anlegen, lokal `git remote add origin git@github.com:<org>/website-template.git`, `git push -u origin main`, danach auf GitHub: Settings → „Template repository“ aktivieren.

## Auf den Mac holen (klonen)
**Variante 1 – GitHub Desktop (einfach):** desktop.github.com installieren, anmelden, *File → Clone Repository* → Repo wählen → Zielordner `~/Websites/<kunde>-website`.
**Variante 2 – Terminal:** `cd ~/Websites && git clone https://github.com/<org>/<kunde>-website.git` (bei privaten Repos fragt Git nach Anmeldung; einfacher mit `brew install gh` und `gh auth login`, dann `gh repo clone <org>/<kunde>-website`).
Danach einmalig Name und Mail für Git: `git config --global user.name "Name"` und `git config --global user.email "mail@…"`.
**Prüfen:** `cd ~/Websites/<kunde>-website && python3 build.py --preview` → „Prüfung: 0 Fehler“ und „OK: … Seiten“. Vorschau lokal ansehen (Browser öffnet `preview/index.html` oder lokaler Server).

## Push-Zugang per Deploy-Key (optional, empfohlen für den Live-Editor)
Der Live-Editor veröffentlicht per Push. Statt persönlicher Anmeldung nutzt man einen **Deploy-Key nur für dieses Repo**:
1. Schlüssel erzeugen (Claude kann das ausführen): `ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_<kunde> -C "<kunde>-website deploy" -N ""`.
2. Öffentlichen Schlüssel anzeigen (`cat ~/.ssh/id_ed25519_<kunde>.pub`) und auf GitHub eintragen: Repo → Settings → Deploy keys → Add deploy key → **„Allow write access“** aktivieren. (Nur den `.pub`-Teil, nie die Datei ohne `.pub`.)
3. Repo-Remote auf SSH stellen und Schlüssel binden: `git remote set-url origin git@github.com:<org>/<kunde>-website.git` und `git config core.sshCommand "ssh -i ~/.ssh/id_ed25519_<kunde> -o IdentitiesOnly=yes"` (gilt nur lokal im Repo).
4. Test: `git push` (oder `git ls-remote origin`) funktioniert ohne Passwortabfrage.
Der private Schlüssel verlässt den Rechner nie. Festplattenverschlüsselung (FileVault) und Bildschirmsperre aktivieren.

## Projekt vorbereiten
1. `docs/SETUP.md` öffnen (Checkliste für dieses Projekt) und mit dem Menschen durchgehen.
2. `CLAUDE.md` des Projekts ausfüllen (Kunde, Domain, Hosting, Sprachen, Regeln). Dort stehen später alle projektspezifischen Entscheidungen.
3. `content/config.json`: Marke, Firma, Domain, Staging-URL, Kontakt, Sprachen (`languages`, `default_language`, `language_names`).
4. **Design-Check scharf stellen:** in `content/config.json` `design.status` von `template` auf `offen` setzen. Der Produktions-Build bleibt dann gesperrt, bis die Design-Phase abgeschlossen ist (`design.md`).
4. Erster Commit ist erst nach Aufforderung.

## Wenn etwas hakt
„Permission denied (publickey)“ → Deploy-Key nicht eingetragen oder `core.sshCommand` fehlt. `git push` abgelehnt („non-fast-forward“) → `git pull --rebase`. `python3` fehlt → `xcode-select --install` wiederholen. Editor startet nicht → Port 8777 belegt (altes Terminal schließen).
