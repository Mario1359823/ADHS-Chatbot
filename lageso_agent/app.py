"""
LaGeSo Befundbericht Generator – Streamlit Hauptanwendung.
Lokale Web-App zur Erstellung strukturierter psychiatrischer Befundberichte
nach dem CU-Standard (Dr. med. Carsten Urbanek).
Vollständige 12-Abschnitt-Struktur mit allen Pflichtfeldern.
"""

import streamlit as st
from datetime import date

from llm_client import OllamaClient
from extractor import extract_data
from report_builder import (
    build_diagnosen,
    build_gehfaehigkeit,
    build_medikation,
    build_psychosoziale_hilfen,
    build_verlauf,
    build_vorstellung,
    build_sucht,
)
from docx_export import export_docx
from prompts import AMDP_KATEGORIEN, AMDP_LABELS, AMDP_NORMALBEFUND

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
    .main .block-container { padding-top: 1.5rem; max-width: 1500px; }
    .stTextArea textarea {
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px; line-height: 1.5;
    }
    div[data-testid="stSidebar"] { min-width: 320px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- Session State initialisieren ---
def init_session_state():
    defaults = {
        # Arzt-Stammdaten
        "arzt_name": "Dr. med. Carsten Urbanek",
        "arzt_fachgebiet": "Facharzt für Psychiatrie und Psychotherapie",
        "arzt_adresse": "Bergmannstraße 5, 10961 Berlin",
        "arzt_kontakt": "Tel.: 0 7000 / 4000 1000 | Fax: 0 7000 / 4000 1001",
        # Ollama
        "ollama_url": "http://localhost:11434",
        "ollama_model": "llama3.1:8b",
        "ollama_connected": False,
        # Eingabe
        "patient_text": "",
        "patient_name": "",
        "geburtsdatum": "",
        "plz_ort": "",
        "strasse": "",
        "aktenzeichen": "",
        "erstvorstellung": "",
        "letzte_vorstellung": "",
        "frequenz": "",
        # Generierte Abschnitte (12 Abschnitte)
        "generated": False,
        "sect_vorstellung": "",
        "sect_diagnosen": "",
        "sect_befund": "",
        "befund_datum": "",
        "sect_medikation": "",
        "sect_verlauf": "",
        "sect_sucht": "",
        "sect_behandlungen": "",
        "sect_psychosoziale": "",
        "sect_ausw_alltag": "",
        "sect_ausw_beruf": "",
        "sect_ausw_sozial": "",
        "sect_gehfaehigkeit": "",
        "sect_akteneinsicht": "",
        # Psychosoziale Hilfen (Checkboxen)
        "psh_betreuung": False,
        "psh_betreuung_bereiche": "",
        "psh_einzelhilfe": False,
        "psh_betreutes_wohnen": False,
        "psh_heimunterbringung": False,
        "psh_pflegegrad": "keiner",
        "psh_au": False,
        "psh_au_seit": "",
        "psh_berentung": False,
        "psh_berentung_seit": "",
        # Gehfähigkeit
        "geh_eingeschraenkt": False,
        "geh_beschreibung": "",
        # Akteneinsicht
        "akteneinsicht_ja": True,
        "akteneinsicht_begruendung": "",
        # Rohdaten
        "raw_data": None,
        "verlauf_data": {},
        "sucht_data": {},
        # Status
        "generation_step": 0,
        "generation_status": "",
        "error_message": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


def get_arzt_daten() -> dict:
    return {
        "name": st.session_state.arzt_name,
        "fachgebiet": st.session_state.arzt_fachgebiet,
        "adresse": st.session_state.arzt_adresse,
        "kontakt": st.session_state.arzt_kontakt,
    }


def run_quality_checks() -> list[tuple[bool, str]]:
    """CU-Standard Qualitätsprüfungen."""
    checks = []
    raw = st.session_state.raw_data
    befund_text = st.session_state.sect_befund

    # 1. AMDP als Fließtext (nicht nummeriert)
    is_fliesstext = befund_text and not any(
        befund_text.strip().startswith(f"{i}.") for i in range(1, 21)
    )
    checks.append((is_fliesstext, "AMDP-Befund als Fließtext (nicht nummeriert)"))

    # 2. AMDP beginnt mit "Pat."
    starts_pat = befund_text.strip().startswith("Pat.") if befund_text else False
    checks.append((starts_pat, 'AMDP-Befund beginnt mit "Pat."'))

    # 3. BMI im AMDP-Befund erwähnt
    has_bmi = "BMI" in befund_text if befund_text else False
    checks.append((has_bmi, "BMI im AMDP-Befund angegeben"))

    # 4. Mindestens 1 ICD-10 Diagnose
    has_diag = bool(raw and raw.get("diagnosen"))
    checks.append((has_diag, "Mindestens 1 ICD-10 Diagnose"))

    # 5. Medikation vorhanden
    has_med = bool(raw and raw.get("medikation"))
    checks.append((has_med, "Psychopharmakologische Medikation dokumentiert"))

    # 6. Nur Psychopharmaka (keine somatische Medikation)
    somatisch_keywords = ["levothyroxin", "metformin", "ramipril", "ibuprofen", "pantoprazol"]
    med_text = st.session_state.sect_medikation.lower()
    no_somatic = not any(kw in med_text for kw in somatisch_keywords)
    checks.append((no_somatic, "Keine somatische Medikation"))

    # 7. Verlauf vorhanden
    has_verlauf = bool(
        st.session_state.sect_verlauf
        and st.session_state.sect_verlauf != "[BITTE ERGÄNZEN]"
    )
    checks.append((has_verlauf, "Verlauf der Erkrankung vorhanden"))

    # 8. Auswirkungen vorhanden (mind. Alltag)
    has_ausw = bool(
        st.session_state.sect_ausw_alltag
        and st.session_state.sect_ausw_alltag != "[BITTE ERGÄNZEN]"
    )
    checks.append((has_ausw, "Krankheitsbedingte Auswirkungen vorhanden"))

    # 9. Sprache auf Deutsch (kein Denglisch)
    denglisch = ["improvement", "musculoskeletal", "treatment", "assessment"]
    all_text = " ".join([
        st.session_state.sect_befund,
        st.session_state.sect_verlauf,
        st.session_state.sect_ausw_alltag,
    ]).lower()
    no_denglisch = not any(w in all_text for w in denglisch)
    checks.append((no_denglisch, "Keine Denglisch-Begriffe"))

    return checks


# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    st.title("\u2699\ufe0f Einstellungen")

    # --- Ollama-Verbindung ---
    st.subheader("Ollama-Verbindung")
    st.session_state.ollama_model = st.text_input(
        "Modell", value=st.session_state.ollama_model,
        help="z.B. llama3.1:8b, mistral, gemma2:9b",
    )
    st.session_state.ollama_url = st.text_input(
        "Ollama URL", value=st.session_state.ollama_url,
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
    st.session_state.arzt_name = st.text_input("Name", value=st.session_state.arzt_name)
    st.session_state.arzt_fachgebiet = st.text_input("Fachgebiet", value=st.session_state.arzt_fachgebiet)
    st.session_state.arzt_adresse = st.text_input("Adresse", value=st.session_state.arzt_adresse)
    st.session_state.arzt_kontakt = st.text_input("Kontakt", value=st.session_state.arzt_kontakt)

    st.divider()

    # --- Generierungs-Status ---
    if st.session_state.generation_step > 0:
        st.subheader("Generierungs-Status")
        steps = ["Extraktion", "AMDP-Befund", "Verlauf/Sucht", "Auswirkungen"]
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
        passed = sum(1 for c, _ in checks if c)
        st.progress(passed / len(checks), text=f"{passed}/{len(checks)} bestanden")
        for ok, desc in checks:
            icon = "\u2705" if ok else "\u274c"
            st.write(f"{icon} {desc}")


# ==========================================================
# HAUPTBEREICH
# ==========================================================
st.title("\U0001f9e0 LaGeSo Befundbericht Generator")
st.caption(
    "Erstellt strukturierte psychiatrische Befundberichte (CU-Standard) aus "
    "unstrukturiertem klinischen Text \u2013 lokal und DSGVO-konform mit Ollama. "
    "Anforderungszeitraum: 2 Jahre."
)

col_input, col_output = st.columns([1, 1], gap="large")

# ==========================================================
# LINKE SEITE: Eingabe
# ==========================================================
with col_input:
    st.header("Eingabe")

    st.session_state.patient_text = st.text_area(
        "Klinischer Text (Arztnotizen, Befunde, Arztbriefe)",
        value=st.session_state.patient_text,
        height=300,
        placeholder=(
            "Fügen Sie hier den unstrukturierten klinischen Text ein...\n\n"
            "Beispiel: Pat. stellt sich erstmals in der Praxis vor. "
            "Bekannte Diagnose einer rezidivierenden depressiven Störung, "
            "gegenwärtig schwere Episode. Medikation: Escitalopram 10mg 1-0-0-0..."
        ),
    )

    # --- Patientendaten ---
    st.subheader("Patientendaten")
    mc1, mc2 = st.columns(2)
    with mc1:
        st.session_state.patient_name = st.text_input(
            "Patientenname", value=st.session_state.patient_name,
            placeholder="Vorname Nachname",
        )
        st.session_state.geburtsdatum = st.text_input(
            "Geburtsdatum", value=st.session_state.geburtsdatum,
            placeholder="TT.MM.JJJJ",
        )
        st.session_state.plz_ort = st.text_input(
            "PLZ und Ort", value=st.session_state.plz_ort,
            placeholder="10961 Berlin",
        )
    with mc2:
        st.session_state.strasse = st.text_input(
            "Straße und Hausnummer", value=st.session_state.strasse,
            placeholder="Musterstraße 1",
        )
        st.session_state.aktenzeichen = st.text_input(
            "Aktenzeichen", value=st.session_state.aktenzeichen,
            placeholder="z.B. DO5 4121849",
        )

    # --- Vorstellungsdaten ---
    st.subheader("Vorstellung")
    vc1, vc2 = st.columns(2)
    with vc1:
        st.session_state.erstvorstellung = st.text_input(
            "Erstvorstellung", value=st.session_state.erstvorstellung,
            placeholder="TT.MM.JJJJ",
        )
        st.session_state.letzte_vorstellung = st.text_input(
            "Letzte Vorstellung", value=st.session_state.letzte_vorstellung,
            placeholder="TT.MM.JJJJ",
        )
    with vc2:
        st.session_state.frequenz = st.text_input(
            "Vorstellungsfrequenz", value=st.session_state.frequenz,
            placeholder="z.B. 2-4x/Jahr, monatlich, vierteljährlich",
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

            ok, msg = client.test_connection()
            if not ok:
                st.error(f"Ollama nicht erreichbar: {msg}")
            else:
                progress_bar = st.progress(0, text="Starte Generierung...")

                def update_progress(step: int, desc: str):
                    st.session_state.generation_step = step
                    st.session_state.generation_status = desc
                    progress_bar.progress(step / 4, text=desc)

                try:
                    result = extract_data(
                        client, st.session_state.patient_text,
                        progress_callback=update_progress,
                    )

                    # Rohdaten speichern
                    st.session_state.raw_data = result["raw_data"]
                    st.session_state.verlauf_data = result.get("verlauf", {})
                    st.session_state.sucht_data = result.get("sucht", {})

                    # 1. Vorstellung
                    st.session_state.sect_vorstellung = build_vorstellung(
                        st.session_state.erstvorstellung,
                        st.session_state.letzte_vorstellung,
                        st.session_state.frequenz,
                    )

                    # 2. Diagnosen
                    st.session_state.sect_diagnosen = build_diagnosen(result["diagnosen"])

                    # 3. Befund
                    st.session_state.sect_befund = result["befund_text"]
                    st.session_state.befund_datum = (
                        st.session_state.letzte_vorstellung
                        or date.today().strftime("%d.%m.%Y")
                    )

                    # 4. Medikation
                    st.session_state.sect_medikation = build_medikation(result["medikation"])

                    # 5. Verlauf
                    verlauf = result.get("verlauf", {})
                    st.session_state.sect_verlauf = build_verlauf(
                        verlauf, result.get("verlauf_text", "")
                    )

                    # 6. Sucht
                    sucht = result.get("sucht", {})
                    st.session_state.sect_sucht = build_sucht(
                        sucht, result.get("sucht_text", "")
                    )

                    # 7. Behandlungen
                    st.session_state.sect_behandlungen = result.get("behandlungen_text", "")

                    # 8. Psychosoziale Hilfen (Standardwerte, vom Arzt auszufüllen)
                    st.session_state.sect_psychosoziale = build_psychosoziale_hilfen({
                        "betreuung": st.session_state.psh_betreuung,
                        "betreuung_bereiche": st.session_state.psh_betreuung_bereiche,
                        "einzelhilfe": st.session_state.psh_einzelhilfe,
                        "betreutes_wohnen": st.session_state.psh_betreutes_wohnen,
                        "heimunterbringung": st.session_state.psh_heimunterbringung,
                        "pflegegrad": st.session_state.psh_pflegegrad,
                        "au_psychisch": st.session_state.psh_au,
                        "au_seit": st.session_state.psh_au_seit,
                        "berentung": st.session_state.psh_berentung,
                        "berentung_seit": st.session_state.psh_berentung_seit,
                    })

                    # 9. Auswirkungen
                    st.session_state.sect_ausw_alltag = result.get("auswirkungen_alltag", "[BITTE ERGÄNZEN]")
                    st.session_state.sect_ausw_beruf = result.get("auswirkungen_beruf", "[BITTE ERGÄNZEN]")
                    st.session_state.sect_ausw_sozial = result.get("auswirkungen_sozial", "[BITTE ERGÄNZEN]")

                    # 10. Gehfähigkeit
                    st.session_state.sect_gehfaehigkeit = build_gehfaehigkeit(
                        st.session_state.geh_eingeschraenkt,
                        st.session_state.geh_beschreibung,
                    )

                    # 11. Akteneinsicht
                    if st.session_state.akteneinsicht_ja:
                        st.session_state.sect_akteneinsicht = "Ja"
                    else:
                        st.session_state.sect_akteneinsicht = (
                            f"Nein - Begründung: "
                            f"{st.session_state.akteneinsicht_begruendung or '[FEHLT]'}"
                        )

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
# RECHTE SEITE: Ergebnis (12 Abschnitte)
# ==========================================================
with col_output:
    st.header("Befundbericht")

    if not st.session_state.generated:
        st.info(
            "Geben Sie links einen klinischen Text ein und klicken Sie auf "
            '"\U0001f9e0 Bericht generieren".'
        )
        with st.expander("AMDP-Normalbefund (Vorlage)"):
            st.text(AMDP_NORMALBEFUND)
    else:
        # === 1. VORSTELLUNG ===
        st.markdown("**1. VORSTELLUNG**")
        st.session_state.sect_vorstellung = st.text_area(
            "Vorstellung", value=st.session_state.sect_vorstellung,
            height=90, label_visibility="collapsed", key="e_vorstellung",
        )

        # === 2. DIAGNOSEN ===
        st.markdown("**2. DIAGNOSEN (ICD-10)**")
        st.caption("Format: ICD-Code (Diagnosetext). F33.2 = ohne Psychose, F33.3 = mit Psychose.")
        st.session_state.sect_diagnosen = st.text_area(
            "Diagnosen", value=st.session_state.sect_diagnosen,
            height=100, label_visibility="collapsed", key="e_diagnosen",
        )

        # === 3. PSYCHOPATHOLOGISCHER BEFUND ===
        st.markdown(
            f"**3. PSYCHOPATHOLOGISCHER BEFUND** "
            f"_(AMDP-System, Datum: {st.session_state.befund_datum})_"
        )
        st.caption(
            "Fließtext, NICHT nummeriert! 20 Kategorien: Bewusstsein \u2192 Stimmung \u2192 "
            "Affekt \u2192 Konzentration \u2192 Merkfähigkeit \u2192 Interesse \u2192 "
            "Formales Denken \u2192 Inhaltliches Denken \u2192 Wahrnehmung+Ich-Störungen \u2192 "
            "Zwänge/Phobien \u2192 Antrieb \u2192 Psychomotorik \u2192 Schlaf \u2192 "
            "Appetit \u2192 Gewicht \u2192 BMI \u2192 Suizidalität \u2192 "
            "Eigen-/Fremdgefährdung \u2192 Psychopharm. Vorbehandlung"
        )
        st.session_state.sect_befund = st.text_area(
            "Befund", value=st.session_state.sect_befund,
            height=250, label_visibility="collapsed", key="e_befund",
        )

        # === 4. MEDIKATION ===
        st.markdown("**4. AKTUELLE MEDIKATION** _(nur psychopharmakologisch)_")
        st.caption("Format: DATUM MEDIKAMENT DOSIS SCHEMA (z.B. 13.01.2026 MIRTAZAPIN 15MG 0-0-0-0,5)")
        st.session_state.sect_medikation = st.text_area(
            "Medikation", value=st.session_state.sect_medikation,
            height=120, label_visibility="collapsed", key="e_medikation",
        )

        # === 5. VERLAUF DER ERKRANKUNG ===
        st.markdown("**5. VERLAUF DER ERKRANKUNG**")
        st.session_state.sect_verlauf = st.text_area(
            "Verlauf", value=st.session_state.sect_verlauf,
            height=180, label_visibility="collapsed", key="e_verlauf",
        )

        # === 6. BEI SUCHTERKRANKUNG ===
        st.markdown("**6. BEI SUCHTERKRANKUNG**")
        st.caption("Bei Sucht: Konsummuster, letzter Konsum, Entzugssymptomatik, stationäre Behandlung, Abstinenzstatus, aktuelle Anbindung.")
        st.session_state.sect_sucht = st.text_area(
            "Suchterkrankung", value=st.session_state.sect_sucht,
            height=120, label_visibility="collapsed", key="e_sucht",
        )

        # === 7. SONSTIGE BEHANDLUNGEN ===
        st.markdown("**7. SONSTIGE BEHANDLUNGEN** _(wo?, wann?)_")
        st.caption("NUR psychiatrische/psychotherapeutische Behandlungen. KEINE Physiotherapie.")
        st.session_state.sect_behandlungen = st.text_area(
            "Behandlungen", value=st.session_state.sect_behandlungen,
            height=120, label_visibility="collapsed", key="e_behandlungen",
        )

        # === 8. PSYCHOSOZIALE HILFEN ===
        st.markdown("**8. PSYCHOSOZIALE HILFEN**")
        with st.expander("Psychosoziale Hilfen bearbeiten", expanded=False):
            pc1, pc2 = st.columns(2)
            with pc1:
                st.session_state.psh_betreuung = st.checkbox(
                    "Gesetzliche Betreuung", value=st.session_state.psh_betreuung,
                    key="cb_betreuung",
                )
                if st.session_state.psh_betreuung:
                    st.session_state.psh_betreuung_bereiche = st.text_input(
                        "Für welche Bereiche?", value=st.session_state.psh_betreuung_bereiche,
                        key="ti_betreuung_bereiche",
                    )
                st.session_state.psh_einzelhilfe = st.checkbox(
                    "Einzelhilfe", value=st.session_state.psh_einzelhilfe, key="cb_einzelhilfe",
                )
                st.session_state.psh_betreutes_wohnen = st.checkbox(
                    "Betreutes Wohnen", value=st.session_state.psh_betreutes_wohnen,
                    key="cb_betreutes_wohnen",
                )
                st.session_state.psh_heimunterbringung = st.checkbox(
                    "Heimunterbringung", value=st.session_state.psh_heimunterbringung,
                    key="cb_heimunterbringung",
                )
            with pc2:
                st.session_state.psh_pflegegrad = st.selectbox(
                    "Pflegegrad",
                    options=["keiner", "1", "2", "3", "4", "5"],
                    index=["keiner", "1", "2", "3", "4", "5"].index(
                        st.session_state.psh_pflegegrad
                    ),
                    key="sel_pflegegrad",
                )
                st.session_state.psh_au = st.checkbox(
                    "AU wegen psych. Erkrankung", value=st.session_state.psh_au,
                    key="cb_au",
                )
                if st.session_state.psh_au:
                    st.session_state.psh_au_seit = st.text_input(
                        "AU seit:", value=st.session_state.psh_au_seit, key="ti_au_seit",
                    )
                st.session_state.psh_berentung = st.checkbox(
                    "Berentung wegen psych. Erkrankung",
                    value=st.session_state.psh_berentung, key="cb_berentung",
                )
                if st.session_state.psh_berentung:
                    st.session_state.psh_berentung_seit = st.text_input(
                        "Berentung seit:", value=st.session_state.psh_berentung_seit,
                        key="ti_berentung_seit",
                    )

            # Rebuild text from checkboxes
            st.session_state.sect_psychosoziale = build_psychosoziale_hilfen({
                "betreuung": st.session_state.psh_betreuung,
                "betreuung_bereiche": st.session_state.psh_betreuung_bereiche,
                "einzelhilfe": st.session_state.psh_einzelhilfe,
                "betreutes_wohnen": st.session_state.psh_betreutes_wohnen,
                "heimunterbringung": st.session_state.psh_heimunterbringung,
                "pflegegrad": st.session_state.psh_pflegegrad,
                "au_psychisch": st.session_state.psh_au,
                "au_seit": st.session_state.psh_au_seit,
                "berentung": st.session_state.psh_berentung,
                "berentung_seit": st.session_state.psh_berentung_seit,
            })

        st.text_area(
            "Psychosoziale Hilfen (Vorschau)",
            value=st.session_state.sect_psychosoziale,
            height=100, disabled=True, label_visibility="collapsed",
            key="e_psychosoziale_preview",
        )

        # === 9. KRANKHEITSBEDINGTE AUSWIRKUNGEN ===
        st.markdown("**9. KRANKHEITSBEDINGTE AUSWIRKUNGEN**")

        st.caption("**Alltag:**")
        st.session_state.sect_ausw_alltag = st.text_area(
            "Alltag", value=st.session_state.sect_ausw_alltag,
            height=100, label_visibility="collapsed", key="e_ausw_alltag",
        )
        st.caption("**Beruf:**")
        st.session_state.sect_ausw_beruf = st.text_area(
            "Beruf", value=st.session_state.sect_ausw_beruf,
            height=100, label_visibility="collapsed", key="e_ausw_beruf",
        )
        st.caption("**Sozial:**")
        st.session_state.sect_ausw_sozial = st.text_area(
            "Sozial", value=st.session_state.sect_ausw_sozial,
            height=100, label_visibility="collapsed", key="e_ausw_sozial",
        )

        # === 10. EINSCHRÄNKUNGEN DER GEHFÄHIGKEIT ===
        st.markdown("**10. EINSCHRÄNKUNGEN DER GEHFÄHIGKEIT**")
        gc1, gc2 = st.columns([1, 3])
        with gc1:
            st.session_state.geh_eingeschraenkt = st.checkbox(
                "Eingeschränkt", value=st.session_state.geh_eingeschraenkt,
                key="cb_geh",
            )
        with gc2:
            if st.session_state.geh_eingeschraenkt:
                st.session_state.geh_beschreibung = st.text_input(
                    "Inwiefern?", value=st.session_state.geh_beschreibung,
                    key="ti_geh_beschr",
                )
        st.session_state.sect_gehfaehigkeit = build_gehfaehigkeit(
            st.session_state.geh_eingeschraenkt,
            st.session_state.geh_beschreibung,
        )

        # === 11. AKTENEINSICHT ===
        st.markdown("**11. AKTENEINSICHT**")
        st.session_state.akteneinsicht_ja = st.checkbox(
            "Kann zur Einsicht gegeben werden", value=st.session_state.akteneinsicht_ja,
            key="cb_akteneinsicht",
        )
        if not st.session_state.akteneinsicht_ja:
            st.session_state.akteneinsicht_begruendung = st.text_input(
                "Begründung (pflicht bei Nein):",
                value=st.session_state.akteneinsicht_begruendung,
                key="ti_akteneinsicht_begr",
            )
        if st.session_state.akteneinsicht_ja:
            st.session_state.sect_akteneinsicht = "Ja"
        else:
            st.session_state.sect_akteneinsicht = (
                f"Nein - Begründung: "
                f"{st.session_state.akteneinsicht_begruendung or '[FEHLT]'}"
            )

        # === 12. ABSCHLUSS === (fester Text)
        st.markdown("**12. ABSCHLUSS**")
        st.text(
            "Den Befundbericht bitte ich gemäß beiliegender Liquidation "
            "zu entschädigen.\n\nMit freundlichen Grüßen\n\n"
            f"{st.session_state.arzt_name}"
        )

        # === EXPORT ===
        st.markdown("---")
        try:
            docx_bytes = export_docx(
                arzt_daten=get_arzt_daten(),
                patient_name=st.session_state.patient_name,
                geburtsdatum=st.session_state.geburtsdatum,
                plz_ort=st.session_state.plz_ort,
                strasse=st.session_state.strasse,
                aktenzeichen=st.session_state.aktenzeichen,
                vorstellung_text=st.session_state.sect_vorstellung,
                diagnosen_text=st.session_state.sect_diagnosen,
                befund_text=st.session_state.sect_befund,
                befund_datum=st.session_state.befund_datum,
                medikation_text=st.session_state.sect_medikation,
                verlauf_text=st.session_state.sect_verlauf,
                sucht_text=st.session_state.sect_sucht,
                behandlungen_text=st.session_state.sect_behandlungen,
                psychosoziale_hilfen_text=st.session_state.sect_psychosoziale,
                auswirkungen_alltag=st.session_state.sect_ausw_alltag,
                auswirkungen_beruf=st.session_state.sect_ausw_beruf,
                auswirkungen_sozial=st.session_state.sect_ausw_sozial,
                gehfaehigkeit_text=st.session_state.sect_gehfaehigkeit,
                akteneinsicht_text=st.session_state.sect_akteneinsicht,
            )

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
