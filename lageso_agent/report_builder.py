"""
Report Builder: Baut den LaGeSo-Befundbericht aus den extrahierten Daten zusammen.
Erzeugt die einzelnen Berichtsabschnitte als Text.
"""

from datetime import date


def build_vorstellung(
    erstvorstellung: str,
    letzte_vorstellung: str,
    frequenz: str,
) -> str:
    """Baut den Vorstellungs-Abschnitt."""
    lines = []
    lines.append(f"erstmalig am: {erstvorstellung or '[BITTE ERGÄNZEN]'}")
    lines.append(f"letztmalig am: {letzte_vorstellung or '[BITTE ERGÄNZEN]'}")
    lines.append(f"in welchen Abständen: {frequenz or '[BITTE ERGÄNZEN]'}")
    return "\n".join(lines)


def build_diagnosen(diagnosen: list) -> str:
    """Baut den Diagnosen-Abschnitt."""
    if not diagnosen:
        return "[BITTE ERGÄNZEN]"
    lines = []
    for d in diagnosen:
        icd = d.get("icd", "?")
        text = d.get("text", "?")
        lines.append(f"{icd} – {text}")
    return "\n".join(lines)


def build_medikation(medikation: list, datum: str = "") -> str:
    """Baut den Medikations-Abschnitt."""
    if not medikation:
        return "[BITTE ERGÄNZEN]"
    if not datum:
        datum = date.today().strftime("%d.%m.%Y")
    lines = []
    for med in medikation:
        name = med.get("name", "?").upper()
        dosis = med.get("dosis", "")
        schema = med.get("schema", "")
        parts = [datum, name]
        if dosis:
            parts.append(dosis)
        if schema:
            parts.append(schema)
        lines.append(" ".join(parts))
    lines.append("")
    lines.append("(Keine somatische Medikation wird aufgeführt.)")
    return "\n".join(lines)


def build_kopfzeile(arzt_daten: dict) -> str:
    """Baut die Kopfzeile mit Arzt-Stammdaten."""
    lines = [
        arzt_daten.get("name", ""),
        arzt_daten.get("fachgebiet", ""),
        arzt_daten.get("adresse", ""),
        arzt_daten.get("kontakt", ""),
    ]
    return "\n".join(line for line in lines if line)


def build_full_report(
    arzt_daten: dict,
    patient_name: str,
    geburtsdatum: str,
    adresse: str,
    aktenzeichen: str,
    vorstellung_text: str,
    diagnosen_text: str,
    befund_text: str,
    befund_datum: str,
    medikation_text: str,
    anamnese_text: str,
    beurteilung_text: str,
) -> str:
    """Baut den vollständigen Bericht als Gesamttext zusammen.

    Wird primär für die Vorschau verwendet.
    """
    heute = date.today().strftime("%d.%m.%Y")

    report = f"""{build_kopfzeile(arzt_daten)}

Berlin, den {heute}

Anlage zur Auskunft über die ärztliche Behandlung (LaGeSo)
Psychiatrischer/psychotherapeutischer Befundbericht

Patient/in {patient_name or '[Name]'}, geb. am {geburtsdatum or '[Geburtsdatum]'}, wohnhaft in {adresse or '[Adresse]'}
Aktenzeichen: {aktenzeichen or '[Aktenzeichen]'}

1. VORSTELLUNG
{vorstellung_text}

2. DIAGNOSEN (ICD-10)
{diagnosen_text}

3. PSYCHOPATHOLOGISCHER BEFUND
(AMDP-System – letzter Befund vom {befund_datum or heute})
{befund_text}

4. AKTUELLE MEDIKATION (nur psychopharmakologisch)
{medikation_text}

5. ANAMNESE UND BEHANDLUNGSVERLAUF
{anamnese_text}

6. SOZIALMEDIZINISCHE BEURTEILUNG
{beurteilung_text}


___________________________
{arzt_daten.get('name', '')}"""

    return report
