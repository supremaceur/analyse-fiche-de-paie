"""
Application principale d'analyse de fiches de paie.
Point d'entrée CLI pour analyser, expliquer et comparer des fiches de paie.
"""

import sys
import os
import json
import argparse

from payslip_parser import parse_payslip, payslip_to_dict
from payslip_explainer import explain_payslip
from payslip_comparator import (
    load_all_payslips,
    build_label_dictionary,
    compare_two_payslips,
    detect_anomalies,
    generate_evolution_report,
)


def analyze_single(filepath: str, output_dir: str = None):
    """Analyse une seule fiche de paie."""
    print(f"\nAnalyse de : {filepath}")
    print("-" * 50)

    payslip = parse_payslip(filepath)
    payslip_dict = payslip_to_dict(payslip)
    explanations, text_report, questions = explain_payslip(payslip_dict)

    # Afficher le rapport texte
    print(text_report)

    # Sauvegarder le JSON si output_dir spécifié
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        basename = os.path.splitext(os.path.basename(filepath))[0]

        json_path = os.path.join(output_dir, f"{basename}_analyse.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payslip_dict, f, ensure_ascii=False, indent=2)
        print(f"\nJSON sauvegardé : {json_path}")

        txt_path = os.path.join(output_dir, f"{basename}_rapport.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text_report)
        print(f"Rapport sauvegardé : {txt_path}")

    return payslip_dict


def analyze_all(folder: str, output_dir: str = None):
    """Analyse toutes les fiches d'un dossier."""
    print(f"\nChargement des fiches depuis : {folder}")
    payslips = load_all_payslips(folder)
    print(f"{len(payslips)} fiches chargées.")

    # Dictionnaire des libellés
    label_dict = build_label_dictionary(payslips)
    print(f"\n{len(label_dict)} libellés différents identifiés.")

    # Rapport d'évolution
    evolution_report = generate_evolution_report(payslips)
    print(evolution_report)

    # Anomalies
    anomalies = detect_anomalies(payslips)
    if anomalies:
        print(f"\n{len(anomalies)} anomalie(s) détectée(s).")

    # Sauvegarder
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

        # Dictionnaire des libellés
        dict_path = os.path.join(output_dir, "dictionnaire_libelles.json")
        with open(dict_path, "w", encoding="utf-8") as f:
            json.dump(label_dict, f, ensure_ascii=False, indent=2)
        print(f"\nDictionnaire sauvegardé : {dict_path}")

        # Rapport d'évolution
        evol_path = os.path.join(output_dir, "rapport_evolution.txt")
        with open(evol_path, "w", encoding="utf-8") as f:
            f.write(evolution_report)
        print(f"Rapport d'évolution sauvegardé : {evol_path}")

        # Anomalies
        if anomalies:
            anom_path = os.path.join(output_dir, "anomalies.json")
            with open(anom_path, "w", encoding="utf-8") as f:
                json.dump(anomalies, f, ensure_ascii=False, indent=2)
            print(f"Anomalies sauvegardées : {anom_path}")

        # Toutes les analyses individuelles
        all_analyses_path = os.path.join(output_dir, "toutes_analyses.json")
        with open(all_analyses_path, "w", encoding="utf-8") as f:
            json.dump(payslips, f, ensure_ascii=False, indent=2)
        print(f"Analyses complètes sauvegardées : {all_analyses_path}")

    return payslips, label_dict, anomalies


def compare(filepath1: str, filepath2: str):
    """Compare deux fiches de paie."""
    p1 = parse_payslip(filepath1)
    p2 = parse_payslip(filepath2)
    d1 = payslip_to_dict(p1)
    d2 = payslip_to_dict(p2)

    diff = compare_two_payslips(d1, d2)

    print(f"\nComparaison : {diff['periode_1']} vs {diff['periode_2']}")
    print("-" * 50)

    if diff["variations"]:
        print("\nVariations :")
        for v in diff["variations"]:
            sign = "+" if v["difference"] > 0 else ""
            print(f"  {v['element']:40s} : {v['valeur_1']:>8.2f} -> {v['valeur_2']:>8.2f} ({sign}{v['difference']:.2f} EUR, {sign}{v['variation_pct']:.1f}%)")

    if diff["lignes_ajoutees"]:
        print(f"\nLignes ajoutées dans {diff['periode_2']} :")
        for l in diff["lignes_ajoutees"]:
            print(f"  + {l}")

    if diff["lignes_supprimees"]:
        print(f"\nLignes supprimées par rapport à {diff['periode_1']} :")
        for l in diff["lignes_supprimees"]:
            print(f"  - {l}")

    return diff


def main():
    parser = argparse.ArgumentParser(description="Analyseur de fiches de paie françaises")
    subparsers = parser.add_subparsers(dest="command")

    # Analyse simple
    p_analyze = subparsers.add_parser("analyser", help="Analyser une fiche de paie")
    p_analyze.add_argument("fichier", help="Chemin vers le fichier PDF")
    p_analyze.add_argument("-o", "--output", help="Dossier de sortie")

    # Analyse de toutes les fiches
    p_all = subparsers.add_parser("tout-analyser", help="Analyser toutes les fiches d'un dossier")
    p_all.add_argument("dossier", help="Dossier contenant les fiches PDF")
    p_all.add_argument("-o", "--output", help="Dossier de sortie", default="output")

    # Comparaison
    p_compare = subparsers.add_parser("comparer", help="Comparer deux fiches")
    p_compare.add_argument("fichier1", help="Première fiche PDF")
    p_compare.add_argument("fichier2", help="Deuxième fiche PDF")

    args = parser.parse_args()

    if args.command == "analyser":
        analyze_single(args.fichier, args.output)
    elif args.command == "tout-analyser":
        analyze_all(args.dossier, args.output)
    elif args.command == "comparer":
        compare(args.fichier1, args.fichier2)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
