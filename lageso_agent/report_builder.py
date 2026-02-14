"""
Report Builder: Baut den LaGeSo-Befundbericht aus den extrahierten Daten zusammen.
Erzeugt die einzelnen Berichtsabschnitte als Text.
Vollständige 12-Abschnitt-Struktur nach CU-Standard.
"""

from datetime import date


def build_vorstellung(
    erstvorstellung: str,
    letzte_vorstellung: str,
    frequenz: str,
) -> str:
    """Baut den Vorstellungs-Abschnitt."""
    lines = [
        f"a) erstmalig am: {erstvorstellung or '[FEHLT]'}",
        f"b) letztmalig am: {letzte_vorstellung or '[FEHLT]'}",
        f"c) in welchen Abständen: {frequenz or '[FEHLT]'}",
    ]
    return "\n".join(lines)


def build_diagnosen(diagnosen: list) -> str:
    """Baut den Diagnosen-Abschnitt mit ICD-10 Codes."""
    if not diagnosen:
        return "[FEHLT]"
    lines = []
    for d in diagnosen:
        icd = d.get("icd", "?")
        text = d.get("text", "?")
        lines.append(f"{icd} ({text})")
    return "\n".join(lines)


def build_medikation(medikation: list) -> str:
    """Baut den Medikations-Abschnitt.

    Format: DATUM MEDIKAMENTENNAME DOSIERUNG SCHEMA
    NUR Psychopharmaka, KEIN Tabellenformat.
    """
    if not medikation:
        return "[FEHLT]"
    lines = []
    for med in medikation:
        datum = med.get("datum", "")
        name = med.get("name", "?").upper()
        dosis = med.get("dosis", "")
        schema = med.get("schema", "")
        parts = []
        if datum:
            parts.append(datum)
        parts.append(name)
        if dosis:
            parts.append(dosis)
        if schema:
            parts.append(schema)
        lines.append(" ".join(parts))
    lines.append("")
    lines.append("(Keine somatische Medikation wird aufgeführt.)")
    return "\n".join(lines)


def build_verlauf(verlauf: dict, verlauf_text: str) -> str:
    """Baut den Verlauf-Abschnitt mit Checkbox-Angaben und Fließtext."""
    form = verlauf.get("form", "nicht erhoben")
    tendenz = verlauf.get("tendenz", "")
    erfolg = verlauf.get("behandlungserfolg", "nicht erhoben")

    lines = []
    lines.append("Verlaufsform:")
    if form == "phasenhaft":
        phasen = verlauf.get("phasen_anzahl", "?")
        lines.append(f"  phasenhaft - Anzahl der Phasen in den letzten 2 Jahren: {phasen}")
    else:
        lines.append(f"  dauerhaft mit Tendenz: {tendenz}")

    lines.append("")
    lines.append("Behandlungserfolg:")
    lines.append(f"  Durch die bisher durchgeführte Behandlung: {erfolg}")

    if verlauf_text and verlauf_text != "[BITTE ERGÄNZEN]":
        lines.append("")
        lines.append(verlauf_text)

    return "\n".join(lines)


def build_sucht(sucht: dict, sucht_text: str) -> str:
    """Baut den Sucht-Abschnitt."""
    if not sucht.get("vorhanden"):
        return "Keine Suchterkrankung bekannt."

    abstinenz = sucht.get("abstinenz_seit", "")
    if abstinenz:
        header = f"Abstinenz seit: {abstinenz}"
    else:
        header = "Fortgesetzter Konsum"

    lines = [header]
    if sucht_text and sucht_text != "Keine Suchterkrankung bekannt.":
        lines.append("")
        lines.append(sucht_text)

    return "\n".join(lines)


def build_psychosoziale_hilfen(hilfen: dict) -> str:
    """Baut den Abschnitt Psychosoziale Hilfen aus den Checkbox-Daten."""
    lines = []

    # Gesetzliche Betreuung
    if hilfen.get("betreuung"):
        bereiche = hilfen.get("betreuung_bereiche", "[FEHLT]")
        lines.append(f"Gesetzliche Betreuung: ja - für: {bereiche}")
    else:
        lines.append("Gesetzliche Betreuung: nein")

    # Einzelhilfe
    val = "ja" if hilfen.get("einzelhilfe") else "nein"
    lines.append(f"Einzelhilfe: {val}")

    # Betreutes Wohnen
    val = "ja" if hilfen.get("betreutes_wohnen") else "nein"
    lines.append(f"Betreutes Wohnen: {val}")

    # Heimunterbringung
    val = "ja" if hilfen.get("heimunterbringung") else "nein"
    lines.append(f"Heimunterbringung: {val}")

    # Pflegegrad
    pflegegrad = hilfen.get("pflegegrad", "keiner")
    lines.append(f"Pflegegrad: {pflegegrad}")

    # AU
    if hilfen.get("au_psychisch"):
        seit = hilfen.get("au_seit", "[FEHLT]")
        lines.append(f"AU wegen psychischer Erkrankung: ja - seit: {seit}")
    else:
        lines.append("AU wegen psychischer Erkrankung: nein")

    # Berentung
    if hilfen.get("berentung"):
        seit = hilfen.get("berentung_seit", "[FEHLT]")
        lines.append(f"Berentung wegen psychischer Erkrankung: ja - seit: {seit}")
    else:
        lines.append("Berentung wegen psychischer Erkrankung: nein")

    return "\n".join(lines)


def build_gehfaehigkeit(eingeschraenkt: bool, beschreibung: str) -> str:
    """Baut den Gehfähigkeits-Abschnitt."""
    if eingeschraenkt:
        return f"Ja, inwiefern: {beschreibung or '[FEHLT]'}"
    return "Nein"


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
    plz_ort: str,
    strasse: str,
    aktenzeichen: str,
    vorstellung_text: str,
    diagnosen_text: str,
    befund_text: str,
    befund_datum: str,
    medikation_text: str,
    verlauf_text: str,
    sucht_text: str,
    behandlungen_text: str,
    psychosoziale_hilfen_text: str,
    auswirkungen_alltag: str,
    auswirkungen_beruf: str,
    auswirkungen_sozial: str,
    gehfaehigkeit_text: str,
    akteneinsicht: bool,
    akteneinsicht_begruendung: str,
) -> str:
    """Baut den vollständigen 12-Abschnitt-Bericht als Gesamttext."""
    heute = date.today().strftime("%d.%m.%Y")

    # Adresse formatieren: PLZ Ort, Straße
    adresse_full = f"{plz_ort}, {strasse}" if plz_ort and strasse else (plz_ort or strasse or "[Adresse]")

    akteneinsicht_text = "Ja"
    if not akteneinsicht:
        akteneinsicht_text = f"Nein - Begründung: {akteneinsicht_begruendung or '[FEHLT]'}"

    report = f"""{build_kopfzeile(arzt_daten)}

Berlin, den {heute}

Anlage zur Auskunft über die ärztliche Behandlung (LaGeSo)
Psychiatrischer/psychotherapeutischer Befundbericht

Patient/in {patient_name or '[Name]'}, geb. am {geburtsdatum or '[Geburtsdatum]'}, wohnhaft in {adresse_full}
Aktenzeichen: {aktenzeichen or '[Aktenzeichen]'}

1. VORSTELLUNG
Die Vorstellung erfolgte:
{vorstellung_text}

2. DIAGNOSEN (ICD-10)
{diagnosen_text}

3. PSYCHOPATHOLOGISCHER BEFUND
(AMDP-System - letzter Befund vom {befund_datum or heute})
{befund_text}

4. AKTUELLE MEDIKATION (nur psychopharmakologisch)
{medikation_text}

5. VERLAUF DER ERKRANKUNG
{verlauf_text}

6. BEI SUCHTERKRANKUNG
{sucht_text}

7. SONSTIGE BEHANDLUNGEN (wo?, wann?)
{behandlungen_text}

8. PSYCHOSOZIALE HILFEN
{psychosoziale_hilfen_text}

9. KRANKHEITSBEDINGTE AUSWIRKUNGEN

Alltag:
{auswirkungen_alltag}

Beruf:
{auswirkungen_beruf}

Sozial:
{auswirkungen_sozial}

10. EINSCHRÄNKUNGEN DER GEHFÄHIGKEIT
{gehfaehigkeit_text}

11. AKTENEINSICHT
Im Falle einer Akteneinsicht kann dieser Befundbericht dem/der Antragsteller/in zur Einsicht gegeben werden?
{akteneinsicht_text}

12. ABSCHLUSS
Den Befundbericht bitte ich gemäß beiliegender Liquidation zu entschädigen.

Mit freundlichen Grüßen


___________________________
{arzt_daten.get('name', '')}"""

    return report
