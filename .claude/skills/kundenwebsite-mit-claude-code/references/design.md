# Gestaltung: jede Website bekommt ein eigenes Design

**Das Template ist bewusst neutral.** `static/assets/css/style.css` liefert nur eine schlichte, funktionierende Basis (System-Schrift, ein Akzent, ruhige Flächen), damit alle Bausteine (Header, Menü, Footer, Sektionen, Formular) sofort brauchbar aussehen. Es ist der Startpunkt, nie das Ergebnis. Wer das Template unverändert ausliefert, hat keine Kundenseite gebaut.

## Pflicht: jede Website sieht anders aus (Design-Check)
Gleiche Bausteine, aber nie gleiches Aussehen: Wer nur die Texte füllt, hat nicht fertig gestaltet. Das erzwingt der Design-Check in `check.py` über den Block `design` in `content/config.json`:

| `design.status` | Bedeutung | Wirkung |
|---|---|---|
| `template` | unveränderte Vorlage (nur im Template-Repo) | im Kundenprojekt Hinweis: auf `offen` setzen |
| `offen` | Projekt angelegt, Design noch nicht individualisiert | Staging geht, **Produktions-Build bricht ab** |
| `individuell` | Design-Phase abgeschlossen | Prüfung: `concept` ausgefüllt, mindestens 5 von 8 `dimensions`, `signature` benannt, `style.css` oder `theme` weichen von der Vorlage ab |

Beim Projektstart (Einrichtung) setzt Claude `design.status` auf `offen`. Nach der Design-Phase trägt Claude ein: `concept` (Designkonzept in 2–4 Sätzen), `inspirations` (Quellen, siehe unten), `dimensions` (die tatsächlich angepassten Dimensionen) und `signature` (das eine Signatur-Element), dann `status: "individuell"`.

**Die acht Dimensionen** (mindestens fünf müssen sich deutlich von der Vorlage unterscheiden): `farbe` (Palette, Flächen, Verlauf) · `schrift` (eigene Schrift, Größenverhältnisse, Gewichte) · `formensprache` (Radius, Linien, Schatten, Rahmen) · `hero` (Aufbau der Kopfzone, Bildanteil, Typografie) · `raster` (Spalten, Abstände, Ausrichtung, Seitenbreite) · `bildstil` (Fotos, Illustration, Icons, Beschnitt) · `signatur` (ein wiedererkennbares Element) · `bewegung` (Übergänge, Scroll-Effekte, Mikro-Interaktionen).
Die Bausteine (Cases-Slider, Prozess, Preise, News, Karten …) sind **Rohbau**: Sie bekommen je Kunde eigene Proportionen, Kartenform, Nummerierung, Badge-Stil, Pfeil-Buttons usw. Dafür CSS in `style.css` umschreiben, Tokens im `theme` setzen oder Varianten (`variant`) wählen; bei Bedarf eigenen Renderer ergänzen.
Nach Änderungen am Template-CSS im Template-Repo: `python3 check.py --design-baseline` (Fingerabdruck der Vorlage erneuern).

## Design-Inspirationen einholen (immer, vor dem ersten Entwurf)
1. **Fragen** (zusammen, nicht einzeln): Welche 2–3 Websites gefallen dir/dem Kunden (auch aus fremden Branchen)? Was genau daran: Farbwelt, Typografie, Fotostil, Layout, Bewegung? Welche Seiten gefallen ausdrücklich nicht? Welche Adjektive sollen die Marke beschreiben (z. B. ruhig, mutig, handwerklich, technisch, warm)? Gibt es ein Logo, eine Markenfarbe, Bildmaterial?
2. **Quellen auswerten**: Vorbildseiten im Browser öffnen, Screenshots Desktop/mobil, Farben, Schriften und Abstände auslesen (nur lernen, **nichts kopieren**: keine Texte, Bilder, Schriften, Code oder erkennbare Layout-Klone). Aus mehreren Vorbildern kombinieren, damit etwas Eigenes entsteht.
3. **Zwei Richtungen** als Prototyp auf der Startseite zeigen, jeweils mit 1–2 Sätzen Begründung, eine empfehlen, Freigabe holen. Die Richtungen müssen sich in mindestens drei Dimensionen unterscheiden (z. B. Farbe, Hero, Formensprache), sonst sind es keine echten Alternativen.
4. **Bestehende Kundenseiten ansehen** (`~/Websites/*`, Referenzprojekt): Die neue Seite darf sich nicht wie ein früheres Projekt anfühlen. Vorher kurz vergleichen und bewusst abgrenzen (Farbwelt, Hero, Formensprache).
5. Ergebnis in `docs/BRIEFING.md` festhalten (Vorbilder, Auswertung, gewählte Richtung) und im `design`-Block der Config zusammenfassen.

## Variationsbausteine für verschiedene Charaktere (Ideen, nicht Pflicht)
- **Ruhig/seriös**: viel Weißraum, feine Linien statt Schatten, kleine Radien, Serif-Überschrift, zurückhaltende Bewegung.
- **Warm/handwerklich**: Erdtöne, große Fotos, weiche Radien, handschriftliches Detail, Karten mit Papier-Anmutung.
- **Technisch/modern**: dunkle Flächen, Monospace-Akzente, Raster sichtbar machen, Zahlen groß, schnelle Übergänge.
- **Mutig/kreativ**: große Typografie, asymmetrisches Raster, kräftige Flächenfarben, eckige oder stark runde Formen, auffälliger Hero.
Slider, Preiskarten und Prozess-Schritte lassen sich in jedem dieser Charaktere umdeuten (z. B. Prozess als Timeline mit Linie, als Karten oder als große Zahlen; Preise als Tabelle oder Karten; Slider als Vollbreiten-Zitate oder Bildergalerie).

## Vorgehen je Kunde
1. **Design-Briefing** (aus `briefing.md` bzw. Analyse in `nachbau.md`): Marke, Zielgruppe, Tonalität, 2–3 Vorbildseiten, No-Gos. Daraus ein Designkonzept in Worten: Charakter (z. B. ruhig/seriös, warm/handwerklich, technisch/modern), Farben, Schrift, Bildstil, Formensprache (Radius, Linien, Schatten), Raster/Layout-Prinzip.
2. **Zwei Richtungen als Prototyp** auf der Startseite zeigen (nicht nur beschreiben), eine empfehlen, Freigabe holen.
3. **Tokens zuerst**: Farben, Radius, Button-Radius, Schrift in `content/config.json` → `theme` (wird als `theme.css` ausgeliefert, überschreibt die CSS-Variablen). Eigene Schriften lokal in `static/assets/fonts/` ablegen, `@font-face` in `style.css` ergänzen, `--font` im theme setzen.
4. **Layout individuell**: Reihenfolge, Raster, Abstände und Komponenten pro Kunde anpassen. Wenn ein Baustein nicht passt, `style.css` für diese Sektion umschreiben oder einen neuen Renderer in `build.py` ergänzen (siehe `architektur.md`) statt die Inhalte zu verbiegen.
5. **Signatur-Element** pro Seite festlegen (ein wiedererkennbarer Effekt, nicht mehrere).
6. Immer prüfen: Kontrast, Mobil (390 px) und Desktop (1440 px), `prefers-reduced-motion`, kein horizontaler Überlauf.

## Erkenntnisse aus dem 24bit-Projekt (Beispiele, keine Vorgaben)

## Grundsätze (Beispiel 24bit)
- Typografie nach Apple-Stil: wenige Schriftstufen (`--fs-*`), überall gleich; Inter lokal; große Headlines, viel Weißraum. Mobile-first, `prefers-reduced-motion` beachten.
- Farbwelt aus der Marke ableiten (24bit: Akzentblau, Navy, helle Blauflächen). Verlauf sparsam: nur für Schlüsselwörter, nie für Fließtext (Kontrast, v. a. am rosa Ende).
- Ein wiedererkennbares „Signatur-Element“ pro Seite genügt (24bit: Hero-Wechselwörter, Verlaufswort, Textmarker). Nicht mehrere Effekte stapeln.
- Hero-CTA: nicht „Produkt anfragen“, bevor Besuchende das Angebot verstehen. Besser niedrigschwellig und nutzenorientiert, z. B. zweizeiliger Button „Digital-Check starten / Wo können Sie Zeit sparen?“ oder „Unverbindliches Erstgespräch buchen“.
- Fazit-/Callout-Kästen: ein vollständiger Satz als Überschrift, optional eine Zeile darunter; kein Satz, der in der Überschrift beginnt und im Fließtext endet.
- Listen nicht doppeln (Dopplungen wie zwei „Tools, die nicht miteinander sprechen“ entfernen); 4–5 Punkte pro Pain-Liste.

## Bausteine, die gut funktioniert haben (im 24bit-Referenzprojekt umgesetzt, im Template nur als neutrale Variante vorhanden)
- **Textmarker** `[[Wort]]`: halbtransparentes Markerband hinter dem Wort (untere Hälfte, leicht schräg), animiert per CSS-Keyframes; langsam (ca. 1,8 s), kurz halten, ausblenden, zweites Aufziehen, dann stehen bleiben. Reduced-motion: statisch.
- **Zweizeiliger Button** (`sub`-Feld): Aktion fett, Nutzen klein darunter.
- **Team-Kacheln**: weiße Karte, quadratisches Foto auf Panel-Hintergrund, Name + Rolle; Platzhalter-Silhouette, bis das Foto da ist. Fotos einheitlich: Schwarz-Weiß, gleiche Kopfgröße und -höhe (Augenlinie ca. 33–40 % der Bildhöhe), neutraler Business-Hintergrund. Freisteller mit unscharfem Hintergrund aus einem passenden Foto kombinieren.
- **Profil-Modal** pro Person: natives `<dialog>`, `showModal()`, Backdrop, Ein-/Ausblend-Animation, Kreuz-Icon + Esc + Klick daneben; Inhalte: großes Foto, Name, Titel, Kurzprofil, Rollen, Skills, Werdegang. Als Feature-Schalter (`team_profiles`), bis Inhalte fertig sind: nur Staging.
- **Sprach-Dropdown** mit runden Flaggen (inline SVG, `clip-path`), Footer/Burger-Menü mit Textkürzeln DE/EN.
- Externe Links: `target="_blank" rel="noopener noreferrer"`.

## Bilder
- Illustrationen als eigenes SVG bauen und per Chrome headless rendern: `chrome --headless --window-size=1000,1000 --screenshot=out.png file.html`, dann als JPG speichern (Pillow in einer venv im Scratchpad). Stil der Serie angleichen (Verlaufshintergrund, Navy/Blau/Grau).
- KI-generierte Bilder prüfen: Blindtext („Lorem ipsum“) und unpassende Motive aussortieren.
- Motiv muss zum Bereich passen (Beispiel: Smartphone/App = Digitalisierung; Balken mit Trendpfeil = Wachstum/Transformation).
- Share-Bild (`og-image.png`) aus HTML-Vorlage mit Chrome headless erzeugen.
