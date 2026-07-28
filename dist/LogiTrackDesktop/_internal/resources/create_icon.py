# Crear: resources/create_icon.py
from PIL import Image, ImageDraw

def create_icon():
    """Crea un icono simple para la aplicación"""
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Fondo circular
    draw.ellipse([10, 10, size-10, size-10], fill=(52, 152, 219, 255))
    
    # Texto "LT"
    from PIL import ImageFont
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()
    
    draw.text((size//2-60, size//2-60), "LT", fill=(255, 255, 255, 255), font=font)
    
    # Guardar como ICO
    img.save("resources/delivery.ico", format="ICO", sizes=[(256, 256)])
    print("✅ Icono creado: resources/delivery.ico")

if __name__ == "__main__":
    create_icon()