"""
Comparateur de fiches de paie.
Permet de comparer plusieurs fiches, détecter des anomalies et identifier des tendances.
"""

import os
import re
from payslip_parser import parse_payslip, payslip_to_dict


def extract_period_key(filename: str) -> str:
    """Extrait la clé de période (YYYYMM) d'un nom de fichier."""
    m = re.search(r"Periode (\d{6})", filename)
    return m.group(1) if m else ""


def load_all_payslips(folder: str) -> list:
    """Charge et parse toutes les fiches de paie d'un dossier."""
    payslips = []
    files = sorted([f for f in os.listdir(folder) if f.endswith(".pdf")])
    for f in files:
        filepath = os.path.join(folder, f)
        try:
            payslip = parse_payslip(filepath)
            payslip_dict = payslip_to_dict(payslip)
            payslip_dict["_filename"] = f
            payslip_dict["_period_key"] = extract_period_key(f)
            payslips.append(payslip_dict)
        except Exception as e:
            print(f"Erreur lors du parsing de {f}: {e}")
    return payslips


def build_label_dictionary(payslips: list) -> dict:
    """
    Construit un dictionnaire de toutes les lignes (designations) rencontrées
    à travers toutes les fiches de paie.

    Retourne: {designation: {count, sections, montant_min, montant_max, periodes}}
    """
    label_dict = {}

    for payslip in payslips:
        period = payslip.get("_period_key", "")
        for section_key in ("remuneration", "primes", "cotisations", "retenues"):
            for line in payslip.get(section_key, []):
                desig = line["designation"]
                if desig.startswith("TOTAL "):
                    continue

                if desig not in label_dict:
                    label_dict[desig] = {
                        "count": 0,
                        "sections": set(),
                        "montants_employe": [],
                        "montants_employeur": [],
                        "periodes": [],
                    }

                entry = label_dict[desig]
                entry["count"] += 1
                entry["sections"].add(section_key)
                entry["periodes"].append(period)

                if line.get("montant_employe"):
                    entry["montants_employe"].append(line["montant_employe"])
                if line.get("montant_employeur"):
                    entry["montants_employeur"].append(line["montant_employeur"])

    # Compute stats
    for desig, entry in label_dict.items():
        entry["sections"] = list(entry["sections"])
        if entry["montants_employe"]:
            entry["montant_employe_min"] = min(entry["montants_employe"])
            entry["montant_employe_max"] = max(entry["montants_employe"])
            entry["montant_employe_moy"] = sum(entry["montants_employe"]) / len(entry["montants_employe"])
        else:
            entry["montant_employe_min"] = 0
            entry["montant_employe_max"] = 0
            entry["montant_employe_moy"] = 0

        if entry["montants_employeur"]:
            entry["montant_employeur_min"] = min(entry["montants_employeur"])
            entry["montant_employeur_max"] = max(entry["montants_employeur"])
            entry["montant_employeur_moy"] = sum(entry["montants_employeur"]) / len(entry["montants_employeur"])
        else:
            entry["montant_employeur_min"] = 0
            entry["montant_employeur_max"] = 0
            entry["montant_employeur_moy"] = 0

        # Remove raw lists for cleaner output
        del entry["montants_employe"]
        del entry["montants_employeur"]

        # First and last occurrence
        if entry["periodes"]:
            entry["premiere_occurrence"] = min(entry["periodes"])
            entry["derniere_occurrence"] = max(entry["periodes"])
        entry["periodes_count"] = len(entry["periodes"])
        del entry["periodes"]

    return label_dict


def compare_two_payslips(payslip1: dict, payslip2: dict) -> dict:
    """Compare deux fiches de paie et retourne les différences."""
    differences = {
        "periode_1": payslip1["resume"]["periode"],
        "periode_2": payslip2["resume"]["periode"],
        "variations": [],
        "lignes_ajoutees": [],
        "lignes_supprimees": [],
    }

    # Compare summary amounts
    summary_fields = [
        ("remuneration_brute", "Rémunération brute"),
        ("cotisations_salariales", "Cotisations salariales"),
        ("net_a_payer", "Net à payer"),
        ("net_fiscal", "Net fiscal"),
        ("cotisations_patronales", "Cotisations patronales"),
        ("total_verse_employeur", "Total versé employeur"),
    ]

    for field, label in summary_fields:
        val1 = payslip1["resume"].get(field, 0)
        val2 = payslip2["resume"].get(field, 0)
        if val1 != val2:
            diff = val2 - val1
            pct = (diff / val1 * 100) if val1 else 0
            differences["variations"].append({
                "element": label,
                "valeur_1": val1,
                "valeur_2": val2,
                "difference": round(diff, 2),
                "variation_pct": round(pct, 2),
            })

    # Compare individual lines
    lines1 = {}
    lines2 = {}
    for section in ("remuneration", "primes", "cotisations", "retenues"):
        for line in payslip1.get(section, []):
            lines1[line["designation"]] = line
        for line in payslip2.get(section, []):
            lines2[line["designation"]] = line

    all_designations = set(lines1.keys()) | set(lines2.keys())
    for desig in sorted(all_designations):
        if desig in lines1 and desig not in lines2:
            differences["lignes_supprimees"].append(desig)
        elif desig not in lines1 and desig in lines2:
            differences["lignes_ajoutees"].append(desig)
        elif desig in lines1 and desig in lines2:
            m1 = lines1[desig].get("montant_employe", 0)
            m2 = lines2[desig].get("montant_employe", 0)
            if m1 != m2:
                differences["variations"].append({
                    "element": desig,
                    "valeur_1": m1,
                    "valeur_2": m2,
                    "difference": round(m2 - m1, 2),
                    "variation_pct": round(((m2 - m1) / m1 * 100) if m1 else 0, 2),
                })

    return differences


def detect_anomalies(payslips: list) -> list:
    """Détecte des anomalies ou variations inhabituelles entre les fiches."""
    anomalies = []

    if len(payslips) < 2:
        return anomalies

    # Track net à payer evolution
    nets = []
    for p in payslips:
        period = p.get("_period_key", "")
        net = p["resume"].get("net_a_payer", 0)
        brut = p["resume"].get("remuneration_brute", 0)
        if net and brut:
            nets.append({"period": period, "net": net, "brut": brut})

    # Detect significant variations (>20% change)
    for i in range(1, len(nets)):
        if nets[i - 1]["net"] == 0:
            continue
        variation = abs(nets[i]["net"] - nets[i - 1]["net"]) / nets[i - 1]["net"] * 100
        if variation > 20:
            anomalies.append({
                "type": "variation_importante",
                "periode": nets[i]["period"],
                "periode_precedente": nets[i - 1]["period"],
                "net_precedent": nets[i - 1]["net"],
                "net_actuel": nets[i]["net"],
                "variation_pct": round(variation, 2),
                "message": f"Variation de {variation:.1f}% du net à payer entre {nets[i-1]['period']} et {nets[i]['period']}",
            })

    # Track taux horaire changes
    taux_horaires = []
    for p in payslips:
        th = p["resume"]["salarie"].get("taux_horaire", "")
        period = p.get("_period_key", "")
        if th:
            taux_horaires.append({"period": period, "taux": th})

    for i in range(1, len(taux_horaires)):
        if taux_horaires[i]["taux"] != taux_horaires[i - 1]["taux"]:
            anomalies.append({
                "type": "changement_taux_horaire",
                "periode": taux_horaires[i]["period"],
                "ancien_taux": taux_horaires[i - 1]["taux"],
                "nouveau_taux": taux_horaires[i]["taux"],
                "message": f"Changement de taux horaire : {taux_horaires[i-1]['taux']} -> {taux_horaires[i]['taux']} EUR en {taux_horaires[i]['period']}",
            })

    return anomalies


def generate_evolution_report(payslips: list) -> str:
    """Génère un rapport d'évolution sur toutes les fiches."""
    report = []
    report.append("=" * 70)
    report.append("  RAPPORT D'EVOLUTION DES FICHES DE PAIE")
    report.append("=" * 70)
    report.append("")
    report.append(f"  Nombre de fiches analysées : {len(payslips)}")

    if payslips:
        first = payslips[0].get("_period_key", "")
        last = payslips[-1].get("_period_key", "")
        report.append(f"  Période couverte : {first} à {last}")
    report.append("")

    # Taux horaire evolution
    report.append("--- EVOLUTION DU TAUX HORAIRE ---")
    seen_taux = set()
    for p in payslips:
        th = p["resume"]["salarie"].get("taux_horaire", "")
        period = p.get("_period_key", "")
        key = f"{th}"
        if key not in seen_taux:
            seen_taux.add(key)
            report.append(f"  {period} : {th} EUR/h")
    report.append("")

    # Net à payer evolution
    report.append("--- EVOLUTION DU NET A PAYER ---")
    for p in payslips:
        period = p.get("_period_key", "")
        net = p["resume"].get("net_a_payer", 0)
        brut = p["resume"].get("remuneration_brute", 0)
        bar = "#" * max(1, int(net / 50))
        report.append(f"  {period} : {net:>8.2f} EUR (brut: {brut:>8.2f}) {bar}")
    report.append("")

    # Anomalies
    anomalies = detect_anomalies(payslips)
    if anomalies:
        report.append("--- ANOMALIES DETECTEES ---")
        for a in anomalies:
            report.append(f"  [{a['type']}] {a['message']}")
        report.append("")

    report.append("=" * 70)
    return "\n".join(report)
