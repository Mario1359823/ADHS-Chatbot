"""
Prompt-Templates für den LaGeSo-Befundbericht-Generator.
Alle Prompts als Konstanten – zentrale Verwaltung.
Basiert auf der CU-Standard Wissensdatenbank (Version 2.0, Februar 2026).
"""

SYSTEM_PROMPT = """\
Du bist ein spezialisierter medizinischer Assistent für die Erstellung \
psychiatrischer Befundberichte für das Landesamt für Gesundheit und Soziales \
(LaGeSo) Berlin nach den Standards von Dr. med. Carsten Urbanek, \
Facharzt für Psychiatrie und Psychotherapie.

KRITISCHE REGELN:
- Schreibe IMMER auf Deutsch in medizinischer Fachsprache, KEIN Denglisch
- AMDP-Befund: IMMER als Fließtext, NIEMALS nummeriert oder als Liste
- AMDP-Befund: ALLE 20 Kategorien in EXAKTER CU-Reihenfolge:
  1. Bewusstseinslage → 2. Stimmung → 3. Affekt → 4. Konzentration →
  5. Merkfähigkeit/Gedächtnis → 6. Interesse → 7. Formales Denken →
  8. Inhaltliches Denken → 9+10. Wahrnehmung UND Ich-Störungen (zusammen!) →
  11. Zwänge/Phobien → 12. Antrieb → 13. Psychomotorik → 14. Schlaf →
  15. Appetit → 16. Gewicht → 17. BMI (separat!) → 18. Suizidalität →
  19. Eigen-/Fremdgefährdung → 20. Psychopharmakologische Vorbehandlung
- Beginne den AMDP-Befund IMMER mit "Pat."
- ICD-10 Codes: Exakte ICD-10-Terminologie mit Untergruppe (z.B. F33.2)
  ACHTUNG: F33.3 = MIT psychotischen Symptomen, F33.2 = OHNE psychotische Symptome
- Medikation: NUR Psychopharmaka, KEINE somatische Medikation
- Medikamente in GROSSBUCHSTABEN, Schema: "X-X-X-X" (morgens-mittags-abends-nachts)
- Behandlungen: NUR psychiatrische/psychotherapeutische, KEINE Physiotherapie/Orthopädie
- Keine Spekulationen – nur dokumentierte Fakten
- Fehlende Informationen als "nicht erhoben" / "[FEHLT]" kennzeichnen
- Zeitraum: maximal 2 Jahre (seit Dezember 2024)"""

# ---------------------------------------------------------------------------
# Schritt 1: Extraktion
# ---------------------------------------------------------------------------
EXTRACTION_PROMPT = """\
Extrahiere aus dem folgenden klinischen Text alle relevanten Informationen \
und gib sie als JSON zurück.

Antworte NUR mit dem JSON-Objekt, KEIN weiterer Text davor oder danach.

Erwartetes Format:
{{
  "diagnosen": [{{"icd": "...", "text": "..."}}],
  "befund": {{
    "bewusstseinslage": "...",
    "stimmung": "...",
    "affekt": "...",
    "konzentration": "...",
    "merkfaehigkeit_gedaechtnis": "...",
    "interesse": "...",
    "formales_denken": "...",
    "inhaltliches_denken": "...",
    "wahrnehmung_ich_stoerungen": "...",
    "zwaenge_phobien": "...",
    "antrieb": "...",
    "psychomotorik": "...",
    "schlaf": "...",
    "appetit": "...",
    "gewicht": "...",
    "bmi": "...",
    "suizidalitaet": "...",
    "eigen_fremdgefaehrdung": "...",
    "psychopharm_vorbehandlung": "..."
  }},
  "medikation": [{{"datum": "...", "name": "...", "dosis": "...", "schema": "..."}}],
  "verlauf": {{
    "form": "dauerhaft oder phasenhaft",
    "tendenz": "chronifizierend oder stabil oder progredient",
    "behandlungserfolg": "verbesserung oder gleichbleibend oder verschlechterung"
  }},
  "sucht": {{
    "vorhanden": true,
    "konsummuster": "...",
    "letzter_konsum": "...",
    "entzugssymptomatik": "...",
    "stationaere_behandlung": "...",
    "abstinenz_seit": "...",
    "aktuelle_anbindung": "..."
  }},
  "behandlungen": {{
    "stationaer": ["..."],
    "teilstationaer": ["..."],
    "ambulant": ["..."],
    "reha": ["..."]
  }},
  "auswirkungen_stichpunkte": {{
    "alltag": ["..."],
    "beruf": ["..."],
    "sozial": ["..."]
  }},
  "anamnese_stichpunkte": ["..."]
}}

WICHTIGE REGELN:
- Wenn eine Information nicht im Text vorkommt, setze den Wert auf "nicht erhoben"
- NUR psychopharmakologische Medikation extrahieren (KEINE somatische wie \
Levothyroxin, Blutdruckmedikamente, Schmerzmittel)
- ICD-10 Codes IMMER vollständig mit Untergruppe (z.B. F33.2, nicht nur F33)
- ACHTUNG: F33.3 = MIT psychotischen Symptomen, F33.2 = OHNE
- F45.1 = "Undifferenzierte Somatisierungsstörung" (NICHT "Somatische Symptomstörung")
- Medikamentennamen in GROSSBUCHSTABEN
- NUR psychiatrische/psychotherapeutische Behandlungen, KEINE Physiotherapie
- Bei Suchterkrankung: Alle 6 Punkte extrahieren (Konsummuster, letzter Konsum, \
Entzugssymptomatik, stationäre Behandlung, Abstinenzstatus, aktuelle Anbindung)
- Wenn keine Suchterkrankung: {{"vorhanden": false}} setzen

KLINISCHER TEXT:
{patient_text}"""

# ---------------------------------------------------------------------------
# Schritt 2: AMDP-Fließtext (DIRECT MODE - Originaltext wird mitgesendet)
# ---------------------------------------------------------------------------
AMDP_PROMPT = """\
Erstelle den psychopathologischen Befund (AMDP-System) als Fließtext \
für einen LaGeSo-Befundbericht nach dem CU-Standard.

Lies den ORIGINALEN KLINISCHEN TEXT sorgfältig und erstelle daraus den \
AMDP-Befund. Die vorextrahierten Stichpunkte dienen nur als Orientierung - \
nutze IMMER den Originaltext als primäre Quelle.

REGELN:
- ALLE 20 Kategorien in EXAKT dieser Reihenfolge:
  1. Bewusstseinslage, 2. Stimmung, 3. Affekt, 4. Konzentration,
  5. Merkfähigkeit/Gedächtnis/Auffassung, 6. Interesse,
  7. Formales Denken, 8. Inhaltliches Denken,
  9+10. Wahrnehmung UND Ich-Störungen (ZUSAMMEN dokumentieren!),
  11. Zwänge/Phobien, 12. Antrieb, 13. Psychomotorik,
  14. Schlaf, 15. Appetit, 16. Gewicht, 17. BMI (SEPARAT als eigene Kategorie!),
  18. Suizidalität, 19. Eigen-/Fremdgefährdung,
  20. Psychopharmakologische Vorbehandlung
- Beginne IMMER mit "Pat."
- Fließtext mit Punkten als Satzzeichen, KEINE Aufzählungszeichen, KEIN Markdown
- KEINE Nummerierung
- Medizinische Fachsprache, knapp und präzise, auf Deutsch
- Fehlende Informationen als "nicht erhoben" / "nicht beurteilbar" kennzeichnen
- Antworte NUR mit dem Fließtext, kein weiterer Text

BEISPIEL-FORMAT:
"Pat. wach, allseits orientiert. Stimmung gedrückt, im Affekt modulierbar. \
Konzentration eingeschränkt. Merkfähigkeit, Gedächtnis und Auffassung intakt. \
Interesse vermindert. Im formalen Denken eingeengt auf Suizidthematik und \
Zukunftsängste. Inhaltlich kein Wahn. Keine Wahrnehmungs- oder Ich-Störungen. \
Kein Anhalt für Zwänge oder Phobien. Antrieb vermindert, Psychomotorik ruhig. \
Schlaf gestört mit Ein- und Durchschlafproblemen. Appetit vermindert. \
Gewichtsabnahme in den letzten Monaten. BMI 21. Keine akute Suizidalität. \
Keine akute Eigen- oder Fremdgefährdung. Psychopharmakologische Vorbehandlung \
mit Escitalopram."

=== ORIGINALER KLINISCHER TEXT (PRIMÄRE QUELLE) ===
{patient_text}

=== VOREXTRAHIERTE STICHPUNKTE (nur Orientierung) ===
{befund_json}"""

# ---------------------------------------------------------------------------
# Schritt 3: Verlauf + Suchtanamnese (DIRECT MODE - Originaltext wird mitgesendet)
# ---------------------------------------------------------------------------
VERLAUF_PROMPT = """\
Erstelle den Abschnitt "Verlauf der Erkrankung" und ggf. "Suchterkrankung" \
für einen LaGeSo-Befundbericht.

Lies den ORIGINALEN KLINISCHEN TEXT sorgfältig und erstelle daraus den \
Verlaufstext. Die vorextrahierten Stichpunkte dienen nur als Orientierung - \
nutze IMMER den Originaltext als primäre Quelle.

REGELN:
- Fließtext, sachlich, medizinisch-fachsprachlich, auf Deutsch
- KEINE Aufzählungszeichen, KEIN Markdown
- Zusammenhängender, logisch strukturierter Text
- Bei Suchterkrankung: ALLE 6 Punkte abdecken (Konsummuster, letzter Konsum, \
Entzugssymptomatik, stationäre Behandlung, Abstinenzstatus, aktuelle Anbindung)
- NUR psychiatrische/psychotherapeutische Behandlungen erwähnen
- KEINE Physiotherapie, Orthopädie oder somatische Behandlungen
- Nur dokumentierte Fakten, keine Spekulationen
- Antworte NUR mit dem Fließtext, kein weiterer Text

=== ORIGINALER KLINISCHER TEXT (PRIMÄRE QUELLE) ===
{patient_text}

=== VOREXTRAHIERTE STICHPUNKTE (nur Orientierung) ===
Anamnese: {anamnese_stichpunkte}
Sucht: {sucht_daten}
Verlauf: {verlauf_daten}"""

# ---------------------------------------------------------------------------
# Schritt 4: Krankheitsbedingte Auswirkungen (DIRECT MODE - Originaltext wird mitgesendet)
# ---------------------------------------------------------------------------
AUSWIRKUNGEN_PROMPT = """\
Erstelle für einen LaGeSo-Befundbericht die drei Abschnitte der \
"Krankheitsbedingten Auswirkungen" (Alltag, Beruf, Sozial).

Lies den ORIGINALEN KLINISCHEN TEXT sorgfältig und erstelle daraus die \
Auswirkungstexte. Die vorextrahierten Stichpunkte dienen nur als Orientierung - \
nutze IMMER den Originaltext als primäre Quelle.

REGELN:
- Sachlich, fachsprachlich, Fließtext, auf Deutsch
- KEINE Aufzählungszeichen, KEIN Markdown
- Für jeden Bereich (Alltag, Beruf, Sozial) einen separaten Absatz
- Trenne die drei Bereiche mit genau "---ALLTAG---", "---BERUF---", "---SOZIAL---"
- Nur dokumentierte Fakten aus dem Text, keine Spekulationen
- Antworte NUR mit den drei Absätzen, kein weiterer Text

=== ORIGINALER KLINISCHER TEXT (PRIMÄRE QUELLE) ===
{patient_text}

=== VOREXTRAHIERTE STICHPUNKTE (nur Orientierung) ===
Diagnosen: {diagnosen}
Alltag: {alltag_stichpunkte}
Beruf: {beruf_stichpunkte}
Sozial: {sozial_stichpunkte}"""

# ---------------------------------------------------------------------------
# AMDP-Kategorien in CU-Standard Reihenfolge (für Validierung)
# ---------------------------------------------------------------------------
AMDP_KATEGORIEN = [
    "bewusstseinslage",
    "stimmung",
    "affekt",
    "konzentration",
    "merkfaehigkeit_gedaechtnis",
    "interesse",
    "formales_denken",
    "inhaltliches_denken",
    "wahrnehmung_ich_stoerungen",
    "zwaenge_phobien",
    "antrieb",
    "psychomotorik",
    "schlaf",
    "appetit",
    "gewicht",
    "bmi",
    "suizidalitaet",
    "eigen_fremdgefaehrdung",
    "psychopharm_vorbehandlung",
]

# Lesbare deutsche Labels für AMDP-Kategorien
AMDP_LABELS = {
    "bewusstseinslage": "Bewusstseinslage",
    "stimmung": "Stimmung",
    "affekt": "Affekt",
    "konzentration": "Konzentration",
    "merkfaehigkeit_gedaechtnis": "Merkfähigkeit, Gedächtnis, Auffassung",
    "interesse": "Interesse",
    "formales_denken": "Formales Denken",
    "inhaltliches_denken": "Inhaltliches Denken",
    "wahrnehmung_ich_stoerungen": "Wahrnehmung und Ich-Störungen",
    "zwaenge_phobien": "Zwänge und Phobien",
    "antrieb": "Antrieb",
    "psychomotorik": "Psychomotorik",
    "schlaf": "Schlaf",
    "appetit": "Appetit",
    "gewicht": "Gewicht",
    "bmi": "BMI",
    "suizidalitaet": "Suizidalität",
    "eigen_fremdgefaehrdung": "Eigen-/Fremdgefährdung",
    "psychopharm_vorbehandlung": "Psychopharmakologische Vorbehandlung",
}

# Standard-Normalbefund (Template)
AMDP_NORMALBEFUND = (
    "Pat. wach und allseits orientiert. Stimmung euthym, im Affekt gut moduliert. "
    "Konzentration regelrecht. Merkfähigkeit, Gedächtnis und Auffassung intakt. "
    "Interesse regelrecht. Im formalen Denken kohärent, inhaltlich kein Wahn. "
    "Weder Wahrnehmungs- noch Ich-Störungen eruierbar. "
    "Kein Anhalt für Zwänge oder Phobien. "
    "Antrieb regelrecht, Psychomotorik ruhig. "
    "Appetit normal, Gewicht konstant. BMI [Zahl]. Schlaf gut. "
    "Keine akute Suizidalität. Keine akute Eigen- oder Fremdgefährdung. "
    "Keine psychopharmakologische Vorbehandlung."
)
