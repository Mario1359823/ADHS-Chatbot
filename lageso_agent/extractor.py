"""
Multi-Step Extraktion: Rohtext → strukturierte Daten → Fließtexte.
Orchestriert die 4-Schritt-LLM-Pipeline.
"""

import json
from typing import Callable, Optional

from llm_client import OllamaClient
from prompts import (
    AMDP_KATEGORIEN,
    AMDP_PROMPT,
    ANAMNESE_PROMPT,
    BEURTEILUNG_PROMPT,
    EXTRACTION_PROMPT,
)


# Leeres Befund-Template (Fallback)
EMPTY_BEFUND = {k: "nicht erhoben" for k in AMDP_KATEGORIEN}

EMPTY_EXTRACTION = {
    "diagnosen": [],
    "befund": dict(EMPTY_BEFUND),
    "medikation": [],
    "anamnese_stichpunkte": [],
    "beurteilung_stichpunkte": [],
}


def extract_data(
    client: OllamaClient,
    patient_text: str,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> dict:
    """Führt die vollständige 4-Schritt-Extraktion durch.

    Args:
        client: OllamaClient-Instanz
        patient_text: Unstrukturierter klinischer Text
        progress_callback: Optional callback(step_number, step_description)

    Returns:
        Dict mit Schlüsseln:
        - raw_data: Extrahierte Rohdaten (JSON)
        - vorstellung: Vorstellungsdaten (aus Metadaten)
        - diagnosen: Liste der Diagnosen
        - befund_text: AMDP-Fließtext
        - medikation: Medikationsliste
        - anamnese_text: Anamnese-Fließtext
        - beurteilung_text: Beurteilungs-Fließtext
    """

    def _progress(step: int, desc: str):
        if progress_callback:
            progress_callback(step, desc)

    # --- Schritt 1: Extraktion ---
    _progress(1, "Extrahiere Informationen aus dem Text...")
    raw_data = _step1_extract(client, patient_text)

    # --- Schritt 2: AMDP-Fließtext ---
    _progress(2, "Erstelle psychopathologischen Befund (AMDP)...")
    befund_text = _step2_amdp(client, raw_data.get("befund", EMPTY_BEFUND))

    # --- Schritt 3: Anamnese-Fließtext ---
    _progress(3, "Erstelle Anamnese und Behandlungsverlauf...")
    anamnese_text = _step3_anamnese(client, raw_data.get("anamnese_stichpunkte", []))

    # --- Schritt 4: Beurteilung ---
    _progress(4, "Erstelle sozialmedizinische Beurteilung...")
    beurteilung_text = _step4_beurteilung(
        client,
        raw_data.get("diagnosen", []),
        befund_text,
        anamnese_text,
    )

    return {
        "raw_data": raw_data,
        "diagnosen": raw_data.get("diagnosen", []),
        "befund_text": befund_text,
        "medikation": raw_data.get("medikation", []),
        "anamnese_text": anamnese_text,
        "beurteilung_text": beurteilung_text,
    }


def _step1_extract(client: OllamaClient, patient_text: str) -> dict:
    """Schritt 1: Extrahiert strukturierte Daten aus dem Rohtext."""
    prompt = EXTRACTION_PROMPT.format(patient_text=patient_text)
    try:
        data = client.extract_json(prompt)
    except ValueError:
        # Fallback: leere Struktur
        data = dict(EMPTY_EXTRACTION)

    # Sicherstellen, dass alle AMDP-Kategorien vorhanden sind
    befund = data.get("befund", {})
    for key in AMDP_KATEGORIEN:
        if key not in befund or not befund[key]:
            befund[key] = "nicht erhoben"
    data["befund"] = befund

    # Sicherstellen, dass Listen vorhanden sind
    if not isinstance(data.get("diagnosen"), list):
        data["diagnosen"] = []
    if not isinstance(data.get("medikation"), list):
        data["medikation"] = []
    if not isinstance(data.get("anamnese_stichpunkte"), list):
        data["anamnese_stichpunkte"] = []
    if not isinstance(data.get("beurteilung_stichpunkte"), list):
        data["beurteilung_stichpunkte"] = []

    return data


def _step2_amdp(client: OllamaClient, befund: dict) -> str:
    """Schritt 2: Generiert AMDP-Fließtext aus den Befunddaten."""
    befund_json = json.dumps(befund, ensure_ascii=False, indent=2)
    prompt = AMDP_PROMPT.format(befund_json=befund_json)

    text = client.generate(prompt)

    # Sicherstellen, dass der Text mit "Pat." beginnt
    if text and not text.startswith("Pat."):
        # Versuche "Pat." am Anfang zu finden und alles davor zu entfernen
        idx = text.find("Pat.")
        if idx != -1:
            text = text[idx:]
        else:
            text = "Pat. " + text

    return text or "[BITTE ERGÄNZEN]"


def _step3_anamnese(client: OllamaClient, stichpunkte: list) -> str:
    """Schritt 3: Generiert Anamnese-Fließtext aus Stichpunkten."""
    if not stichpunkte:
        return "[BITTE ERGÄNZEN]"

    stichpunkte_text = "\n".join(f"- {s}" for s in stichpunkte)
    prompt = ANAMNESE_PROMPT.format(stichpunkte=stichpunkte_text)

    text = client.generate(prompt)
    return text or "[BITTE ERGÄNZEN]"


def _step4_beurteilung(
    client: OllamaClient,
    diagnosen: list,
    befund_text: str,
    anamnese_text: str,
) -> str:
    """Schritt 4: Generiert sozialmedizinische Beurteilung."""
    if not diagnosen:
        diagnosen_text = "Keine Diagnosen extrahiert."
    else:
        diagnosen_text = "\n".join(
            f"- {d.get('icd', '?')} – {d.get('text', '?')}" for d in diagnosen
        )

    prompt = BEURTEILUNG_PROMPT.format(
        diagnosen=diagnosen_text,
        befund_zusammenfassung=befund_text[:500] if befund_text else "Kein Befund.",
        anamnese_zusammenfassung=anamnese_text[:500] if anamnese_text else "Keine Anamnese.",
    )

    text = client.generate(prompt)
    return text or "[BITTE ERGÄNZEN]"
