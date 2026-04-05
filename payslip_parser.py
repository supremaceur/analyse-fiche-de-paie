"""
Parseur de fiches de paie PDF.
Extrait les données structurées à partir du texte brut des bulletins de paie.
"""

import re
import pdfplumber
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EmployerInfo:
    nom: str = ""
    adresse: str = ""
    siret: str = ""
    ape: str = ""
    convention_collective: str = ""
    etablissement: str = ""


@dataclass
class EmployeeInfo:
    nom: str = ""
    adresse: str = ""
    matricule: str = ""
    num_securite_sociale: str = ""
    affectation: str = ""
    emploi: str = ""
    coefficient: str = ""
    classification: str = ""
    date_entree: str = ""
    date_anciennete: str = ""
    date_sortie: str = ""
    horaire: str = ""
    taux_horaire: str = ""
    salaire_mensuel_ref: str = ""
    centre_cout: str = ""


@dataclass
class PayslipLine:
    designation: str = ""
    nombre_ou_base: str = ""
    taux_ou_pourcent: str = ""
    montant_employe: float = 0.0
    montant_employeur: float = 0.0
    section: str = ""  # remuneration, sante, retraite, famille, chomage, csg, cotisations, exonerations, retenues


@dataclass
class PayslipSummary:
    remuneration_brute: float = 0.0
    cotisations_salariales: float = 0.0
    indemnites_non_soumises: float = 0.0
    autres_retenues: float = 0.0
    cotisations_patronales: float = 0.0
    montant_net_social: float = 0.0
    net_avant_impot: float = 0.0
    net_a_payer: float = 0.0
    net_fiscal: float = 0.0
    hs_exonerees: float = 0.0
    total_verse_employeur: float = 0.0
    taux_impot: str = ""
    mode_paiement: str = ""


@dataclass
class PayslipData:
    periode: str = ""
    date_debut: str = ""
    date_fin: str = ""
    date_paiement: str = ""
    employeur: EmployerInfo = field(default_factory=EmployerInfo)
    salarie: EmployeeInfo = field(default_factory=EmployeeInfo)
    lignes: list = field(default_factory=list)
    resume: PayslipSummary = field(default_factory=PayslipSummary)
    conges_acquis: str = ""
    conges_pris: str = ""
    # Compteurs CP détaillés
    cp_en_cours_acquis: str = ""      # DT CP EN COURS : droits acquis période en cours (N)
    cp_en_cours_pris: str = ""        # PRIS CP EN COURS
    cp_en_cours_solde: str = ""       # SLD CP EN COURS : solde restant période en cours
    cp_acquis_droits: str = ""        # DT CP EN ACQUIS : droits acquis période précédente (N-1)
    cp_acquis_pris: str = ""          # PRIS CP ACQUIS : CP pris sur N-1
    cp_acquis_solde: str = ""         # SLD CP ACQUIS : solde restant N-1
    raw_text: str = ""


def extract_text_from_pdf(filepath: str) -> str:
    """Extrait le texte brut d'un fichier PDF."""
    full_text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text


def parse_amount(text: str) -> float:
    """Convertit un montant texte en float. Gère les formats comme '1823,03' ou '20,19-'."""
    if not text:
        return 0.0
    text = text.strip()
    negative = text.endswith("-")
    text = text.replace("-", "").replace(",", ".").replace(" ", "")
    try:
        val = float(text)
        return -val if negative else val
    except ValueError:
        return 0.0


def parse_employer_info(text: str) -> EmployerInfo:
    """Extrait les informations de l'employeur."""
    info = EmployerInfo()

    # Nom entreprise (SITEL FRANCE ou FOUNDEVER FRANCE)
    m = re.search(r"(SITEL|FOUNDEVER)\s+FRANCE", text)
    if m:
        info.nom = m.group(0)

    # Adresse
    m = re.search(r"(\d{4}\s+RUE\s+[A-Z\s]+)\n(\d{5}\s+[A-Z\s]+)", text)
    if m:
        info.adresse = f"{m.group(1).strip()}, {m.group(2).strip()}"

    # SIRET
    m = re.search(r"SIRET:\s*(\d+)", text)
    if m:
        info.siret = m.group(1)

    # APE
    m = re.search(r"APE:\s*(\w+)", text)
    if m:
        info.ape = m.group(1)

    # Convention collective
    m = re.search(r"CONVENTION\s+(.*?)(?:COLLECTIVE:)?\s*(.*?)(?:\n|$)", text)
    if m:
        info.convention_collective = "Prestataires de service du secteur tertiaire"

    # Établissement
    m = re.search(r"(?:SITEL|FOUNDEVER)\s+TROYES\s*/(\d+)", text)
    if m:
        info.etablissement = f"TROYES /{m.group(1)}"

    return info


def parse_employee_info(text: str) -> EmployeeInfo:
    """Extrait les informations du salarié."""
    info = EmployeeInfo()

    # Matricule
    m = re.search(r"NO DE SALARIE\s*:\s*(\d+)", text)
    if m:
        info.matricule = m.group(1)

    # Numéro SS
    m = re.search(r"SECURITE SOCIALE\s*:\s*(\d+)", text)
    if m:
        info.num_securite_sociale = m.group(1)

    # Nom - sur la meme ligne que "CONVENTION PRESTATAIRES DE SERV"
    m = re.search(r"PRESTATAIRES DE SERV\s+([A-Z]+\s+[A-Z]+)", text)
    if not m:
        m = re.search(r"(?:SITEL|FOUNDEVER)\s+TROYES\s*/\d+\.\d+\n.*?\n.*?([A-Z]+\s+[A-Z]+)\n", text)
    if not m:
        m = re.search(r"ICE DU SECTEUR TERTIAIRE\s*\n\s*([A-Z]+\s+[A-Z]+)", text)
    if m:
        info.nom = m.group(1).strip()

    # Adresse salarié
    m = re.search(r"(?:ICE DU SECTEUR TERTIAIRE)\s*\n\s*[A-Z]+\s+[A-Z]+\s*\n\s*(.+)\n\s*(\d{5}\s+.+)", text)
    if m:
        info.adresse = f"{m.group(1).strip()}, {m.group(2).strip()}"

    # Affectation
    m = re.search(r"AFFECTATION\s*:(\w+)", text)
    if m:
        info.affectation = m.group(1)

    # Emploi
    m = re.search(r"EMPLOI\s*:([A-Z\s]+?)(?=DATE)", text)
    if m:
        info.emploi = m.group(1).strip()

    # Coefficient
    m = re.search(r"COEFFICIENT\s*:\s*([\d,]+)", text)
    if m:
        info.coefficient = m.group(1)

    # Classification
    m = re.search(r"CLASSIFICATION\s*:([A-Z\s\.\d]+?)(?=CENTRE)", text)
    if m:
        info.classification = m.group(1).strip()

    # Dates
    m = re.search(r"DATE ENTREE\s*:\s*([\d/]+)", text)
    if m:
        info.date_entree = m.group(1)

    m = re.search(r"DATE ANCIENNETE:\s*([\d/]+)", text)
    if m:
        info.date_anciennete = m.group(1)

    m = re.search(r"DATE DE SORTIE\s*:\s*([\d/]*)", text)
    if m:
        info.date_sortie = m.group(1)

    # Horaire
    m = re.search(r"HORAIRE\s*:\s*([\d,]+)", text)
    if m:
        info.horaire = m.group(1)

    # Taux horaire
    m = re.search(r"TAUX HORAIRE\s*:\s*([\d,]+)", text)
    if m:
        info.taux_horaire = m.group(1)

    # Salaire mensuel de référence
    m = re.search(r"SAL\.MENS\.REF\.\s*:\s*([\d,]+)", text)
    if m:
        info.salaire_mensuel_ref = m.group(1)

    # Centre de coût
    m = re.search(r"CENTRE DE COUT\s*:(\w+)", text)
    if m:
        info.centre_cout = m.group(1)

    return info


def parse_period_info(text: str) -> tuple:
    """Extrait les informations de période."""
    periode = ""
    date_debut = ""
    date_fin = ""
    date_paiement = ""

    m = re.search(r"PERIODE D'EMPLOI DU\s*:\s*(\d+\s+\w+\s+\d{4})", text)
    if m:
        date_debut = m.group(1)

    m = re.search(r"AU\s*:\s*(\d+\s+\w+\s+\d{4})", text)
    if m:
        date_fin = m.group(1)

    m = re.search(r"DATE DE PAIEMENT\s*:\s*(\d+\s+\w+\s+\d{4})", text)
    if m:
        date_paiement = m.group(1)

    if date_debut and date_fin:
        periode = f"Du {date_debut} au {date_fin}"

    return periode, date_debut, date_fin, date_paiement


def _parse_line_amount(raw_val: str) -> float:
    """Parse un montant depuis le texte brut de la fiche, gère le format sans virgule."""
    if not raw_val:
        return 0.0
    raw_val = raw_val.strip()
    negative = raw_val.endswith("-")
    raw_val = raw_val.replace("-", "").strip()
    if not raw_val:
        return 0.0
    # Les montants sont en centimes (ex: 182303 = 1823,03)
    try:
        val = int(raw_val)
        result = val / 100.0
        return -result if negative else result
    except ValueError:
        return 0.0


def parse_payslip_lines(text: str) -> list:
    """Extrait les lignes de la fiche de paie avec leurs montants."""
    lines = []
    current_section = "remuneration"

    # Sections markers
    section_markers = {
        "SANTE": "sante",
        "RETRAITE": "retraite",
        "FAMILLE": "famille",
        "ASSURANCE CHOMAGE": "chomage",
        "COTISATIONS STATUTAIRES": "cotisations_statutaires",
        "AUTRES CHARGES DUES": "autres_charges",
        "AUTRES CONTRIBUTIONS DUES": "autres_charges",
        "CSG DEDUCTIBLE": "csg_crds",
        "CSG/CRDS": "csg_crds",
        "EXONERATIONS": "exonerations",
        "COTISATIONS ET CONTRIBUTIONS SOCIALES FACULTATIVES": "cotisations_facultatives",
    }

    # Pattern for main data lines
    # Format: DESIGNATION [NOMBRE BASE] [TAUX] MONTANT_EMPLOYE [MONTANT_EMPLOYEUR]
    # Example: SALAIRE DE BASE 15167 182303
    # Example: SECURITE SOCIALE PLAFONNEE 209946 6900 14486- 17950

    text_lines = text.split("\n")

    for raw_line in text_lines:
        raw_line = raw_line.strip()

        # Skip empty, header, or info lines
        if not raw_line:
            continue
        if raw_line.startswith(("BULLETIN", "NO DE SALARIE", "FICHE ANNEXE", "DESIGNATION",
                                "OU BASE", "TAUX OU", "NOMBRE", "JOUR", "TRAVAIL",
                                "INFORMATIONS", "DU ", "Nous vous", "REVENUS",
                                "PRELEVEMENT", "TOTAL VERSE", "NET FISCAL",
                                "ALLEGEMENTS", "----", "HS/HC", "DT CP", "SLD CP",
                                "CONVENTION", "COLLECTIVE", "AFFECTATION", "EMPLOI",
                                "COEFFICIENT", "CLASSIFICATION", "PERIODE",
                                "0001 RUE", "10000", "SITEL", "FOUNDEVER",
                                "N°", "SIRET")):
            continue

        # Skip daily info lines (D 15, L 16, etc.)
        if re.match(r"^[DLMJVS]\s+\d{1,2}", raw_line):
            continue

        # Skip legend lines
        if re.match(r"^(CP |NN |ZV |DL |H1 |MA |JF |NP |SO )", raw_line):
            continue

        # Detect section changes
        for marker, section in section_markers.items():
            if raw_line.startswith(marker):
                current_section = section
                break

        # Detect totals
        if raw_line.startswith("*REMUNERATION BRUTE"):
            m = re.search(r"\.+(\d+)", raw_line)
            if m:
                lines.append(PayslipLine(
                    designation="TOTAL REMUNERATION BRUTE",
                    montant_employe=_parse_line_amount(m.group(1)),
                    section="total_brut"
                ))
            continue

        if raw_line.startswith("*COTISAT.SALARIALES"):
            m = re.search(r"\.+(\d+)-?", raw_line)
            if m:
                val = m.group(1)
                if raw_line.rstrip().endswith("-"):
                    val += "-"
                lines.append(PayslipLine(
                    designation="TOTAL COTISATIONS SALARIALES",
                    montant_employe=_parse_line_amount(val),
                    section="total_cotisations"
                ))
            continue

        if raw_line.startswith("*INDEM.NON SOUMISES"):
            m = re.search(r"\.+(\d+)", raw_line)
            if m:
                lines.append(PayslipLine(
                    designation="TOTAL INDEMNITES NON SOUMISES",
                    montant_employe=_parse_line_amount(m.group(1)),
                    section="total_indemnites"
                ))
            continue

        if raw_line.startswith("*AUTRES RETENUES"):
            m = re.search(r"\.+(\d+)-?", raw_line)
            if m:
                val = m.group(1)
                if raw_line.rstrip().endswith("-"):
                    val += "-"
                lines.append(PayslipLine(
                    designation="TOTAL AUTRES RETENUES",
                    montant_employe=_parse_line_amount(val),
                    section="total_retenues"
                ))
            continue

        if raw_line.startswith("*COTISAT.PATRONALES"):
            m = re.search(r"\.+(\d+)", raw_line)
            if m:
                lines.append(PayslipLine(
                    designation="TOTAL COTISATIONS PATRONALES",
                    montant_employeur=_parse_line_amount(m.group(1)),
                    section="total_patronales"
                ))
            continue

        # Parse standard data lines
        # Known line designations
        known_designations = [
            "SALAIRE DE BASE",
            "SAL MIN CONV",
            "COMPL SAL IND",
            "HRES AU TAUX NORMAL",
            "HRES SUPPL. A 125%",
            "BONUS MENSUEL",
            "ABS. NON AUTORISEE",
            "ABS CONGES PAYES",
            "IND CONGES PAYES",
            "ABS. JOUR FERIE",
            "IND. JOUR FERIE",
            "ABS. AUTOR.NON PAYEE",
            "ABSENCE DIVERS",
            "INDEMNITE DIVERS",
            "ABSENCE H.MALADIE",
            "REGUL CP.ANTICIPES",
            "ABS. DELEGATION CSE",
            "IND.DELEGATION CSE",
            "ABS. DELEGATION",
            "IND. DELEGATION",
            "ABS ECO ET SYNDICAL",
            "IND ECO ET SYNDICAL",
            "PR.PART.VALEUR NS/NI",
            "SECURITE SOCIALE - MALADIE MATERNITE",
            "PREVOYANCE INCAPACITE INVALIDITE DECES TA",
            "COMPLEMENTAIRE INCAPACITE INVALIDITE DECES TA",
            "COMPLEMENTAIRE SANTE OBLIGATOIRE",
            "COMPLEMENTAIRE SANTE",
            "ACCIDENTS DU TRAVAIL-MALADIES PROFESSIONNELLES",
            "SECURITE SOCIALE PLAFONNEE",
            "SECURITE SOCIALE DEPLAFONNEE",
            "RETRAITE COMPLEMENTAIRE ET CEG TRANCHE 1",
            "COMPLEMENTAIRE TRANCHE 1",
            "FAMILLE",
            "ASSURANCE CHOMAGE",
            "COTISATIONS STATUTAIRES",
            "AUTRES CHARGES DUES PAR L'EMPLOYEUR",
            "AUTRES CONTRIBUTIONS DUES PAR L'EMPLOYEUR",
            "CSG DEDUCTIBLE DE L'IMPOT SUR LE REVENU",
            "CSG/CRDS NON DEDUCTIBLES DE L'IMPOT SUR LE REVENU",
            "CSG/CRDS SUR LES REVENUS NON IMPOSABLES",
            "EXONERATIONS ET ALLEGEMENTS DE COTISATIONS",
            "EXONERATIONS DE COTISATIONS SALARIALES",
            "EXONERATIONS DE COTISATIONS EMPLOYEUR",
            "TRANSPORT PROVINCE",
            "IND.FORF.TELETRAV.NS",
            "IND.TELETRVAIL NS NI",
            "RET.TITRE REPAS",
            "FR.SANTE IMP.",
            "IMPOT SUR LE REVENU PRELEVE",
            "OPPOSITION 2",
            "HS EXO SOC.",
            "HS EXO",
        ]

        matched_designation = None
        remaining = ""
        for desig in sorted(known_designations, key=len, reverse=True):
            if raw_line.startswith(desig):
                matched_designation = desig
                remaining = raw_line[len(desig):].strip()
                break

        if not matched_designation:
            # Try fuzzy match for variations
            for desig in sorted(known_designations, key=len, reverse=True):
                # Normalize both for comparison
                norm_line = re.sub(r"[\s\.]+", " ", raw_line).strip().upper()
                norm_desig = re.sub(r"[\s\.]+", " ", desig).strip().upper()
                if norm_line.startswith(norm_desig):
                    matched_designation = desig
                    remaining = raw_line[len(norm_desig):].strip()
                    break

        if matched_designation:
            line = PayslipLine(designation=matched_designation, section=current_section)

            # Parse remaining numbers
            # Remove daily info that might be appended (like "D 15", "L 16 7 00")
            remaining = re.sub(r"[DLMJVS]\s+\d{1,2}.*$", "", remaining).strip()

            numbers = re.findall(r"(\d+)-?", remaining)
            is_negative = [bool(re.search(r"\d+" + re.escape("-"), part))
                           for part in re.findall(r"\d+-?", remaining)]

            if matched_designation == "SALAIRE DE BASE":
                # Format: BASE MONTANT (ex: 15167 182303)
                if len(numbers) >= 2:
                    line.nombre_ou_base = str(int(numbers[0]) / 100)
                    line.montant_employe = _parse_line_amount(numbers[1])
            elif matched_designation in ("SAL MIN CONV", "COMPL SAL IND"):
                # Just a reference value
                if numbers:
                    line.montant_employe = parse_amount(remaining.replace(" ", ""))
            elif matched_designation in ("BONUS MENSUEL", "REGUL CP.ANTICIPES", "PR.PART.VALEUR NS/NI"):
                if numbers:
                    line.montant_employe = _parse_line_amount(numbers[0])
            elif matched_designation.startswith("HS EXO"):
                # Info line, extract the amount
                remaining_clean = remaining.replace(":", "").strip()
                if remaining_clean:
                    line.montant_employe = parse_amount(remaining_clean)
            elif matched_designation == "FR.SANTE IMP.":
                line.montant_employe = parse_amount(remaining)
            elif matched_designation == "OPPOSITION 2":
                if numbers:
                    raw_vals = re.findall(r"\d+-?", remaining)
                    if raw_vals:
                        line.montant_employe = _parse_line_amount(raw_vals[0])
            else:
                # General pattern: [BASE] [TAUX] [MONTANT_EMP] [MONTANT_PATRON]
                raw_vals = re.findall(r"\d+-?", remaining)
                if len(raw_vals) >= 1:
                    # Determine which values are base, taux, montant_emp, montant_patron
                    if matched_designation in ("HRES AU TAUX NORMAL", "HRES SUPPL. A 125%"):
                        if len(raw_vals) >= 3:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.taux_ou_pourcent = str(int(raw_vals[1]) / 1000)
                            line.montant_employe = _parse_line_amount(raw_vals[2])
                        elif len(raw_vals) >= 2:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.montant_employe = _parse_line_amount(raw_vals[1])
                    elif matched_designation in (
                        "ABS. NON AUTORISEE", "ABS CONGES PAYES", "IND CONGES PAYES",
                        "ABS. JOUR FERIE", "IND. JOUR FERIE", "ABS. AUTOR.NON PAYEE",
                        "ABSENCE DIVERS", "INDEMNITE DIVERS", "ABSENCE H.MALADIE",
                        "ABS. DELEGATION CSE", "IND.DELEGATION CSE",
                        "ABS. DELEGATION", "IND. DELEGATION",
                        "ABS ECO ET SYNDICAL", "IND ECO ET SYNDICAL",
                    ):
                        if len(raw_vals) >= 3:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.taux_ou_pourcent = str(int(raw_vals[1]) / 1000)
                            line.montant_employe = _parse_line_amount(raw_vals[2])
                        elif len(raw_vals) >= 2:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.montant_employe = _parse_line_amount(raw_vals[1])
                    elif matched_designation == "RET.TITRE REPAS":
                        # BASE TAUX MONTANT_EMP MONTANT_PATRON
                        if len(raw_vals) >= 4:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.taux_ou_pourcent = str(int(raw_vals[1]) / 100)
                            line.montant_employe = _parse_line_amount(raw_vals[2])
                            line.montant_employeur = _parse_line_amount(raw_vals[3])
                        elif len(raw_vals) >= 2:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.montant_employe = _parse_line_amount(raw_vals[1])
                    elif matched_designation == "IMPOT SUR LE REVENU PRELEVE":
                        if len(raw_vals) >= 2:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.taux_ou_pourcent = str(int(raw_vals[1]) / 10000)
                            line.montant_employe = 0.0  # Often 0 with taux personnalisé
                    elif matched_designation in (
                        "SECURITE SOCIALE - MALADIE MATERNITE",
                        "ACCIDENTS DU TRAVAIL-MALADIES PROFESSIONNELLES",
                        "FAMILLE", "ASSURANCE CHOMAGE",
                        "AUTRES CHARGES DUES PAR L'EMPLOYEUR",
                        "AUTRES CONTRIBUTIONS DUES PAR L'EMPLOYEUR",
                    ):
                        # Patronal only: BASE TAUX MONTANT_PATRON
                        if len(raw_vals) >= 2:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.taux_ou_pourcent = str(int(raw_vals[1]) / 10000)
                            if len(raw_vals) >= 3:
                                line.montant_employeur = _parse_line_amount(raw_vals[2])
                            else:
                                line.montant_employeur = _parse_line_amount(raw_vals[1])
                    elif matched_designation in ("COTISATIONS STATUTAIRES",):
                        if len(raw_vals) >= 1:
                            line.montant_employeur = _parse_line_amount(raw_vals[0])
                    elif matched_designation.startswith("EXONERATION"):
                        if len(raw_vals) >= 1:
                            raw_all = re.findall(r"\d+-?", remaining)
                            # Could be just a taux or montant
                            if len(raw_all) == 1:
                                line.montant_employeur = _parse_line_amount(raw_all[0])
                            elif len(raw_all) >= 2:
                                line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                                line.montant_employeur = _parse_line_amount(raw_all[-1])
                    elif matched_designation == "TRANSPORT PROVINCE":
                        if numbers:
                            line.montant_employe = _parse_line_amount(numbers[0])
                    else:
                        # General: BASE TAUX MONTANT_EMP MONTANT_PATRON
                        if len(raw_vals) >= 4:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.taux_ou_pourcent = str(int(raw_vals[1]) / 10000)
                            line.montant_employe = _parse_line_amount(raw_vals[2])
                            line.montant_employeur = _parse_line_amount(raw_vals[3])
                        elif len(raw_vals) >= 3:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.taux_ou_pourcent = str(int(raw_vals[1]) / 10000)
                            line.montant_employe = _parse_line_amount(raw_vals[2])
                        elif len(raw_vals) >= 2:
                            line.nombre_ou_base = str(int(raw_vals[0]) / 100)
                            line.montant_employe = _parse_line_amount(raw_vals[1])

            lines.append(line)

    return lines


def parse_summary(text: str) -> PayslipSummary:
    """Extrait le résumé financier de la fiche."""
    summary = PayslipSummary()

    # Rémunération brute
    m = re.search(r"\*REMUNERATION BRUTE.*?\.+(\d+)", text)
    if m:
        summary.remuneration_brute = _parse_line_amount(m.group(1))

    # Cotisations salariales
    m = re.search(r"\*COTISAT\.SALARIALES.*?\.+(\d+)-?", text)
    if m:
        val = m.group(1)
        summary.cotisations_salariales = _parse_line_amount(val + "-")

    # Indemnités non soumises
    m = re.search(r"\*INDEM\.NON SOUMISES.*?\.+(\d+)", text)
    if m:
        summary.indemnites_non_soumises = _parse_line_amount(m.group(1))

    # Autres retenues
    m = re.search(r"\*AUTRES RETENUES.*?\.+(\d+)-?", text)
    if m:
        val = m.group(1)
        summary.autres_retenues = _parse_line_amount(val + "-")

    # Cotisations patronales
    m = re.search(r"\*COTISAT\.PATRONALES.*?\.+(\d+)", text)
    if m:
        summary.cotisations_patronales = _parse_line_amount(m.group(1))

    # Montant net social - format "1575 38" = 1575.38
    m = re.search(r"MONTANT NET SOCIAL\s+(\d+)\s+(\d{2})", text)
    if m:
        summary.montant_net_social = float(f"{m.group(1)}.{m.group(2)}")

    # Net avant impôt
    m = re.search(r"NET A PAYER AVANT IMPOT.*?(\d+)\s+(\d{2})", text)
    if m:
        summary.net_avant_impot = float(f"{m.group(1)}.{m.group(2)}")

    # Net à payer
    m = re.search(r"NE T A P A Y E R.*?(\d+)\s+(\d{2})", text)
    if m:
        summary.net_a_payer = float(f"{m.group(1)}.{m.group(2)}")
    else:
        m = re.search(r"NET A PAYER\s+(\d+)\s+(\d{2})", text)
        if m:
            summary.net_a_payer = float(f"{m.group(1)}.{m.group(2)}")

    # Total versé employeur
    m = re.search(r"TOTAL VERSE EMPLOYEUR\s+(\d+)\s+(\d{2})", text)
    if m:
        summary.total_verse_employeur = float(f"{m.group(1)}.{m.group(2)}")

    # Net fiscal
    m = re.search(r"NET FISCAL\s+(\d+)\s+(\d{2})", text)
    if m:
        summary.net_fiscal = float(f"{m.group(1)}.{m.group(2)}")

    # Mode de paiement
    if "VIREMENT" in text:
        summary.mode_paiement = "Virement"
    elif "CHEQUE" in text:
        summary.mode_paiement = "Chèque"

    # Taux d'imposition
    if "TAUX PERSONNALISE" in text:
        summary.taux_impot = "Taux personnalisé"
    elif "TAUX NON PERSONNALISE" in text:
        summary.taux_impot = "Taux non personnalisé (neutre)"

    # HS exonérées
    m = re.search(r"HS/HC EXONEREES.*?(\d[\d ]+\d{2})", text)
    if m:
        summary.hs_exonerees = parse_amount(m.group(1).replace(" ", ""))

    return summary


def parse_payslip(filepath: str) -> PayslipData:
    """Parse complet d'une fiche de paie PDF."""
    text = extract_text_from_pdf(filepath)

    payslip = PayslipData()
    payslip.raw_text = text

    # Période
    periode, date_debut, date_fin, date_paiement = parse_period_info(text)
    payslip.periode = periode
    payslip.date_debut = date_debut
    payslip.date_fin = date_fin
    payslip.date_paiement = date_paiement

    # Employeur
    payslip.employeur = parse_employer_info(text)

    # Salarié
    payslip.salarie = parse_employee_info(text)

    # Lignes
    payslip.lignes = parse_payslip_lines(text)

    # Résumé
    payslip.resume = parse_summary(text)

    # Congés — extraction détaillée
    # CP en cours (période N : juin → mai)
    m = re.search(r"DT CP EN COURS\s+([\d,]+)", text)
    if m:
        payslip.cp_en_cours_acquis = m.group(1)

    m = re.search(r"PRIS CP EN COURS\s+([\d,]+)", text)
    if m:
        payslip.cp_en_cours_pris = m.group(1)

    m = re.search(r"SLD CP EN COURS\s+([\d,]+)", text)
    if m:
        payslip.cp_en_cours_solde = m.group(1)

    # CP acquis (période N-1)
    m = re.search(r"DT CP EN ACQUIS\s+([\d,]+)", text)
    if m:
        payslip.cp_acquis_droits = m.group(1)

    m = re.search(r"PRIS CP ACQUIS\s+([\d,]+)", text)
    if m:
        payslip.cp_acquis_pris = m.group(1)

    # SLD CP ACQUIS peut apparaître plusieurs fois, prendre la première
    m = re.search(r"SLD CP ACQUIS\s+([\d,]+)", text)
    if m:
        payslip.cp_acquis_solde = m.group(1)
        payslip.conges_acquis = m.group(1)  # rétro-compatibilité

    return payslip


def payslip_to_dict(payslip: PayslipData) -> dict:
    """Convertit un PayslipData en dictionnaire pour export JSON."""
    result = {
        "resume": {
            "periode": payslip.periode,
            "date_debut": payslip.date_debut,
            "date_fin": payslip.date_fin,
            "date_paiement": payslip.date_paiement,
            "employeur": {
                "nom": payslip.employeur.nom,
                "adresse": payslip.employeur.adresse,
                "siret": payslip.employeur.siret,
                "ape": payslip.employeur.ape,
                "convention_collective": payslip.employeur.convention_collective,
            },
            "salarie": {
                "nom": payslip.salarie.nom,
                "matricule": payslip.salarie.matricule,
                "num_securite_sociale": payslip.salarie.num_securite_sociale,
                "emploi": payslip.salarie.emploi,
                "coefficient": payslip.salarie.coefficient,
                "classification": payslip.salarie.classification,
                "date_entree": payslip.salarie.date_entree,
                "horaire": payslip.salarie.horaire,
                "taux_horaire": payslip.salarie.taux_horaire,
                "salaire_mensuel_ref": payslip.salarie.salaire_mensuel_ref,
            },
            "conges_acquis": payslip.conges_acquis,
            "conges": {
                "en_cours": {
                    "acquis": payslip.cp_en_cours_acquis,
                    "pris": payslip.cp_en_cours_pris,
                    "solde": payslip.cp_en_cours_solde,
                },
                "acquis_n1": {
                    "droits": payslip.cp_acquis_droits,
                    "pris": payslip.cp_acquis_pris,
                    "solde": payslip.cp_acquis_solde,
                },
            },
            "remuneration_brute": payslip.resume.remuneration_brute,
            "cotisations_salariales": payslip.resume.cotisations_salariales,
            "indemnites_non_soumises": payslip.resume.indemnites_non_soumises,
            "autres_retenues": payslip.resume.autres_retenues,
            "cotisations_patronales": payslip.resume.cotisations_patronales,
            "montant_net_social": payslip.resume.montant_net_social,
            "net_avant_impot": payslip.resume.net_avant_impot,
            "net_a_payer": payslip.resume.net_a_payer,
            "net_fiscal": payslip.resume.net_fiscal,
            "total_verse_employeur": payslip.resume.total_verse_employeur,
            "mode_paiement": payslip.resume.mode_paiement,
        },
        "remuneration": [],
        "primes": [],
        "cotisations": [],
        "retenues": [],
        "net": {
            "montant_net_social": payslip.resume.montant_net_social,
            "net_avant_impot": payslip.resume.net_avant_impot,
            "net_a_payer": payslip.resume.net_a_payer,
            "net_fiscal": payslip.resume.net_fiscal,
            "hs_exonerees": payslip.resume.hs_exonerees,
            "mode_paiement": payslip.resume.mode_paiement,
            "taux_impot": payslip.resume.taux_impot,
        },
        "questions": [],
    }

    for line in payslip.lignes:
        line_dict = {
            "designation": line.designation,
            "nombre_ou_base": line.nombre_ou_base,
            "taux_ou_pourcent": line.taux_ou_pourcent,
            "montant_employe": line.montant_employe,
            "montant_employeur": line.montant_employeur,
        }

        if line.section in ("remuneration",):
            result["remuneration"].append(line_dict)
        elif line.section in ("sante", "retraite", "famille", "chomage",
                               "csg_crds", "cotisations_statutaires",
                               "autres_charges", "exonerations",
                               "cotisations_facultatives"):
            result["cotisations"].append(line_dict)
        elif line.section in ("retenues",):
            result["retenues"].append(line_dict)
        elif line.section.startswith("total_"):
            # Add totals to appropriate section
            pass  # Handled in resume

        # Separate primes
        if line.designation in ("BONUS MENSUEL", "PR.PART.VALEUR NS/NI"):
            if line_dict in result["remuneration"]:
                result["remuneration"].remove(line_dict)
            result["primes"].append(line_dict)

    return result
