# Nachbau momente.yoga: Analyse und Seitenplan (Stand 10.11.2026)

**Quellen (nur gelesen, nie ausgeführt; der FTP-Abzug war infiziert):**
- Dateien: `~/Websites/Website-Cleanup/momente.yoga/files/` (Joomla 4.4.14, SP Page Builder 6.8)
- Datenbank (bereinigt, Export 10.11.2026): `Synology …/Momente Macher GbR/Yoga Momente/dbs198627.sql`, Präfix `n7go8_`
- Nicht verwenden: `db607568396.sql` (WordPress, momente-macher.de), `.jpa`-Backups, `restore.php`, `logs/`, `configuration.php`, Plugins/Zusatztools (jfixplugin, htprotect, jantivirus, jmwascanner)
- Extrahierte Seitentexte: `docs/nachbau-quellen/<id>_<titel>.txt`

**Rahmen:** Kunde Yoga Momente (Susanne Müller, Coburg) / Momente Macher GbR · Sprachen DE + EN · Hosting IONOS, Staging-Subdomain · Rechte: laut Auftraggeber beim Kunden (Stockfotos/Demo-Bilder einzeln prüfen).

## Aktives Design im Altsystem
Aktiv ist Helix Ultimate Style „yoga momente (V2)“ (id 14, Standard). Das Template `yamas` ist ein älterer Style (id 11, nicht Standard). Logo: `images/Yoga/logo-titel_transparent.png` (Höhe 88px), weitere: `Yoga_Logo_Gold.png`, `yoga-logo-rund.png`. Farben/Schriften des Live-Designs müssen noch aus Template-CSS und Seiten-JSON gemessen werden (Joomla-Preset allein ist Platzhalter: Akzent `#e74c3c`/`#0345BF`). Absender: `flow@momente.yoga`, Tel. +49 (0)9561 29831.

## Seitenmapping mit neuen URL-Handles (freigegeben 10.11.2026)
Schema: sprechende Kleinbuchstaben-Pfade, Umlaute ausgeschrieben, ohne `index.php`, pro Sprache lokalisiert, Orts-Keyword „coburg“ nur dort, wo gesucht wird. Alte Pfade → 301 (`redirects` in der config).

| Alt-ID | Titel | Alte URL | Neu DE | Neu EN |
|---|---|---|---|---|
| 5 | Home | `/` | `/` | `/en/` |
| 6 | Über mich | `/about` | `/ueber-mich` | `/en/about-me` |
| 7 | Kurse | `/yoga/classes` | `/yoga-kurse-coburg` | `/en/yoga-classes-coburg` |
| 12 | Preise & YogaCard | `/momente/card` | `/preise` | `/en/prices` |
| 15 | Stundenplan | `/momente/schedule` | `/stundenplan` | `/en/schedule` |
| 13 | Yoga Bewegungen | `/yoga/poses` | `/yoga-uebungen` | `/en/yoga-poses` |
| 70 | Yoga 4.0 | `/yoga/yoga-4-0` | `/online-yoga` | `/en/online-yoga` |
| 75 | Ölgeflüster | `/oelgefluester` | `/aetherische-oele` | `/en/essential-oils` |
| 9 | Events | `/events` | `/events` | `/en/events` |
| 77 | Retreat Rottal Nov. 2026 | `/events/yoga-retreats` | `/events/yoga-retreat-rottal` | `/en/events/yoga-retreat-rottal` |
| 16 | Kontakt | `/contact-us` | `/kontakt` | `/en/contact` |
| 68 | Impressum | `/impressum` | `/impressum` | `/en/imprint` |
| 57 | Datenschutz | `/privacy-policy` | `/datenschutz` | `/en/privacy-policy` |
| 58 | AGB | `/terms-conditions` | `/agb` | `/en/terms-and-conditions` |

(Das Sprachpräfix und die Slug-Lokalisierung folgen der Template-Logik; vor dem Bauen gegen `build.py` prüfen.)
Footer: Modul 67 (+ Adresse 55, Kontakt 56) → globaler Footer. Menüs „Momente“ und „Yoga“ waren nur Ordner.

## Wichtiger Fund: zwei Inhaltsfelder
SP Page Builder speichert neuere Seiten im Feld `content`, ältere in `text`. Aktuell gültig ist `content`, sofern gefüllt (Home, Events, Yoga 4.0, Ölgeflüster, Retreats). Die Extrakte in `docs/nachbau-quellen/` verwenden bereits `content`.

## Preise (aus Seite 12, Stand Altseite)
- Yin Yoga & Hatha Yoga: 10 × 60 Min. 3–4 Teiln. 150 €/Pers., ab 5 Teiln. 135 €/Pers.; 10 × 90 Min. 3–4 Teiln. 225 €, ab 5 Teiln. 200 €
- Early Morning Yoga: 10 × 60 Min., 3–4 Teiln. 150 €/Pers.
- Hormon Yoga: 5 × 90 Min., 3 Teiln. 200 €, 4 Teiln. 150 €/Pers., inkl. Hormon-Booklet
- Personal Yoga: 60 Min. 75 €, 90 Min. 100 €
- Schnupperstunde: 1 Probestunde à 60 Min., 60 € (Anmeldung per Tel. +49 (0)9561 29831 oder flow@momente.yoga)
- YogaCard: Stempelkarte, gibt es bei der Anmeldung
- Fasten-Workshop (Events): ab 5 Pers. 140 €, ab 10 Pers. 90 € p. P.
- Retreat Rottal 13.–15.11.2026: 295 €/Pers. (Übernachtung/Verpflegung vor Ort), max. 10 Pers., Anmeldung extern `retreat-anmeldung.momente.yoga`
Hinweis: Die Preise sind von 2021; vor Livegang vom Kunden bestätigen lassen. Corona-Hinweis („Aktuelles“) entfällt.

## Entscheidungen (10.11.2026)
- Seitenmapping und neue URL-Handles freigegeben.
- Das **Retreat Rottal (13.–15.11.2026)** wird als Landingpage übernommen und auf Conversion optimiert. Die Anmeldung läuft weiter über die externe Anmeldeseite.
- Das **Retreat Allgäu (30.10.–01.11.2026)** und alle älteren Retreats werden nicht übernommen (301 auf die Events-Übersicht).
- Preise werden aus der Altseite übernommen und neu aufgebaut.
- Die Startseite wird aktualisiert (veraltete Hinweise und Template-Reste entfallen).
- Bildrechte-Hinweise werden für alle weiterverwendeten Bilder übernommen.

## Offen / zu klären (nicht stillschweigend entscheiden)
- **Retreat Rottal:** Der Anmeldeschluss in der Altseite war der 31.07.2026, der Termin ist am 13.11.2026. Bitte Kundin fragen: Gibt es noch freie Plätze, soll der Anmeldeschluss entfallen oder wird die Seite nach dem Termin archiviert?
- **Preise:** stammen teils aus 2021. Bitte aktuelle Preise bestätigen lassen.
- **Seite 10** „Event Yoga & Kunst“ (unveröffentlicht, aber als verstecktes Menü live): behalten?
- Home enthält Template-Reste („Item number 1“, „Introducing IMAGE LAYOUTS ADDON“, Flyer-Platzhalter) und teils veraltete Hinweise („3 Plätze frei“, Corona-Hinweis, Link auf Retreat 2022) → aktualisieren oder streichen.
- Kontaktformular/Buchung: Altseite nutzt Joomla-Funktionen; Template-Formular verwenden (Mail-Ziel `flow@momente.yoga` bestätigen).
- Bildrechte: Unsplash-Bilder (u. a. `zoltan-tasi`, `bekir-donmez`, `lesly-juarez`, `jd-mason`) sind frei nutzbar, aber Quellenhinweis prüfen; Template-Demobilder (`images/Demo`, `sampledata`) nicht übernehmen.
- Weiterleitungen: alle alten Pfade (`/yoga/classes`, `/momente/card` …) per 301 auf neue Seiten.

## Aussortiert (Template-Demo, kein Kundeninhalt)
Retreats Allgäu (alle Jahre) und Spitzingsee; 10 Demo-Artikel (angelegt 28.10.2019 durch Demo-Import: Trump/Science-Texte), SPPB-Blogbeiträge 19–29, „Nam Fest 2019“ 31–37, 38–45, unveröffentlichte Gallery/Media (11, 18), Menüs `company`/`hidden-menu` (Demo), Login/Registration/404.
