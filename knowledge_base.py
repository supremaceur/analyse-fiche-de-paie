"""
Base de connaissances sur les lignes de fiches de paie françaises.
Mise à jour : mars 2026 — Valeurs conformes à la réglementation en vigueur au 1er janvier 2026.

Références :
- SMIC 2026 : 12,02 €/h brut — 1 823,03 €/mois (151,67h)
- Plafond SS (PMSS) : 4 005 €/mois — PASS : 48 060 €/an
- RGDU (ex-Fillon) : seuil 3 SMIC, coefficient max 0,4021 (≥50 sal.)
- Assurance chômage patronale : 4,05 % (depuis mai 2025)
- Vieillesse déplafonnée patronale : 2,11 % (+0,09 pt vs 2025)
- Tickets restaurant : exonération employeur max 7,32 €/titre
- HS exonérées : plafond 7 500 € net imposable/an
"""

# Dictionnaire des libellés connus avec leurs explications
PAYSLIP_KNOWLEDGE = {
    # === RÉMUNÉRATION ===
    "SALAIRE DE BASE": {
        "type": "salaire",
        "categorie": "remuneration",
        "explication": (
            "C'est votre salaire mensuel fixe, calculé à partir de votre taux horaire "
            "multiplié par le nombre d'heures du mois (151,67h pour un temps plein à 35h/semaine). "
            "En 2026, le SMIC horaire brut est de 12,02 €, soit un salaire de base minimum "
            "de 1 823,03 € brut/mois pour un temps plein."
        ),
        "a_quoi_ca_sert": "C'est la base de votre rémunération, sur laquelle sont calculées la plupart des cotisations.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "SAL MIN CONV": {
        "type": "salaire",
        "categorie": "remuneration",
        "explication": (
            "Salaire minimum conventionnel : c'est le minimum que votre convention collective "
            "(Prestataires de services du secteur tertiaire) impose pour votre poste et coefficient. "
            "Votre salaire de base doit être au moins égal à ce montant. "
            "Si le SMIC (1 823,03 € brut/mois en 2026) est supérieur au minimum conventionnel, "
            "c'est le SMIC qui s'applique."
        ),
        "a_quoi_ca_sert": "Référence pour vérifier que votre salaire respecte les minimums de la convention collective.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "COMPL SAL IND": {
        "type": "salaire",
        "categorie": "remuneration",
        "explication": (
            "Complément de salaire individuel : c'est la différence entre votre salaire de base "
            "et le minimum conventionnel. Cela montre que votre employeur vous paie au-dessus du minimum."
        ),
        "a_quoi_ca_sert": "Garantir que votre rémunération totale atteint au moins le niveau de base prévu.",
        "qui_paie": "employeur",
        "obligatoire": False,
    },
    "HRES AU TAUX NORMAL": {
        "type": "salaire",
        "categorie": "remuneration",
        "explication": (
            "Heures travaillées au taux horaire normal. Le nombre d'heures est multiplié "
            "par votre taux horaire de base. Pour un temps plein, la durée légale est de "
            "151,67h/mois (35h × 52 semaines / 12 mois)."
        ),
        "a_quoi_ca_sert": "Rémunération des heures de travail effectuées dans le mois.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "HRES SUPPL. A 125%": {
        "type": "salaire",
        "categorie": "remuneration",
        "explication": (
            "Heures supplémentaires majorées à 125 % : ce sont les 8 premières heures travaillées "
            "au-delà de 35h/semaine (de la 36e à la 43e heure). Elles sont payées 25 % de plus "
            "que le taux normal. En 2026, ces heures sont exonérées de cotisations salariales "
            "et d'impôt sur le revenu dans la limite de 7 500 € net imposable par an."
        ),
        "a_quoi_ca_sert": "Rémunérer le travail au-delà de la durée légale avec une majoration de 25 %.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "BONUS MENSUEL": {
        "type": "prime",
        "categorie": "primes",
        "explication": (
            "Prime de performance mensuelle versée en fonction de critères définis "
            "(qualité, productivité, objectifs atteints, etc.). Cette prime est soumise "
            "à cotisations sociales et à l'impôt sur le revenu."
        ),
        "a_quoi_ca_sert": "Récompenser la performance individuelle ou collective du mois.",
        "qui_paie": "employeur",
        "obligatoire": False,
    },

    # === ABSENCES ET CONGÉS ===
    "ABS CONGES PAYES": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": (
            "Déduction pour jours de congés payés pris. Le montant est retiré du salaire de base "
            "car ces jours ne sont pas 'travaillés' au sens strict. En 2026, tout salarié acquiert "
            "2,5 jours ouvrables de congés par mois de travail effectif, soit 30 jours ouvrables (5 semaines) par an."
        ),
        "a_quoi_ca_sert": "Retirer les jours de congés du calcul du salaire de base (ils sont compensés par l'indemnité de congés payés).",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "IND CONGES PAYES": {
        "type": "indemnite",
        "categorie": "remuneration",
        "explication": (
            "Indemnité de congés payés : c'est le montant versé pour compenser les jours de congés. "
            "Calculée selon la méthode la plus avantageuse pour le salarié : soit le maintien de salaire "
            "(salaire normal), soit la règle du 1/10e (10 % du brut total de la période de référence)."
        ),
        "a_quoi_ca_sert": "Vous rémunérer pendant vos congés payés.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "ABS. NON AUTORISEE": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": (
            "Absence non autorisée : retenue sur salaire pour une absence qui n'a pas été "
            "justifiée ou autorisée par l'employeur. La retenue est proportionnelle au temps d'absence."
        ),
        "a_quoi_ca_sert": "Déduire du salaire les heures/jours d'absence non justifiée.",
        "qui_paie": "salarié (retenue)",
        "obligatoire": True,
    },
    "ABS. AUTOR.NON PAYEE": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": (
            "Absence autorisée non payée : l'absence a été validée par l'employeur "
            "mais elle n'est pas rémunérée (ex : convenance personnelle, congé sans solde)."
        ),
        "a_quoi_ca_sert": "Déduire du salaire une absence accordée mais sans maintien de rémunération.",
        "qui_paie": "salarié (retenue)",
        "obligatoire": True,
    },
    "ABS. JOUR FERIE": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": (
            "Déduction liée à un jour férié chômé. Le montant est déduit puis compensé "
            "par l'indemnité correspondante (IND. JOUR FERIE). En 2026, la France compte "
            "11 jours fériés légaux."
        ),
        "a_quoi_ca_sert": "Traitement comptable des jours fériés (débit/crédit).",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "IND. JOUR FERIE": {
        "type": "indemnite",
        "categorie": "remuneration",
        "explication": "Indemnité de jour férié : compensation versée pour le jour férié chômé.",
        "a_quoi_ca_sert": "Maintenir votre salaire les jours fériés non travaillés.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "ABSENCE DIVERS": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": (
            "Déduction pour une absence de nature diverse (délégation, formation, événement familial, etc.). "
            "Généralement compensée par une indemnité correspondante (INDEMNITE DIVERS)."
        ),
        "a_quoi_ca_sert": "Retirer comptablement les heures d'absence du salaire de base.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "INDEMNITE DIVERS": {
        "type": "indemnite",
        "categorie": "remuneration",
        "explication": "Indemnité compensant une absence diverse. Maintient la rémunération pendant l'absence.",
        "a_quoi_ca_sert": "Compenser la retenue liée à l'absence diverse.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "ABSENCE H.MALADIE": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": (
            "Retenue pour absence maladie. Pendant l'arrêt, vous percevez des indemnités journalières "
            "de la Sécurité sociale (IJSS) après un délai de carence de 3 jours, égales à environ 50 % "
            "du salaire journalier de base (plafond 1,8 × SMIC en 2026). Votre convention collective "
            "peut prévoir un complément employeur."
        ),
        "a_quoi_ca_sert": "Déduire les jours non travaillés pour cause de maladie.",
        "qui_paie": "salarié (retenue) / CPAM (indemnités journalières)",
        "obligatoire": True,
    },
    "REGUL CP.ANTICIPES": {
        "type": "regularisation",
        "categorie": "remuneration",
        "explication": (
            "Régularisation de congés payés anticipés : ajustement lié à des congés pris "
            "par anticipation avant leur acquisition complète."
        ),
        "a_quoi_ca_sert": "Corriger un écart entre congés pris et congés acquis.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },

    # === DÉLÉGATION / CSE ===
    "ABS. DELEGATION CSE": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": (
            "Heures de délégation CSE (Comité Social et Économique) : temps passé par un élu "
            "du personnel pour ses activités de représentation. Déduit du salaire puis compensé "
            "par l'indemnité correspondante. Le crédit d'heures dépend de l'effectif de l'entreprise "
            "(ex : 24h/mois pour les entreprises de 500 à 1 499 salariés)."
        ),
        "a_quoi_ca_sert": "Traitement comptable des heures de délégation CSE.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "IND.DELEGATION CSE": {
        "type": "indemnite",
        "categorie": "remuneration",
        "explication": (
            "Indemnité de délégation CSE : compensation des heures de délégation. "
            "Le salarié élu est payé normalement pendant ses heures de représentation du personnel."
        ),
        "a_quoi_ca_sert": "Maintenir la rémunération pendant les activités de représentation du personnel.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "ABS. DELEGATION": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": "Heures de délégation pour activités de représentation du personnel (hors CSE spécifiquement).",
        "a_quoi_ca_sert": "Traitement comptable des heures de délégation.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "IND. DELEGATION": {
        "type": "indemnite",
        "categorie": "remuneration",
        "explication": "Indemnité compensant les heures de délégation.",
        "a_quoi_ca_sert": "Maintenir le salaire pendant les activités de représentation.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "ABS ECO ET SYNDICAL": {
        "type": "absence",
        "categorie": "remuneration",
        "explication": (
            "Absence pour activité économique et syndicale (réunions syndicales, négociations, "
            "formations économiques, etc.). Temps rémunéré comme du travail effectif."
        ),
        "a_quoi_ca_sert": "Traitement comptable des heures consacrées aux activités syndicales.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "IND ECO ET SYNDICAL": {
        "type": "indemnite",
        "categorie": "remuneration",
        "explication": "Indemnité compensant les heures d'absence pour activité économique et syndicale.",
        "a_quoi_ca_sert": "Maintenir le salaire pendant les activités syndicales.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },

    # === PRIMES SPÉCIALES ===
    "PR.PART.VALEUR NS/NI": {
        "type": "prime",
        "categorie": "primes",
        "explication": (
            "Prime de Partage de la Valeur (PPV, ex-prime Macron) : prime exceptionnelle "
            "non soumise à cotisations sociales (NS) et non imposable (NI) sous conditions. "
            "En 2026, le régime d'exonération sociale et fiscale est maintenu pour les salariés "
            "dont la rémunération est inférieure à 3 SMIC annuel (65 629 € brut/an). "
            "Plafond : 3 000 € (ou 6 000 € si accord d'intéressement ou de participation)."
        ),
        "a_quoi_ca_sert": "Redistribuer une partie de la valeur créée par l'entreprise aux salariés, avec un régime fiscal avantageux.",
        "qui_paie": "employeur",
        "obligatoire": False,
    },

    # === COTISATIONS SANTÉ ===
    "SECURITE SOCIALE - MALADIE MATERNITE": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation patronale pour l'assurance maladie-maternité. Finance les remboursements de soins médicaux, "
            "les indemnités maternité/paternité et les arrêts maladie. "
            "En 2026 : taux patronal de 7,00 % (taux réduit pour les salaires < 2,5 SMIC, soit < 4 558 € brut/mois) "
            "ou 13,00 % (taux plein au-delà). La part salariale est de 0 % depuis 2018."
        ),
        "a_quoi_ca_sert": "Financer la Sécurité sociale : remboursement des soins, arrêts maladie, congés maternité/paternité.",
        "qui_paie": "employeur uniquement (depuis 2018, la part salariale a été supprimée et compensée par la hausse de CSG)",
        "obligatoire": True,
    },
    "PREVOYANCE INCAPACITE INVALIDITE DECES TA": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation de prévoyance sur la Tranche A (jusqu'au plafond SS : 4 005 €/mois en 2026). "
            "Couvre les risques d'incapacité de travail, d'invalidité et de décès au-delà de ce que "
            "couvre la Sécurité sociale. La part employeur doit être d'au moins 50 % de la cotisation."
        ),
        "a_quoi_ca_sert": "Garantir un revenu complémentaire en cas d'arrêt de travail prolongé, d'invalidité, ou verser un capital aux ayants droit en cas de décès.",
        "qui_paie": "les deux (salarié + employeur, minimum 50 % employeur)",
        "obligatoire": True,
    },
    "COMPLEMENTAIRE INCAPACITE INVALIDITE DECES TA": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation complémentaire de prévoyance (incapacité, invalidité, décès) sur Tranche A "
            "(jusqu'à 4 005 €/mois en 2026). Même rôle que la prévoyance de base, "
            "avec une couverture complémentaire supplémentaire."
        ),
        "a_quoi_ca_sert": "Assurer un complément de revenus en cas d'incapacité, invalidité ou décès.",
        "qui_paie": "les deux (salarié + employeur)",
        "obligatoire": True,
    },
    "COMPLEMENTAIRE SANTE OBLIGATOIRE": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation pour la mutuelle d'entreprise obligatoire. Depuis 2016, tout employeur "
            "doit proposer une complémentaire santé à ses salariés et en financer au moins 50 %. "
            "En 2026, le plafond d'exonération sociale de la part employeur est de 6 % du PASS "
            "(2 883,60 €) + 1,5 % du brut annuel, plafonné à 12 % du PASS (5 767,20 €)."
        ),
        "a_quoi_ca_sert": "Compléter les remboursements de la Sécurité sociale pour vos frais de santé (médecin, dentiste, optique, hospitalisation...).",
        "qui_paie": "les deux (au moins 50 % employeur, le reste salarié)",
        "obligatoire": True,
    },
    "COMPLEMENTAIRE SANTE": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation pour la mutuelle d'entreprise (complémentaire santé). Complète les remboursements "
            "de la Sécurité sociale. L'employeur prend en charge au minimum 50 % du coût."
        ),
        "a_quoi_ca_sert": "Compléter les remboursements de soins au-delà de la part Sécurité sociale.",
        "qui_paie": "les deux (salarié + employeur)",
        "obligatoire": True,
    },
    "ACCIDENTS DU TRAVAIL-MALADIES PROFESSIONNELLES": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation patronale AT/MP (Accidents du Travail / Maladies Professionnelles). "
            "Le taux varie selon le secteur d'activité, la taille de l'entreprise et sa sinistralité. "
            "Il est fixé chaque année par la CARSAT. Cette cotisation est intégralement à la charge "
            "de l'employeur et calculée sur la totalité du salaire brut."
        ),
        "a_quoi_ca_sert": "Financer l'indemnisation des salariés victimes d'accidents du travail ou de maladies professionnelles.",
        "qui_paie": "employeur uniquement",
        "obligatoire": True,
    },

    # === COTISATIONS RETRAITE ===
    "SECURITE SOCIALE PLAFONNEE": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation retraite de base plafonnée : calculée sur la partie du salaire jusqu'au "
            "plafond de la Sécurité sociale (PMSS : 4 005 €/mois en 2026, soit 48 060 €/an). "
            "Elle finance votre retraite de base du régime général. "
            "Taux 2026 : 6,90 % salarié + 8,55 % employeur = 15,45 % au total."
        ),
        "a_quoi_ca_sert": "Constituer vos droits à la retraite de base versée par la Sécurité sociale (trimestres et montant).",
        "qui_paie": "les deux (salarié 6,90 % + employeur 8,55 %)",
        "obligatoire": True,
    },
    "SECURITE SOCIALE DEPLAFONNEE": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation retraite de base déplafonnée : calculée sur la totalité du salaire brut "
            "(sans plafond). Complète la cotisation plafonnée pour le financement du régime général. "
            "Taux 2026 : 0,40 % salarié + 2,11 % employeur = 2,51 % au total "
            "(hausse de +0,09 point côté employeur par rapport à 2025)."
        ),
        "a_quoi_ca_sert": "Contribuer au financement du régime de retraite de base sur l'ensemble du salaire.",
        "qui_paie": "les deux (salarié 0,40 % + employeur 2,11 %)",
        "obligatoire": True,
    },
    "RETRAITE COMPLEMENTAIRE ET CEG TRANCHE 1": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation retraite complémentaire AGIRC-ARRCO + Contribution d'Équilibre Général (CEG) "
            "sur la Tranche 1 (jusqu'au plafond SS : 4 005 €/mois en 2026). "
            "Taux 2026 — Retraite T1 : 3,15 % salarié + 4,72 % employeur. "
            "CEG T1 : 0,86 % salarié + 1,29 % employeur. "
            "Total T1 : 4,01 % salarié + 6,01 % employeur = 10,02 %. "
            "Chaque cotisation génère des points AGIRC-ARRCO pour votre retraite complémentaire."
        ),
        "a_quoi_ca_sert": "Constituer vos droits à la retraite complémentaire (points AGIRC-ARRCO), en plus de la retraite de base.",
        "qui_paie": "les deux (salarié 4,01 % + employeur 6,01 %)",
        "obligatoire": True,
    },
    "COMPLEMENTAIRE TRANCHE 1": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation retraite complémentaire AGIRC-ARRCO Tranche 1 (jusqu'au plafond SS : 4 005 €/mois en 2026). "
            "Taux 2026 : 3,15 % salarié + 4,72 % employeur = 7,87 %. "
            "Finance votre retraite complémentaire obligatoire."
        ),
        "a_quoi_ca_sert": "Constituer vos droits à la retraite complémentaire obligatoire.",
        "qui_paie": "les deux (salarié 3,15 % + employeur 4,72 %)",
        "obligatoire": True,
    },

    # === FAMILLE / CHÔMAGE ===
    "FAMILLE": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation patronale d'allocations familiales. Finance la CAF (allocations familiales, "
            "APL, prime d'activité, RSA, etc.). "
            "Taux 2026 : 3,45 % (taux réduit, pour les salaires < 3,5 SMIC soit < 6 381 € brut/mois) "
            "ou 5,25 % (taux plein au-delà). Calculée sur la totalité du salaire brut."
        ),
        "a_quoi_ca_sert": "Financer les prestations familiales versées par la CAF à toutes les familles.",
        "qui_paie": "employeur uniquement",
        "obligatoire": True,
    },
    "ASSURANCE CHOMAGE": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisation patronale d'assurance chômage. Depuis octobre 2018, la part salariale a été "
            "supprimée (compensée par la hausse de la CSG). Finance les allocations chômage (ARE) "
            "versées par France Travail (ex-Pôle Emploi). "
            "Taux 2026 : 4,05 % employeur (taux de droit commun depuis mai 2025). "
            "Un dispositif de bonus-malus (de 2,95 % à 5,00 %) s'applique dans certains secteurs "
            "en fonction du taux de séparation de l'entreprise. "
            "Assiette : jusqu'à 4 fois le plafond SS (16 020 €/mois en 2026)."
        ),
        "a_quoi_ca_sert": "Garantir un revenu de remplacement en cas de perte involontaire d'emploi.",
        "qui_paie": "employeur uniquement (depuis oct. 2018)",
        "obligatoire": True,
    },

    # === CSG / CRDS ===
    "CSG DEDUCTIBLE DE L'IMPOT SUR LE REVENU": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Contribution Sociale Généralisée (part déductible) : prélevée au taux de 6,80 % "
            "sur 98,25 % du salaire brut (abattement de 1,75 % pour frais professionnels, "
            "dans la limite de 4 PASS soit 192 240 €/an en 2026). "
            "Cette part est déductible de votre revenu imposable, ce qui réduit votre impôt sur le revenu."
        ),
        "a_quoi_ca_sert": "Financer la Sécurité sociale (maladie, famille, vieillesse, handicap). La part déductible allège votre impôt.",
        "qui_paie": "salarié uniquement",
        "obligatoire": True,
    },
    "CSG/CRDS NON DEDUCTIBLES DE L'IMPOT SUR LE REVENU": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "CSG non déductible (2,40 %) + CRDS (0,50 %) = 2,90 % sur 98,25 % du brut. "
            "Ces contributions ne réduisent PAS votre revenu imposable : elles s'ajoutent à votre impôt. "
            "La CRDS finance le remboursement de la dette sociale (CADES). "
            "Assiette 2026 : 98,25 % du brut (abattement 1,75 %) dans la limite de 4 PASS (192 240 €/an)."
        ),
        "a_quoi_ca_sert": "Financer la Sécurité sociale (CSG) et rembourser la dette sociale (CRDS). Non déductibles = pas d'avantage fiscal.",
        "qui_paie": "salarié uniquement",
        "obligatoire": True,
    },
    "CSG/CRDS SUR LES REVENUS NON IMPOSABLES": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "CSG/CRDS calculée sur les revenus exonérés d'impôt (comme les heures supplémentaires exonérées). "
            "Même si ces revenus ne sont pas imposables (exonération jusqu'à 7 500 €/an en 2026), "
            "ils restent soumis à la CSG (9,20 %) et à la CRDS (0,50 %) sur 98,25 % de leur montant."
        ),
        "a_quoi_ca_sert": "Appliquer la CSG/CRDS même sur les revenus bénéficiant d'une exonération fiscale.",
        "qui_paie": "salarié uniquement",
        "obligatoire": True,
    },

    # === COTISATIONS DIVERSES ===
    "COTISATIONS STATUTAIRES": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Cotisations prévues par la convention collective ou les accords d'entreprise "
            "(ex : contribution au dialogue social 0,016 %, formation spécifique, etc.)."
        ),
        "a_quoi_ca_sert": "Financer des dispositifs spécifiques à votre branche professionnelle.",
        "qui_paie": "variable selon la cotisation",
        "obligatoire": True,
    },
    "AUTRES CHARGES DUES PAR L'EMPLOYEUR": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Ensemble de contributions patronales diverses. En 2026 : "
            "formation professionnelle (0,55 % ou 1 % selon l'effectif), "
            "taxe d'apprentissage (0,68 %), "
            "FNAL (0,10 % plafonné si < 50 salariés, ou 0,50 % déplafonné si ≥ 50 salariés), "
            "contribution solidarité autonomie (0,30 %), "
            "contribution au dialogue social (0,016 %), "
            "AGS — garantie des salaires (0,25 % sur max 4 PMSS)."
        ),
        "a_quoi_ca_sert": "Financer la formation professionnelle, l'apprentissage, le logement, l'autonomie et la garantie des salaires.",
        "qui_paie": "employeur uniquement",
        "obligatoire": True,
    },
    "AUTRES CONTRIBUTIONS DUES PAR L'EMPLOYEUR": {
        "type": "cotisation",
        "categorie": "cotisations",
        "explication": (
            "Contributions patronales diverses regroupées : formation professionnelle, "
            "taxe d'apprentissage, FNAL, CSA, contribution au dialogue social, AGS. "
            "Voir 'Autres charges dues par l'employeur' pour le détail des taux 2026."
        ),
        "a_quoi_ca_sert": "Financer la formation, l'apprentissage, le logement et la garantie des salaires.",
        "qui_paie": "employeur uniquement",
        "obligatoire": True,
    },

    # === EXONÉRATIONS ===
    "EXONERATIONS ET ALLEGEMENTS DE COTISATIONS": {
        "type": "exoneration",
        "categorie": "cotisations",
        "explication": (
            "Réductions de cotisations patronales accordées par l'État. "
            "En 2026, la RGDU (Réduction Générale Dégressive Unique) remplace l'ancienne réduction Fillon "
            "et les réductions séparées sur l'assurance maladie et les allocations familiales. "
            "Elle s'applique jusqu'à 3 SMIC (5 469 € brut/mois), avec un coefficient maximum de 0,4021 "
            "(entreprises ≥ 50 salariés) ou 0,3981 (< 50 salariés). "
            "La réduction est maximale au niveau du SMIC et dégressive selon une formule avec exposant 1,75."
        ),
        "a_quoi_ca_sert": "Réduire le coût du travail pour l'employeur, notamment pour les salaires proches du SMIC.",
        "qui_paie": "réduction pour l'employeur (financée par l'État)",
        "obligatoire": True,
    },
    "EXONERATIONS DE COTISATIONS SALARIALES": {
        "type": "exoneration",
        "categorie": "cotisations",
        "explication": (
            "Exonération de cotisations salariales sur les heures supplémentaires. "
            "En 2026, les heures supplémentaires sont exonérées de cotisations salariales "
            "(assurance vieillesse et retraite complémentaire) et d'impôt sur le revenu "
            "dans la limite de 7 500 € net imposable par an."
        ),
        "a_quoi_ca_sert": "Augmenter le net perçu par le salarié sur les heures supplémentaires.",
        "qui_paie": "avantage pour le salarié",
        "obligatoire": True,
    },
    "EXONERATIONS DE COTISATIONS EMPLOYEUR": {
        "type": "exoneration",
        "categorie": "cotisations",
        "explication": (
            "Allègements de cotisations patronales. En 2026, la RGDU (ex-Fillon) permet une réduction "
            "dégressive des cotisations employeur pour les salaires jusqu'à 3 SMIC. "
            "Coefficient max : 0,4021 (≥ 50 salariés). "
            "Également : déduction forfaitaire patronale sur les heures supplémentaires pour les entreprises "
            "de 20 à 249 salariés (0,50 €/heure) et < 20 salariés (1,50 €/heure)."
        ),
        "a_quoi_ca_sert": "Réduire le coût du travail pour l'employeur.",
        "qui_paie": "réduction pour l'employeur",
        "obligatoire": True,
    },

    # === INDEMNITÉS NON SOUMISES ===
    "TRANSPORT PROVINCE": {
        "type": "indemnite",
        "categorie": "indemnites_non_soumises",
        "explication": (
            "Participation de l'employeur aux frais de transport en province. "
            "L'employeur est obligé de prendre en charge 50 % de l'abonnement aux transports en commun. "
            "Cette prise en charge est exonérée de cotisations sociales et d'impôt sur le revenu. "
            "En 2026, le Forfait Mobilités Durables (vélo, covoiturage, etc.) peut aller jusqu'à "
            "600 €/an exonérés (ou 900 €/an si cumulé avec les transports en commun)."
        ),
        "a_quoi_ca_sert": "Participer à vos frais de déplacement domicile-travail.",
        "qui_paie": "employeur",
        "obligatoire": True,
    },
    "IND.FORF.TELETRAV.NS": {
        "type": "indemnite",
        "categorie": "indemnites_non_soumises",
        "explication": (
            "Indemnité forfaitaire de télétravail non soumise à cotisations (NS). "
            "Compense les frais liés au travail à domicile (électricité, internet, chauffage, etc.). "
            "En 2026, l'URSSAF admet une exonération forfaitaire de 2,70 €/jour de télétravail, "
            "dans la limite de 59,40 €/mois (ou un forfait mensuel selon l'accord d'entreprise)."
        ),
        "a_quoi_ca_sert": "Rembourser vos frais professionnels liés au télétravail.",
        "qui_paie": "employeur",
        "obligatoire": False,
    },
    "IND.TELETRVAIL NS NI": {
        "type": "indemnite",
        "categorie": "indemnites_non_soumises",
        "explication": (
            "Indemnité de télétravail non soumise à cotisations (NS) et non imposable (NI). "
            "Compense les frais du travail à domicile. Mêmes plafonds URSSAF 2026 : "
            "2,70 €/jour, max 59,40 €/mois. En franchise totale de cotisations et d'impôt."
        ),
        "a_quoi_ca_sert": "Rembourser vos frais professionnels de télétravail, en franchise de cotisations et d'impôt.",
        "qui_paie": "employeur",
        "obligatoire": False,
    },

    # === RETENUES ===
    "RET.TITRE REPAS": {
        "type": "retenue",
        "categorie": "retenues",
        "explication": (
            "Retenue pour titres-restaurant : c'est votre part salariale du coût des tickets restaurant. "
            "L'employeur finance entre 50 % et 60 % de la valeur faciale. "
            "En 2026, la part employeur est exonérée de cotisations jusqu'à 7,32 € par titre. "
            "Exemple : pour un titre à 12,20 €, l'employeur peut payer jusqu'à 7,32 € (60 %) "
            "et le salarié paie 4,88 € (40 %)."
        ),
        "a_quoi_ca_sert": "Financer votre part des titres-restaurant.",
        "qui_paie": "les deux (salarié 40-50 % + employeur 50-60 %)",
        "obligatoire": False,
    },
    "FR.SANTE IMP.": {
        "type": "retenue",
        "categorie": "retenues",
        "explication": (
            "Part patronale de la mutuelle santé réintégrée dans le revenu imposable. "
            "Ce n'est pas une retenue réelle sur votre salaire, mais un ajout à votre base imposable : "
            "la contribution de votre employeur à la mutuelle est considérée comme un avantage en nature "
            "fiscalement imposable depuis 2013."
        ),
        "a_quoi_ca_sert": "Ajouter à votre revenu imposable la contribution employeur à la mutuelle (avantage en nature fiscal).",
        "qui_paie": "impact fiscal pour le salarié",
        "obligatoire": True,
    },
    "IMPOT SUR LE REVENU PRELEVE": {
        "type": "impot",
        "categorie": "retenues",
        "explication": (
            "Prélèvement à la source (PAS) de l'impôt sur le revenu. Prélevé chaque mois par "
            "l'employeur sur votre salaire net imposable. "
            "Le taux appliqué est soit personnalisé (transmis par la DGFiP via la DSN, "
            "basé sur votre dernière déclaration), soit le taux neutre (grille par défaut). "
            "En 2026 : nouveau barème revalorisé de +0,9 % à partir du 1er mai 2026. "
            "Pour les CDD ≤ 2 mois au taux neutre, un abattement de 748 € s'applique."
        ),
        "a_quoi_ca_sert": "Payer votre impôt sur le revenu directement chaque mois, au lieu d'un paiement annuel.",
        "qui_paie": "salarié (prélevé par l'employeur pour le compte de l'État)",
        "obligatoire": True,
    },
    "OPPOSITION 2": {
        "type": "retenue",
        "categorie": "retenues",
        "explication": (
            "Saisie sur salaire (opposition) : retenue ordonnée par un tribunal ou un créancier. "
            "Une partie de votre salaire est prélevée pour rembourser une dette. "
            "Le montant saisissable est encadré par un barème progressif revalorisé chaque année "
            "(le salarié conserve au minimum le montant du RSA, soit 635,71 €/mois pour une personne seule en 2026)."
        ),
        "a_quoi_ca_sert": "Rembourser une dette conformément à une décision de justice ou une procédure de saisie.",
        "qui_paie": "salarié (retenue obligatoire)",
        "obligatoire": True,
    },

    # === HEURES SUPPLÉMENTAIRES EXONÉRÉES ===
    "HS EXO SOC.": {
        "type": "information",
        "categorie": "informations",
        "explication": (
            "Montant des heures supplémentaires exonérées de cotisations sociales salariales. "
            "En 2026, les HS sont exonérées de cotisations salariales (vieillesse de base + retraite "
            "complémentaire) et d'impôt sur le revenu dans la limite de 7 500 € net imposable par an. "
            "Elles restent soumises à la CSG/CRDS (9,70 % sur 98,25 % du montant)."
        ),
        "a_quoi_ca_sert": "Information sur le montant d'heures sup bénéficiant d'une exonération sociale (augmente votre net à payer).",
        "qui_paie": "avantage pour le salarié",
        "obligatoire": True,
    },
    "HS EXO": {
        "type": "information",
        "categorie": "informations",
        "explication": (
            "Montant des heures supplémentaires exonérées d'impôt sur le revenu. "
            "En 2026, les heures supplémentaires et complémentaires sont exonérées d'IR "
            "dans la limite de 7 500 € net imposable par an. Ce montant n'est pas inclus "
            "dans votre revenu imposable pour le calcul de l'impôt."
        ),
        "a_quoi_ca_sert": "Information sur les HS exonérées d'impôt (non incluses dans votre net imposable).",
        "qui_paie": "avantage pour le salarié",
        "obligatoire": True,
    },
}

# Patterns pour reconnaître des libellés similaires
LABEL_PATTERNS = {
    r"SALAIRE DE BASE": "SALAIRE DE BASE",
    r"SAL MIN CONV": "SAL MIN CONV",
    r"COMPL SAL IND": "COMPL SAL IND",
    r"HRES? (AU )?TAUX NORMAL": "HRES AU TAUX NORMAL",
    r"HRES? SUPPL.*125%": "HRES SUPPL. A 125%",
    r"BONUS MENSUEL": "BONUS MENSUEL",
    r"ABS[\. ]*CONGES PAYES": "ABS CONGES PAYES",
    r"IND[\. ]*CONGES PAYES": "IND CONGES PAYES",
    r"ABS[\. ]*NON AUTORISEE": "ABS. NON AUTORISEE",
    r"ABS[\. ]*AUTOR[\. ]*NON PAYEE": "ABS. AUTOR.NON PAYEE",
    r"ABS[\. ]*JOUR FERIE": "ABS. JOUR FERIE",
    r"IND[\. ]*JOUR FERIE": "IND. JOUR FERIE",
    r"ABSENCE DIVERS": "ABSENCE DIVERS",
    r"INDEMNITE DIVERS": "INDEMNITE DIVERS",
    r"ABSENCE H[\. ]*MALADIE": "ABSENCE H.MALADIE",
    r"REGUL CP": "REGUL CP.ANTICIPES",
    r"ABS[\. ]*DELEGATION CSE": "ABS. DELEGATION CSE",
    r"IND[\. ]*DELEGATION CSE": "IND.DELEGATION CSE",
    r"ABS[\. ]*DELEGATION(?! CSE)": "ABS. DELEGATION",
    r"IND[\. ]*DELEGATION(?! CSE)": "IND. DELEGATION",
    r"ABS ECO ET SYNDICAL": "ABS ECO ET SYNDICAL",
    r"IND ECO ET SYNDICAL": "IND ECO ET SYNDICAL",
    r"PR[\. ]*PART[\. ]*VALEUR": "PR.PART.VALEUR NS/NI",
    r"SECURITE SOCIALE.*MALADIE": "SECURITE SOCIALE - MALADIE MATERNITE",
    r"PREVOYANCE INCAPACITE": "PREVOYANCE INCAPACITE INVALIDITE DECES TA",
    r"COMPLEMENTAIRE INCAPACITE": "COMPLEMENTAIRE INCAPACITE INVALIDITE DECES TA",
    r"COMPLEMENTAIRE SANTE OBLIGATOIRE": "COMPLEMENTAIRE SANTE OBLIGATOIRE",
    r"COMPLEMENTAIRE SANTE(?! OBLIGATOIRE)": "COMPLEMENTAIRE SANTE",
    r"ACCIDENTS DU TRAVAIL": "ACCIDENTS DU TRAVAIL-MALADIES PROFESSIONNELLES",
    r"SECURITE SOCIALE PLAFONNEE": "SECURITE SOCIALE PLAFONNEE",
    r"SECURITE SOCIALE DEPLAFONNEE": "SECURITE SOCIALE DEPLAFONNEE",
    r"RETRAITE COMPLEMENTAIRE.*CEG.*TRANCHE 1": "RETRAITE COMPLEMENTAIRE ET CEG TRANCHE 1",
    r"COMPLEMENTAIRE TRANCHE 1": "COMPLEMENTAIRE TRANCHE 1",
    r"^FAMILLE$": "FAMILLE",
    r"ASSURANCE CHOMAGE": "ASSURANCE CHOMAGE",
    r"CSG DEDUCTIBLE": "CSG DEDUCTIBLE DE L'IMPOT SUR LE REVENU",
    r"CSG.CRDS NON DEDUCTIBLE": "CSG/CRDS NON DEDUCTIBLES DE L'IMPOT SUR LE REVENU",
    r"CSG.CRDS SUR LES REVENUS NON": "CSG/CRDS SUR LES REVENUS NON IMPOSABLES",
    r"COTISATIONS STATUTAIRES": "COTISATIONS STATUTAIRES",
    r"AUTRES CHARGES DUES": "AUTRES CHARGES DUES PAR L'EMPLOYEUR",
    r"AUTRES CONTRIBUTIONS DUES": "AUTRES CONTRIBUTIONS DUES PAR L'EMPLOYEUR",
    r"EXONERATIONS ET ALLEGEMENTS": "EXONERATIONS ET ALLEGEMENTS DE COTISATIONS",
    r"EXONERATIONS DE COTISATIONS SALARIALES": "EXONERATIONS DE COTISATIONS SALARIALES",
    r"EXONERATIONS DE COTISATIONS EMPLOYEUR": "EXONERATIONS DE COTISATIONS EMPLOYEUR",
    r"TRANSPORT PROVINCE": "TRANSPORT PROVINCE",
    r"IND[\. ]*FORF[\. ]*TELETRAV": "IND.FORF.TELETRAV.NS",
    r"IND[\. ]*TELETRVAIL": "IND.TELETRVAIL NS NI",
    r"RET[\. ]*TITRE REPAS": "RET.TITRE REPAS",
    r"FR[\. ]*SANTE IMP": "FR.SANTE IMP.",
    r"IMPOT SUR LE REVENU": "IMPOT SUR LE REVENU PRELEVE",
    r"OPPOSITION": "OPPOSITION 2",
    r"HS EXO SOC": "HS EXO SOC.",
    r"HS EXO(?! SOC)": "HS EXO",
}
