# Stolpersteine und Lösungen

- **macOS `sed -i`** braucht `sed -i ''`; bei `&&`-Ketten bricht ein Fehler alles Folgende ab, danach Zustand prüfen. Für mehrzeilige Änderungen besser kurze Python-Skripte.
- **Kein PHP lokal**: PHP-Änderungen sorgfältig prüfen (PHP ≥ 7.2, keine neuen Syntax-Features) und auf Staging real testen; Formular-Test ist Pflicht vor Live.
- **Bildbearbeitung**: Pillow in einer venv im Scratchpad installieren (`python3 -m venv v && v/bin/pip install pillow numpy`), nicht global.
- **Live-Editor-Commits**: Der Editor committet Inhalte selbst; Änderungen an `content/` können unbemerkt mit „Inhalte aktualisiert“ auf `main` landen. Vor Push `git pull --rebase`; Hinweis an den Kunden, wer wann veröffentlicht.
- **Editor-Zähler/„Veröffentlichen 2“** zeigt ungespeicherte Textänderungen; nicht mit Dateiänderungen von Claude verwechseln.
- **Animationen testen**: Zustände zeitlich per `getComputedStyle` abfragen (Start erst, wenn das Element sichtbar wird); Screenshots allein zeigen nur einen Moment. Dialoge im Screenshot erst nach der Animation prüfen.
- **Responsives Testen**: Viewport auf 390 px setzen, am Ende zurück auf Desktop; `scrollWidth <= innerWidth` prüfen.
- **CSS-Details**: `isolation: isolate` + `z-index: -1`, damit Hintergrund-Elemente (Marker) hinter dem Text bleiben; Fotos mit eigenem Hintergrund brauchen kein `mix-blend-mode: multiply`.
- **`<dialog>`**: `cancel`-Event abfangen, um die Ausblend-Animation zu spielen; Scroll sperren (`no-scroll`), Fokus auf Auslöser zurücksetzen.
- **CSP**: nach jedem neuen Script/Style/Bild-Quelle neu testen; Header-Wert nicht per fehleranfälligem `sed` aus der `.htaccess` ziehen (leerer Header → CSP scheinbar „aktiv“). Immer per `curl -I` verifizieren und Gegenprobe machen.
- **Kopierte Listen**: doppelte Aussagen in Pain-Listen vermeiden; Fazit-Sätze vollständig in einer Zeile formulieren.
- **GitHub-Plan**: Freigabe-/Ruleset-Features erst bei bezahltem Plan; dokumentieren, was nur organisatorisch gilt.
- **Rückfragen minimieren**: Standardentscheidungen treffen, nennen und fortfahren; nachfragen nur bei echten Kundenentscheidungen (Preise, Rechtliches, Veröffentlichung).
- **Template-Design nicht ausliefern**: `style.css` ist eine neutrale Basis; ohne eigenes Design (Tokens, Layout, Typo) ist die Seite nicht fertig.
- **Platzhalter vergessen**: vor Live `grep -rn "Muster\|example.com\|Platzhalter\|20XX" content static` ausführen; Rechtstexte, Bilder, Logo, Favicon, Share-Bild ersetzen.
- **Staging-URL/SSL**: Staging-Prüfung im Workflow scheitert, wenn die Subdomain nicht auf den Zielordner zeigt oder kein Zertifikat hat.
- **Falscher Remote-Pfad**: Pfad ab der Wurzel des FTP/SFTP-Benutzers angeben, nicht den Gesamtpfad aus dem Hoster-Panel.
