# Voice Notes - iOS App

Eine moderne iOS-App für Notizen und Aufgaben mit Sprachsteuerung und Widgets.

## Features

### Notizen & Aufgaben
- Erstelle Notizen mit Titel, Inhalt und Tags
- Markiere Notizen als Aufgaben (Todos)
- Kategorisiere nach: Persönlich, Arbeit, Einkaufen, Gesundheit, Ideen, Sonstiges
- Prioritäten: Niedrig, Normal, Hoch, Dringend
- Notizen anpinnen für schnellen Zugriff
- Suche und Filter

### Sprachsteuerung
- Erstelle Notizen per Spracheingabe
- Deutsche Spracherkennung (weitere Sprachen verfügbar)
- Echtzeit-Transkription
- Audio-Level-Anzeige während der Aufnahme

### Widgets
- **Small Widget**: Schnelle Übersicht der Notizanzahl
- **Medium Widget**: Zeigt die neuesten 3 Notizen
- **Large Widget**: Vollständige Übersicht mit Statistiken
- **Lock Screen Widgets**: Circular, Rectangular, Inline
- **Todo Widget**: Zeigt offene Aufgaben

### Siri Shortcuts
- "Neue Notiz" - Erstellt eine neue Notiz
- "Neue Aufgabe" - Erstellt eine neue Aufgabe
- "Zeige meine Notizen" - Öffnet die Notizliste
- "Sprachnotiz" - Startet die Spracheingabe

## Installation

1. Öffne das Projekt in Xcode 15 oder neuer
2. Wähle dein Entwickler-Team unter Signing & Capabilities
3. Konfiguriere die App Group für Widget-Datenaustausch:
   - App: `group.com.voicenotes.app`
   - Widget: `group.com.voicenotes.app`
4. Baue und installiere die App auf deinem iPhone

## Systemanforderungen

- iOS 17.0 oder neuer
- iPhone oder iPad
- Xcode 15.0 oder neuer

## Projektstruktur

```
VoiceNotes/
├── VoiceNotesApp.swift          # App Entry Point
├── ContentView.swift            # Haupt-TabView
├── Info.plist                   # App-Konfiguration
├── Models/
│   └── NoteModel.swift          # Datenmodelle
├── Views/
│   ├── NoteListView.swift       # Notizliste
│   ├── NoteDetailView.swift     # Detailansicht
│   ├── NoteEditorView.swift     # Editor
│   ├── NoteCardView.swift       # Karten-Komponenten
│   └── VoiceInputView.swift     # Spracheingabe-UI
├── ViewModels/
│   └── NotesViewModel.swift     # Business Logic
├── Services/
│   ├── DataService.swift        # Datenpersistenz
│   ├── SpeechRecognitionService.swift  # Spracherkennung
│   └── SiriShortcutsManager.swift      # Siri Integration
├── Extensions/
│   └── Extensions.swift         # Swift Extensions
└── Assets.xcassets/             # App Icons & Farben

VoiceNotesWidget/
├── VoiceNotesWidget.swift       # Widget-Implementierung
├── VoiceNotesWidgetBundle.swift # Widget-Bundle
└── Info.plist                   # Widget-Konfiguration
```

## Berechtigungen

Die App benötigt folgende Berechtigungen:
- **Mikrofon**: Für Sprachaufnahmen
- **Spracherkennung**: Für die Umwandlung von Sprache in Text
- **Siri**: Für Siri Shortcuts

## Datenspeicherung

Notizen werden lokal in UserDefaults gespeichert und über App Groups mit dem Widget geteilt.

## Anpassung

### Neue Kategorie hinzufügen
Füge einen neuen Fall zu `Category` in `NoteModel.swift` hinzu:

```swift
enum Category: String, Codable, CaseIterable {
    case personal = "Persönlich"
    case work = "Arbeit"
    // Neue Kategorie:
    case fitness = "Fitness"

    var icon: String {
        switch self {
        // ...
        case .fitness: return "figure.run"
        }
    }
}
```

### App Icon hinzufügen
Füge ein 1024x1024 PNG zu `Assets.xcassets/AppIcon.appiconset/` hinzu.

## Lizenz

Dieses Projekt ist für persönliche Nutzung bestimmt.

## Changelog

### Version 1.0.0
- Erste Version
- Notizen & Aufgaben
- Sprachsteuerung
- Widgets
- Siri Shortcuts
