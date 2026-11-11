# Konzept: Pflege durch Kunden ohne Claude Code („Verwaltungs-Frontend“)

Status: **Entwurf zur Validierung**, nichts davon ist gebaut. Bedarf bei Kunden ist noch nicht bestätigt (siehe „Offene Entscheidungen“). Betrifft nur das Template-Repo; Kundenprojekte übernehmen es erst nach Umsetzung.

## Ziel
Kunden ändern **Texte** ihrer Website selbst, ohne Claude-Abonnement, ohne GitHub-Konto, ohne lokale Software. Struktur, Layout und neue Bausteine bleiben beim Berater (mit Claude Code). Produktion geht weiterhin nur nach Freigabe des Beraters live.

## Ausgangslage (Bestand)
- **Live-Editor** (`editor.py`): Texte anklicken, ändern; Änderung = (Datei, JSON-Pfad, Text). Nur Textfelder, Pfad auf `content/<lang>/*.json` begrenzt, danach `check.py`, Commit nur `content/`, Push. Das Datenmodell trägt auch ein Online-Frontend.
- **Hosting**: Apache + PHP (Shared Hosting), kein Python auf dem Server. Der Editor kann dort nicht laufen; ein Online-Teil muss PHP + JavaScript sein.
- **Deploy**: Push auf `main` → Action prüft, baut `--noindex`, lädt auf Staging. Produktion nur per Tag/manuell. Deploy-Zugangsdaten liegen als Environment-Secrets in GitHub.
- **Edit-Build** (`build.py --edit`): erzeugt die Seiten mit Fundstellen-Markierung (`data-ed`), die der Editor zum Anklicken braucht.

## Grundentscheidung: Wie kommen Änderungen ins Repo?
Das ist der sicherheitskritische Punkt. Wer ins Repo (Branch `main`) schreiben kann, kann auch `build.py` oder den Workflow ändern, und der Workflow hat Zugriff auf die Deploy-Secrets. Ein GitHub-Token auf dem Webserver wäre damit praktisch ein Generalschlüssel für Server und Repo. Ein feingranulares Token kann weder Pfade noch Branches einschränken, und ohne bezahlten Plan gibt es keinen Branch-Schutz.

### Variante A: Pull-Modell (empfohlen)
Der Webserver hält **keine GitHub-Zugangsdaten**.
1. Das Frontend speichert Änderungen als „ausstehend“ in einer Datei außerhalb des Web-Roots (JSON-Liste: Datei, Pfad, alter Text, neuer Text, Zeit, Benutzer).
2. Eine Action (zeitgesteuert, z. B. alle 10 Minuten, und manuell auslösbar) ruft einen **nur lesenden, signierten Endpunkt** (HMAC-Geheimnis als Secret) ab.
3. Ein Skript im Repo (Wiederverwendung von `set_value`-Logik) wendet die Änderungen auf `content/` an, führt `check.py` aus, committet nur `content/` und pusht. Dadurch läuft der normale Deploy auf Staging.
4. Danach bestätigt die Action die verarbeiteten Änderungen (signierter Aufruf), das Frontend leert die Warteschlange und zeigt den Status. Abgelehnte Änderungen (z. B. Prüfung fehlgeschlagen) erscheinen mit Grund beim Kunden.
- Vorteil: Ein kompromittierter Webserver kann keinen Code ins Repo bringen. Geändert werden können nur Textfelder, und jede Änderung läuft durch `check.py`.
- Nachteil: Verzögerung bis zur Sichtbarkeit (Zeitplan der Action, plus ca. 1 Minute Deploy). Zeitgesteuerte Actions können sich verspäten. Verbrauchte Action-Minuten beachten.
- Der Server darf den Endpunkt nicht für Fremde öffnen: HMAC, Zeitstempel, Rate-Limit.

### Variante B: Push-Modell mit Token (nicht empfohlen)
Das PHP-Frontend schreibt per GitHub-API direkt ins Repo. Sofortiger Start des Deploys, aber das Token auf dem Server wäre ein hohes Risiko (siehe oben). Nur sinnvoll mit bezahltem GitHub-Plan, geschütztem `main`, Pull-Request-Pflicht und Environments mit Branch-Einschränkung. Dann neu bewerten.

## Aufbau (bei Variante A)
```
Kunde (Browser)
   │  Login, Texte ändern
   ▼
/verwaltung/ auf Staging (PHP + JS)         ← Edit-Build der Seiten, hinter Login
   │  speichert „ausstehend“ (außerhalb Web-Root)
   ▼
GitHub Action (Zeitplan / manuell)
   │  holt Änderungen (signiert), wendet an, check.py, Commit auf main
   ▼
Deploy auf Staging (bestehender Ablauf)
   │
   ▼
Kunde sieht Ergebnis → „Zur Freigabe vorschlagen“ → Mail an Berater
   ▼
Berater startet Produktion (Tag live-… oder Actions → production), wie bisher
```

### Bausteine
1. **Edit-Build auf Staging**: Der Deploy-Workflow baut zusätzlich `--edit` in einen Unterordner (z. B. `/verwaltung/seiten/`). Dieser Ordner ist nur nach Login erreichbar (PHP-Vorschaltung oder Apache-Zugangsschutz). Er ist `noindex`, wird nie in die Produktion übertragen und hat keinen Zugang zur Produktions-Domain.
2. **Editor-JS** (neu, aus `editor/assets/` ableiten): Klick auf Text → Eingabe → „Speichern“ sendet `(Datei, Pfad, Text)` an die PHP-API. Das Original-JS arbeitet gegen `/__api/…`; dort wird die Gegenstelle ersetzt.
3. **PHP-API** (`api/verwaltung/…`, neben `contact.php`, mit eigenen Helfern analog zu `common.php`): Anmelden/Abmelden, Änderung speichern, Status lesen, Freigabe vorschlagen. Dazu die zwei signierten Endpunkte für die Action (lesen, quittieren).
4. **Übernahme-Skript im Repo** (z. B. `tools/apply_pending.py`): Holt die Warteschlange, nutzt dieselbe Pfad-Auflösung wie `editor.py`, prüft mit `check.py`, committet nur `content/`.
5. **Workflow-Erweiterung**: Job „Kundenänderungen übernehmen“ (Zeitplan + manuell), Edit-Build-Upload im bestehenden Deploy.
6. **Sprachen**: Das Gegenstück je Sprache (`counterparts`) sollte sichtbar sein, damit Kunden nicht nur eine Sprache ändern und die andere vergessen. Optional: Änderung nur in einer Sprache als „Übersetzung offen“ markieren.

## Sicherheit
- **Login**: eigene Benutzer je Kunde (nicht GitHub), Passwort-Hash (`password_hash`), Sperre nach Fehlversuchen, Sitzung mit `HttpOnly`/`Secure`/`SameSite`, Abmelden. Optional zweiter Faktor (TOTP) später.
- **Schreibrechte**: Nur Strings, Whitelist der editierbaren Feldtypen. **Standardmäßig nicht editierbar**: Links (`href`, `*_url`), IDs, Slugs, Typen, Konfiguration. Link-Felder eventuell später für Einzelfälle freigeben, dann nur mit `safe_url()`-Prüfung. Längenlimit je Feld, Steuerzeichen entfernen.
- **Darstellung**: Alles weiter über `T()`/`rich()` (escaped). Keine HTML-Eingabe. Ausgabe der Frontend-Texte mit `textContent`.
- **CSRF**: Token je Sitzung, Prüfung von Origin/Referer gegen `ALLOWED_HOSTS`.
- **CSP**: Wie die Website (`script-src 'self'`, keine Inline-Skripte, keine Fremdressourcen). Keine Bibliotheken von CDNs.
- **Server-Daten**: Warteschlange und Geheimnisse außerhalb des Web-Roots, Rechte `0600`. Nicht ins Repo.
- **Rate-Limits und Größenlimits** je Benutzer und gesamt, wie beim Kontaktformular.
- **Protokoll**: Wer hat wann was geändert, mit altem und neuem Text. Das ergänzt die Git-Historie.
- **Datenschutz**: Kundenkonten sind personenbezogene Daten; Auftragsverarbeitung, Löschkonzept und Hinweis in der Übergabe klären.
- **Rückgängig machen**: über Git (Commit zurücknehmen). Für Kunden eine „Letzte Änderung zurücknehmen“-Funktion erst in Phase 2.

## Phasen
**Phase 0 – Validierung (jetzt)**: Bedarf je Kunde klären; zunächst den manuellen Weg (Berater pflegt, Kunde sitzt dabei, Mail/Formular) sauber in `uebergabe.md` beschreiben. Ergebnis entscheidet, ob Phase 1 gebaut wird.

**Phase 1 – MVP (Text, ein Kunde)**
- Edit-Build hinter Login, Texte ändern, Warteschlange, Übernahme-Action, Statusanzeige, „Zur Freigabe vorschlagen“ per Mail.
- Ein Benutzer je Kunde, nur de/en wie im Template, keine Bilder, kein Rückgängig.
- Pilot bei einem Kunden, der den Bedarf bestätigt hat.

**Phase 2 – Ausbau**: mehrere Benutzer, Rollen (Redakteur/Freigeber), „Letzte Änderung zurücknehmen“, Bild-Austausch (Größen- und Typprüfung, Dateinamen vergeben), Abschnitte ausblenden, TOTP, Änderungsübersicht für den Berater.

**Phase 3 (nur bei Bedarf)**: Neue Seiten/Abschnitte aus vorgegebenen Bausteinen (FAQ, Karten …), Vorschau-Link für Dritte, Mehrere Kunden-Repos zentral verwalten.

## Abgrenzung
- Kein WYSIWYG-Seitenbaukasten und keine freie Layoutänderung. Das ist der Wert des Pflegevertrags und bleibt bei Claude Code.
- Keine Pflege der Produktion ohne Freigabe.
- Kein Ersatz für Rechtstexte-Pflege: Impressum/Datenschutz bewusst außerhalb der Kundenbearbeitung oder mit Warnhinweis.

## Aufwand (grobe Einschätzung)
Der Aufwand liegt im Sicherheitskonzept und in den Randfällen (Warteschlange, Konflikte, Fehlerrückmeldung), nicht in der Oberfläche. MVP: mehrere Arbeitstage Entwicklung plus gründlicher Test (PHP-Seite, Action, Edit-Build, CSP). Fertige Bausteine, die sich wiederverwenden lassen: Pfad-Auflösung und Prüfung aus `editor.py`, Edit-Build, Helfer-Muster aus `api/common.php`.

## Konflikte und Randfälle
- **Gleichzeitige Änderungen** durch Berater (Git) und Kunde: Die Übernahme vergleicht den „alten Text“ mit dem aktuellen Stand; weicht er ab, wird die Änderung nicht stillschweigend überschrieben, sondern als Konflikt zurückgemeldet.
- **Mehrere Änderungen am selben Feld** vor der Übernahme: zusammenführen, letzte gewinnt, beide im Protokoll.
- **Fehlgeschlagene Prüfung** (z. B. verbotene Schreibweise nach Glossar): Änderung bleibt ausstehend mit Meldung, geht nicht live.
- **Template-Updates** ändern den Edit-Build: Kunden-Repos müssen die Frontend-Dateien nachziehen (Vermerk in `README.md` unter „Template pflegen“ und im Skill).

## Offene Entscheidungen (noch zu validieren)
1. Wie viele Kunden brauchen Selbstpflege, wie oft und welche Änderungen (Preise, Öffnungszeiten, Texte, Bilder)?
2. Reichen Textänderungen, oder sind Bilder und Ein-/Ausblenden von Abschnitten nötig?
3. Darf der Kunde selbst veröffentlichen, oder bleibt die Freigabe beim Berater (Empfehlung: beim Berater)?
4. Zeitplan-Verzögerung (ca. 10 bis 15 Minuten) akzeptabel, oder ist sofortige Sichtbarkeit Pflicht? Letzteres spricht für Variante B mit bezahltem GitHub-Plan.
5. Wo liegt Staging? Eigene Subdomain auf demselben Hoster wie Produktion, oder getrennt? Beeinflusst, wo Login, Warteschlange und Edit-Build liegen dürfen.
6. Abrechnung: Teil des Pflegevertrags oder eigenes Modul?
