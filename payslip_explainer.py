"""
Moteur d'explication pédagogique des fiches de paie.
Génère des explications claires et accessibles pour chaque ligne.
"""

import re
from knowledge_base import PAYSLIP_KNOWLEDGE, LABEL_PATTERNS


def find_knowledge(designation: str) -> dict:
    """Trouve l'explication dans la base de connaissances pour un libellé donné."""
    # Recherche exacte
    if designation in PAYSLIP_KNOWLEDGE:
        return PAYSLIP_KNOWLEDGE[designation]

    # Recherche par pattern
    for pattern, key in LABEL_PATTERNS.items():
        if re.search(pattern, designation, re.IGNORECASE):
            if key in PAYSLIP_KNOWLEDGE:
                return PAYSLIP_KNOWLEDGE[key]

    return None


def explain_line(line_dict: dict) -> dict:
    """Génère une explication pédagogique pour une ligne de fiche de paie."""
    designation = line_dict.get("designation", "")
    knowledge = find_knowledge(designation)

    explanation = {
        "designation": designation,
        "montant_employe": line_dict.get("montant_employe", 0),
        "montant_employeur": line_dict.get("montant_employeur", 0),
        "base": line_dict.get("nombre_ou_base", ""),
        "taux": line_dict.get("taux_ou_pourcent", ""),
    }

    if knowledge:
        explanation.update({
            "type": knowledge["type"],
            "categorie": knowledge["categorie"],
            "explication": knowledge["explication"],
            "a_quoi_ca_sert": knowledge["a_quoi_ca_sert"],
            "qui_paie": knowledge["qui_paie"],
            "obligatoire": knowledge["obligatoire"],
            "connu": True,
        })
    else:
        explanation.update({
            "type": "inconnu",
            "categorie": "inconnu",
            "explication": f"Ligne non reconnue : '{designation}'. Vérification manuelle nécessaire.",
            "a_quoi_ca_sert": "À déterminer",
            "qui_paie": "À déterminer",
            "obligatoire": None,
            "connu": False,
        })

    return explanation


def generate_text_report(payslip_dict: dict, explanations: list) -> str:
    """Génère un rapport textuel lisible et pédagogique."""
    report = []
    resume = payslip_dict["resume"]

    # En-tête
    report.append("=" * 70)
    report.append("  ANALYSE DE VOTRE FICHE DE PAIE")
    report.append("=" * 70)
    report.append("")

    # Informations générales
    report.append("--- INFORMATIONS GENERALES ---")
    report.append(f"  Entreprise     : {resume['employeur']['nom']}")
    report.append(f"  SIRET          : {resume['employeur']['siret']}")
    report.append(f"  Convention     : {resume['employeur']['convention_collective']}")
    report.append(f"  Salarié        : {resume['salarie']['nom']}")
    report.append(f"  Matricule      : {resume['salarie']['matricule']}")
    report.append(f"  N° SS          : {resume['salarie']['num_securite_sociale']}")
    report.append(f"  Emploi         : {resume['salarie']['emploi']}")
    report.append(f"  Classification : {resume['salarie']['classification']}")
    report.append(f"  Coefficient    : {resume['salarie']['coefficient']}")
    report.append(f"  Période        : {resume['periode']}")
    report.append(f"  Date paiement  : {resume['date_paiement']}")
    report.append(f"  Horaire        : {resume['salarie']['horaire']}h/semaine")
    report.append(f"  Taux horaire   : {resume['salarie']['taux_horaire']} EUR")
    report.append(f"  Sal. mensuel   : {resume['salarie']['salaire_mensuel_ref']} EUR")
    report.append(f"  Congés acquis  : {resume.get('conges_acquis', 'N/A')}")
    report.append("")

    # Résumé des montants
    report.append("--- RESUME FINANCIER ---")
    report.append(f"  Rémunération brute      : {resume['remuneration_brute']:>10.2f} EUR")
    report.append(f"  Cotisations salariales   : {resume['cotisations_salariales']:>10.2f} EUR")
    if resume['indemnites_non_soumises']:
        report.append(f"  Indemnités non soumises  : {resume['indemnites_non_soumises']:>10.2f} EUR")
    report.append(f"  Autres retenues          : {resume['autres_retenues']:>10.2f} EUR")
    report.append(f"  Cotisations patronales   : {resume['cotisations_patronales']:>10.2f} EUR")
    if resume['montant_net_social']:
        report.append(f"  Montant net social       : {resume['montant_net_social']:>10.2f} EUR")
    report.append(f"  Net avant impôt          : {resume['net_avant_impot']:>10.2f} EUR")
    report.append(f"  >>> NET A PAYER          : {resume['net_a_payer']:>10.2f} EUR <<<")
    report.append(f"  Net fiscal               : {resume['net_fiscal']:>10.2f} EUR")
    report.append(f"  Total versé employeur    : {resume['total_verse_employeur']:>10.2f} EUR")
    report.append(f"  Mode de paiement         : {resume['mode_paiement']}")
    report.append("")

    # Le calcul expliqué
    report.append("--- COMMENT ON ARRIVE AU NET A PAYER ---")
    report.append(f"  Brut                       {resume['remuneration_brute']:>10.2f}")
    report.append(f"  - Cotisations salariales   {resume['cotisations_salariales']:>10.2f}")
    if resume['indemnites_non_soumises']:
        report.append(f"  + Indemnités non soumises  {resume['indemnites_non_soumises']:>10.2f}")
    report.append(f"  - Autres retenues          {resume['autres_retenues']:>10.2f}")
    report.append(f"  = NET A PAYER              {resume['net_a_payer']:>10.2f}")
    report.append("")
    report.append("  Formule : Net = Brut (1) - Cotisations (2) + Indemnités (3) - Retenues (4)")
    report.append("")

    # Détail par section
    sections = [
        ("REMUNERATION", "remuneration",
         "Ce que vous gagnez avant toute déduction."),
        ("PRIMES", "primes",
         "Compléments de rémunération liés à la performance ou à des événements."),
        ("COTISATIONS SOCIALES", "cotisations",
         "Contributions obligatoires qui financent la protection sociale (santé, retraite, chômage...)."),
        ("RETENUES", "retenues",
         "Déductions supplémentaires sur votre salaire (tickets restaurant, impôt, saisies...)."),
    ]

    for title, key, description in sections:
        items = payslip_dict.get(key, [])
        if not items:
            continue

        report.append(f"--- {title} ---")
        report.append(f"  {description}")
        report.append("")

        for item in items:
            desig = item["designation"]

            # Skip totals in display
            if desig.startswith("TOTAL "):
                continue

            explanation = None
            for exp in explanations:
                if exp["designation"] == desig:
                    explanation = exp
                    break

            montant_emp = item.get("montant_employe", 0)
            montant_pat = item.get("montant_employeur", 0)

            report.append(f"  [{desig}]")
            if montant_emp:
                report.append(f"    Part salarié   : {montant_emp:>10.2f} EUR")
            if montant_pat:
                report.append(f"    Part employeur  : {montant_pat:>10.2f} EUR")
            if item.get("nombre_ou_base"):
                report.append(f"    Base            : {item['nombre_ou_base']}")
            if item.get("taux_ou_pourcent"):
                report.append(f"    Taux            : {item['taux_ou_pourcent']}")

            if explanation and explanation.get("connu"):
                report.append(f"    Type            : {explanation['type']}")
                report.append(f"    Explication     : {explanation['explication']}")
                report.append(f"    A quoi ça sert  : {explanation['a_quoi_ca_sert']}")
                report.append(f"    Qui paie        : {explanation['qui_paie']}")
                report.append(f"    Obligatoire     : {'Oui' if explanation['obligatoire'] else 'Non'}")
            elif explanation:
                report.append(f"    /!\\ LIGNE NON RECONNUE - vérification manuelle nécessaire")

            report.append("")

    # Net
    net = payslip_dict.get("net", {})
    report.append("--- NET A PAYER ---")
    report.append(f"  Montant net social   : {net.get('montant_net_social', 0):>10.2f} EUR")
    report.append(f"    -> C'est le montant de référence pour les aides sociales (ex: prime d'activité)")
    report.append(f"  Net avant impôt      : {net.get('net_avant_impot', 0):>10.2f} EUR")
    report.append(f"    -> Ce que vous recevez avant le prélèvement de l'impôt sur le revenu")
    report.append(f"  Net à payer          : {net.get('net_a_payer', 0):>10.2f} EUR")
    report.append(f"    -> Le montant réellement versé sur votre compte bancaire")
    report.append(f"  Net fiscal           : {net.get('net_fiscal', 0):>10.2f} EUR")
    report.append(f"    -> Base de calcul de votre impôt sur le revenu")
    if net.get('hs_exonerees'):
        report.append(f"  HS exonérées         : {net['hs_exonerees']:>10.2f} EUR")
        report.append(f"    -> Heures supplémentaires exonérées d'impôt (jusqu'à 7 500 EUR/an)")
    report.append(f"  Taux d'imposition    : {net.get('taux_impot', 'N/A')}")
    report.append(f"  Mode de paiement     : {net.get('mode_paiement', 'N/A')}")
    report.append("")

    # Questions
    questions = []
    for exp in explanations:
        if not exp.get("connu"):
            questions.append(exp["designation"])

    if questions:
        report.append("--- QUESTIONS / LIGNES AMBIGUES ---")
        report.append("  Les lignes suivantes n'ont pas pu être identifiées avec certitude :")
        for q in questions:
            report.append(f"  - {q}")
        report.append("  -> Pouvez-vous nous préciser leur signification ?")
        report.append("")

    report.append("=" * 70)
    report.append("  Fin de l'analyse")
    report.append("=" * 70)

    return "\n".join(report)


def explain_payslip(payslip_dict: dict) -> tuple:
    """
    Analyse complète d'une fiche de paie.
    Retourne (explanations_list, text_report, questions_list).
    """
    explanations = []
    questions = []

    # Explain all lines from all sections
    for section_key in ("remuneration", "primes", "cotisations", "retenues"):
        for line in payslip_dict.get(section_key, []):
            exp = explain_line(line)
            explanations.append(exp)
            if not exp.get("connu"):
                questions.append({
                    "ligne": exp["designation"],
                    "montant_employe": exp["montant_employe"],
                    "montant_employeur": exp["montant_employeur"],
                    "question": f"Qu'est-ce que '{exp['designation']}' ? Cette ligne n'est pas dans notre base de connaissances."
                })

    # Update questions in dict
    payslip_dict["questions"] = questions

    # Generate text report
    text_report = generate_text_report(payslip_dict, explanations)

    return explanations, text_report, questions
