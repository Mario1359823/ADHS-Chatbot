# LaGeSo Befundbericht Generator

Lokale Streamlit Web-App zur automatischen Erstellung strukturierter psychiatrischer/psychotherapeutischer Befundberichte nach dem LaGeSo-Standard (CU-Standard) aus unstrukturiertem klinischem Text.

## Features

- **Automatische Textextraktion**: Extrahiert Diagnosen, Befunde, Medikation und Anamnese aus Freitext
- **AMDP-System**: Alle 20 psychopathologischen Kategorien in korrekter Reihenfolge
- **Multi-Step LLM-Pipeline**: 4-Schritt-Verarbeitung (Extraktion → AMDP → Anamnese → Beurteilung)
- **Editierbar**: Jeder Berichtsabschnitt ist nach Generierung bearbeitbar
- **DOCX-Export**: Professionell formatierter Word-Export im CU-Standard
- **100% lokal**: Keine Cloud, keine externe API – DSGVO-konform mit Ollama
- **Qualitätsprüfung**: Automatische Checkliste zur Vollständigkeit

## Voraussetzungen

- Python 3.9+
- [Ollama](https://ollama.ai) installiert und gestartet
- Ein LLM-Modell (Standard: `llama3.1:8b`)

## Installation

```bash
# Ollama installieren (falls noch nicht vorhanden)
# https://ollama.ai

# Modell herunterladen
ollama pull llama3.1:8b

# In das Projektverzeichnis wechseln
cd lageso_agent

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Starten

```bash
cd lageso_agent
./start.sh
```

Oder manuell:

```bash
cd lageso_agent
streamlit run app.py
```

Die App öffnet sich unter `http://localhost:8501`.

## Verwendung

1. **Text einfügen**: Klinischen Freitext (Arztnotizen, Befunde, Arztbriefe) links einfügen
2. **Metadaten ausfüllen**: Patientendaten, Aktenzeichen, Termine eintragen
3. **Generieren**: "Bericht generieren" klicken
4. **Prüfen & Bearbeiten**: Jeden Abschnitt rechts prüfen und bei Bedarf anpassen
5. **Exportieren**: Als DOCX herunterladen

## Dateistruktur

```
lageso_agent/
├── app.py              # Streamlit Hauptanwendung
├── llm_client.py       # Ollama-Client
├── extractor.py        # Multi-Step Extraktion
├── report_builder.py   # Berichts-Zusammenstellung
├── docx_export.py      # Word-Export
├── prompts.py          # Prompt-Templates
├── requirements.txt    # Python-Abhängigkeiten
└── start.sh            # Startskript
```

## Konfiguration

Alle Einstellungen sind in der Sidebar der App anpassbar:

- **Ollama-Modell**: Standard `llama3.1:8b`, beliebig konfigurierbar
- **Ollama-URL**: Standard `http://localhost:11434`
- **Arzt-Stammdaten**: Name, Fachgebiet, Adresse, Kontakt
