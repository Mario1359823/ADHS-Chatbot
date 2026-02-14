"""
DOCX-Export im CU-Standard für den LaGeSo-Befundbericht.
Formatierung: Arial 11pt, Überschriften fett 12pt, Kopfzeile 13pt.
"""

import io
from datetime import date

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor


def _set_run_font(run, size=11, bold=False, font_name="Arial"):
    """Setzt Schriftart-Eigenschaften für einen Run."""
    run.font.name = font_name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)


def _add_paragraph(doc, text, size=11, bold=False, alignment=None, spacing_after=6):
    """Fügt einen formatierten Absatz hinzu."""
    para = doc.add_paragraph()
    if alignment is not None:
        para.alignment = alignment
    para.paragraph_format.space_after = Pt(spacing_after)
    para.paragraph_format.space_before = Pt(0)

    run = para.add_run(text)
    _set_run_font(run, size=size, bold=bold)
    return para


def _add_fliesstext(doc, text, spacing_after=6):
    """Fügt einen Fließtext-Absatz mit Zeilenabstand 1.3 hinzu."""
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(spacing_after)
    para.paragraph_format.space_before = Pt(0)
    para.paragraph_format.line_spacing = 1.3

    run = para.add_run(text)
    _set_run_font(run, size=11)
    return para


def export_docx(
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
) -> bytes:
    """Exportiert den Bericht als DOCX und gibt die Bytes zurück.

    Returns:
        DOCX-Datei als bytes
    """
    doc = Document()

    # --- Seitenränder ---
    for section in doc.sections:
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)

    # --- Kopfzeile: Arzt-Stammdaten ---
    _add_paragraph(
        doc,
        arzt_daten.get("name", ""),
        size=13,
        bold=True,
        spacing_after=2,
    )
    _add_paragraph(
        doc,
        arzt_daten.get("fachgebiet", ""),
        size=10,
        spacing_after=2,
    )
    _add_paragraph(
        doc,
        arzt_daten.get("adresse", ""),
        size=10,
        spacing_after=2,
    )
    _add_paragraph(
        doc,
        arzt_daten.get("kontakt", ""),
        size=10,
        spacing_after=12,
    )

    # --- Datum rechtsbündig ---
    heute = date.today().strftime("%d.%m.%Y")
    _add_paragraph(
        doc,
        f"Berlin, den {heute}",
        size=11,
        alignment=WD_ALIGN_PARAGRAPH.RIGHT,
        spacing_after=12,
    )

    # --- Titel ---
    _add_paragraph(
        doc,
        "Anlage zur Auskunft über die ärztliche Behandlung (LaGeSo)",
        size=11,
        bold=True,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
        spacing_after=2,
    )
    _add_paragraph(
        doc,
        "Psychiatrischer/psychotherapeutischer Befundbericht",
        size=11,
        bold=True,
        alignment=WD_ALIGN_PARAGRAPH.CENTER,
        spacing_after=12,
    )

    # --- Patienten-Kopf ---
    _add_paragraph(
        doc,
        f"Patient/in {patient_name or '[Name]'}, "
        f"geb. am {geburtsdatum or '[Geburtsdatum]'}, "
        f"wohnhaft in {adresse or '[Adresse]'}",
        size=11,
        spacing_after=2,
    )
    _add_paragraph(
        doc,
        f"Aktenzeichen: {aktenzeichen or '[Aktenzeichen]'}",
        size=11,
        spacing_after=12,
    )

    # --- 1. Vorstellung ---
    _add_paragraph(doc, "1. VORSTELLUNG", size=12, bold=True, spacing_after=6)
    for line in vorstellung_text.strip().split("\n"):
        line = line.strip()
        if line:
            _add_paragraph(doc, f"\u2022 {line}", size=11, spacing_after=2)

    # Abstand
    _add_paragraph(doc, "", size=6, spacing_after=6)

    # --- 2. Diagnosen ---
    _add_paragraph(doc, "2. DIAGNOSEN (ICD-10)", size=12, bold=True, spacing_after=6)
    for line in diagnosen_text.strip().split("\n"):
        line = line.strip()
        if line:
            _add_paragraph(doc, f"\u2022 {line}", size=11, spacing_after=2)

    _add_paragraph(doc, "", size=6, spacing_after=6)

    # --- 3. Psychopathologischer Befund ---
    _add_paragraph(
        doc,
        "3. PSYCHOPATHOLOGISCHER BEFUND",
        size=12,
        bold=True,
        spacing_after=2,
    )
    _add_paragraph(
        doc,
        f"(AMDP-System \u2013 letzter Befund vom {befund_datum or heute})",
        size=10,
        spacing_after=6,
    )
    _add_fliesstext(doc, befund_text, spacing_after=12)

    # --- 4. Medikation ---
    _add_paragraph(
        doc,
        "4. AKTUELLE MEDIKATION (nur psychopharmakologisch)",
        size=12,
        bold=True,
        spacing_after=6,
    )
    for line in medikation_text.strip().split("\n"):
        line = line.strip()
        if line:
            if line.startswith("("):
                _add_paragraph(doc, line, size=10, spacing_after=2)
            else:
                _add_paragraph(doc, f"\u2022 {line}", size=11, spacing_after=2)

    _add_paragraph(doc, "", size=6, spacing_after=6)

    # --- 5. Anamnese ---
    _add_paragraph(
        doc,
        "5. ANAMNESE UND BEHANDLUNGSVERLAUF",
        size=12,
        bold=True,
        spacing_after=6,
    )
    _add_fliesstext(doc, anamnese_text, spacing_after=12)

    # --- 6. Beurteilung ---
    _add_paragraph(
        doc,
        "6. SOZIALMEDIZINISCHE BEURTEILUNG",
        size=12,
        bold=True,
        spacing_after=6,
    )
    _add_fliesstext(doc, beurteilung_text, spacing_after=24)

    # --- Unterschrift ---
    _add_paragraph(doc, "", spacing_after=24)
    _add_paragraph(doc, "___________________________", size=11, spacing_after=2)
    _add_paragraph(
        doc,
        arzt_daten.get("name", ""),
        size=11,
        spacing_after=0,
    )

    # --- In Bytes konvertieren ---
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
