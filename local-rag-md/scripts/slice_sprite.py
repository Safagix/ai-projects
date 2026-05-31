import sys
from PIL import Image
import os

def slice_spritesheet(img_path, cols=4):
    try:
        img = Image.open(img_path)
    except Exception as e:
        print(f"Error abriendo imagen: {e}")
        return
        
    width, height = img.size
    frame_width = width // cols
    
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    out_dir = os.path.dirname(img_path)
    
    print(f"Cortando imagen de {width}x{height} en {cols} fotogramas de {frame_width}x{height}...")
    
    for i in range(cols):
        left = i * frame_width
        right = (i + 1) * frame_width
        
        # Crop box: (left, upper, right, lower)
        bbox = (left, 0, right, height)
        frame = img.crop(bbox)
        
        out_path = os.path.join(out_dir, f"{base_name}_frame{i}.png")
        frame.save(out_path)
        print(f"-> Guardado: {out_path}")
        
    print("¡Corte completado con éxito!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python slice_sprite.py <ruta_a_la_imagen> [numero_de_columnas]")
        sys.exit(1)
        
    cols = 4
    if len(sys.argv) >= 3:
        cols = int(sys.argv[2])
        
    slice_spritesheet(sys.argv[1], cols)
