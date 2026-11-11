# Geführtes Briefing für den Neuaufbau (Weiche 1)

Ziel: aus Gesprächen eine freigegebene Struktur, Texte und ein Designkonzept machen. **In Blöcken von höchstens 3–4 Fragen**, nach jedem Block kurz zusammenfassen („Habe ich das richtig verstanden?“), Antworten sofort in `docs/BRIEFING.md` im Projekt festhalten. Wo der Kunde unsicher ist, eigene Vorschläge machen (Empfehlung + Begründung) statt offene Fragen zu stapeln.

## Block 1 – Ziel und Zielgruppe
Was soll die Website erreichen (Anfragen, Termine, Bewerbungen, Image, Verkauf)? Wer sind die 2–3 wichtigsten Zielgruppen, was wollen sie wissen oder lösen? Was ist der gewünschte nächste Schritt für Besuchende (Hauptaktion)?
## Block 2 – Angebot und Positionierung
Leistungen/Produkte (max. 3–5 Hauptbereiche), Alleinstellung, Belege (Zahlen, Referenzen mit Freigabe, Zertifikate), Preise nennen ja/nein, Claim oder Slogan, Tonalität (Sie/du, geschlechtsneutral, locker/seriös), Wörter, die vermieden werden.
## Block 3 – Marke und Design
Logo (SVG/PNG), Farben, Schrift, Bildstil und vorhandene Fotos. **Design-Inspirationen einholen** (Pflicht, Ablauf in `design.md`): 2–3 Vorbildseiten („Was gefällt daran: Farbe, Typografie, Fotostil, Layout, Bewegung?“), No-Gos, drei bis fünf Adjektive für die Marke. Danach Vorbilder auswerten und zwei Richtungen als Prototyp zeigen. Daraus das Designkonzept (`design`-Block in `content/config.json`; ohne ihn kein Produktions-Build).
## Block 4 – Struktur und Funktionen
Seitenliste und Menü (Vorschlag machen), Sprachen (welche, Standardsprache, Slug-Regeln), Formular (Themen, Pflichtfelder, Empfänger), Terminbuchung, Social-Links, Team/Personen, Referenzen/Logos, Referenz-Cases (Slider), Prozess-Schritte, Preise/Pläne, Blog/News (Bausteine sind im Template als Rohbau vorhanden: `cases`, `process`, `pricing`, `news` + `posts/`).
## Block 5 – Rechtliches und Technik
Impressum-Daten, Datenschutz (Verantwortliche, Datenschutzbeauftragte, Hoster, eingesetzte Dienste), Tracking geplant? (dann Consent-Lösung), Domain/Hosting/Mail (siehe `hosting-deployment.md`), Weiterleitungen alter URLs, Wer pflegt Inhalte später, Live-Termin.

## Ergebnisse (vor dem Bauen freigeben lassen)
1. **Sitemap** (Seiten + Menüstruktur) mit Seitenzweck. 2. **Seitengerüste**: je Seite die Sektionsfolge (hero, text, features, grid, offers, faq, about/Team, logos, cta, contact …) und Kernbotschaft. 3. **Designkonzept** mit zwei Richtungen und Empfehlung. 4. **Textstrategie**: wer liefert Texte (Kunde, Content-Chat, Claude-Entwurf), Platzhalter klar markieren. 5. **Zeitplan** bis Staging und Live.

## Texte erarbeiten
Entwürfe nach der Struktur schreiben, nie Fakten erfinden. Je Seite Titel (50–60 Zeichen mit Suchbegriff und Marke/Ort) und Beschreibung (140–160 Zeichen). Alle Sprachen parallel. Glossar (`content/glossary.json`) mit Fachbegriffen und verbotenen Schreibweisen füllen.
