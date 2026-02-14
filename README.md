# LaGeSo Befundbericht Generator

Lokale Streamlit Web-App zur automatischen Erstellung strukturierter psychiatrischer/psychotherapeutischer Befundberichte nach dem LaGeSo-Standard (CU-Standard, Dr. med. Carsten Urbanek) aus unstrukturiertem klinischem Text.

## Features

- **Vollständige 12-Abschnitt-Struktur** nach CU-Standard (Vorstellung, Diagnosen, AMDP, Medikation, Verlauf, Sucht, Behandlungen, Psychosoziale Hilfen, Auswirkungen, Gehfähigkeit, Akteneinsicht, Abschluss)
- **20 AMDP-Kategorien** in exakter CU-Reihenfolge als Fließtext (Bewusstsein bis Psychopharm. Vorbehandlung)
- **Multi-Step LLM-Pipeline**: 4-Schritt-Verarbeitung (Extraktion, AMDP, Verlauf/Sucht, Auswirkungen)
- **ICD-10 Validierung**: Erkennung häufiger Fehler (F33.2 vs F33.3, F45.1 etc.)
- **Checkbox-Widgets** für strukturierte Felder (Psychosoziale Hilfen, Gehfähigkeit, Akteneinsicht)
- **Editierbar**: Jeder Berichtsabschnitt ist nach Generierung bearbeitbar
- **DOCX-Export**: Professionell formatierter Word-Export im CU-Standard
- **Qualitäts-Checkliste**: 9 automatische Prüfungen (AMDP Fließtext, BMI, Sprache, etc.)
- **100% lokal**: Keine Cloud, keine externe API - DSGVO-konform mit Ollama
- **Anforderungszeitraum**: 2 Jahre (seit Dezember 2024)

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
2. **Metadaten ausfüllen**: Patientendaten, Aktenzeichen, Vorstellungstermine eintragen
3. **Generieren**: "Bericht generieren" klicken - 4-Schritt-Pipeline läuft
4. **Prüfen & Bearbeiten**: Alle 12 Abschnitte rechts prüfen und bei Bedarf anpassen
5. **Checkboxen setzen**: Psychosoziale Hilfen, Gehfähigkeit, Akteneinsicht
6. **Qualitätsprüfung**: Sidebar-Checkliste beachten (AMDP, BMI, Sprache etc.)
7. **Exportieren**: Als DOCX herunterladen

## Berichtsstruktur (12 Abschnitte)

1. Vorstellung (Termine, Frequenz)
2. Diagnosen (ICD-10)
3. Psychopathologischer Befund (AMDP-System, 20 Kategorien als Fließtext)
4. Aktuelle Medikation (nur Psychopharmaka)
5. Verlauf der Erkrankung
6. Bei Suchterkrankung (6-Punkte-Anamnese)
7. Sonstige Behandlungen (nur psychiatrisch/psychotherapeutisch)
8. Psychosoziale Hilfen (Betreuung, Pflege, AU, Berentung)
9. Krankheitsbedingte Auswirkungen (Alltag, Beruf, Sozial)
10. Einschränkungen der Gehfähigkeit
11. Akteneinsicht
12. Abschluss

## Dateistruktur

```
lageso_agent/
├── app.py              # Streamlit Hauptanwendung (12-Abschnitt-UI)
├── llm_client.py       # Ollama-Client (generate, extract_json, test_connection)
├── extractor.py        # 4-Schritt-LLM-Pipeline
├── report_builder.py   # 12-Abschnitt-Berichts-Zusammenstellung
├── docx_export.py      # Word-Export im CU-Standard
├── prompts.py          # Prompt-Templates und AMDP-Kategorien
├── requirements.txt    # Python-Abhängigkeiten
└── start.sh            # Startskript
```

## Konfiguration

Alle Einstellungen sind in der Sidebar der App anpassbar:

- **Ollama-Modell**: Standard `llama3.1:8b`, beliebig konfigurierbar
- **Ollama-URL**: Standard `http://localhost:11434`
- **Arzt-Stammdaten**: Name, Fachgebiet, Adresse, Kontakt
