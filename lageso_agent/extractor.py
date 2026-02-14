"""
Multi-Step Extraktion: Rohtext → strukturierte Daten → Fließtexte.
Orchestriert die 4-Schritt-LLM-Pipeline nach CU-Standard.

DIRECT MODE: Der originale Patiententext wird bei JEDEM Schritt an das LLM
gesendet. Die JSON-Extraktion aus Schritt 1 dient nur als strukturelle
Orientierung – das LLM hat immer Zugriff auf den vollständigen Originaltext.
"""

import json
from typing import Callable, Optional

from llm_client import OllamaClient
from prompts import (
    AMDP_KATEGORIEN,
    AMDP_PROMPT,
    AUSWIRKUNGEN_PROMPT,
    EXTRACTION_PROMPT,
    VERLAUF_PROMPT,
)

# Leeres Befund-Template (Fallback)
EMPTY_BEFUND = {k: "nicht erhoben" for k in AMDP_KATEGORIEN}

EMPTY_EXTRACTION = {
    "diagnosen": [],
    "befund": dict(EMPTY_BEFUND),
    "medikation": [],
    "verlauf": {
        "form": "nicht erhoben",
        "tendenz": "nicht erhoben",
        "behandlungserfolg": "nicht erhoben",
    },
    "sucht": {"vorhanden": False},
    "behandlungen": {
        "stationaer": [],
        "teilstationaer": [],
        "ambulant": [],
        "reha": [],
    },
    "auswirkungen_stichpunkte": {
        "alltag": [],
        "beruf": [],
        "sozial": [],
    },
    "anamnese_stichpunkte": [],
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
        Dict mit allen extrahierten und generierten Abschnitten.
    """

    def _progress(step: int, desc: str):
        if progress_callback:
            progress_callback(step, desc)

    # --- Schritt 1: Extraktion ---
    _progress(1, "Extrahiere Informationen aus dem Text...")
    raw_data = _step1_extract(client, patient_text)

    # --- Schritt 2: AMDP-Fließtext (mit Originaltext!) ---
    _progress(2, "Erstelle psychopathologischen Befund (AMDP)...")
    befund_text = _step2_amdp(client, patient_text, raw_data.get("befund", EMPTY_BEFUND))

    # --- Schritt 3: Verlauf + Suchtanamnese (mit Originaltext!) ---
    _progress(3, "Erstelle Verlauf und Behandlungshistorie...")
    verlauf_text, sucht_text = _step3_verlauf(
        client,
        patient_text,
        raw_data.get("anamnese_stichpunkte", []),
        raw_data.get("sucht", {}),
        raw_data.get("verlauf", {}),
    )

    # --- Schritt 4: Krankheitsbedingte Auswirkungen (mit Originaltext!) ---
    _progress(4, "Erstelle krankheitsbedingte Auswirkungen...")
    alltag, beruf, sozial = _step4_auswirkungen(
        client,
        patient_text,
        raw_data.get("diagnosen", []),
        raw_data.get("auswirkungen_stichpunkte", {}),
    )

    # Behandlungen formatieren
    behandlungen_text = _format_behandlungen(raw_data.get("behandlungen", {}))

    return {
        "raw_data": raw_data,
        "diagnosen": raw_data.get("diagnosen", []),
        "befund_text": befund_text,
        "medikation": raw_data.get("medikation", []),
        "verlauf": raw_data.get("verlauf", {}),
        "verlauf_text": verlauf_text,
        "sucht": raw_data.get("sucht", {}),
        "sucht_text": sucht_text,
        "behandlungen_text": behandlungen_text,
        "auswirkungen_alltag": alltag,
        "auswirkungen_beruf": beruf,
        "auswirkungen_sozial": sozial,
    }


def _step1_extract(client: OllamaClient, patient_text: str) -> dict:
    """Schritt 1: Extrahiert strukturierte Daten aus dem Rohtext."""
    prompt = EXTRACTION_PROMPT.format(patient_text=patient_text)
    try:
        data = client.extract_json(prompt)
    except ValueError:
        data = dict(EMPTY_EXTRACTION)

    # Sicherstellen, dass alle AMDP-Kategorien vorhanden sind
    befund = data.get("befund", {})
    for key in AMDP_KATEGORIEN:
        if key not in befund or not befund[key]:
            befund[key] = "nicht erhoben"
    data["befund"] = befund

    # Sicherstellen, dass alle Top-Level-Schlüssel vorhanden sind
    if not isinstance(data.get("diagnosen"), list):
        data["diagnosen"] = []
    if not isinstance(data.get("medikation"), list):
        data["medikation"] = []
    if not isinstance(data.get("anamnese_stichpunkte"), list):
        data["anamnese_stichpunkte"] = []
    if not isinstance(data.get("verlauf"), dict):
        data["verlauf"] = EMPTY_EXTRACTION["verlauf"]
    if not isinstance(data.get("sucht"), dict):
        data["sucht"] = {"vorhanden": False}
    if not isinstance(data.get("behandlungen"), dict):
        data["behandlungen"] = EMPTY_EXTRACTION["behandlungen"]
    if not isinstance(data.get("auswirkungen_stichpunkte"), dict):
        data["auswirkungen_stichpunkte"] = EMPTY_EXTRACTION["auswirkungen_stichpunkte"]

    return data


def _step2_amdp(client: OllamaClient, patient_text: str, befund: dict) -> str:
    """Schritt 2: Generiert AMDP-Fließtext.

    DIRECT MODE: Das LLM bekommt den ORIGINALEN Patiententext plus die
    vorextrahierten Befund-Stichpunkte als Orientierung.
    """
    befund_json = json.dumps(befund, ensure_ascii=False, indent=2)
    prompt = AMDP_PROMPT.format(patient_text=patient_text, befund_json=befund_json)

    text = client.generate(prompt)

    # Sicherstellen, dass der Text mit "Pat." beginnt
    if text and not text.startswith("Pat."):
        idx = text.find("Pat.")
        if idx != -1:
            text = text[idx:]
        else:
            text = "Pat. " + text

    return text or "[BITTE ERGÄNZEN]"


def _step3_verlauf(
    client: OllamaClient,
    patient_text: str,
    anamnese_stichpunkte: list,
    sucht: dict,
    verlauf: dict,
) -> tuple[str, str]:
    """Schritt 3: Generiert Verlauf- und Suchtanamnese-Text.

    DIRECT MODE: Das LLM bekommt den ORIGINALEN Patiententext plus die
    vorextrahierten Stichpunkte als Orientierung.

    Returns:
        Tuple (verlauf_text, sucht_text)
    """
    stichpunkte = (
        "\n".join(f"- {s}" for s in anamnese_stichpunkte)
        if anamnese_stichpunkte
        else "Keine Stichpunkte extrahiert."
    )

    sucht_daten = json.dumps(sucht, ensure_ascii=False, indent=2)
    verlauf_daten = json.dumps(verlauf, ensure_ascii=False, indent=2)

    prompt = VERLAUF_PROMPT.format(
        patient_text=patient_text,
        anamnese_stichpunkte=stichpunkte,
        sucht_daten=sucht_daten,
        verlauf_daten=verlauf_daten,
    )

    text = client.generate(prompt)

    # Versuche den Text in Verlauf und Sucht zu splitten
    verlauf_text = text or "[BITTE ERGÄNZEN]"
    sucht_text = ""

    if sucht.get("vorhanden"):
        # Wenn Suchterkrankung vorhanden, versuche den Text aufzuteilen
        # Der LLM sollte beides zusammen liefern
        sucht_text = verlauf_text  # Fallback: gleicher Text
    else:
        sucht_text = "Keine Suchterkrankung bekannt."

    return verlauf_text, sucht_text


def _step4_auswirkungen(
    client: OllamaClient,
    patient_text: str,
    diagnosen: list,
    auswirkungen_stichpunkte: dict,
) -> tuple[str, str, str]:
    """Schritt 4: Generiert die drei Auswirkungs-Texte.

    DIRECT MODE: Das LLM bekommt den ORIGINALEN Patiententext plus die
    vorextrahierten Stichpunkte als Orientierung.

    Returns:
        Tuple (alltag, beruf, sozial)
    """
    diagnosen_text = (
        "\n".join(f"- {d.get('icd', '?')} – {d.get('text', '?')}" for d in diagnosen)
        if diagnosen
        else "Keine Diagnosen extrahiert."
    )

    alltag_sp = auswirkungen_stichpunkte.get("alltag", [])
    beruf_sp = auswirkungen_stichpunkte.get("beruf", [])
    sozial_sp = auswirkungen_stichpunkte.get("sozial", [])

    prompt = AUSWIRKUNGEN_PROMPT.format(
        patient_text=patient_text,
        diagnosen=diagnosen_text,
        alltag_stichpunkte=", ".join(alltag_sp) if alltag_sp else "nicht erhoben",
        beruf_stichpunkte=", ".join(beruf_sp) if beruf_sp else "nicht erhoben",
        sozial_stichpunkte=", ".join(sozial_sp) if sozial_sp else "nicht erhoben",
    )

    text = client.generate(prompt)

    # Parse die drei Bereiche
    alltag = "[BITTE ERGÄNZEN]"
    beruf = "[BITTE ERGÄNZEN]"
    sozial = "[BITTE ERGÄNZEN]"

    if text:
        if "---ALLTAG---" in text and "---BERUF---" in text and "---SOZIAL---" in text:
            parts = text.split("---ALLTAG---")
            if len(parts) > 1:
                rest = parts[1]
                parts2 = rest.split("---BERUF---")
                if len(parts2) > 1:
                    alltag = parts2[0].strip()
                    rest2 = parts2[1]
                    parts3 = rest2.split("---SOZIAL---")
                    if len(parts3) > 1:
                        beruf = parts3[0].strip()
                        sozial = parts3[1].strip()
        else:
            # Fallback: gesamten Text als Alltag verwenden
            alltag = text.strip()

    return alltag, beruf, sozial


def _format_behandlungen(behandlungen: dict) -> str:
    """Formatiert die extrahierten Behandlungen als Text."""
    lines = []

    stationaer = behandlungen.get("stationaer", [])
    if stationaer:
        lines.append("Vollstationär psychiatrisch:")
        for b in stationaer:
            if isinstance(b, str) and b != "nicht erhoben":
                lines.append(f"  {b}")

    reha = behandlungen.get("reha", [])
    if reha:
        lines.append("Rehabilitationsbehandlung:")
        for b in reha:
            if isinstance(b, str) and b != "nicht erhoben":
                lines.append(f"  {b}")

    teilstationaer = behandlungen.get("teilstationaer", [])
    if teilstationaer:
        lines.append("Teilstationär (Tagesklinik):")
        for b in teilstationaer:
            if isinstance(b, str) and b != "nicht erhoben":
                lines.append(f"  {b}")

    ambulant = behandlungen.get("ambulant", [])
    if ambulant:
        lines.append("Ambulante Psychotherapie:")
        for b in ambulant:
            if isinstance(b, str) and b != "nicht erhoben":
                lines.append(f"  {b}")

    if not lines:
        return "Keine im geforderten Zeitraum."

    return "\n".join(lines)
