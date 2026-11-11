# Nachbau einer bestehenden Website (Weiche 2)

Eingabe vom Kunden: **URL** der bestehenden Seite plus die wichtigsten Assets (Logo als SVG/PNG, Farben/CI, Schriften, Bilder, Styleguide falls vorhanden). Ziel: dieselben Inhalte und dieselbe Wiedererkennbarkeit auf dem neuen Stack, mit verbesserter Technik (schnell, sicher, SEO/GEO, Editor).

## 1. Aufnahme (nur lesen, nichts übernehmen ohne Rechteklärung)
1. **Rechte und Umfang klären**: Gehört die Seite dem Kunden? Welche Texte/Bilder/Schriften dürfen übernommen werden (Lizenzen prüfen, Stockfotos neu lizenzieren)? Was bleibt, was fällt weg?
2. **Seiten entdecken**: `sitemap.xml`, `robots.txt`, Menü, interne Links. Liste aller URLs mit Titel, Zweck, Traffic-Bedeutung (falls der Kunde Zahlen hat).
3. **Struktur je Seite erfassen** (Browser öffnen, Text lesen, Screenshots Desktop/mobil): Sektionsfolge, Überschriften, Texte, Bilder, Formulare, Verlinkungen, eingebettete Dienste (Karten, Videos, Tracking, Chat, Shop: jeweils Datenschutz/Consent und Machbarkeit prüfen).
4. **Design auslesen**: Farben (Hex), Schriftfamilie/-größen, Abstände, Button-/Karten-Stil per Browser-Inspektion (computed styles), Logo-Varianten. Als Tokens notieren (`theme` in `content/config.json`).
5. **SEO-Bestand**: Titel/Beschreibungen, H1, Slugs, bestehende Rankings/Backlinks (URLs, die erhalten oder weitergeleitet werden müssen), Google Business Profil, Search-Console-Zugang falls vorhanden.
6. **Technikbestand**: CMS/Hoster, Formular-Ziel, Mailadressen, Domain/DNS, Zertifikate.

Alles in `docs/NACHBAU.md` festhalten (URL-Liste, Seitenmapping, Tokens, offene Fragen).

## 2. Plan
- **Mapping**: alte Seite → neue Seiten-ID/Sektionen (Template-Sektionstypen aus `architektur.md`); wo kein Baustein passt, Renderer ergänzen.
- **Verbesserungen vorschlagen** (nicht stillschweigend ändern): Struktur, Textqualität, Mehrsprachigkeit, CTAs, GEO-Aussagen, Barrierefreiheit.
- **Weiterleitungen**: jede alte URL, die sich ändert, in `redirects` (config) eintragen (301).
- Vom Kunden freigeben lassen, bevor gebaut wird.

## 3. Umsetzen
Texte 1:1 übernehmen oder behutsam überarbeiten (mit Freigabe) und in `content/<lang>/` eintragen; Assets lokal ablegen (`static/assets/img/`, Schriften nur mit Lizenz lokal). Design aus den Tokens aufbauen und am Original messen: Nebeneinander-Screenshots (alt/neu, Desktop/mobil). Eigenständigkeit: gleiche CI heißt nicht gleiche Technik oder Layout-Fehler übernehmen; bei Bedarf Layout modernisieren (siehe `design.md`).

## 4. Abnahme und Umzug
Staging mit dem Kunden prüfen (Inhaltsvergleich: nichts vergessen? Links, Formulare, Mails). Redirects testen (`curl -I https://alt…/pfad`). Erst dann Produktion und Domain-Umzug (`hosting-deployment.md`), Search Console/Bing, Sitemap neu einreichen, 404-Meldungen die ersten Wochen beobachten.
