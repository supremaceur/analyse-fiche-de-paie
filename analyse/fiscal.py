"""
Analyse fiscale : comparaison abattement forfaitaire 10% vs frais réels.
Barèmes 2026 (déclaration des revenus 2025).

Sources :
- Barème kilométrique : Arrêté du 27 mars 2025 (reconduit 2026)
- Abattement forfaitaire 10% : Article 83 CGI, revalorisation +0,9 % 2026
- Frais repas : Bulletin Officiel des Finances Publiques
"""

from __future__ import annotations
import re
from typing import Any

# ============================================================
# BARÈMES 2026
# ============================================================

# Voitures (essence/diesel) — distance totale annuelle (A/R × jours)
# Format par tranche : (taux, fixed_amount, seuil_superieur)
#   montant = taux × distance         si distance ≤ seuil tranche 1
#   montant = taux × distance + fix   si distance ≤ seuil tranche 2
#   montant = taux × distance         si distance > seuil tranche 2
BAREME_VOITURE: dict[int, dict] = {
    3: {"lim1": 5_000, "t1": 0.529, "lim2": 20_000, "t2": 0.316, "f2": 1_065, "t3": 0.370},
    4: {"lim1": 5_000, "t1": 0.606, "lim2": 20_000, "t2": 0.340, "f2": 1_330, "t3": 0.407},
    5: {"lim1": 5_000, "t1": 0.636, "lim2": 20_000, "t2": 0.357, "f2": 1_395, "t3": 0.427},
    6: {"lim1": 5_000, "t1": 0.665, "lim2": 20_000, "t2": 0.374, "f2": 1_457, "t3": 0.447},
    7: {"lim1": 5_000, "t1": 0.697, "lim2": 20_000, "t2": 0.394, "f2": 1_515, "t3": 0.470},
}

# Motocyclettes (cylindrée > 50 cm³)
BAREME_MOTO: dict[str, dict] = {
    "1-2": {"lim1": 3_000, "t1": 0.395, "lim2": 6_000, "t2": 0.099, "f2": 891,   "t3": 0.248},
    "3-5": {"lim1": 3_000, "t1": 0.468, "lim2": 6_000, "t2": 0.082, "f2": 1_158, "t3": 0.275},
    "6+":  {"lim1": 3_000, "t1": 0.606, "lim2": 6_000, "t2": 0.079, "f2": 1_583, "t3": 0.343},
}

# Cyclomoteurs / scooters (cylindrée ≤ 50 cm³)
BAREME_CYCLO: dict[str, dict] = {
    "any": {"lim1": 2_000, "t1": 0.147, "lim2": 5_000, "t2": 0.082, "f2": 130, "t3": 0.108},
}

# Abattement forfaitaire 10%
ABATTEMENT_TAUX = 0.10
ABATTEMENT_MIN  = 499     # plancher 2026 (revenus 2025)
ABATTEMENT_MAX  = 13_643  # plafond 2026 (revenus 2025)

# Bonus véhicule électrique
BONUS_ELECTRIQUE = 1.20   # +20% sur le barème kilométrique


# ============================================================
# FONCTIONS DE CALCUL
# ============================================================

def _appliquer_bareme(distance_km: float, b: dict) -> float:
    """Applique un barème à 3 tranches sur une distance totale."""
    if distance_km <= b["lim1"]:
        return distance_km * b["t1"]
    elif distance_km <= b["lim2"]:
        return distance_km * b["t2"] + b["f2"]
    else:
        return distance_km * b["t3"]


def calcul_frais_km_voiture(
    cv_fiscaux: int,
    distance_aller_km: float,
    jours_travailles: int,
    electrique: bool = False,
) -> dict:
    """
    Calcule les frais kilométriques déductibles pour une voiture.

    Args:
        cv_fiscaux:         Puissance fiscale du véhicule (3 à 7+ CV).
        distance_aller_km:  Distance domicile → travail (sens unique, en km).
        jours_travailles:   Nombre de jours travaillés dans l'année.
        electrique:         True si véhicule électrique (+20% barème).

    Returns:
        dict avec distance_totale, taux_applique, montant, detail.
    """
    cv = min(max(int(cv_fiscaux), 3), 7)
    bareme = BAREME_VOITURE[cv]
    distance_totale = distance_aller_km * 2 * jours_travailles
    montant = _appliquer_bareme(distance_totale, bareme)
    if electrique:
        montant *= BONUS_ELECTRIQUE
    return {
        "distance_totale_km": round(distance_totale, 1),
        "cv_fiscaux": cv,
        "electrique": electrique,
        "montant": round(montant, 2),
    }


def calcul_frais_km_moto(
    cv_moto: str,
    distance_aller_km: float,
    jours_travailles: int,
    electrique: bool = False,
) -> dict:
    """
    Calcule les frais kilométriques pour une motocyclette (> 50 cm³).

    Args:
        cv_moto: '1-2', '3-5' ou '6+'.
    """
    key = cv_moto if cv_moto in BAREME_MOTO else "3-5"
    bareme = BAREME_MOTO[key]
    distance_totale = distance_aller_km * 2 * jours_travailles
    montant = _appliquer_bareme(distance_totale, bareme)
    if electrique:
        montant *= BONUS_ELECTRIQUE
    return {
        "distance_totale_km": round(distance_totale, 1),
        "cv_moto": key,
        "electrique": electrique,
        "montant": round(montant, 2),
    }


def calcul_frais_km_cyclo(
    distance_aller_km: float,
    jours_travailles: int,
    electrique: bool = False,
) -> dict:
    """Calcule les frais kilométriques pour un cyclomoteur (≤ 50 cm³)."""
    bareme = BAREME_CYCLO["any"]
    distance_totale = distance_aller_km * 2 * jours_travailles
    montant = _appliquer_bareme(distance_totale, bareme)
    if electrique:
        montant *= BONUS_ELECTRIQUE
    return {
        "distance_totale_km": round(distance_totale, 1),
        "electrique": electrique,
        "montant": round(montant, 2),
    }


def calcul_abattement_forfaitaire(revenu_imposable: float) -> dict:
    """
    Calcule l'abattement forfaitaire de 10%.

    Returns:
        dict avec abattement, plancher_applique, plafond_applique, revenu_net.
    """
    abattement_brut = revenu_imposable * ABATTEMENT_TAUX
    abattement = max(min(abattement_brut, ABATTEMENT_MAX), ABATTEMENT_MIN)
    plancher = abattement_brut < ABATTEMENT_MIN
    plafond = abattement_brut > ABATTEMENT_MAX
    return {
        "taux": ABATTEMENT_TAUX,
        "abattement_brut": round(abattement_brut, 2),
        "abattement": round(abattement, 2),
        "plancher_applique": plancher,
        "plafond_applique": plafond,
        "revenu_net": round(revenu_imposable - abattement, 2),
    }


# ============================================================
# EXTRACTION DES DONNÉES DES FICHES
# ============================================================

def _safe_float(v: Any) -> float:
    """Convertit en float sans lever d'exception."""
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _parse_yyyymm(nom_fichier: str) -> int:
    """Extrait YYYYMM depuis un nom du type 'Periode 202312 - ...'  → 202312."""
    m = re.search(r"(\d{6})", nom_fichier)
    return int(m.group(1)) if m else 0


def extraire_donnees_annuelles(resultats: list[dict]) -> dict:
    """
    Extrait les données fiscales annuelles depuis les fiches analysées.

    Stratégie : utilise le champ NET FISCAL CUMUL de la fiche la plus récente
    (décembre ou dernier mois disponible), qui contient déjà le cumul annuel
    tel qu'affiché sur la fiche de paie. Ne fait donc PAS la somme des mois.

    Args:
        resultats: list des dicts retournés par analyser_fiche().

    Returns:
        dict avec revenu_fiscal_annuel, source_fiche, mois_source,
              tickets_resto, mutuelle, mois_disponibles, annee_detectee.
    """
    if not resultats:
        return {
            "revenu_fiscal_brut": 0.0,
            "source_cumul": "aucune fiche",
            "mois_source": None,
            "tickets_resto_salarie": 0.0,
            "mutuelle_salarie": 0.0,
            "primes_total": 0.0,
            "mois_disponibles": 0,
            "annee_detectee": None,
        }

    # --- Trier les fiches par date (YYYYMM) pour trouver la plus récente ---
    def _sort_key(r):
        fichier = r.get("detail", {}).get("fichier", "")
        return _parse_yyyymm(fichier)

    resultats_tries = sorted(resultats, key=_sort_key, reverse=True)
    fiche_recente = resultats_tries[0]

    det = fiche_recente.get("detail", {})
    payslip_dict = det.get("payslip_dict", {})
    resume = payslip_dict.get("resume", {})
    fichier_nom = det.get("fichier", "")
    yyyymm = _parse_yyyymm(fichier_nom)
    mois_source = yyyymm % 100 if yyyymm else None

    # NET FISCAL CUMUL = colonne "DEPUIS janvier" de la ligne NET FISCAL
    net_fiscal_cumul = _safe_float(
        det.get("net_fiscal_cumul") or resume.get("net_fiscal_cumul", 0)
    )
    # Fallback : si cumul absent, prend le mensuel (fiche incomplète ou ancienne)
    if net_fiscal_cumul == 0:
        net_fiscal_cumul = _safe_float(
            det.get("net_fiscal") or resume.get("net_fiscal", 0)
        )
        source_cumul = f"net fiscal mensuel uniquement ({fichier_nom})"
    else:
        source_cumul = f"cumul annuel depuis {fichier_nom}"

    # Détection de l'année depuis toutes les fiches
    annees: list[int] = []
    tickets_resto_salarie = 0.0
    mutuelle_salarie = 0.0
    primes_total = 0.0

    for r in resultats:
        det_r = r.get("detail", {})
        pd_r = det_r.get("payslip_dict", {})
        res_r = pd_r.get("resume", {})
        periode = res_r.get("periode", "") or r.get("periode", "")
        for yr in re.findall(r"\b(20\d{2})\b", periode):
            annees.append(int(yr))

        primes_total += _safe_float(r.get("primes", 0))

        # Tickets restaurant et mutuelle : chercher dans cotisations ET retenues
        for section in ("cotisations", "retenues"):
            for row in pd_r.get(section, []):
                desig = row.get("designation", "").upper()

                # RET.TITRE REPAS / TICKET RESTAURANT
                if "TITRE" in desig or "REPAS" in desig or "TICKET" in desig:
                    tickets_resto_salarie += abs(_safe_float(row.get("montant_employe", 0)))

                # Mutuelle / complémentaire santé obligatoire
                if ("SANTE" in desig or "MUTUELLE" in desig) and (
                    "COMPL" in desig or "OBLIG" in desig
                ):
                    mutuelle_salarie += abs(_safe_float(row.get("montant_employe", 0)))

    annee = max(annees) if annees else None

    return {
        "revenu_fiscal_brut": round(net_fiscal_cumul, 2),
        "source_cumul": source_cumul,
        "mois_source": mois_source,
        "tickets_resto_salarie": round(tickets_resto_salarie, 2),
        "mutuelle_salarie": round(mutuelle_salarie, 2),
        "primes_total": round(primes_total, 2),
        "mois_disponibles": len(resultats),
        "annee_detectee": annee,
    }


# ============================================================
# ANALYSE PRINCIPALE
# ============================================================

def analyse_fiscale(
    resultats: list[dict],
    inputs: dict,
) -> dict:
    """
    Compare l'abattement forfaitaire 10% et les frais réels.

    Args:
        resultats: fiches analysées (session_state["resultats"]).
        inputs: dict avec les clés suivantes :
            - type_vehicule   : "voiture" | "moto" | "cyclo"
            - cv_fiscaux      : int (voiture 3-7)
            - cv_moto         : str "1-2" | "3-5" | "6+"
            - electrique      : bool
            - distance_km     : float (aller simple, km)
            - jours_travailles: int
            - frais_repas     : float (€/an, saisi manuellement)
            - autres_frais    : float (€/an, saisi manuellement)
            - revenu_manuel   : float | None  (si pas de fiches chargées)

    Returns:
        dict complet avec revenu, frais_reels_detail, abattement, comparaison.
    """
    # --- 1. Données des fiches ---
    donnees = extraire_donnees_annuelles(resultats) if resultats else {
        "revenu_fiscal_brut": 0.0,
        "source_cumul": "aucune fiche",
        "mois_source": None,
        "tickets_resto_salarie": 0.0,
        "mutuelle_salarie": 0.0,
        "primes_total": 0.0,
        "mois_disponibles": 0,
        "annee_detectee": None,
    }

    # Revenus : cumul depuis la fiche la plus récente, ou saisie manuelle
    revenu = donnees["revenu_fiscal_brut"]
    if inputs.get("revenu_manuel") and revenu == 0:
        revenu = _safe_float(inputs["revenu_manuel"])
    revenu_annuel_estime = revenu  # pas d'extrapolation : on utilise le cumul réel

    # --- 2. Frais kilométriques ---
    type_v = inputs.get("type_vehicule", "voiture")
    distance = _safe_float(inputs.get("distance_km", 0))
    jours = int(inputs.get("jours_travailles", 0))
    electrique = bool(inputs.get("electrique", False))

    if distance > 0 and jours > 0:
        if type_v == "voiture":
            km_result = calcul_frais_km_voiture(
                cv_fiscaux=int(inputs.get("cv_fiscaux", 5)),
                distance_aller_km=distance,
                jours_travailles=jours,
                electrique=electrique,
            )
        elif type_v == "moto":
            km_result = calcul_frais_km_moto(
                cv_moto=inputs.get("cv_moto", "3-5"),
                distance_aller_km=distance,
                jours_travailles=jours,
                electrique=electrique,
            )
        else:  # cyclo
            km_result = calcul_frais_km_cyclo(
                distance_aller_km=distance,
                jours_travailles=jours,
                electrique=electrique,
            )
        frais_km_montant = km_result["montant"]
        km_detail = km_result
    else:
        frais_km_montant = 0.0
        km_detail = {"distance_totale_km": 0, "montant": 0.0}

    # --- 3. Frais repas saisis manuellement ---
    frais_repas = _safe_float(inputs.get("frais_repas", 0))

    # --- 4. Tickets restaurant (part salariale détectée dans les fiches) ---
    # RET. TITRE REPAS = la part que le salarié paie lui-même → déductible en frais réels
    tickets_resto = _safe_float(inputs.get("tickets_resto_auto", 0))
    if inputs.get("inclure_tickets_resto", True):
        frais_repas_total = frais_repas + tickets_resto
    else:
        frais_repas_total = frais_repas

    # --- 5. Mutuelle obligatoire (part salariale, ex: COMPLEMENTAIRE SANTE OBLIGATOIRE) ---
    # La cotisation mutuelle d'entreprise est déductible en frais réels
    mutuelle = _safe_float(inputs.get("mutuelle_auto", 0))
    if inputs.get("inclure_mutuelle", True):
        mutuelle_deductible = mutuelle
    else:
        mutuelle_deductible = 0.0

    # --- 6. Autres frais ---
    autres_frais = _safe_float(inputs.get("autres_frais", 0))

    # --- 7. Total frais réels ---
    total_frais_reels = frais_km_montant + frais_repas_total + mutuelle_deductible + autres_frais

    # --- 6. Abattement forfaitaire ---
    abo = calcul_abattement_forfaitaire(revenu_annuel_estime)

    # --- 7. Comparaison ---
    revenu_apres_abattement = abo["revenu_net"]
    revenu_apres_frais_reels = round(revenu_annuel_estime - total_frais_reels, 2)

    difference = round(revenu_apres_abattement - revenu_apres_frais_reels, 2)
    # difference > 0 → frais réels = assiette plus basse = plus avantageux
    # difference < 0 → abattement 10% = assiette plus basse = plus avantageux

    if difference > 0:
        option_optimale = "frais_reels"
        gain_fiscal = difference  # assiette réduite de cette somme
        explication = (
            f"Vos frais reels ({total_frais_reels:.0f} €) depassent l'abattement forfaitaire "
            f"({abo['abattement']:.0f} €). En declarant vos frais reels, votre revenu "
            f"imposable est reduit de {difference:.0f} € supplementaires."
        )
    elif difference < 0:
        option_optimale = "forfait_10"
        gain_fiscal = abs(difference)
        explication = (
            f"L'abattement forfaitaire de 10% ({abo['abattement']:.0f} €) depasse "
            f"vos frais reels estimes ({total_frais_reels:.0f} €). Le forfait vous est "
            f"plus favorable de {gain_fiscal:.0f} €."
        )
    else:
        option_optimale = "egal"
        gain_fiscal = 0.0
        explication = "Les deux options sont equivalentes dans votre situation."

    return {
        # Revenus
        "revenu_brut": revenu,
        "revenu_annuel_estime": revenu_annuel_estime,
        "mois_disponibles": donnees["mois_disponibles"],
        "mois_source": donnees.get("mois_source"),
        "source_cumul": donnees.get("source_cumul", ""),
        "annee_detectee": donnees["annee_detectee"],
        # Données fiches
        "donnees_fiches": donnees,
        # Abattement 10%
        "abattement": abo,
        "revenu_apres_abattement": revenu_apres_abattement,
        # Frais réels
        "frais_reels": {
            "km": km_detail,
            "frais_km": frais_km_montant,
            "frais_repas_manuel": frais_repas,
            "tickets_resto": tickets_resto,
            "frais_repas_total": round(frais_repas_total, 2),
            "mutuelle": round(mutuelle_deductible, 2),
            "autres_frais": autres_frais,
            "total": round(total_frais_reels, 2),
        },
        "revenu_apres_frais_reels": revenu_apres_frais_reels,
        # Comparaison
        "option_optimale": option_optimale,
        "gain_fiscal": round(gain_fiscal, 2),
        "difference_assiette": difference,
        "explication": explication,
    }
