"""
Application web Streamlit pour l'analyse de fiches de paie.
Interface premium accessible pour les salaries.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from analyse.analyzer import analyser_fiche
from analyse.fiscal import analyse_fiscale, extraire_donnees_annuelles
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
# PWA — Favicon et titre personnalisés (l'installation PWA est
# gérée par la page GitHub Pages wrapper, pas par Streamlit)
# ============================================================
components.html("""
<script>
(function() {
    var doc = window.parent.document;
    var head = doc.head;
    var base = './app/static/';

    function customizePage() {
        doc.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"]').forEach(function(e) { e.remove(); });
        var f = doc.createElement('link');
        f.rel='icon'; f.type='image/png'; f.sizes='32x32'; f.href=base+'favicon.png';
        head.appendChild(f);
        doc.title = 'PaySlip Analyzer';
    }

    customizePage();
    setTimeout(customizePage, 300);
    setTimeout(customizePage, 2000);

    new MutationObserver(function(muts) {
        muts.forEach(function(mut) {
            mut.addedNodes.forEach(function(n) {
                if (n.nodeType === 1 && n.tagName === 'LINK' && (n.rel === 'icon' || n.rel === 'shortcut icon') && n.href.indexOf('app/static') === -1) {
                    n.remove(); customizePage();
                }
            });
        });
    }).observe(head, { childList: true });
})();
</script>
""", height=0)

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
            st.markdown(
                f'<div class="metric-row">'
                f'<div class="metric-card accent-blue">'
                f'<div class="metric-label">Remuneration brute</div>'
                f'<div class="metric-value blue">{r["brut"]:.2f} EUR</div>'
                f'</div>'
                f'<div class="metric-card accent-red">'
                f'<div class="metric-label">Cotisations salariales</div>'
                f'<div class="metric-value red">{detail["cotisations_salariales"]:.2f} EUR</div>'
                f'</div>'
                f'<div class="metric-card accent-amber">'
                f'<div class="metric-label">Net avant impot</div>'
                f'<div class="metric-value amber">{detail["net_avant_impot"]:.2f} EUR</div>'
                f'</div>'
                f'<div class="metric-card accent-green">'
                f'<div class="metric-label">Net a payer</div>'
                f'<div class="metric-value green">{r["net"]:.2f} EUR</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            # --- Formula ---
            indemnites = resume.get('indemnites_non_soumises', 0)
            retenues = resume.get('autres_retenues', 0)
            formula_lines = [
                f'<div class="formula-line"><span class="formula-op">&nbsp;</span> Brut <strong>{r["brut"]:.2f}</strong></div>',
                f'<div class="formula-line"><span class="formula-op">-</span> Cotisations <strong>{abs(detail["cotisations_salariales"]):.2f}</strong></div>',
            ]
            if indemnites:
                formula_lines.append(f'<div class="formula-line"><span class="formula-op">+</span> Indemnites <strong>{indemnites:.2f}</strong></div>')
            if retenues:
                formula_lines.append(f'<div class="formula-line"><span class="formula-op">-</span> Retenues <strong>{abs(retenues):.2f}</strong></div>')
            formula_lines.append(f'<div class="formula-line formula-total"><span class="formula-op">=</span> <span class="result">{r["net"]:.2f} EUR</span></div>')
            formula_html = "\n".join(formula_lines)
            st.markdown(f'<div class="formula-box">{formula_html}</div>', unsafe_allow_html=True)

            # --- Tabs ---
            tab_rem, tab_cot, tab_abs, tab_cp, tab_exp, tab_json = st.tabs([
                "Remuneration",
                "Cotisations",
                "Absences",
                "Conges Payes",
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

            # --- Tab Conges Payes ---
            with tab_cp:
                conges_data = detail.get("conges", {})
                en_cours = conges_data.get("en_cours", {})
                acquis_n1 = conges_data.get("acquis_n1", {})

                has_data = any([
                    en_cours.get("acquis"), en_cours.get("solde"),
                    acquis_n1.get("droits"), acquis_n1.get("solde"),
                ])

                if has_data:
                    # --- Période de la fiche ---
                    periode_fiche = r.get("periode", "")
                    st.markdown(
                        '<div class="section-header" style="font-size:1.1rem;margin-top:0;">'
                        '<span class="icon">&#127965;</span> Conges payes — Compteurs de la fiche'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    # --- Avertissement date ---
                    st.markdown(
                        '<div style="background:rgba(255,171,0,0.1);border:1px solid rgba(255,171,0,0.3);'
                        'border-radius:10px;padding:0.8rem 1rem;margin-bottom:1rem;font-size:0.85rem;color:#FFD166;">'
                        '<strong>&#9888; Attention :</strong> Les compteurs ci-dessous correspondent '
                        f'a la fiche de paie analysee (<strong>{periode_fiche}</strong>). '
                        'Si vous consultez une ancienne fiche, les soldes ne refletent pas votre situation actuelle : '
                        'vous avez probablement acquis de nouveaux CP depuis, et/ou pose des jours supplementaires.'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    # --- Extraction des valeurs ---
                    dt_en_cours = en_cours.get("acquis", "")
                    pris_en_cours = en_cours.get("pris", "")
                    sld_en_cours = en_cours.get("solde", "")
                    dt_acquis = acquis_n1.get("droits", "")
                    pris_acquis = acquis_n1.get("pris", "")
                    sld_acquis = acquis_n1.get("solde", "")

                    def _val(s):
                        """Convertit '16,43' -> 16.43, '' -> None."""
                        if not s:
                            return None
                        try:
                            return float(s.replace(",", "."))
                        except ValueError:
                            return None

                    # ============================================================
                    # LIGNE 1 — CP EN COURS (cumul de l'année en cours)
                    # ============================================================
                    if dt_en_cours or sld_en_cours:
                        v_dt = _val(dt_en_cours)
                        v_sld = _val(sld_en_cours)
                        pct_acquis = min((v_dt / 25.0 * 100), 100) if v_dt else 0

                        # Cartes
                        cards = []
                        cards.append(
                            '<div class="metric-card accent-blue">'
                            f'<div class="metric-label">DT CP EN COURS</div>'
                            f'<div class="metric-value blue">{dt_en_cours or "-"} j</div>'
                            '</div>'
                        )
                        cards.append(
                            '<div class="metric-card accent-green">'
                            f'<div class="metric-label">SLD CP EN COURS</div>'
                            f'<div class="metric-value green">{sld_en_cours or "-"} j</div>'
                            '</div>'
                        )
                        cards_html = "".join(cards)

                        # Barre de progression
                        bar_html = (
                            '<div style="margin-top:0.8rem;">'
                            '<div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#9CA3AF;margin-bottom:4px;">'
                            f'<span>Acquisition : {pct_acquis:.0f}% de 25 jours</span>'
                            f'<span>{dt_en_cours or "0"} / 25 j</span>'
                            '</div>'
                            '<div style="background:rgba(255,255,255,0.1);border-radius:8px;height:12px;overflow:hidden;">'
                            f'<div style="width:{pct_acquis:.0f}%;background:linear-gradient(90deg,#6C63FF,#8B83FF);border-radius:8px;height:100%;"></div>'
                            '</div>'
                            '</div>'
                        )

                        st.markdown(
                            '<div class="glass-card">'
                            '<div style="font-size:1rem;font-weight:700;margin-bottom:0.5rem;color:#8B83FF;">'
                            '&#128197; Ligne 1 — Cumul de l\'annee en cours (CP EN COURS)'
                            '</div>'
                            '<div style="font-size:0.85rem;color:#9CA3AF;margin-bottom:0.8rem;line-height:1.6;">'
                            'Ces conges sont en train de se cumuler pour l\'annee prochaine '
                            '(periode du 1er juin au 31 mai). Vous gagnez <strong style="color:#6C63FF;">2,08 jours par mois</strong> travaille.'
                            '</div>'
                            f'<div class="metric-row">{cards_html}</div>'
                            f'{bar_html}'
                            '<div style="margin-top:0.8rem;font-size:0.82rem;color:#9CA3AF;line-height:1.7;">'
                            '<strong style="color:#6C63FF;">DT CP EN COURS'
                            f' ({dt_en_cours or "-"})</strong> : Droits aux Conges Payes en cours. '
                            'Nombre de jours cumules depuis le debut de la periode de reference actuelle.<br>'
                            '<strong style="color:#4ECDC4;">SLD CP EN COURS'
                            f' ({sld_en_cours or "-"})</strong> : Solde des Conges Payes en cours. '
                            'Comme ces jours ne sont generalement pas encore posables, '
                            'le solde est souvent identique aux droits.'
                            '</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                    # ============================================================
                    # LIGNE 2 — CP ACQUIS (ceux que vous pouvez poser)
                    # ============================================================
                    if dt_acquis or pris_acquis or sld_acquis:
                        v_dt_a = _val(dt_acquis)
                        v_pris_a = _val(pris_acquis)
                        v_sld_a = _val(sld_acquis)

                        # Calcul pourcentages
                        if v_dt_a and v_dt_a > 0:
                            pct_pris = (v_pris_a / v_dt_a * 100) if v_pris_a else 0
                            pct_rest = (v_sld_a / v_dt_a * 100) if v_sld_a else 0
                        else:
                            pct_pris = 0
                            pct_rest = (v_sld_a / 25.0 * 100) if v_sld_a else 0

                        # Cartes
                        cards2 = []
                        if dt_acquis:
                            cards2.append(
                                '<div class="metric-card accent-blue">'
                                '<div class="metric-label">DT CP ACQUIS</div>'
                                f'<div class="metric-value blue">{dt_acquis} j</div>'
                                '</div>'
                            )
                        if pris_acquis:
                            cards2.append(
                                '<div class="metric-card accent-red">'
                                '<div class="metric-label">PRIS CP ACQUIS</div>'
                                f'<div class="metric-value red">{pris_acquis} j</div>'
                                '</div>'
                            )
                        if sld_acquis:
                            cards2.append(
                                '<div class="metric-card accent-green">'
                                '<div class="metric-label">SLD CP ACQUIS</div>'
                                f'<div class="metric-value green">{sld_acquis} j</div>'
                                '</div>'
                            )
                        cards2_html = "".join(cards2)

                        # Barre pris/restant
                        has_full_detail = bool(dt_acquis and pris_acquis)
                        if has_full_detail:
                            bar2_html = (
                                '<div style="margin-top:0.8rem;">'
                                '<div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#9CA3AF;margin-bottom:4px;">'
                                f'<span>Pris : {pct_pris:.0f}%</span>'
                                f'<span>Restant : {pct_rest:.0f}%</span>'
                                '</div>'
                                '<div style="background:rgba(255,255,255,0.1);border-radius:8px;height:12px;overflow:hidden;">'
                                '<div style="display:flex;height:100%;">'
                                f'<div style="width:{pct_pris:.0f}%;background:linear-gradient(90deg,#FF6B6B,#FF8E8E);border-radius:8px 0 0 8px;"></div>'
                                f'<div style="width:{pct_rest:.0f}%;background:linear-gradient(90deg,#4ECDC4,#6EDDD5);border-radius:0 8px 8px 0;"></div>'
                                '</div></div>'
                                '<div style="display:flex;gap:1rem;margin-top:6px;font-size:0.75rem;color:#9CA3AF;">'
                                '<span style="display:flex;align-items:center;gap:4px;">'
                                '<span style="width:8px;height:8px;border-radius:50%;background:#FF6B6B;"></span> Pris</span>'
                                '<span style="display:flex;align-items:center;gap:4px;">'
                                '<span style="width:8px;height:8px;border-radius:50%;background:#4ECDC4;"></span> Restant</span>'
                                '</div></div>'
                            )
                        else:
                            bar2_html = (
                                '<div style="margin-top:0.8rem;">'
                                '<div style="font-size:0.8rem;color:#9CA3AF;margin-bottom:4px;">'
                                f'Solde : {sld_acquis or "-"} / 25 jours</div>'
                                '<div style="background:rgba(255,255,255,0.1);border-radius:8px;height:12px;overflow:hidden;">'
                                f'<div style="width:{min(pct_rest, 100):.0f}%;background:linear-gradient(90deg,#4ECDC4,#6EDDD5);border-radius:8px;height:100%;"></div>'
                                '</div></div>'
                            )

                        # Explications ligne 2
                        expl2_parts = []
                        if dt_acquis:
                            expl2_parts.append(
                                f'<strong style="color:#6C63FF;">DT CP ACQUIS ({dt_acquis})</strong> : '
                                'Droits aux Conges Payes acquis. Total de jours gagnes sur la periode '
                                'precedente (1er juin N-2 au 31 mai N-1). C\'est votre reserve totale.'
                            )
                        if pris_acquis:
                            expl2_parts.append(
                                f'<strong style="color:#FF6B6B;">PRIS CP ACQUIS ({pris_acquis})</strong> : '
                                'Conges Payes acquis deja pris. Nombre de jours que vous avez poses '
                                'et consommes sur cette reserve.'
                            )
                        expl2_html = "<br>".join(expl2_parts)

                        st.markdown(
                            '<div class="glass-card" style="margin-top:1rem;">'
                            '<div style="font-size:1rem;font-weight:700;margin-bottom:0.5rem;color:#4ECDC4;">'
                            '&#9989; Ligne 2 — Conges acquis (CP ACQUIS) — ceux que vous pouvez poser'
                            '</div>'
                            '<div style="font-size:0.85rem;color:#9CA3AF;margin-bottom:0.8rem;line-height:1.6;">'
                            'Ces conges ont ete accumules sur la periode precedente. '
                            'Ce sont ceux que vous etes en train d\'utiliser cette annee.'
                            '</div>'
                            f'<div class="metric-row">{cards2_html}</div>'
                            f'{bar2_html}'
                            + (f'<div style="margin-top:0.8rem;font-size:0.82rem;color:#9CA3AF;line-height:1.7;">{expl2_html}</div>' if expl2_html else '')
                            + '</div>',
                            unsafe_allow_html=True,
                        )

                    # ============================================================
                    # LIGNE 3 — SLD CP ACQUIS (reste à poser) — résumé final
                    # ============================================================
                    if sld_acquis:
                        calcul_parts = []
                        if dt_acquis and pris_acquis:
                            calcul_parts.append(f'{dt_acquis} jours acquis - {pris_acquis} jours pris')
                        calcul_txt = (" = ".join(calcul_parts) + f' = <strong>{sld_acquis} jours restants</strong>') if calcul_parts else ""

                        st.markdown(
                            '<div class="glass-card" style="margin-top:1rem;border-left:3px solid #4ECDC4;">'
                            '<div style="font-size:1rem;font-weight:700;margin-bottom:0.5rem;color:#4ECDC4;">'
                            f'&#127944; Ligne 3 — Reste a poser : <span style="font-size:1.3rem;">{sld_acquis} jours</span>'
                            '</div>'
                            '<div style="font-size:0.85rem;color:#9CA3AF;line-height:1.7;">'
                            f'<strong style="color:#4ECDC4;">SLD CP ACQUIS ({sld_acquis})</strong> : '
                            'Solde des Conges Payes acquis. C\'est le nombre de jours qu\'il vous '
                            'reste a poser (generalement avant le 31 mai).'
                            + (f'<br><br><span style="color:#B8B5FF;">Calcul : {calcul_txt}</span>' if calcul_txt else '')
                            + '</div></div>',
                            unsafe_allow_html=True,
                        )

                    # ============================================================
                    # Nota : detail pas toujours présent
                    # ============================================================
                    if not dt_acquis and not pris_acquis and sld_acquis:
                        st.markdown(
                            '<div style="font-size:0.82rem;color:#6B7280;font-style:italic;margin-top:0.5rem;">'
                            'Le detail (DT CP ACQUIS / PRIS CP ACQUIS) n\'apparait pas sur toutes les fiches de paie. '
                            'Consultez une fiche de juin, aout ou octobre pour voir le detail complet des 3 lignes.'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                else:
                    st.markdown(
                        '<div class="info-banner">Aucune information de conges disponible sur cette fiche.</div>',
                        unsafe_allow_html=True,
                    )

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
# ONGLET IMPÔT — Simulateur frais réels vs abattement 10%
# ============================================================
st.markdown('<div style="margin-top:2.5rem;"></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-header">'
    '<span class="icon">&#128202;</span> Simulateur fiscal — Frais reels vs Abattement 10%'
    '</div>',
    unsafe_allow_html=True,
)

# Contexte pédagogique
st.markdown(
    '<div class="glass-card" style="border-left:3px solid #6C63FF;margin-bottom:1.2rem;">'
    '<div style="font-size:0.92rem;color:#9CA3AF;line-height:1.75;">'
    '<strong style="color:#B8B5FF;">Pourquoi ce simulateur ?</strong><br>'
    'Chaque annee, lors de votre declaration d\'impots, vous choisissez entre deux options :<br>'
    '<strong style="color:#6C63FF;">&#9312; Abattement forfaitaire de 10%</strong> — '
    'l\'administration deduit automatiquement 10% de vos revenus (min 499 € / max 13 643 €).<br>'
    '<strong style="color:#4ECDC4;">&#9313; Deduction des frais reels</strong> — '
    'vous deduisez vos vraies depenses professionnelles (trajets, repas, formation…).<br>'
    'Ce simulateur calcule quelle option vous fait payer le moins d\'impots.'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# Récupération des fiches disponibles
_resultats_dispo = st.session_state.get("resultats", [])
if _resultats_dispo:
    _donnees_dispo = extraire_donnees_annuelles(_resultats_dispo)
    _annee = _donnees_dispo.get("annee_detectee")
    _mois = _donnees_dispo.get("mois_disponibles", 0)
    _revenu_dispo = _donnees_dispo.get("revenu_fiscal_brut", 0)
    _mois_source = _donnees_dispo.get("mois_source")
    _dec_manquant = _donnees_dispo.get("decembre_manquant", True)
    _une_valeur = _donnees_dispo.get("une_seule_valeur", False)

    # Bannière principale : état des fiches
    if _dec_manquant:
        # Avertissement rouge : fiche de décembre absente
        st.markdown(
            '<div style="background:rgba(255,80,80,0.10);border:1.5px solid rgba(255,80,80,0.45);'
            'border-radius:10px;padding:0.8rem 1.1rem;margin-bottom:1rem;font-size:0.9rem;">'
            '<strong style="color:#FF6B6B;">&#9888; Fiche de decembre introuvable</strong><br>'
            '<span style="color:#9CA3AF;">'
            f'{_mois} fiche(s) chargee(s), mais aucune de decembre. '
            'Le revenu net fiscal annuel ne peut pas etre calcule de facon fiable sans la fiche de decembre. '
            'Deposez-la dans la zone d\'upload ci-dessus, ou saisissez le montant manuellement.'
            '</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    elif _une_valeur:
        # Avertissement orange : une seule valeur (pas de cumul dans le PDF)
        st.markdown(
            '<div style="background:rgba(255,171,0,0.10);border:1.5px solid rgba(255,171,0,0.4);'
            'border-radius:10px;padding:0.8rem 1.1rem;margin-bottom:1rem;font-size:0.9rem;">'
            '<strong style="color:#FFD166;">&#9888; Valeur annuelle non trouvee dans la fiche de decembre</strong><br>'
            '<span style="color:#9CA3AF;">'
            'La ligne NET FISCAL de la fiche de decembre ne contient qu\'une seule valeur (mensuelle). '
            f'Revenu utilise : <strong style="color:#FFD166;">{_revenu_dispo:,.2f} \u20ac</strong> — '
            'Verifiez ce montant avec votre fiche de paie avant de declarer.'
            '</span>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        # Bannière verte : source fiable (décembre, cumul annuel)
        st.markdown(
            f'<div class="info-banner" style="margin-bottom:1rem;">'
            f'&#9989; <strong>{_mois} fiche(s) disponible(s)</strong>'
            + (f' — Annee <strong>{_annee}</strong>' if _annee else '')
            + f' — Revenu fiscal annuel (cumul decembre) : <strong>{_revenu_dispo:,.2f} \u20ac</strong>'
            + f' <em style="color:#9CA3AF;font-size:0.85rem;">(source : fiche decembre {_annee or ""})</em>'
            + '</div>',
            unsafe_allow_html=True,
        )
else:
    _donnees_dispo = {}
    _dec_manquant = True
    _une_valeur = False
    _revenu_dispo = 0.0
    st.markdown(
        '<div class="info-banner" style="border-color:rgba(255,171,0,0.4);background:rgba(255,171,0,0.08);margin-bottom:1rem;">'
        '&#9888; Aucune fiche analysee. Deposez vos fiches dans la zone d\'upload ci-dessus, '
        'puis revenez ici — ou saisissez votre revenu annuel manuellement.'
        '</div>',
        unsafe_allow_html=True,
    )

# ---- FORMULAIRE ----
with st.form("form_fiscal"):
    st.markdown(
        '<div style="font-size:1rem;font-weight:600;color:#B8B5FF;margin-bottom:0.5rem;">'
        '&#9997; Vos informations personnelles'
        '</div>',
        unsafe_allow_html=True,
    )

    col_rev, col_jours, col_syndicat = st.columns(3)
    with col_rev:
        if _resultats_dispo:
            revenu_manuel = st.number_input(
                "Revenu fiscal annuel (€) — pre-rempli depuis vos fiches",
                min_value=0.0,
                value=float(_revenu_dispo) if _resultats_dispo else 0.0,
                step=100.0,
                help="Le revenu net imposable total issu de vos fiches de paie. "
                     "Vous pouvez le corriger si certains mois manquent.",
            )
        else:
            revenu_manuel = st.number_input(
                "Revenu fiscal annuel (€) — a saisir manuellement",
                min_value=0.0,
                value=0.0,
                step=100.0,
                help="Votre revenu net imposable annuel, visible sur votre dernier bulletin "
                     "ou sur votre declaration pre-remplie.",
            )
    with col_jours:
        jours_travailles = st.number_input(
            "Jours travailles dans l'annee",
            min_value=0,
            max_value=365,
            value=218,
            step=1,
            help="Nombre de jours effectivement travailles (hors week-ends, conges, RTT). "
                 "En moyenne : 218 jours/an pour un temps plein.",
        )
    with col_syndicat:
        cotisation_syndicale = st.number_input(
            "\U0001F91D Cotisation syndicale annuelle (\u20ac)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Montant annuel de vos cotisations syndicales. "
                 "Elles sont deductibles en frais reels (CGI art. 83, 3\u00b0). "
                 "Saisissez le montant total annuel — ne pas mensualiser.",
        )

    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1rem;font-weight:600;color:#B8B5FF;margin-bottom:0.5rem;">'
        '&#128664; Frais de trajet domicile — travail'
        '</div>',
        unsafe_allow_html=True,
    )

    col_v1, col_v2, col_v3 = st.columns([2, 2, 1])
    with col_v1:
        type_vehicule = st.selectbox(
            "Type de vehicule",
            ["voiture", "moto", "cyclo"],
            format_func=lambda x: {
                "voiture": "\U0001F697 Voiture (essence / diesel)",
                "moto": "\U0001F3CD Motocyclette (> 50 cm\u00B3)",
                "cyclo": "\U0001F6F5 Cyclomoteur / scooter (\u226450 cm\u00B3)",
            }[x],
            help="Choisissez le vehicule que vous utilisez pour aller au travail.",
        )
    with col_v2:
        if type_vehicule == "voiture":
            cv_fiscaux = st.selectbox(
                "Puissance fiscale (CV)",
                [3, 4, 5, 6, 7],
                index=2,
                help="Nombre de chevaux fiscaux de votre voiture, visible sur la carte grise (rubrique P.6).",
            )
            cv_moto = "3-5"
        elif type_vehicule == "moto":
            cv_moto = st.selectbox(
                "Cylindree moto",
                ["1-2", "3-5", "6+"],
                index=1,
                format_func=lambda x: {"1-2": "1 ou 2 CV", "3-5": "3, 4 ou 5 CV", "6+": "6 CV et plus"}[x],
            )
            cv_fiscaux = 5
        else:
            st.markdown('<div style="color:#9CA3AF;font-size:0.85rem;padding-top:1.5rem;">Tarif unique (≤ 50 cm³)</div>', unsafe_allow_html=True)
            cv_fiscaux = 3
            cv_moto = "3-5"
    with col_v3:
        electrique = st.checkbox(
            "Vehicule electrique",
            value=False,
            help="Les vehicules electriques beneficient d'un bonus de 20% sur le bareme kilometrique.",
        )

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        distance_km = st.number_input(
            "Distance domicile → travail (km, sens aller)",
            min_value=0.0,
            max_value=500.0,
            value=0.0,
            step=0.5,
            help="Distance en kilometres de votre domicile jusqu'a votre lieu de travail (un seul sens). "
                 "Le calcul multipliera par 2 pour l'aller-retour.",
        )
    with col_d2:
        st.markdown(
            '<div style="font-size:0.82rem;color:#9CA3AF;padding-top:1.6rem;line-height:1.6;">'
            'Le bareme fiscal 2026 prend en compte :<br>'
            '&#10003; L\'usure du vehicule<br>'
            '&#10003; Le carburant<br>'
            '&#10003; L\'assurance et les reparations'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1rem;font-weight:600;color:#B8B5FF;margin-bottom:0.5rem;">'
        '&#127860; Repas et frais professionnels'
        '</div>',
        unsafe_allow_html=True,
    )

    # Valeurs auto-détectées depuis les fiches
    _tickets_auto = float(round(_donnees_dispo.get("tickets_resto_salarie", 0), 2)) if _resultats_dispo else 0.0
    _mutuelle_auto = float(round(_donnees_dispo.get("mutuelle_salarie", 0), 2)) if _resultats_dispo else 0.0

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        frais_repas = st.number_input(
            "Autres frais de repas (€/an)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Repas pris hors domicile non couverts par les tickets restaurant "
                 "(ex : repas d'affaires, repas lors de deplacements).",
        )
        if _tickets_auto > 0:
            inclure_tickets = st.checkbox(
                f"Inclure tickets restaurant part salariale ({_tickets_auto:,.2f} \u20ac detectes)",
                value=True,
                help="RET. TITRE REPAS : la part que vous payez pour vos tickets restaurant. "
                     "Cette somme est deductible en frais reels.",
            )
        else:
            inclure_tickets = False
    with col_r2:
        autres_frais = st.number_input(
            "Autres frais professionnels (€/an)",
            min_value=0.0,
            value=0.0,
            step=50.0,
            help="Formation, outils, vetements professionnels, abonnements… "
                 "Montant annuel non rembourse par l'employeur.",
        )
        if _mutuelle_auto > 0:
            inclure_mutuelle = st.checkbox(
                f"Inclure mutuelle obligatoire ({_mutuelle_auto:,.2f} \u20ac detectes)",
                value=True,
                help="COMPLEMENTAIRE SANTE OBLIGATOIRE : votre cotisation mutuelle d'entreprise. "
                     "Elle est deductible en frais reels.",
            )
        else:
            inclure_mutuelle = False

    # Avertissement si revenu < 1
    submitted = st.form_submit_button(
        "&#128200; Analyser ma situation fiscale",
        type="primary",
        use_container_width=True,
    )

# ---- RÉSULTATS ----
if submitted:
    if revenu_manuel < 1:
        st.markdown(
            '<div style="background:rgba(255,100,100,0.1);border:1px solid rgba(255,100,100,0.3);'
            'border-radius:10px;padding:0.8rem 1rem;color:#FF6B6B;font-size:0.9rem;">'
            '&#9888; Le revenu annuel doit etre superieur a 0 pour effectuer le calcul.'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        inputs_fiscal = {
            "type_vehicule": type_vehicule,
            "cv_fiscaux": cv_fiscaux,
            "cv_moto": cv_moto,
            "electrique": electrique,
            "distance_km": distance_km,
            "jours_travailles": jours_travailles,
            "frais_repas": frais_repas,
            "tickets_resto_auto": _tickets_auto,
            "inclure_tickets_resto": inclure_tickets,
            "mutuelle_auto": _mutuelle_auto,
            "inclure_mutuelle": inclure_mutuelle,
            "cotisation_syndicale": cotisation_syndicale,
            "autres_frais": autres_frais,
            "revenu_manuel": revenu_manuel,
        }
        _res_fiscaux = _resultats_dispo if _resultats_dispo else []
        result_fiscal = analyse_fiscale(_res_fiscaux, inputs_fiscal)

        # ---- Carte résumé ----
        opt = result_fiscal["option_optimale"]
        gain = result_fiscal["gain_fiscal"]
        abo = result_fiscal["abattement"]
        fr = result_fiscal["frais_reels"]
        rev = result_fiscal["revenu_annuel_estime"]
        rev_abo = result_fiscal["revenu_apres_abattement"]
        rev_fr = result_fiscal["revenu_apres_frais_reels"]

        _res_dec_manquant = result_fiscal.get("donnees_fiches", {}).get("decembre_manquant", False)
        _res_une_valeur = result_fiscal.get("donnees_fiches", {}).get("une_seule_valeur", False)
        if _res_dec_manquant:
            st.markdown(
                '<div style="background:rgba(255,80,80,0.10);border:1px solid rgba(255,80,80,0.4);'
                'border-radius:10px;padding:0.7rem 1rem;font-size:0.83rem;color:#FF6B6B;margin-bottom:0.8rem;">'
                '&#9888; <strong>Fiche de decembre absente</strong> — '
                'Le revenu saisi manuellement est utilise. '
                'Pour un calcul fiable, ajoutez la fiche de decembre.'
                '</div>',
                unsafe_allow_html=True,
            )
        elif _res_une_valeur:
            st.markdown(
                '<div style="background:rgba(255,171,0,0.1);border:1px solid rgba(255,171,0,0.3);'
                'border-radius:10px;padding:0.7rem 1rem;font-size:0.83rem;color:#FFD166;margin-bottom:0.8rem;">'
                '&#9888; <strong>Cumul annuel non trouve</strong> dans la fiche de decembre — '
                'seule la valeur mensuelle a ete extraite. Verifiez le revenu saisi.'
                '</div>',
                unsafe_allow_html=True,
            )

        # Bannière résultat
        if opt == "frais_reels":
            banner_color = "#4ECDC4"
            banner_icon = "&#9989;"
            banner_label = "FRAIS REELS"
        elif opt == "forfait_10":
            banner_color = "#6C63FF"
            banner_icon = "&#9989;"
            banner_label = "ABATTEMENT FORFAITAIRE 10%"
        else:
            banner_color = "#9CA3AF"
            banner_icon = "&#9866;"
            banner_label = "LES DEUX OPTIONS SONT EQUIVALENTES"

        gain_line = (
            f'<div style="font-size:1rem;color:#B8B5FF;margin-top:0.5rem;">'
            f'Gain fiscal estime : <strong style="color:{banner_color};">{gain:,.0f} \u20ac</strong> '
            f'de revenu imposable en moins</div>'
        ) if gain > 0 else ''
        st.markdown(
            f'<div style="background:rgba(30,30,60,0.6);border:2px solid {banner_color};'
            f'border-radius:14px;padding:1.2rem 1.5rem;text-align:center;margin:1rem 0;">'
            f'<div style="font-size:0.85rem;color:#9CA3AF;margin-bottom:0.3rem;">Option la plus avantageuse</div>'
            f'<div style="font-size:1.8rem;font-weight:800;color:{banner_color};">'
            f'{banner_icon} {banner_label}'
            f'</div>'
            + gain_line
            + '</div>',
            unsafe_allow_html=True,
        )

        # Tableau comparatif
        st.markdown(
            '<div style="font-size:1rem;font-weight:700;color:#B8B5FF;margin:1rem 0 0.5rem;">Comparaison detaillee</div>',
            unsafe_allow_html=True,
        )

        col_f, col_r10, col_rfr = st.columns(3)
        _annee_src = result_fiscal.get("annee_detectee", "")
        _src_ok = not _res_dec_manquant and not _res_une_valeur
        _src_sub = (
            f'cumul annuel — fiche dec. {_annee_src}'
            if _src_ok
            else ('valeur mensuelle (a verifier)' if _res_une_valeur else 'saisi manuellement')
        )
        with col_f:
            st.markdown(
                f'<div class="glass-card" style="text-align:center;">'
                f'<div style="font-size:0.85rem;color:#9CA3AF;">Revenu net fiscal annuel</div>'
                f'<div style="font-size:1.6rem;font-weight:700;color:#B8B5FF;">{rev:,.2f} \u20ac</div>'
                f'<div style="font-size:0.78rem;color:#6B7280;margin-top:0.3rem;">'
                + f'({_src_sub})'
                + '</div></div>',
                unsafe_allow_html=True,
            )
        with col_r10:
            active10 = opt == "forfait_10"
            border10 = "border:2px solid #6C63FF;" if active10 else ""
            st.markdown(
                f'<div class="glass-card" style="text-align:center;{border10}">'
                f'<div style="font-size:0.85rem;color:#6C63FF;font-weight:600;">&#9312; Abattement forfaitaire 10%</div>'
                f'<div style="font-size:1rem;color:#9CA3AF;margin:0.4rem 0;">'
                f'- {abo["abattement"]:,.2f} €'
                + (' <small style="color:#FFD166;">(plancher)</small>' if abo["plancher_applique"] else '')
                + (' <small style="color:#FFD166;">(plafond)</small>' if abo["plafond_applique"] else '')
                + '</div>'
                + f'<div style="font-size:1.5rem;font-weight:700;color:#6C63FF;">= {rev_abo:,.2f} €</div>'
                + (f'<div style="font-size:0.78rem;color:#4ECDC4;margin-top:0.3rem;">&#9989; Option optimale</div>' if active10 else '')
                + '</div>',
                unsafe_allow_html=True,
            )
        with col_rfr:
            activefr = opt == "frais_reels"
            borderfr = "border:2px solid #4ECDC4;" if activefr else ""
            st.markdown(
                f'<div class="glass-card" style="text-align:center;{borderfr}">'
                f'<div style="font-size:0.85rem;color:#4ECDC4;font-weight:600;">&#9313; Frais reels</div>'
                f'<div style="font-size:1rem;color:#9CA3AF;margin:0.4rem 0;">'
                f'- {fr["total"]:,.2f} €'
                + '</div>'
                + f'<div style="font-size:1.5rem;font-weight:700;color:#4ECDC4;">= {rev_fr:,.2f} €</div>'
                + (f'<div style="font-size:0.78rem;color:#4ECDC4;margin-top:0.3rem;">&#9989; Option optimale</div>' if activefr else '')
                + '</div>',
                unsafe_allow_html=True,
            )

        # Détail frais réels
        if fr["total"] > 0:
            detail_lines = []
            if fr["frais_km"] > 0:
                km = fr["km"]
                detail_lines.append(
                    f'<div style="display:flex;justify-content:space-between;">'
                    f'<span>\U0001F664 Frais kilometriques '
                    + (f'({km.get("distance_totale_km", 0):,.0f} km/an, '
                       + (f'{km.get("cv_fiscaux", "")} CV' if "cv_fiscaux" in km else f'{km.get("cv_moto", "")}')
                       + (' electrique' if km.get("electrique") else '') + ')')
                    + f'</span><strong>{fr["frais_km"]:,.2f} \u20ac</strong></div>'
                )
            if fr["frais_repas_manuel"] > 0:
                detail_lines.append(
                    f'<div style="display:flex;justify-content:space-between;">'
                    f'<span>\U0001F37D Frais de repas (saisis)</span>'
                    f'<strong>{fr["frais_repas_manuel"]:,.2f} \u20ac</strong></div>'
                )
            if fr["tickets_resto"] > 0:
                detail_lines.append(
                    f'<div style="display:flex;justify-content:space-between;">'
                    f'<span>\U0001F3AB Tickets restaurant — part salarie (RET. TITRE REPAS)</span>'
                    f'<strong>{fr["tickets_resto"]:,.2f} \u20ac</strong></div>'
                )
            if fr["mutuelle"] > 0:
                detail_lines.append(
                    f'<div style="display:flex;justify-content:space-between;">'
                    f'<span>\U0001FA7A Mutuelle obligatoire — part salarie (COMPLEMENTAIRE SANTE)</span>'
                    f'<strong>{fr["mutuelle"]:,.2f} \u20ac</strong></div>'
                )
            if fr.get("cotisation_syndicale", 0) > 0:
                detail_lines.append(
                    f'<div style="display:flex;justify-content:space-between;">'
                    f'<span>\U0001F91D Cotisation syndicale annuelle</span>'
                    f'<strong>{fr["cotisation_syndicale"]:,.2f} \u20ac</strong></div>'
                )
            if fr["autres_frais"] > 0:
                detail_lines.append(
                    f'<div style="display:flex;justify-content:space-between;">'
                    f'<span>\U0001F4C4 Autres frais professionnels</span>'
                    f'<strong>{fr["autres_frais"]:,.2f} \u20ac</strong></div>'
                )
            detail_lines.append(
                f'<div style="display:flex;justify-content:space-between;border-top:1px solid rgba(108,99,255,0.3);'
                f'margin-top:0.4rem;padding-top:0.4rem;font-weight:700;">'
                f'<span>Total frais reels</span>'
                f'<strong style="color:#4ECDC4;">{fr["total"]:,.2f} \u20ac</strong></div>'
            )
            st.markdown(
                '<div class="glass-card" style="margin-top:1rem;">'
                '<div style="font-size:0.95rem;font-weight:600;color:#B8B5FF;margin-bottom:0.6rem;">'
                'Detail des frais reels'
                '</div>'
                '<div style="font-size:0.87rem;color:#9CA3AF;line-height:2;">'
                + "".join(detail_lines)
                + '</div></div>',
                unsafe_allow_html=True,
            )

        # Données fiches détectées
        df_fiches = result_fiscal["donnees_fiches"]
        if df_fiches["mois_disponibles"] > 0:
            extras = []
            if df_fiches["tickets_resto_salarie"] > 0:
                extras.append(
                    f'\U0001F3AB Tickets restaurant (part salariale) detectes : '
                    f'<strong>{df_fiches["tickets_resto_salarie"]:,.2f} \u20ac</strong>'
                )
            if df_fiches["mutuelle_salarie"] > 0:
                extras.append(
                    f'\U0001FA7A Mutuelle obligatoire detectee : '
                    f'<strong>{df_fiches["mutuelle_salarie"]:,.2f} \u20ac</strong>'
                )
            if extras:
                st.markdown(
                    '<div class="glass-card" style="margin-top:0.8rem;border-left:3px solid #6C63FF;">'
                    '<div style="font-size:0.85rem;color:#9CA3AF;line-height:1.9;">'
                    '<strong style="color:#B8B5FF;">Donnees detectees dans vos fiches :</strong><br>'
                    + '<br>'.join(extras)
                    + '<br><span style="font-style:italic;color:#6B7280;">Ces montants sont inclus dans votre revenu fiscal et peuvent egalement '
                    'constituer des frais reels si non rembourses. Verifiez votre situation.</span>'
                    + '</div></div>',
                    unsafe_allow_html=True,
                )

        # Explication pédagogique
        st.markdown(
            '<div class="glass-card" style="margin-top:1rem;border-left:3px solid #FFD166;">'
            '<div style="font-size:0.92rem;font-weight:600;color:#FFD166;margin-bottom:0.5rem;">'
            '&#128218; Explication'
            '</div>'
            f'<div style="font-size:0.87rem;color:#9CA3AF;line-height:1.7;">'
            f'{result_fiscal["explication"]}'
            '<br><br>'
            '<strong style="color:#B8B5FF;">Pour declarer les frais reels :</strong> '
            'dans votre declaration en ligne (impots.gouv.fr), cochez la case "Frais reels" '
            'dans la section Traitements et salaires, et saisissez le montant total. '
            'Conservez toutes vos justificatifs (factures, notes de carburant, etc.).'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
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
