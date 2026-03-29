"""
Module de parsing des fiches de paie.
Wrapper autour du parseur existant, avec support des uploads Streamlit (UploadedFile).
"""

import sys
import os
import tempfile

# Ajouter le répertoire parent au path pour importer les modules existants
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from payslip_parser import (
    parse_payslip,
    payslip_to_dict,
    extract_text_from_pdf,
    PayslipData,
)


def parse_uploaded_file(uploaded_file) -> dict:
    """
    Parse un fichier uploadé via Streamlit.
    Accepte un objet UploadedFile et retourne un dictionnaire structuré.
    """
    # Écrire le fichier uploadé dans un fichier temporaire
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            payslip = parse_payslip(tmp_path)
            return payslip_to_dict(payslip)
        else:
            raise ValueError(f"Format non supporté : {suffix}. Formats acceptés : PDF")
    finally:
        os.unlink(tmp_path)


def parse_file_path(filepath: str) -> dict:
    """Parse un fichier depuis son chemin sur le disque."""
    payslip = parse_payslip(filepath)
    return payslip_to_dict(payslip)
