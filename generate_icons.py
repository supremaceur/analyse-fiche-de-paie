"""
Génère les icônes PWA à partir du logo source (static/logo-source.png).
Exécuter une seule fois : python generate_icons.py
"""
from PIL import Image
import os

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
SOURCE = os.path.join(STATIC_DIR, "logo-source.png")

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]


def generate():
    if not os.path.exists(SOURCE):
        print(f"ERREUR: {SOURCE} introuvable. Place ton logo dans static/logo-source.png")
        return

    src = Image.open(SOURCE).convert("RGBA")
    print(f"Source: {src.size[0]}x{src.size[1]}")

    for s in SIZES:
        icon = src.resize((s, s), Image.LANCZOS)
        path = os.path.join(STATIC_DIR, f"icon-{s}x{s}.png")
        icon.save(path, "PNG")
        print(f"  -> icon-{s}x{s}.png")

    # Favicon 32x32
    fav = src.resize((32, 32), Image.LANCZOS)
    fav.save(os.path.join(STATIC_DIR, "favicon.png"), "PNG")
    print("  -> favicon.png (32x32)")

    # Apple touch icon 180x180
    apple = src.resize((180, 180), Image.LANCZOS)
    apple.save(os.path.join(STATIC_DIR, "apple-touch-icon.png"), "PNG")
    print("  -> apple-touch-icon.png (180x180)")

    # Maskable icon 512x512 (avec padding 20% + fond)
    maskable_size = 512
    inner_size = int(maskable_size * 0.70)
    inner = src.resize((inner_size, inner_size), Image.LANCZOS)
    # Fond couleur #0E1117 (dark background de l'app)
    bg = Image.new("RGBA", (maskable_size, maskable_size), (14, 17, 23, 255))
    offset = (maskable_size - inner_size) // 2
    bg.paste(inner, (offset, offset), inner)
    bg.save(os.path.join(STATIC_DIR, "icon-maskable-512x512.png"), "PNG")
    print("  -> icon-maskable-512x512.png (512x512 maskable)")

    # ICO pour navigateurs desktop
    ico_sizes = [16, 32, 48]
    ico_images = [src.resize((s, s), Image.LANCZOS) for s in ico_sizes]
    ico_images[0].save(
        os.path.join(STATIC_DIR, "favicon.ico"),
        format="ICO",
        sizes=[(s, s) for s in ico_sizes],
        append_images=ico_images[1:],
    )
    print("  -> favicon.ico (16/32/48)")

    print("\nAll icons generated!")


if __name__ == "__main__":
    generate()
