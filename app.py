"""
Application web Streamlit pour l'analyse de fiches de paie.
Interface premium accessible pour les salaries.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import json
from analyse.analyzer import analyser_fiche
from payslip_explainer import find_knowledge


# ============================================================
# CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="PaySlip Analyzer",
    page_icon="./app/static/favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# DESIGN SYSTEM - CSS PREMIUM
# ============================================================
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="PaySlip Analyzer">
<meta name="application-name" content="PaySlip Analyzer">
<meta name="theme-color" content="#6C63FF">
<meta name="msapplication-TileColor" content="#6C63FF">
<link rel="manifest" href="./app/static/manifest.json">
<link rel="apple-touch-icon" sizes="180x180" href="./app/static/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="./app/static/favicon.png">
<link rel="icon" type="image/png" sizes="192x192" href="./app/static/icon-192x192.png">
<style>
    /* --- Import Google Fonts --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* --- Global --- */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp {
        background: linear-gradient(180deg, #0E1117 0%, #131620 50%, #0E1117 100%);
    }

    /* --- Hide Streamlit branding --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* --- Hero Header --- */
    .hero {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        margin-bottom: 1rem;
    }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(108,99,255,0.15), rgba(78,205,196,0.15));
        border: 1px solid rgba(108,99,255,0.3);
        border-radius: 50px;
        padding: 0.4rem 1.2rem;
        font-size: 0.78rem;
        font-weight: 600;
        color: #8B83FF;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .hero h1 {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #B8B5FF 50%, #6C63FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
        line-height: 1.2;
    }
    .hero p {
        font-size: 1.1rem;
        color: #8892A5;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* --- Glassmorphism Cards --- */
    .glass-card {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.75rem 0;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(108,99,255,0.3);
        box-shadow: 0 8px 32px rgba(108,99,255,0.1);
    }

    /* --- Metric Cards --- */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        flex: 1;
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(108,99,255,0.4);
        box-shadow: 0 12px 40px rgba(108,99,255,0.15);
    }
    .metric-card.accent-blue { border-top: 3px solid #6C63FF; }
    .metric-card.accent-red { border-top: 3px solid #FF6B6B; }
    .metric-card.accent-amber { border-top: 3px solid #FFB84D; }
    .metric-card.accent-green { border-top: 3px solid #4ECDC4; }

    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #FAFAFA;
        line-height: 1.2;
    }
    .metric-value.blue { color: #8B83FF; }
    .metric-value.red { color: #FF6B6B; }
    .metric-value.amber { color: #FFB84D; }
    .metric-value.green { color: #4ECDC4; }

    /* --- Section Headers --- */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #FAFAFA;
        margin: 2rem 0 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(108,99,255,0.3);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-header .icon {
        font-size: 1.5rem;
    }

    /* --- Upload Zone --- */
    [data-testid="stFileUploader"] {
        background: rgba(108,99,255,0.04);
        border: 2px dashed rgba(108,99,255,0.25);
        border-radius: 16px;
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(108,99,255,0.5);
        background: rgba(108,99,255,0.08);
    }

    /* --- Buttons --- */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6C63FF, #5A52E0) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(108,99,255,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(108,99,255,0.4) !important;
    }
    .stDownloadButton > button {
        background: rgba(78,205,196,0.1) !important;
        border: 1px solid rgba(78,205,196,0.3) !important;
        border-radius: 12px !important;
        color: #4ECDC4 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(78,205,196,0.2) !important;
        border-color: #4ECDC4 !important;
    }

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        color: #8892A5;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(108,99,255,0.15) !important;
        color: #8B83FF !important;
    }

    /* --- Expanders --- */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        font-weight: 500;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(108,99,255,0.08);
    }

    /* --- DataFrames --- */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        overflow: hidden;
    }

    /* --- Success/Error messages --- */
    .success-banner {
        background: linear-gradient(135deg, rgba(78,205,196,0.1), rgba(78,205,196,0.05));
        border: 1px solid rgba(78,205,196,0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #4ECDC4;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 1rem 0;
    }
    .error-banner {
        background: linear-gradient(135deg, rgba(255,107,107,0.1), rgba(255,107,107,0.05));
        border: 1px solid rgba(255,107,107,0.3);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #FF6B6B;
        font-weight: 500;
        margin: 0.5rem 0;
    }
    .info-banner {
        background: linear-gradient(135deg, rgba(108,99,255,0.1), rgba(108,99,255,0.05));
        border: 1px solid rgba(108,99,255,0.25);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        color: #8B83FF;
        font-weight: 500;
        margin: 1rem 0;
    }

    /* --- Formula Box --- */
    .formula-box {
        background: linear-gradient(135deg, rgba(108,99,255,0.08), rgba(78,205,196,0.05));
        border: 1px solid rgba(108,99,255,0.2);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-family: 'Inter', monospace;
        font-size: 0.9rem;
        color: #B8B5FF;
        margin: 0.75rem 0;
    }
    .formula-box .result {
        font-size: 1.2rem;
        font-weight: 700;
        color: #4ECDC4;
    }
    .formula-line {
        padding: 0.2rem 0;
    }
    .formula-op {
        display: inline-block;
        width: 1.2rem;
        font-weight: 700;
        color: #8B83FF;
    }
    .formula-total {
        border-top: 1px solid rgba(108,99,255,0.3);
        margin-top: 0.4rem;
        padding-top: 0.5rem;
    }

    /* --- Explanation Cards --- */
    .explanation-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.5rem 0;
        border-left: 3px solid #6C63FF;
    }
    .explanation-card .tag {
        display: inline-block;
        background: rgba(108,99,255,0.15);
        color: #8B83FF;
        border-radius: 6px;
        padding: 0.2rem 0.6rem;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 0.5rem;
    }
    .explanation-card .tag.green {
        background: rgba(78,205,196,0.15);
        color: #4ECDC4;
    }
    .explanation-card .tag.amber {
        background: rgba(255,184,77,0.15);
        color: #FFB84D;
    }

    /* --- Footer --- */
    .premium-footer {
        text-align: center;
        padding: 2rem 0 1rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        color: #4B5563;
        font-size: 0.8rem;
    }
    .premium-footer a {
        color: #6C63FF;
        text-decoration: none;
    }

    /* --- File count pill --- */
    .file-count {
        display: inline-block;
        background: linear-gradient(135deg, #6C63FF, #5A52E0);
        color: white;
        border-radius: 50px;
        padding: 0.3rem 1rem;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* --- Progress bar --- */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #6C63FF, #4ECDC4) !important;
        border-radius: 10px;
    }

    /* ============================================================
       RESPONSIVE - MOBILE FIRST
       ============================================================ */

    /* --- Viewport meta (force proper scaling) --- */
    @viewport { width: device-width; }

    /* --- Small phones (< 480px) --- */
    @media screen and (max-width: 480px) {
        /* Global padding */
        .block-container {
            padding: 0.5rem 0.8rem !important;
            max-width: 100% !important;
        }

        /* Hero */
        .hero {
            padding: 1.2rem 0.5rem 1rem;
            margin-bottom: 0.5rem;
        }
        .hero-badge {
            font-size: 0.65rem;
            padding: 0.3rem 0.8rem;
        }
        .hero h1 {
            font-size: 1.6rem;
            line-height: 1.3;
        }
        .hero p {
            font-size: 0.85rem;
            line-height: 1.5;
            padding: 0 0.25rem;
        }

        /* Metrics: 2x2 grid */
        .metric-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
        }
        .metric-card {
            padding: 0.85rem 0.6rem;
            border-radius: 12px;
        }
        .metric-label {
            font-size: 0.6rem;
            letter-spacing: 0.5px;
        }
        .metric-value {
            font-size: 1.1rem;
        }

        /* Formula box */
        .formula-box {
            padding: 0.75rem;
            font-size: 0.75rem;
            line-height: 1.8;
            word-break: break-word;
        }
        .formula-box .result {
            font-size: 1rem;
            display: block;
            margin-top: 0.4rem;
        }

        /* Banners */
        .success-banner, .error-banner, .info-banner {
            padding: 0.75rem 1rem;
            font-size: 0.85rem;
            border-radius: 10px;
        }

        /* Section headers */
        .section-header {
            font-size: 1.1rem;
            margin: 1.25rem 0 0.75rem;
            padding-bottom: 0.5rem;
        }
        .section-header .icon {
            font-size: 1.2rem;
        }

        /* Upload */
        [data-testid="stFileUploader"] {
            border-radius: 12px;
            padding: 0.25rem;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            flex-wrap: nowrap;
            gap: 2px;
            padding: 3px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.4rem 0.7rem;
            font-size: 0.75rem;
            white-space: nowrap;
            min-width: auto;
        }

        /* DataFrame: horizontal scroll */
        [data-testid="stDataFrame"] {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }

        /* Explanation cards */
        .explanation-card {
            padding: 0.85rem;
            border-radius: 10px;
        }
        .explanation-card .tag {
            font-size: 0.6rem;
            padding: 0.15rem 0.5rem;
            margin-bottom: 0.4rem;
        }
        .explanation-card p {
            font-size: 0.82rem;
            line-height: 1.5;
        }

        /* Glass card */
        .glass-card {
            padding: 1rem;
            border-radius: 12px;
        }

        /* File count pill */
        .file-count {
            padding: 0.2rem 0.7rem;
            font-size: 0.75rem;
        }

        /* Footer */
        .premium-footer {
            padding: 1.5rem 0 0.75rem;
            margin-top: 2rem;
        }
        .premium-footer p {
            font-size: 0.72rem;
        }

        /* Expander text */
        .streamlit-expanderHeader p {
            font-size: 0.82rem !important;
        }

        /* Buttons */
        .stButton > button[kind="primary"] {
            padding: 0.65rem 1.2rem !important;
            font-size: 0.9rem !important;
            border-radius: 10px !important;
        }
        .stDownloadButton > button {
            font-size: 0.82rem !important;
            border-radius: 10px !important;
        }
    }

    /* --- Tablets & large phones (481px - 768px) --- */
    @media screen and (min-width: 481px) and (max-width: 768px) {
        .block-container {
            padding: 0.75rem 1.5rem !important;
            max-width: 100% !important;
        }

        .hero {
            padding: 1.5rem 0.75rem 1rem;
        }
        .hero h1 {
            font-size: 2rem;
        }
        .hero p {
            font-size: 0.95rem;
        }

        /* Metrics: 2x2 grid */
        .metric-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
        }
        .metric-card {
            padding: 1rem;
        }
        .metric-value {
            font-size: 1.3rem;
        }

        /* Formula */
        .formula-box {
            font-size: 0.82rem;
            padding: 0.85rem 1rem;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.45rem 0.9rem;
            font-size: 0.82rem;
        }

        .section-header {
            font-size: 1.2rem;
        }
    }

    /* --- Small desktop (769px - 1024px) --- */
    @media screen and (min-width: 769px) and (max-width: 1024px) {
        .block-container {
            padding: 1rem 2rem !important;
        }
        .hero h1 {
            font-size: 2.4rem;
        }
        .metric-value {
            font-size: 1.4rem;
        }
    }

    /* --- Touch device optimizations --- */
    @media (hover: none) and (pointer: coarse) {
        /* Larger tap targets */
        .stButton > button {
            min-height: 48px !important;
        }
        .stDownloadButton > button {
            min-height: 48px !important;
        }
        .stTabs [data-baseweb="tab"] {
            min-height: 42px;
        }

        /* Disable hover effects on touch */
        .metric-card:hover {
            transform: none;
        }
        .glass-card:hover {
            border-color: rgba(255,255,255,0.08);
            box-shadow: none;
        }
    }

    /* --- Safe area for notched phones --- */
    @supports (padding: env(safe-area-inset-bottom)) {
        .premium-footer {
            padding-bottom: calc(0.75rem + env(safe-area-inset-bottom));
        }
        .block-container {
            padding-left: calc(0.8rem + env(safe-area-inset-left)) !important;
            padding-right: calc(0.8rem + env(safe-area-inset-right)) !important;
        }
    }

    /* --- Landscape phone --- */
    @media screen and (max-height: 500px) and (orientation: landscape) {
        .hero {
            padding: 0.75rem 0.5rem 0.5rem;
        }
        .hero h1 {
            font-size: 1.4rem;
        }
        .hero p {
            font-size: 0.8rem;
        }
        .metric-row {
            grid-template-columns: 1fr 1fr 1fr 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HERO HEADER
# ============================================================
st.markdown("""
<div class="hero">
    <div class="hero-badge">Analyse intelligente</div>
    <h1>PaySlip Analyzer</h1>
    <p>Deposez vos fiches de paie et obtenez une analyse detaillee, claire et pedagogique de chaque ligne en quelques secondes.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# UPLOAD ZONE
# ============================================================
uploaded_files = st.file_uploader(
    "Deposez vos fiches de paie (PDF)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Glissez-deposez vos fichiers PDF ici, ou cliquez pour parcourir.",
    label_visibility="collapsed",
)


# ============================================================
# ANALYSE
# ============================================================
if uploaded_files:
    st.markdown(
        f'<div class="info-banner">'
        f'<span class="file-count">{len(uploaded_files)}</span>&nbsp;&nbsp;'
        f'fichier{"s" if len(uploaded_files) > 1 else ""} '
        f'pret{"s" if len(uploaded_files) > 1 else ""} pour l\'analyse'
        f'</div>',
        unsafe_allow_html=True,
    )

    if st.button("Lancer l'analyse", type="primary", use_container_width=True):
        resultats = []
        erreurs = []

        progress_bar = st.progress(0, text="Initialisation...")

        for i, uploaded_file in enumerate(uploaded_files):
            progress_bar.progress(
                (i) / len(uploaded_files),
                text=f"Analyse de {uploaded_file.name}...",
            )
            try:
                resultat = analyser_fiche(uploaded_file)
                resultats.append(resultat)
            except Exception as e:
                erreurs.append({
                    "fichier": uploaded_file.name,
                    "erreur": str(e),
                })

        progress_bar.progress(1.0, text="Analyse terminee !")

        st.session_state["resultats"] = resultats
        st.session_state["erreurs"] = erreurs


# ============================================================
# ERREURS
# ============================================================
if "erreurs" in st.session_state and st.session_state["erreurs"]:
    for err in st.session_state["erreurs"]:
        st.markdown(
            f'<div class="error-banner">'
            f'Erreur sur <strong>{err["fichier"]}</strong> : {err["erreur"]}'
            f'</div>',
            unsafe_allow_html=True,
        )


# ============================================================
# RESULTATS
# ============================================================
if "resultats" in st.session_state and st.session_state["resultats"]:
    resultats = st.session_state["resultats"]

    st.markdown(
        f'<div class="success-banner">'
        f'<span style="font-size:1.4rem">&#10003;</span> '
        f'{len(resultats)} fiche{"s" if len(resultats) > 1 else ""} '
        f'analysee{"s" if len(resultats) > 1 else ""} avec succes'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ======= TABLEAU DE SYNTHESE =======
    st.markdown(
        '<div class="section-header">'
        '<span class="icon">&#128202;</span> Tableau de synthese'
        '</div>',
        unsafe_allow_html=True,
    )

    tableau_data = []
    for r in resultats:
        tableau_data.append({
            "Nom": r["nom"],
            "Periode": r["periode"],
            "Coefficient": r["coefficient"],
            "Taux horaire": r["taux_horaire"],
            "Heures": r["heures"],
            "Absences": r["absences"],
            "Brut (EUR)": r["brut"],
            "Primes (EUR)": r["primes"],
            "Net a payer (EUR)": r["net"],
        })

    df = pd.DataFrame(tableau_data)

    st.dataframe(
        df.style.format({
            "Brut (EUR)": "{:.2f}",
            "Primes (EUR)": "{:.2f}",
            "Net a payer (EUR)": "{:.2f}",
        }).set_properties(**{
            'background-color': 'rgba(255,255,255,0.02)',
            'color': '#FAFAFA',
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ======= EXPORT CSV =======
    csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
    st.download_button(
        label="Telecharger le tableau en CSV",
        data=csv,
        file_name="analyse_fiches_de_paie.csv",
        mime="text/csv",
        use_container_width=True,
    )

    # ======= DETAIL PAR FICHE =======
    st.markdown(
        '<div class="section-header">'
        '<span class="icon">&#128196;</span> Detail par fiche'
        '</div>',
        unsafe_allow_html=True,
    )

    for idx, r in enumerate(resultats):
        detail = r["detail"]
        fichier = detail["fichier"]
        payslip_dict = detail["payslip_dict"]
        resume = payslip_dict["resume"]

        with st.expander(
            f"{fichier}  |  {r['periode']}  |  Net : {r['net']:.2f} EUR",
            expanded=(len(resultats) == 1),
        ):
            # --- Metrics Row ---
            st.markdown(f"""
            <div class="metric-row">
                <div class="metric-card accent-blue">
                    <div class="metric-label">Remuneration brute</div>
                    <div class="metric-value blue">{r['brut']:.2f} EUR</div>
                </div>
                <div class="metric-card accent-red">
                    <div class="metric-label">Cotisations salariales</div>
                    <div class="metric-value red">{detail['cotisations_salariales']:.2f} EUR</div>
                </div>
                <div class="metric-card accent-amber">
                    <div class="metric-label">Net avant impot</div>
                    <div class="metric-value amber">{detail['net_avant_impot']:.2f} EUR</div>
                </div>
                <div class="metric-card accent-green">
                    <div class="metric-label">Net a payer</div>
                    <div class="metric-value green">{r['net']:.2f} EUR</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- Formula ---
            indemnites = resume.get('indemnites_non_soumises', 0)
            retenues = resume.get('autres_retenues', 0)
            indemnites_line = f'<div class="formula-line"><span class="formula-op">+</span> Indemnites <strong>{indemnites:.2f}</strong></div>' if indemnites else ""
            st.markdown(f"""
            <div class="formula-box">
                <div class="formula-line"><span class="formula-op">&nbsp;</span> Brut <strong>{r['brut']:.2f}</strong></div>
                <div class="formula-line"><span class="formula-op">-</span> Cotisations <strong>{detail['cotisations_salariales']:.2f}</strong></div>
                {indemnites_line}
                <div class="formula-line"><span class="formula-op">-</span> Retenues <strong>{abs(retenues):.2f}</strong></div>
                <div class="formula-line formula-total"><span class="formula-op">=</span> <span class="result">{r['net']:.2f} EUR</span></div>
            </div>
            """, unsafe_allow_html=True)

            # --- Tabs ---
            tab_rem, tab_cot, tab_abs, tab_exp, tab_json = st.tabs([
                "Remuneration",
                "Cotisations",
                "Absences",
                "Explications",
                "Donnees brutes",
            ])

            # --- Tab Remuneration ---
            with tab_rem:
                lines = []
                for section in ("remuneration", "primes"):
                    for line in payslip_dict.get(section, []):
                        if line["designation"].startswith("TOTAL "):
                            continue
                        knowledge = find_knowledge(line["designation"])
                        lines.append({
                            "Designation": line["designation"],
                            "Base": line.get("nombre_ou_base", ""),
                            "Taux": line.get("taux_ou_pourcent", ""),
                            "Montant (EUR)": line.get("montant_employe", 0),
                            "Type": knowledge["type"].capitalize() if knowledge else "?",
                        })
                if lines:
                    st.dataframe(
                        pd.DataFrame(lines).style.format({"Montant (EUR)": "{:.2f}"}),
                        use_container_width=True, hide_index=True,
                    )

            # --- Tab Cotisations ---
            with tab_cot:
                lines = []
                for line in payslip_dict.get("cotisations", []):
                    if line["designation"].startswith("TOTAL "):
                        continue
                    knowledge = find_knowledge(line["designation"])
                    lines.append({
                        "Designation": line["designation"],
                        "Base": line.get("nombre_ou_base", ""),
                        "Part salarie (EUR)": line.get("montant_employe", 0),
                        "Part employeur (EUR)": line.get("montant_employeur", 0),
                        "Qui paie": knowledge["qui_paie"] if knowledge else "?",
                    })
                if lines:
                    st.dataframe(
                        pd.DataFrame(lines).style.format({
                            "Part salarie (EUR)": "{:.2f}",
                            "Part employeur (EUR)": "{:.2f}",
                        }),
                        use_container_width=True, hide_index=True,
                    )

                # Totals
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-card accent-red">
                        <div class="metric-label">Cotisations salariales</div>
                        <div class="metric-value red">{detail['cotisations_salariales']:.2f} EUR</div>
                    </div>
                    <div class="metric-card accent-amber">
                        <div class="metric-label">Cotisations patronales</div>
                        <div class="metric-value amber">{detail['cotisations_patronales']:.2f} EUR</div>
                    </div>
                    <div class="metric-card accent-blue">
                        <div class="metric-label">Cout total employeur</div>
                        <div class="metric-value blue">{detail['total_verse_employeur']:.2f} EUR</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # --- Tab Absences ---
            with tab_abs:
                absences = detail.get("absences_detail", [])
                if absences:
                    abs_data = []
                    for a in absences:
                        abs_data.append({
                            "Type d'absence": a["type"],
                            "Duree": a["jours"] if a["jours"] else "-",
                            "Montant retenu (EUR)": a["montant"],
                        })
                    st.dataframe(
                        pd.DataFrame(abs_data).style.format({
                            "Montant retenu (EUR)": "{:.2f}",
                        }),
                        use_container_width=True, hide_index=True,
                    )
                else:
                    st.markdown(
                        '<div class="info-banner">Aucune absence detectee sur cette periode.</div>',
                        unsafe_allow_html=True,
                    )

                conges = resume.get("conges_acquis", "")
                if conges:
                    st.markdown(f"""
                    <div class="glass-card" style="display:inline-block;">
                        <div class="metric-label">Solde conges acquis</div>
                        <div class="metric-value green">{conges} jours</div>
                    </div>
                    """, unsafe_allow_html=True)

            # --- Tab Explications ---
            with tab_exp:
                st.markdown(
                    '<div class="section-header" style="font-size:1.1rem;margin-top:0;">'
                    '<span class="icon">&#128218;</span> Explication ligne par ligne'
                    '</div>',
                    unsafe_allow_html=True,
                )

                for exp in detail["explanations"]:
                    if not exp.get("connu"):
                        st.markdown(
                            f'<div class="error-banner" style="font-size:0.85rem;">'
                            f'Ligne non reconnue : <strong>{exp["designation"]}</strong>'
                            f' — Montant : {exp["montant_employe"]:.2f} EUR'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        continue

                    type_colors = {
                        "salaire": "", "prime": "green", "cotisation": "",
                        "absence": "amber", "indemnite": "green", "retenue": "amber",
                        "impot": "amber", "exoneration": "green", "information": "",
                        "regularisation": "",
                    }
                    tag_class = type_colors.get(exp["type"], "")
                    obligatoire_txt = "Obligatoire" if exp.get("obligatoire") else "Optionnel"

                    with st.expander(f"{exp['designation']}"):
                        st.markdown(f"""
                        <div class="explanation-card">
                            <div style="margin-bottom:0.75rem;">
                                <span class="tag {tag_class}">{exp['type']}</span>
                                <span class="tag {'green' if exp.get('obligatoire') else 'amber'}">{obligatoire_txt}</span>
                            </div>
                            <p style="color:#D1D5DB;margin:0.5rem 0;line-height:1.6;">
                                <strong style="color:#FAFAFA;">Explication :</strong> {exp['explication']}
                            </p>
                            <p style="color:#D1D5DB;margin:0.5rem 0;line-height:1.6;">
                                <strong style="color:#FAFAFA;">A quoi ca sert :</strong> {exp['a_quoi_ca_sert']}
                            </p>
                            <p style="color:#D1D5DB;margin:0.5rem 0;">
                                <strong style="color:#FAFAFA;">Qui paie :</strong> {exp['qui_paie']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                questions = detail.get("questions", [])
                if questions:
                    st.markdown(
                        f'<div class="error-banner">'
                        f'{len(questions)} ligne(s) non identifiee(s) — '
                        f'verification manuelle recommandee'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            # --- Tab JSON ---
            with tab_json:
                st.json(payslip_dict)
                json_str = json.dumps(payslip_dict, ensure_ascii=False, indent=2)
                st.download_button(
                    label=f"Telecharger JSON — {fichier}",
                    data=json_str,
                    file_name=f"{os.path.splitext(fichier)[0]}_analyse.json",
                    mime="application/json",
                )


# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div class="premium-footer">
    <p>PaySlip Analyzer &mdash; Analyse intelligente de fiches de paie</p>
    <p style="font-size:0.72rem;margin-top:0.25rem;">
        Vos donnees restent privees et ne sont jamais stockees.
    </p>
</div>
""", unsafe_allow_html=True)
