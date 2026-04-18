"""
Génère le QR code badge SUD :
- Cercle jaune cerclé de noir (fidèle au logo SUD Solidaires)
- QR code centré dans le cercle, lisible et fonctionnel
- Texte "SUD" petit, positionné juste en dessous du QR code
- Pas de texte "Solidaires" — supprimé
- Rendu propre et professionnel
"""
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "static", "qrcode-payslip.png")
URL = "https://supremaceur.github.io/analyse-fiche-de-paie/"

SIZE = 1200
CENTER = SIZE // 2
BORDER_WIDTH = 35
YELLOW = "#FFE500"
BLACK = "#000000"


def get_font(name_list, size):
    for name in name_list:
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def generate():
    # --- 1. Canvas transparent + cercle jaune/noir ---
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Cercle noir (bordure épaisse)
    draw.ellipse([0, 0, SIZE - 1, SIZE - 1], fill=BLACK)
    # Cercle jaune intérieur
    inner = BORDER_WIDTH
    draw.ellipse(
        [inner, inner, SIZE - inner - 1, SIZE - inner - 1],
        fill=YELLOW,
    )

    # --- 2. Générer le QR code ---
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=14,
        border=1,
    )
    qr.add_data(URL)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=BLACK, back_color=YELLOW).convert("RGBA")

    # --- 3. Préparer le texte "SUD" pour calculer l'espace nécessaire ---
    font_sud = get_font([
        "arialbi.ttf", "arialbd.ttf", "arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ], 100)
    sud_text = "SUD"
    bbox_sud = draw.textbbox((0, 0), sud_text, font=font_sud)
    sud_h = bbox_sud[3] - bbox_sud[1]
    sud_w = bbox_sud[2] - bbox_sud[0]

    # --- 4. Calculer les dimensions pour que tout tienne dans le cercle ---
    # Le QR + SUD doivent tenir dans le cercle inscrit.
    # Pour un carré inscrit dans un cercle de rayon R : côté = R * sqrt(2)
    # On prend une marge de sécurité supplémentaire.
    usable_radius = (SIZE // 2) - inner - 20
    gap = 15
    # Le QR est un carré : ses 4 coins doivent rester dans le cercle.
    # Pour un carré centré dans un cercle de rayon R, côté max = R * sqrt(2).
    # Mais le QR n'est pas centré verticalement (SUD est en dessous),
    # donc on prend une marge confortable : 65% du diamètre utilisable.
    total_h_avail = int(usable_radius * 2 * 0.65)
    qr_size = total_h_avail - sud_h - gap
    qr_max_w = int(usable_radius * 2 * 0.65)
    qr_size = min(qr_size, qr_max_w)

    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)

    # --- 5. Positionner QR + SUD centrés verticalement dans le cercle ---
    total_h = qr_size + gap + sud_h
    start_y = CENTER - total_h // 2

    # Coller le QR code
    qr_x = CENTER - qr_size // 2
    qr_y = start_y
    img.paste(qr_img, (qr_x, qr_y), qr_img)

    # Petit cadre noir autour du QR pour délimiter
    frame = 3
    draw.rectangle(
        [qr_x - frame, qr_y - frame, qr_x + qr_size + frame, qr_y + qr_size + frame],
        outline=BLACK, width=frame,
    )

    # --- 6. Texte "SUD" centré sous le QR code ---
    sud_x = CENTER - sud_w // 2
    sud_y = qr_y + qr_size + gap
    draw.text((sud_x, sud_y), sud_text, fill=BLACK, font=font_sud)

    # --- 7. Sauvegarder ---
    img.save(OUTPUT, "PNG")
    print(f"QR code saved: {OUTPUT}  ({SIZE}x{SIZE}px)")


if __name__ == "__main__":
    generate()
