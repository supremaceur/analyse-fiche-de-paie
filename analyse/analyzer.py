"""
Module d'analyse centralisé.
Fonction unique analyser_fiche() qui retourne un dictionnaire de synthèse.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from payslip_explainer import explain_payslip, find_knowledge
from knowledge_base import PAYSLIP_KNOWLEDGE


def _extraire_absences(payslip_dict: dict) -> list:
    """
    Extrait et structure les absences depuis une fiche de paie.
    Retourne une liste de dicts : {type, jours, montant}
    """
    absences = []

    # Mapping des libellés vers les types d'absence lisibles
    absence_labels = {
        "ABS CONGES PAYES": "Congés payés",
        "ABS. JOUR FERIE": "Jour férié",
        "ABSENCE H.MALADIE": "Arrêt maladie",
        "ABS. NON AUTORISEE": "Absence non autorisée",
        "ABS. AUTOR.NON PAYEE": "Absence autorisée non payée",
        "ABS. DELEGATION CSE": "Délégation CSE",
        "ABS. DELEGATION": "Délégation",
        "ABS ECO ET SYNDICAL": "Activité syndicale",
        "ABSENCE DIVERS": "Absence diverse",
    }

    for section_key in ("remuneration", "cotisations"):
        for line in payslip_dict.get(section_key, []):
            desig = line.get("designation", "")
            if desig in absence_labels:
                base = line.get("nombre_ou_base", "")
                # Essayer de calculer les jours à partir de la base
                jours = ""
                if base:
                    try:
                        val = float(base)
                        if val > 0:
                            # La base est en heures centièmes, convertir en jours (7h/jour)
                            jours_calc = val / 7
                            if jours_calc == int(jours_calc):
                                jours = f"{int(jours_calc)} jour(s)"
                            else:
                                jours = f"{jours_calc:.1f} jour(s)"
                    except (ValueError, ZeroDivisionError):
                        jours = base

                montant = abs(line.get("montant_employe", 0))
                absences.append({
                    "type": absence_labels[desig],
                    "jours": jours,
                    "montant": montant,
                })

    return absences


def _formater_absences(absences: list) -> str:
    """Formate les absences en texte lisible."""
    if not absences:
        return "Aucune"

    parts = []
    for a in absences:
        if a["jours"]:
            parts.append(f"{a['jours']} - {a['type']}")
        else:
            parts.append(a["type"])
    return " | ".join(parts)


def _extraire_primes(payslip_dict: dict) -> float:
    """Calcule le total des primes."""
    total = 0.0
    for line in payslip_dict.get("primes", []):
        montant = line.get("montant_employe", 0)
        if montant > 0:
            total += montant
    return total


def _extraire_heures(payslip_dict: dict) -> str:
    """Extrait les heures travaillées."""
    horaire = payslip_dict["resume"]["salarie"].get("horaire", "35,00")
    # Chercher les heures normales et supplémentaires
    hs = 0.0
    hn_base = horaire.replace(",", ".")

    for line in payslip_dict.get("remuneration", []):
        desig = line.get("designation", "")
        if "HRES SUPPL" in desig:
            base = line.get("nombre_ou_base", "0")
            try:
                hs += float(base)
            except ValueError:
                pass

    result = f"{hn_base}h/sem"
    if hs > 0:
        result += f" + {hs:.1f}h sup"
    return result


def analyser_fiche(uploaded_file) -> dict:
    """
    Fonction centralisée d'analyse d'une fiche de paie.

    Args:
        uploaded_file: fichier uploadé via Streamlit (UploadedFile)

    Returns:
        Dictionnaire de synthèse avec les clés principales.
    """
    from analyse.parser import parse_uploaded_file

    # Parser le fichier
    payslip_dict = parse_uploaded_file(uploaded_file)

    # Extraire les explications
    explanations, text_report, questions = explain_payslip(payslip_dict)

    # Extraire les absences
    absences = _extraire_absences(payslip_dict)
    absences_text = _formater_absences(absences)

    # Extraire les primes
    total_primes = _extraire_primes(payslip_dict)

    # Extraire les heures
    heures = _extraire_heures(payslip_dict)

    resume = payslip_dict["resume"]

    return {
        # --- Synthèse pour le tableau ---
        "nom": resume["salarie"].get("nom", "Inconnu"),
        "periode": resume.get("periode", ""),
        "coefficient": resume["salarie"].get("coefficient", ""),
        "taux_horaire": resume["salarie"].get("taux_horaire", ""),
        "heures": heures,
        "absences": absences_text,
        "brut": resume.get("remuneration_brute", 0),
        "primes": total_primes,
        "net": resume.get("net_a_payer", 0),
        # --- Détails complets ---
        "detail": {
            "fichier": uploaded_file.name,
            "payslip_dict": payslip_dict,
            "explanations": explanations,
            "text_report": text_report,
            "questions": questions,
            "absences_detail": absences,
            "net_fiscal": resume.get("net_fiscal", 0),
            "net_avant_impot": resume.get("net_avant_impot", 0),
            "montant_net_social": resume.get("montant_net_social", 0),
            "cotisations_salariales": resume.get("cotisations_salariales", 0),
            "cotisations_patronales": resume.get("cotisations_patronales", 0),
            "total_verse_employeur": resume.get("total_verse_employeur", 0),
            "mode_paiement": resume.get("mode_paiement", ""),
            "employeur": resume.get("employeur", {}),
            "conges": resume.get("conges", {}),
        },
    }
