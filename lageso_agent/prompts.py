"""
Prompt-Templates für den LaGeSo-Befundbericht-Generator.
Alle Prompts als Konstanten – zentrale Verwaltung.
"""

SYSTEM_PROMPT = """Du bist ein medizinischer Dokumentationsassistent für psychiatrische Befundberichte nach dem Standard von Dr. med. Carsten Urbanek (CU-Standard).

REGELN:
- Schreibe IMMER auf Deutsch in medizinischer Fachsprache
- Fließtext, NIEMALS Aufzählungszeichen oder Markdown im Berichtstext
- AMDP-Befund: Alle 20 Kategorien in exakter Reihenfolge (Bewusstsein → Orientierung → Aufmerksamkeit → Gedächtnis → Formales Denken → Befürchtungen → Wahn → Sinnestäuschungen → Ich-Störungen → Zwänge → Phobien → Affektivität → Antrieb → Psychomotorik → Circadiane Rhythmik → Schlaf → Appetit → Gewicht → Suizidalität → Eigen-/Fremdgefährdung)
- Beginne den AMDP-Befund IMMER mit "Pat."
- ICD-10 Codes: Immer vollständig mit Untergruppe (z.B. F33.2, nicht nur F33)
- Medikation: NUR Psychopharmaka, KEINE somatische Medikation
- Medikamente in GROSSBUCHSTABEN
- Dosierungsschema: Format "X-X-X-X" (morgens-mittags-abends-nachts)
- Keine Spekulationen – nur was aus dem Quelltext hervorgeht
- Fehlende Informationen als "nicht erhoben" / "nicht beurteilbar" kennzeichnen"""

EXTRACTION_PROMPT = """Extrahiere aus dem folgenden klinischen Text alle relevanten Informationen und gib sie als JSON zurück.

Antworte NUR mit dem JSON-Objekt, KEIN weiterer Text davor oder danach.

Erwartetes Format:
{{
  "diagnosen": [{{"icd": "...", "text": "..."}}],
  "befund": {{
    "bewusstsein": "...",
    "orientierung": "...",
    "aufmerksamkeit": "...",
    "gedaechtnis": "...",
    "formales_denken": "...",
    "befuerchtungen": "...",
    "wahn": "...",
    "sinnestaueschungen": "...",
    "ich_stoerungen": "...",
    "zwang": "...",
    "phobie": "...",
    "affektivitaet": "...",
    "antrieb": "...",
    "psychomotorik": "...",
    "circadiane_rhythmik": "...",
    "schlaf": "...",
    "appetit": "...",
    "gewicht_bmi": "...",
    "suizidalitaet": "...",
    "eigen_fremdgefaehrdung": "..."
  }},
  "medikation": [{{"name": "...", "dosis": "...", "schema": "..."}}],
  "anamnese_stichpunkte": ["..."],
  "beurteilung_stichpunkte": ["..."]
}}

Wenn eine Information nicht im Text vorkommt, setze den Wert auf "nicht erhoben".
NUR psychopharmakologische Medikation extrahieren, keine somatische.
ICD-10 Codes immer vollständig mit Untergruppe angeben (z.B. F33.2, nicht nur F33).

KLINISCHER TEXT:
{patient_text}"""

AMDP_PROMPT = """Erstelle aus den folgenden AMDP-Befunddaten einen medizinischen Fließtext für einen psychiatrischen Befundbericht.

REGELN:
- Alle 20 AMDP-Kategorien müssen in exakt dieser Reihenfolge vorkommen:
  1. Bewusstsein, 2. Orientierung, 3. Aufmerksamkeit, 4. Gedächtnis,
  5. Formales Denken, 6. Befürchtungen, 7. Wahn, 8. Sinnestäuschungen,
  9. Ich-Störungen, 10. Zwänge, 11. Phobien, 12. Affektivität,
  13. Antrieb, 14. Psychomotorik, 15. Circadiane Rhythmik, 16. Schlaf,
  17. Appetit, 18. Gewicht/BMI, 19. Suizidalität, 20. Eigen-/Fremdgefährdung
- Beginne IMMER mit "Pat."
- Fließtext, KEINE Aufzählungszeichen, KEIN Markdown
- Medizinische Fachsprache, knapp und präzise
- Antworte NUR mit dem Fließtext, kein weiterer Text

AMDP-BEFUNDDATEN:
{befund_json}"""

ANAMNESE_PROMPT = """Erstelle aus den folgenden Stichpunkten einen Anamnesetext für einen LaGeSo-Befundbericht.

REGELN:
- Fließtext, sachlich, medizinisch-fachsprachlich
- KEINE Aufzählungszeichen, KEIN Markdown
- Zusammenhängender, logisch strukturierter Text
- Beginne NICHT mit einer Überschrift
- Antworte NUR mit dem Fließtext, kein weiterer Text

STICHPUNKTE:
{stichpunkte}"""

BEURTEILUNG_PROMPT = """Erstelle eine sozialmedizinische Beurteilung für einen LaGeSo-Befundbericht.

REGELN:
- Sachlich, fachsprachlich, Fließtext
- KEINE Aufzählungszeichen, KEIN Markdown
- Auf Basis der Diagnosen und Befunde
- Beginne NICHT mit einer Überschrift
- Beziehe dich auf die Auswirkungen der Erkrankung auf die Lebensführung und Teilhabe
- Antworte NUR mit dem Fließtext, kein weiterer Text

DIAGNOSEN:
{diagnosen}

BEFUND-ZUSAMMENFASSUNG:
{befund_zusammenfassung}

ANAMNESE-ZUSAMMENFASSUNG:
{anamnese_zusammenfassung}"""

# AMDP-Kategorien in korrekter Reihenfolge (für Validierung)
AMDP_KATEGORIEN = [
    "bewusstsein",
    "orientierung",
    "aufmerksamkeit",
    "gedaechtnis",
    "formales_denken",
    "befuerchtungen",
    "wahn",
    "sinnestaueschungen",
    "ich_stoerungen",
    "zwang",
    "phobie",
    "affektivitaet",
    "antrieb",
    "psychomotorik",
    "circadiane_rhythmik",
    "schlaf",
    "appetit",
    "gewicht_bmi",
    "suizidalitaet",
    "eigen_fremdgefaehrdung",
]

# Lesbare deutsche Labels für AMDP-Kategorien
AMDP_LABELS = {
    "bewusstsein": "Bewusstsein",
    "orientierung": "Orientierung",
    "aufmerksamkeit": "Aufmerksamkeit",
    "gedaechtnis": "Gedächtnis",
    "formales_denken": "Formales Denken",
    "befuerchtungen": "Befürchtungen",
    "wahn": "Wahn",
    "sinnestaueschungen": "Sinnestäuschungen",
    "ich_stoerungen": "Ich-Störungen",
    "zwang": "Zwänge",
    "phobie": "Phobien",
    "affektivitaet": "Affektivität",
    "antrieb": "Antrieb",
    "psychomotorik": "Psychomotorik",
    "circadiane_rhythmik": "Circadiane Rhythmik",
    "schlaf": "Schlaf",
    "appetit": "Appetit",
    "gewicht_bmi": "Gewicht/BMI",
    "suizidalitaet": "Suizidalität",
    "eigen_fremdgefaehrdung": "Eigen-/Fremdgefährdung",
}
