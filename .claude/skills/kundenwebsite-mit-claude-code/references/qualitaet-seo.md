# Qualität, SEO/GEO, Rechtliches (vor jedem Live-Gang)

## Technik-SEO
- Je Seite `title` (ca. 50–60 Zeichen, Suchbegriff + Marke/Ort) und `description` (ca. 140–160); `check.py` meldet Längen als Hinweis.
- Genau ein H1, saubere Überschriftenhierarchie, Alt-Texte, aussagekräftige Linktexte, interne Verlinkung.
- Produktions-Build erzeugt `sitemap.xml` (mit hreflang), `robots.txt` (inkl. KI-Crawler-Regeln), `llms.txt`, kanonische URLs, `hreflang` + `x-default`.
- Strukturierte Daten (JSON-LD): Organization/LocalBusiness, Person, WebSite, WebPage/Service je Seite; stimmen mit sichtbaren Inhalten überein.
- Open-Graph/Share-Bild, Favicon, Apple-Touch-Icon.
- Staging immer `noindex` (Meta + robots-Disallow); Prüfung im Workflow, dass Produktion kein `noindex` enthält.
- Search Console und Bing Webmaster Tools einrichten (Meta-Tag/DNS), Sitemap einreichen; Google Business Profil bei lokalem Geschäft.

## GEO (Auffindbarkeit in KI-Suchen)
Klare, zitierfähige Aussagen (Wer, was, für wen, wo), Fakten und Zahlen mit Belegen, FAQ-/Frageformulierungen, konsistente Namen und Begriffe (Glossar), `llms.txt`, KI-Crawler in `robots.txt` bewusst erlauben/sperren.

## Barrierefreiheit und Performance
Kontrast (Verlauf nur für große Schrift), Fokus-Zustände, Tastatur (Menü, Dialoge: Esc, Fokus zurück), `aria`-Labels, `prefers-reduced-motion`, ausreichende Klickflächen. Bilder mit Breite/Höhe und `loading="lazy"`; Versions-Query an CSS/JS für langes Caching; keine externen Ressourcen.

## Rechtliches
Impressum, Datenschutz (Formular, Hosting, Server-Logs, ggf. Analytics), Einwilligung im Formular, geschlechtsneutrale Sprache nach Kundenwunsch. Cookie-Consent nur nötig, wenn Tracking, Karten-Embeds, Videos oder Tag-Manager dazukommen (Karte als Bild-Link statt Embed). Rechtstexte vom Kunden/Juristen prüfen lassen; Claude entwirft nur.

## Review-Reihenfolge
1. Design-Review (Best Practices, Vorbildseiten, Barrierefreiheit) 2. Content-Review (Copywriting, GEO) 3. SEO-Basis 4. Sicherheit (`sicherheit.md`) 5. Formular-Test auf Staging 6. Mobil/Desktop-Überlauf 7. Live.
