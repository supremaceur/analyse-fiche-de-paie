"""
Application web Streamlit pour l'analyse de fiches de paie.
Interface simple et accessible pour les salaries.
"""

import sys
import os

# S'assurer que le repertoire du projet est dans le path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import json
from analyse.analyzer import analyser_fiche
from payslip_explainer import find_knowledge


# --- Configuration de la page ---
st.set_page_config(
    page_title="Analyse des fiches de paie",
    page_icon="📄",
    layout="wide",
)

# --- CSS personnalise ---
st.markdown("""
<style>
    .main-title {
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .detail-section {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# --- Titre principal ---
st.markdown("# 📄 Analyse des fiches de paie")
st.markdown("Deposez vos fiches de paie et obtenez une analyse claire et detaillee.")
st.divider()


# --- Upload de fichiers ---
uploaded_files = st.file_uploader(
    "Deposez vos fiches de paie ici",
    type=["pdf"],
    accept_multiple_files=True,
    help="Formats acceptes : PDF. Vous pouvez deposer plusieurs fichiers en meme temps.",
)


# --- Bouton Analyser ---
if uploaded_files:
    st.info(f"{len(uploaded_files)} fichier(s) selectionne(s)")

    if st.button("Analyser", type="primary", use_container_width=True):
        resultats = []
        erreurs = []

        # Barre de progression
        progress_bar = st.progress(0, text="Analyse en cours...")

        for i, uploaded_file in enumerate(uploaded_files):
            progress_bar.progress(
                (i) / len(uploaded_files),
                text=f"Analyse de {uploaded_file.name}..."
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

        # Stocker les resultats en session
        st.session_state["resultats"] = resultats
        st.session_state["erreurs"] = erreurs


# --- Affichage des erreurs ---
if "erreurs" in st.session_state and st.session_state["erreurs"]:
    for err in st.session_state["erreurs"]:
        st.error(f"Erreur sur **{err['fichier']}** : {err['erreur']}")


# --- Affichage des resultats ---
if "resultats" in st.session_state and st.session_state["resultats"]:
    resultats = st.session_state["resultats"]

    st.success(f"{len(resultats)} fiche(s) analysee(s) avec succes !")
    st.divider()

    # ===== TABLEAU DE SYNTHESE =====
    st.markdown("## Tableau de synthese")

    # Construire le DataFrame
    tableau_data = []
    for r in resultats:
        tableau_data.append({
            "Nom": r["nom"],
            "Periode": r["periode"],
            "Coefficient": r["coefficient"],
            "Taux horaire (EUR)": r["taux_horaire"],
            "Heures": r["heures"],
            "Absences": r["absences"],
            "Brut (EUR)": r["brut"],
            "Primes (EUR)": r["primes"],
            "Net a payer (EUR)": r["net"],
        })

    df = pd.DataFrame(tableau_data)

    # Formater les colonnes monetaires
    st.dataframe(
        df.style.format({
            "Brut (EUR)": "{:.2f}",
            "Primes (EUR)": "{:.2f}",
            "Net a payer (EUR)": "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # ===== EXPORT CSV =====
    csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
    st.download_button(
        label="Telecharger le tableau en CSV",
        data=csv,
        file_name="analyse_fiches_de_paie.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.divider()

    # ===== DETAIL PAR FICHE =====
    st.markdown("## Detail par fiche")

    for idx, r in enumerate(resultats):
        detail = r["detail"]
        fichier = detail["fichier"]
        payslip_dict = detail["payslip_dict"]
        resume = payslip_dict["resume"]

        with st.expander(
            f"📄 {fichier} — {r['periode']} — Net : {r['net']:.2f} EUR",
            expanded=(len(resultats) == 1),
        ):
            # --- Metriques cles ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Brut", f"{r['brut']:.2f} EUR")
            with col2:
                st.metric("Cotisations", f"{detail['cotisations_salariales']:.2f} EUR")
            with col3:
                st.metric("Net avant impot", f"{detail['net_avant_impot']:.2f} EUR")
            with col4:
                st.metric("Net a payer", f"{r['net']:.2f} EUR")

            st.caption(
                f"Formule : Brut ({r['brut']:.2f}) "
                f"- Cotisations ({detail['cotisations_salariales']:.2f}) "
                f"+ Indemnites ({resume.get('indemnites_non_soumises', 0):.2f}) "
                f"- Retenues ({resume.get('autres_retenues', 0):.2f}) "
                f"= **{r['net']:.2f} EUR**"
            )

            # --- Onglets de detail ---
            tab_rem, tab_cot, tab_abs, tab_exp, tab_json = st.tabs([
                "Remuneration", "Cotisations", "Absences", "Explications", "JSON"
            ])

            # --- Onglet Remuneration ---
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
                            "Type": knowledge["type"] if knowledge else "?",
                        })
                if lines:
                    st.dataframe(
                        pd.DataFrame(lines).style.format({"Montant (EUR)": "{:.2f}"}),
                        use_container_width=True, hide_index=True,
                    )

            # --- Onglet Cotisations ---
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

                # Totaux
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total cotisations salariales", f"{detail['cotisations_salariales']:.2f} EUR")
                with col_b:
                    st.metric("Total cotisations patronales", f"{detail['cotisations_patronales']:.2f} EUR")
                with col_c:
                    st.metric("Cout total employeur", f"{detail['total_verse_employeur']:.2f} EUR")

            # --- Onglet Absences ---
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
                        pd.DataFrame(abs_data).style.format({"Montant retenu (EUR)": "{:.2f}"}),
                        use_container_width=True, hide_index=True,
                    )
                else:
                    st.info("Aucune absence detectee sur cette periode.")

                conges = resume.get("conges_acquis", "")
                if conges:
                    st.metric("Solde conges acquis", conges)

            # --- Onglet Explications ---
            with tab_exp:
                st.markdown("### Explication ligne par ligne")
                st.caption("Cliquez sur une ligne pour voir l'explication detaillee.")

                for exp in detail["explanations"]:
                    if not exp.get("connu"):
                        with st.expander(f"⚠️ {exp['designation']} — LIGNE NON RECONNUE"):
                            st.warning(
                                f"Cette ligne n'a pas ete identifiee automatiquement. "
                                f"Montant salarie : {exp['montant_employe']:.2f} EUR"
                            )
                        continue

                    icon = {
                        "salaire": "💰", "prime": "🎁", "cotisation": "🏛️",
                        "absence": "📅", "indemnite": "💵", "retenue": "📌",
                        "impot": "🏦", "exoneration": "✅", "information": "ℹ️",
                        "regularisation": "🔄",
                    }.get(exp["type"], "📋")

                    with st.expander(f"{icon} {exp['designation']}"):
                        st.markdown(f"**Type** : {exp['type']}")
                        st.markdown(f"**Explication** : {exp['explication']}")
                        st.markdown(f"**A quoi ca sert** : {exp['a_quoi_ca_sert']}")
                        st.markdown(f"**Qui paie** : {exp['qui_paie']}")
                        st.markdown(f"**Obligatoire** : {'Oui' if exp.get('obligatoire') else 'Non'}")
                        if exp.get("montant_employe"):
                            st.markdown(f"**Montant salarie** : {exp['montant_employe']:.2f} EUR")
                        if exp.get("montant_employeur"):
                            st.markdown(f"**Montant employeur** : {exp['montant_employeur']:.2f} EUR")

                # Questions
                questions = detail.get("questions", [])
                if questions:
                    st.divider()
                    st.warning(f"{len(questions)} ligne(s) non identifiee(s)")
                    for q in questions:
                        st.markdown(f"- **{q['ligne']}** : {q['question']}")

            # --- Onglet JSON ---
            with tab_json:
                st.json(payslip_dict)
                json_str = json.dumps(payslip_dict, ensure_ascii=False, indent=2)
                st.download_button(
                    label=f"Telecharger le JSON ({fichier})",
                    data=json_str,
                    file_name=f"{os.path.splitext(fichier)[0]}_analyse.json",
                    mime="application/json",
                )


# --- Footer ---
st.divider()
st.caption(
    "Application d'analyse de fiches de paie | "
    "Les donnees restent sur votre navigateur et ne sont pas stockees."
)
