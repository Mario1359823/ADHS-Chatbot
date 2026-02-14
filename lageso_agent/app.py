"""
LaGeSo Befundbericht Generator – Streamlit Hauptanwendung.
Lokale Web-App zur Erstellung strukturierter psychiatrischer Befundberichte.
"""

import streamlit as st
from datetime import date

from llm_client import OllamaClient
from extractor import extract_data
from report_builder import build_vorstellung, build_diagnosen, build_medikation
from docx_export import export_docx
from prompts import AMDP_KATEGORIEN, AMDP_LABELS

# --- Seiteneinstellungen ---
st.set_page_config(
    page_title="LaGeSo Befundbericht Generator",
    page_icon="\U0001f9e0",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    .stTextArea textarea {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
        line-height: 1.5;
    }
    div[data-testid="stSidebar"] {
        min-width: 320px;
    }
    .section-header {
        font-size: 16px;
        font-weight: bold;
        margin-top: 12px;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Session State initialisieren ---
def init_session_state():
    """Initialisiert alle Session-State-Variablen."""
    defaults = {
        # Arzt-Stammdaten
        "arzt_name": "Dr. med. Carsten Urbanek",
        "arzt_fachgebiet": "Facharzt für Psychiatrie und Psychotherapie",
        "arzt_adresse": "Bergmannstraße 5 | 10961 Berlin",
        "arzt_kontakt": "Tel.: 0 7000 / 4000 1000 | Fax: 0 7000 / 4000 1001",
        # Ollama
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3.1:8b",
        "ollama_connected": False,
        # Eingabe
        "patient_text": "",
        "patient_name": "",
        "geburtsdatum": "",
        "adresse": "",
        "aktenzeichen": "",
        "erstvorstellung": "",
        "letzte_vorstellung": "",
        "frequenz": "",
        # Generierte Abschnitte
        "generated": False,
        "section_vorstellung": "",
        "section_diagnosen": "",
        "section_befund": "",
        "section_medikation": "",
        "section_anamnese": "",
        "section_beurteilung": "",
        "befund_datum": "",
        # Rohdaten (für Qualitätsprüfung)
        "raw_data": None,
        # Status
        "generation_step": 0,
        "generation_status": "",
        "error_message": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# --- Hilfsfunktionen ---
def get_arzt_daten() -> dict:
    """Gibt die aktuellen Arzt-Stammdaten zurück."""
    return {
        "name": st.session_state.arzt_name,
        "fachgebiet": st.session_state.arzt_fachgebiet,
        "adresse": st.session_state.arzt_adresse,
        "kontakt": st.session_state.arzt_kontakt,
    }


def run_quality_checks() -> list[tuple[bool, str]]:
    """Führt die Qualitätsprüfungen durch.

    Returns:
        Liste von (bestanden, beschreibung) Tuples
    """
    checks = []
    raw = st.session_state.raw_data

    # 1. Alle 20 AMDP-Kategorien vorhanden
    if raw and "befund" in raw:
        befund = raw["befund"]
        all_present = all(
            befund.get(k) and befund[k] != "nicht erhoben"
            for k in AMDP_KATEGORIEN
        )
        # Auch prüfen: sind überhaupt alle Schlüssel da?
        all_keys = all(k in befund for k in AMDP_KATEGORIEN)
        checks.append((all_present, "Alle 20 AMDP-Kategorien erhoben"))
    else:
        checks.append((False, "Alle 20 AMDP-Kategorien erhoben"))

    # 2. Mindestens 1 ICD-10 Diagnose
    has_diag = bool(raw and raw.get("diagnosen"))
    checks.append((has_diag, "Mindestens 1 ICD-10 Diagnose"))

    # 3. Medikation vorhanden
    has_med = bool(raw and raw.get("medikation"))
    checks.append((has_med, "Medikation vorhanden"))

    # 4. Anamnese vorhanden
    has_anam = bool(
        st.session_state.section_anamnese
        and st.session_state.section_anamnese != "[BITTE ERGÄNZEN]"
    )
    checks.append((has_anam, "Anamnese vorhanden"))

    # 5. Beurteilung vorhanden
    has_beurt = bool(
        st.session_state.section_beurteilung
        and st.session_state.section_beurteilung != "[BITTE ERGÄNZEN]"
    )
    checks.append((has_beurt, "Beurteilung vorhanden"))

    # 6. Befund beginnt mit "Pat."
    starts_pat = st.session_state.section_befund.strip().startswith("Pat.")
    checks.append((starts_pat, 'Befund beginnt mit "Pat."'))

    return checks


# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    st.title("\u2699\ufe0f Einstellungen")

    # --- Ollama-Verbindung ---
    st.subheader("Ollama-Verbindung")
    st.session_state.ollama_model = st.text_input(
        "Modell",
        value=st.session_state.ollama_model,
        help="Name des Ollama-Modells (z.B. llama3.1:8b, mistral, etc.)",
    )
    st.session_state.ollama_url = st.text_input(
        "Ollama URL",
        value=st.session_state.ollama_url,
        help="URL des Ollama-Servers",
    )

    if st.button("Verbindung testen", use_container_width=True):
        client = OllamaClient(
            base_url=st.session_state.ollama_url,
            model=st.session_state.ollama_model,
        )
        ok, msg = client.test_connection()
        st.session_state.ollama_connected = ok
        if ok:
            st.success(msg)
        else:
            st.error(msg)

    st.divider()

    # --- Arzt-Stammdaten ---
    st.subheader("Arzt-Stammdaten")
    st.session_state.arzt_name = st.text_input(
        "Name", value=st.session_state.arzt_name
    )
    st.session_state.arzt_fachgebiet = st.text_input(
        "Fachgebiet", value=st.session_state.arzt_fachgebiet
    )
    st.session_state.arzt_adresse = st.text_input(
        "Adresse", value=st.session_state.arzt_adresse
    )
    st.session_state.arzt_kontakt = st.text_input(
        "Kontakt", value=st.session_state.arzt_kontakt
    )

    st.divider()

    # --- Generierungs-Status ---
    if st.session_state.generation_step > 0:
        st.subheader("Generierungs-Status")
        steps = [
            "Extraktion",
            "AMDP-Befund",
            "Anamnese",
            "Beurteilung",
        ]
        for i, step_name in enumerate(steps, 1):
            if i < st.session_state.generation_step:
                st.write(f"\u2705 {step_name}")
            elif i == st.session_state.generation_step:
                st.write(f"\u23f3 {step_name}...")
            else:
                st.write(f"\u2b1c {step_name}")

        st.divider()

    # --- Qualitäts-Checkliste ---
    if st.session_state.generated:
        st.subheader("Qualitäts-Checkliste")
        checks = run_quality_checks()
        for passed, desc in checks:
            icon = "\u2705" if passed else "\u274c"
            st.write(f"{icon} {desc}")


# ==========================================================
# HAUPTBEREICH
# ==========================================================
st.title("\U0001f9e0 LaGeSo Befundbericht Generator")
st.caption(
    "Erstellt strukturierte psychiatrische Befundberichte aus unstrukturiertem "
    "klinischen Text \u2013 lokal und DSGVO-konform mit Ollama."
)

# --- 2-Panel Layout ---
col_input, col_output = st.columns([1, 1], gap="large")

# ==========================================================
# LINKE SEITE: Eingabe
# ==========================================================
with col_input:
    st.header("Eingabe")

    # Freitext
    st.session_state.patient_text = st.text_area(
        "Klinischer Text (Arztnotizen, Befunde, Arztbriefe)",
        value=st.session_state.patient_text,
        height=300,
        placeholder=(
            "Fügen Sie hier den unstrukturierten klinischen Text ein...\n\n"
            "Beispiel: Pat. stellt sich erstmals in der Praxis vor. "
            "Bekannte Diagnose einer rezidivierenden depressiven Störung, "
            "gegenwärtig schwere Episode..."
        ),
    )

    # Metadaten
    st.subheader("Patientendaten")
    meta_col1, meta_col2 = st.columns(2)

    with meta_col1:
        st.session_state.patient_name = st.text_input(
            "Patientenname",
            value=st.session_state.patient_name,
            placeholder="Nachname, Vorname",
        )
        st.session_state.geburtsdatum = st.text_input(
            "Geburtsdatum",
            value=st.session_state.geburtsdatum,
            placeholder="TT.MM.JJJJ",
        )
        st.session_state.adresse = st.text_input(
            "Adresse",
            value=st.session_state.adresse,
            placeholder="Straße Nr., PLZ Ort",
        )

    with meta_col2:
        st.session_state.aktenzeichen = st.text_input(
            "Aktenzeichen",
            value=st.session_state.aktenzeichen,
            placeholder="Az. ...",
        )
        st.session_state.erstvorstellung = st.text_input(
            "Datum Erstvorstellung",
            value=st.session_state.erstvorstellung,
            placeholder="TT.MM.JJJJ",
        )
        st.session_state.letzte_vorstellung = st.text_input(
            "Datum letzte Vorstellung",
            value=st.session_state.letzte_vorstellung,
            placeholder="TT.MM.JJJJ",
        )

    st.session_state.frequenz = st.text_input(
        "Vorstellungsfrequenz",
        value=st.session_state.frequenz,
        placeholder="z.B. 14-tägig, monatlich, vierteljährlich",
    )

    # --- Generate Button ---
    st.markdown("---")

    generate_clicked = st.button(
        "\U0001f9e0 Bericht generieren",
        type="primary",
        use_container_width=True,
        disabled=not st.session_state.patient_text.strip(),
    )

    if generate_clicked:
        if not st.session_state.patient_text.strip():
            st.error("Bitte geben Sie einen klinischen Text ein.")
        else:
            st.session_state.error_message = ""
            st.session_state.generated = False

            client = OllamaClient(
                base_url=st.session_state.ollama_url,
                model=st.session_state.ollama_model,
            )

            # Verbindung prüfen
            ok, msg = client.test_connection()
            if not ok:
                st.error(f"Ollama nicht erreichbar: {msg}")
            else:
                progress_bar = st.progress(0, text="Starte Generierung...")
                status_text = st.empty()

                def update_progress(step: int, desc: str):
                    st.session_state.generation_step = step
                    st.session_state.generation_status = desc
                    progress_bar.progress(step / 4, text=desc)

                try:
                    result = extract_data(
                        client,
                        st.session_state.patient_text,
                        progress_callback=update_progress,
                    )

                    # Ergebnisse in Session State
                    st.session_state.raw_data = result["raw_data"]

                    st.session_state.section_vorstellung = build_vorstellung(
                        st.session_state.erstvorstellung,
                        st.session_state.letzte_vorstellung,
                        st.session_state.frequenz,
                    )
                    st.session_state.section_diagnosen = build_diagnosen(
                        result["diagnosen"]
                    )
                    st.session_state.section_befund = result["befund_text"]
                    st.session_state.befund_datum = (
                        st.session_state.letzte_vorstellung
                        or date.today().strftime("%d.%m.%Y")
                    )
                    st.session_state.section_medikation = build_medikation(
                        result["medikation"],
                        datum=st.session_state.letzte_vorstellung,
                    )
                    st.session_state.section_anamnese = result["anamnese_text"]
                    st.session_state.section_beurteilung = result["beurteilung_text"]
                    st.session_state.generated = True
                    st.session_state.generation_step = 4

                    progress_bar.progress(1.0, text="Bericht erfolgreich generiert!")
                    st.rerun()

                except ConnectionError as e:
                    st.error(str(e))
                except TimeoutError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Fehler bei der Generierung: {str(e)}")

    if st.session_state.error_message:
        st.error(st.session_state.error_message)


# ==========================================================
# RECHTE SEITE: Ergebnis
# ==========================================================
with col_output:
    st.header("Befundbericht")

    if not st.session_state.generated:
        st.info(
            "Geben Sie links einen klinischen Text ein und klicken Sie auf "
            '"\U0001f9e0 Bericht generieren", um den Befundbericht zu erstellen.'
        )
    else:
        # --- Editierbare Abschnitte ---

        # 1. Vorstellung
        st.markdown("**1. VORSTELLUNG**")
        st.session_state.section_vorstellung = st.text_area(
            "Vorstellung",
            value=st.session_state.section_vorstellung,
            height=100,
            label_visibility="collapsed",
            key="edit_vorstellung",
        )

        # 2. Diagnosen
        st.markdown("**2. DIAGNOSEN (ICD-10)**")
        st.session_state.section_diagnosen = st.text_area(
            "Diagnosen",
            value=st.session_state.section_diagnosen,
            height=100,
            label_visibility="collapsed",
            key="edit_diagnosen",
        )

        # 3. Psychopathologischer Befund
        st.markdown(
            f"**3. PSYCHOPATHOLOGISCHER BEFUND** "
            f"_(AMDP-System \u2013 letzter Befund vom "
            f"{st.session_state.befund_datum})_"
        )
        st.session_state.section_befund = st.text_area(
            "Befund",
            value=st.session_state.section_befund,
            height=250,
            label_visibility="collapsed",
            key="edit_befund",
        )

        # 4. Medikation
        st.markdown("**4. AKTUELLE MEDIKATION** _(nur psychopharmakologisch)_")
        st.session_state.section_medikation = st.text_area(
            "Medikation",
            value=st.session_state.section_medikation,
            height=120,
            label_visibility="collapsed",
            key="edit_medikation",
        )

        # 5. Anamnese
        st.markdown("**5. ANAMNESE UND BEHANDLUNGSVERLAUF**")
        st.session_state.section_anamnese = st.text_area(
            "Anamnese",
            value=st.session_state.section_anamnese,
            height=200,
            label_visibility="collapsed",
            key="edit_anamnese",
        )

        # 6. Beurteilung
        st.markdown("**6. SOZIALMEDIZINISCHE BEURTEILUNG**")
        st.session_state.section_beurteilung = st.text_area(
            "Beurteilung",
            value=st.session_state.section_beurteilung,
            height=200,
            label_visibility="collapsed",
            key="edit_beurteilung",
        )

        # --- Export Button ---
        st.markdown("---")

        export_col1, export_col2 = st.columns([1, 1])
        with export_col1:
            try:
                docx_bytes = export_docx(
                    arzt_daten=get_arzt_daten(),
                    patient_name=st.session_state.patient_name,
                    geburtsdatum=st.session_state.geburtsdatum,
                    adresse=st.session_state.adresse,
                    aktenzeichen=st.session_state.aktenzeichen,
                    vorstellung_text=st.session_state.section_vorstellung,
                    diagnosen_text=st.session_state.section_diagnosen,
                    befund_text=st.session_state.section_befund,
                    befund_datum=st.session_state.befund_datum,
                    medikation_text=st.session_state.section_medikation,
                    anamnese_text=st.session_state.section_anamnese,
                    beurteilung_text=st.session_state.section_beurteilung,
                )

                # Dateiname
                patient = st.session_state.patient_name.replace(" ", "_") or "Patient"
                filename = f"LaGeSo_Befundbericht_{patient}_{date.today().strftime('%Y%m%d')}.docx"

                st.download_button(
                    label="\U0001f4e5 Als DOCX exportieren",
                    data=docx_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary",
                )
            except Exception as e:
                st.error(f"Fehler beim Export: {str(e)}")
