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

# Réduction d'impôt scolarité (art. 199 quater F CGI) — barème 2026
REDUCTION_COLLEGE    = 61   # € par enfant au collège
REDUCTION_LYCEE      = 153  # € par enfant au lycée
REDUCTION_SUPERIEUR  = 183  # € par enfant en études supérieures

# Crédit d'impôt garde d'enfants (art. 200 quater B CGI)
TAUX_CREDIT_GARDE       = 0.50   # 50% des dépenses
PLAFOND_GARDE_HORS_DOM  = 3_500  # €/enfant/an pour crèche + assistante maternelle
PLAFOND_GARDE_DOMICILE  = 12_000 # €/an pour garde à domicile (emploi à domicile)


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


def calcul_parts_fiscales(situation: str, nb_enfants: int) -> dict:
    """
    Estime le nombre de parts fiscales du foyer (simplification CGI art. 194).

    Args:
        situation : 'celibataire' | 'marie_pacse' | 'parent_isole'
        nb_enfants: nombre d'enfants à charge (tous âges confondus)

    Returns:
        dict avec parts_base, parts_enfants, bonus_parent_isole, total_parts.

    Note : Calcul simplifié — cas complexes (invalidité, veuvage, garde alternée…)
           non traités. Le résultat est indicatif.
    """
    nb_enfants = max(0, int(nb_enfants))

    parts_base = 2.0 if situation == "marie_pacse" else 1.0

    parts_enfants = 0.0
    for i in range(nb_enfants):
        parts_enfants += 0.5 if i < 2 else 1.0   # 1er/2e: +0.5 ; 3e et +: +1

    # Parent isolé avec au moins 1 enfant : +0.5 part supplémentaire (art. 194 II)
    bonus_parent_isole = 0.5 if (situation == "parent_isole" and nb_enfants >= 1) else 0.0

    total = parts_base + parts_enfants + bonus_parent_isole
    return {
        "situation": situation,
        "nb_enfants": nb_enfants,
        "parts_base": parts_base,
        "parts_enfants": round(parts_enfants, 1),
        "bonus_parent_isole": bonus_parent_isole,
        "total_parts": round(total, 1),
    }


def calcul_reduction_scolarite(
    enfants_college: int,
    enfants_lycee: int,
    enfants_superieur: int,
) -> dict:
    """
    Calcule la réduction d'impôt pour frais de scolarité (art. 199 quater F CGI).
    Applicable directement sur l'impôt dû (réduction, pas déduction du revenu).

    Returns:
        dict avec détail par niveau et total_reduction.
    """
    enfants_college   = max(0, int(enfants_college))
    enfants_lycee     = max(0, int(enfants_lycee))
    enfants_superieur = max(0, int(enfants_superieur))

    r_college    = enfants_college   * REDUCTION_COLLEGE
    r_lycee      = enfants_lycee     * REDUCTION_LYCEE
    r_superieur  = enfants_superieur * REDUCTION_SUPERIEUR
    total        = r_college + r_lycee + r_superieur

    return {
        "enfants_college": enfants_college,
        "enfants_lycee": enfants_lycee,
        "enfants_superieur": enfants_superieur,
        "reduction_college": r_college,
        "reduction_lycee": r_lycee,
        "reduction_superieur": r_superieur,
        "total_reduction": total,
    }


def calcul_credit_garde(
    frais_creche: float,
    frais_assmat: float,
    frais_garde_domicile: float,
) -> dict:
    """
    Calcule le crédit d'impôt garde d'enfants (art. 200 quater B CGI).

    Garde hors domicile (crèche agréée + assistante maternelle agréée) :
    - 50% des dépenses plafonnées à 3 500 €/enfant/an
    - Pour simplification : plafond global de 3 500 € (un plafond par enfant
      nécessiterait de connaître le nombre exact d'enfants < 6 ans)

    Garde à domicile (emploi à domicile) :
    - 50% des dépenses plafonnées à 12 000 €/an

    Returns:
        dict avec détail des crédits et total_credit.
    """
    frais_creche         = max(0.0, _safe_float(frais_creche))
    frais_assmat         = max(0.0, _safe_float(frais_assmat))
    frais_garde_domicile = max(0.0, _safe_float(frais_garde_domicile))

    # Crèche + assistante maternelle (hors domicile)
    frais_hors_dom  = frais_creche + frais_assmat
    base_hors_dom   = min(frais_hors_dom, PLAFOND_GARDE_HORS_DOM)
    credit_hors_dom = round(base_hors_dom * TAUX_CREDIT_GARDE, 2)

    # Garde à domicile
    base_dom        = min(frais_garde_domicile, PLAFOND_GARDE_DOMICILE)
    credit_dom      = round(base_dom * TAUX_CREDIT_GARDE, 2)

    credit_total = credit_hors_dom + credit_dom

    return {
        "frais_creche": frais_creche,
        "frais_assmat": frais_assmat,
        "frais_hors_domicile": frais_hors_dom,
        "frais_hors_plafonne": base_hors_dom,
        "credit_hors_domicile": credit_hors_dom,
        "frais_garde_domicile": frais_garde_domicile,
        "frais_domicile_plafonne": base_dom,
        "credit_domicile": credit_dom,
        "credit_total": round(credit_total, 2),
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


def extraire_net_fiscal_annuel(fiche_decembre: dict) -> dict:
    """
    Extrait le net fiscal annuel UNIQUEMENT depuis une fiche de décembre.

    Règle absolue :
    - Ignorer la valeur mensuelle (1re colonne)
    - Prendre la valeur cumul annuel (2e colonne)

    Args:
        fiche_decembre: dict retourné par analyser_fiche() pour la fiche de décembre.

    Returns:
        dict avec net_fiscal_annuel, source, fiabilite.
    """
    if not fiche_decembre:
        return {
            "net_fiscal_annuel": 0.0,
            "source": "aucune_fiche",
            "fiabilite": "nulle",
        }

    det = fiche_decembre.get("detail", {})
    pd = det.get("payslip_dict", {})
    resume = pd.get("resume", {})

    # Valeur annuelle = colonne DEPUIS (cumul depuis janvier)
    net_fiscal_cumul = _safe_float(
        det.get("net_fiscal_cumul") or resume.get("net_fiscal_cumul", 0)
    )
    if net_fiscal_cumul > 0:
        return {
            "net_fiscal_annuel": round(net_fiscal_cumul, 2),
            "source": "fiche_decembre",
            "fiabilite": "élevée",
        }

    # Fallback : seulement la valeur mensuelle trouvée
    net_fiscal_mensuel = _safe_float(
        det.get("net_fiscal") or resume.get("net_fiscal", 0)
    )
    if net_fiscal_mensuel > 0:
        return {
            "net_fiscal_annuel": round(net_fiscal_mensuel, 2),
            "source": "fiche_decembre_mensuel_uniquement",
            "fiabilite": "faible",
        }

    return {
        "net_fiscal_annuel": 0.0,
        "source": "non_trouve",
        "fiabilite": "nulle",
    }


def extraire_donnees_annuelles(resultats: list[dict]) -> dict:
    """
    Extrait les données fiscales annuelles depuis les fiches analysées.

    Règle absolue :
    - Le revenu net fiscal annuel est lu UNIQUEMENT sur la fiche de DÉCEMBRE.
    - On prend la valeur CUMUL (colonne « DEPUIS janvier »), pas la valeur mensuelle.
    - Si aucune fiche de décembre n'est disponible → decembre_manquant = True,
      revenu_fiscal_brut = 0, pas d'invention.

    Args:
        resultats: list des dicts retournés par analyser_fiche().

    Returns:
        dict avec revenu_fiscal_brut, source_cumul, mois_source,
              decembre_manquant, une_seule_valeur,
              tickets_resto_salarie, mutuelle_salarie,
              primes_total, mois_disponibles, annee_detectee.
    """
    _empty = {
        "revenu_fiscal_brut": 0.0,
        "source_cumul": "aucune fiche",
        "mois_source": None,
        "decembre_manquant": True,
        "une_seule_valeur": False,
        "tickets_resto_salarie": 0.0,
        "mutuelle_salarie": 0.0,
        "primes_total": 0.0,
        "mois_disponibles": 0,
        "annee_detectee": None,
    }
    if not resultats:
        return _empty

    # ------------------------------------------------------------------ #
    # 1. Chercher SPÉCIFIQUEMENT une fiche de décembre (mois == 12)       #
    # ------------------------------------------------------------------ #
    def _sort_key(r):
        fichier = r.get("detail", {}).get("fichier", "")
        return _parse_yyyymm(fichier)

    resultats_tries = sorted(resultats, key=_sort_key, reverse=True)

    fiche_decembre: dict | None = None
    annee_decembre: int | None = None

    for r in resultats_tries:
        fichier = r.get("detail", {}).get("fichier", "")
        yyyymm = _parse_yyyymm(fichier)
        if yyyymm % 100 == 12:          # mois == décembre
            fiche_decembre = r
            annee_decembre = yyyymm // 100
            break

    decembre_manquant = fiche_decembre is None
    une_seule_valeur = False

    if decembre_manquant:
        # Aucune fiche de décembre → ne pas inventer le revenu
        net_fiscal_annuel = 0.0
        source_cumul = "fiche décembre introuvable — revenu non calculé"
        mois_source = None
    else:
        # Extraire depuis la fiche de décembre uniquement
        extraction = extraire_net_fiscal_annuel(fiche_decembre)
        net_fiscal_annuel = extraction["net_fiscal_annuel"]
        fiabilite = extraction["fiabilite"]

        if fiabilite == "élevée":
            source_cumul = f"cumul annuel — fiche décembre {annee_decembre}"
            une_seule_valeur = False
        elif fiabilite == "faible":
            source_cumul = f"valeur mensuelle uniquement (cumul introuvable) — fiche décembre {annee_decembre}"
            une_seule_valeur = True
        else:
            source_cumul = f"NET FISCAL introuvable dans la fiche décembre {annee_decembre}"
            une_seule_valeur = False

        mois_source = 12

    # ------------------------------------------------------------------ #
    # 2. Cumul tickets restaurant + mutuelle sur TOUTES les fiches         #
    # ------------------------------------------------------------------ #
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

        # Chercher dans cotisations ET retenues
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

    annee = annee_decembre or (max(annees) if annees else None)

    return {
        "revenu_fiscal_brut": round(net_fiscal_annuel, 2),
        "source_cumul": source_cumul,
        "mois_source": mois_source,
        "decembre_manquant": decembre_manquant,
        "une_seule_valeur": une_seule_valeur,
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
    # NOTE : les tickets restaurant (RET. TITRE REPAS) et la mutuelle obligatoire
    # (COMPLEMENTAIRE SANTE OBLIGATOIRE) NE sont PAS déductibles en frais réels.
    frais_repas = _safe_float(inputs.get("frais_repas", 0))

    # --- 4. Autres frais professionnels ---
    autres_frais = _safe_float(inputs.get("autres_frais", 0))

    # --- 5. Cotisation syndicale annuelle ---
    cotisation_syndicale = _safe_float(inputs.get("cotisation_syndicale", 0))

    # --- 6. Foyer fiscal ---
    situation   = inputs.get("situation_familiale", "celibataire")
    nb_enfants  = int(inputs.get("nb_enfants", 0))
    foyer       = calcul_parts_fiscales(situation, nb_enfants)

    # --- 6d. Réduction scolarité ---
    red_scolarite = calcul_reduction_scolarite(
        enfants_college   = int(inputs.get("enfants_college", 0)),
        enfants_lycee     = int(inputs.get("enfants_lycee", 0)),
        enfants_superieur = int(inputs.get("enfants_superieur", 0)),
    )

    # --- 6e. Crédit garde d'enfants ---
    cred_garde = calcul_credit_garde(
        frais_creche         = _safe_float(inputs.get("frais_creche", 0)),
        frais_assmat         = _safe_float(inputs.get("frais_assmat", 0)),
        frais_garde_domicile = _safe_float(inputs.get("frais_garde_domicile", 0)),
    )

    # --- 7. Total frais réels ---
    total_frais_reels = (
        frais_km_montant
        + frais_repas
        + autres_frais
        + cotisation_syndicale
    )

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
        # Frais réels (tickets restaurant et mutuelle exclus : non déductibles)
        "frais_reels": {
            "km": km_detail,
            "frais_km": frais_km_montant,
            "frais_repas": frais_repas,
            "cotisation_syndicale": round(cotisation_syndicale, 2),
            "autres_frais": autres_frais,
            "total": round(total_frais_reels, 2),
        },
        "revenu_apres_frais_reels": revenu_apres_frais_reels,
        # Comparaison
        "option_optimale": option_optimale,
        "gain_fiscal": round(gain_fiscal, 2),
        "difference_assiette": difference,
        "explication": explication,
        # Foyer fiscal
        "foyer": foyer,
        # Avantages fiscaux complémentaires (hors frais réels / abattement)
        "reduction_scolarite": red_scolarite,
        "credit_garde": cred_garde,
        "total_avantages_complementaires": round(
            red_scolarite["total_reduction"] + cred_garde["credit_total"], 2
        ),
    }
