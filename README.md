# Chronische Wunden CME Plattform

Diese statische Web-Anwendung bietet eine komplette ärztliche Fortbildung zur Versorgung chronischer Wunden. Die Inhalte beinhalten ein interaktives Versorgungstool, ein herunterladbares Skript sowie eine CME-Prüfung mit Bestehensnachweis.

## Inhalte
- Zugangsschutz mit Login und simulierter Zahlungsstrecke (Pflicht vor Nutzung).
- Modulbasiertes Curriculum mit klaren Lernzielen.
- Interaktives Versorgungstool zur Entscheidungsunterstützung über fünf Versorgungsschritte.
- Downloadbares Fortbildungsskript als PDF.
- Abschließende CME-Prüfung mit Ergebnisfeedback.

## Entwicklung
Die Seite ist in Vanilla HTML, CSS und JavaScript umgesetzt und benötigt keinen Build-Prozess.

### Lokale Nutzung
```bash
# Entwicklungsserver starten
python3 -m http.server 8000
```

Anschließend im Browser `http://localhost:8000` öffnen.

### Struktur
- `index.html` – Hauptseite mit allen Fortbildungsabschnitten
- `styles.css` – Modernes Styling inklusive Dark-Sections und Responsive Layout
- `app.js` – Interaktive Logik für Zugangsschutz, Versorgungstool und CME-Prüfung
- `assets/skript-chronische-wunden.pdf` – Fortbildungsskript zum Download
