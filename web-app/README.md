# Voice Notes - Progressive Web App

Eine moderne Web-App für Notizen und Aufgaben mit Sprachsteuerung. Funktioniert auf jedem Gerät - auch offline!

## Auf dem iPhone installieren

### Schritt 1: Web-App hosten

Die App muss auf einem Webserver laufen. Kostenlose Optionen:

**Option A: GitHub Pages (empfohlen)**
1. Forke dieses Repository
2. Gehe zu Repository Settings → Pages
3. Wähle "Deploy from branch" → main → /web-app
4. Warte 1-2 Minuten, dann ist die App unter `https://[username].github.io/ADHS-Chatbot/web-app/` erreichbar

**Option B: Netlify**
1. Gehe zu [netlify.com](https://netlify.com)
2. Drag & Drop den `web-app` Ordner
3. Fertig! Du bekommst eine URL

**Option C: Lokal testen**
```bash
cd web-app
python3 -m http.server 8000
# Öffne http://localhost:8000
```

### Schritt 2: Icons generieren (optional)

1. Öffne `icons/generate-icons.html` im Browser
2. Klicke bei jeder Größe auf "Download"
3. Speichere die PNGs im `icons/` Ordner

### Schritt 3: Auf iPhone installieren

1. Öffne Safari auf deinem iPhone
2. Gehe zur URL deiner Web-App
3. Tippe auf das **Teilen-Symbol** (Quadrat mit Pfeil nach oben)
4. Scrolle nach unten und tippe auf **"Zum Home-Bildschirm"**
5. Gib einen Namen ein und tippe auf **"Hinzufügen"**

Die App erscheint jetzt als Icon auf deinem Home-Bildschirm!

## Features

### Notizen & Aufgaben
- Erstellen, bearbeiten, löschen
- Kategorien: Persönlich, Arbeit, Einkaufen, Gesundheit, Ideen, Sonstiges
- Prioritäten: Niedrig, Normal, Hoch, Dringend
- Tags für bessere Organisation
- Notizen anpinnen
- Aufgaben abhaken

### Sprachsteuerung
- Tippe auf das Mikrofon-Symbol
- Sprich deine Notiz
- Speichere als Notiz oder Aufgabe

### Offline-Funktionalität
- App funktioniert auch ohne Internet
- Daten werden lokal gespeichert

## Browser-Kompatibilität

| Browser | Unterstützt | Spracheingabe |
|---------|-------------|---------------|
| Safari (iOS) | ✅ | ✅ |
| Chrome (Android) | ✅ | ✅ |
| Chrome (Desktop) | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Edge | ✅ | ✅ |

## Datenschutz

- Alle Daten bleiben auf deinem Gerät
- Keine Server-Verbindung nötig
- Keine Tracking oder Analytics

## Technologie

- HTML5, CSS3, JavaScript (Vanilla)
- Progressive Web App (PWA)
- Web Speech API für Spracherkennung
- Service Worker für Offline-Support
- LocalStorage für Datenpersistenz

## Entwicklung

```bash
# Lokaler Server
cd web-app
python3 -m http.server 8000

# Oder mit Node.js
npx serve .
```

## Lizenz

MIT License - Frei verwendbar
