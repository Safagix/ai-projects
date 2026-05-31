import sys
from PIL import Image, ImageEnhance
import os
import json

def resize_image(image, new_width=80):
    width, height = image.size
    # A single unicode full-block character is generally taller than it is wide.
    # We use half blocks (2 vertical pixels = 1 char). 
    # So we need height * aspect_ratio.
    ratio = height / width
    new_height = int(new_width * ratio)
    # Ensure height is even for the 2-pixel vertical chunking
    if new_height % 2 != 0:
        new_height += 1
    return image.resize((new_width, new_height))

def pixels_to_halfblocks(image):
    width, height = image.size
    pixels = image.load()
    
    ascii_img = ""
    # We step 2 pixels at a time vertically
    for y in range(0, height, 2):
        for x in range(width):
            # Get intensity of top pixel (0-255)
            p_top = pixels[x, y]
            # Get intensity of bottom pixel
            p_bot = pixels[x, y + 1]
            
            # Threshold to 1-bit (light vs dark)
            threshold = 128
            is_light_top = p_top > threshold
            is_light_bot = p_bot > threshold
            
            # Map combinations to half-block characters
            # Assuming light background and drawing the character in dark
            # Wait, our terminal is black background, text is cyan.
            # So "light" means we draw a block (cyan), "dark" means space (black).
            if is_light_top and is_light_bot:
                ascii_img += "█"
            elif is_light_top and not is_light_bot:
                ascii_img += "▀"
            elif not is_light_top and is_light_bot:
                ascii_img += "▄"
            else:
                ascii_img += " "
        ascii_img += "\n"
    return ascii_img

def process_image(img_path, width=80):
    try:
        image = Image.open(img_path).convert("L")
    except Exception as e:
        print(f"Error opening {img_path}: {e}")
        return ""
    
    # Increase contrast massively to emulate hard pixel-art lines
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(3.0) # Boost contrast
    
    image = resize_image(image, new_width=width)
    return pixels_to_halfblocks(image)
    
def generate_js_frames(image_paths, output_path, width=80):
    frames = []
    for path in image_paths:
        art = process_image(path, width=width)
        if art:
            frames.append(art)
    
    if not frames:
        return
        
    js_content = "window.ASCII_FRAMES = " + json.dumps(frames, indent=4) + ";\n"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"Succesfully generated ultra-crisp blocks in {output_path}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "..", "static", "avatar", "frames.js")
    out_path = os.path.abspath(out_path)
    generate_js_frames(sys.argv[1:], out_path)
