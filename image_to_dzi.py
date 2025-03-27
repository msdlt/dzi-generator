import os
import math
import argparse
from xml.etree import ElementTree as ET

from PIL import Image
from openslide import OpenSlide
from openslide.lowlevel import OpenSlideUnsupportedFormatError

# 🧩 DeepZoom settings
TILE_SIZE = 254
OVERLAP = 1
TILE_FORMAT = 'jpeg'

def get_max_level(width, height):
    return int(math.ceil(math.log2(max(width, height))))

def generate_dzi_descriptor(width, height, dzi_path):
    image = ET.Element("Image", TileSize=str(TILE_SIZE), Overlap=str(OVERLAP),
                       Format=TILE_FORMAT, xmlns="http://schemas.microsoft.com/deepzoom/2008")
    size = ET.SubElement(image, "Size", Width=str(width), Height=str(height))
    tree = ET.ElementTree(image)
    tree.write(dzi_path, encoding='utf-8', xml_declaration=True)

def save_tiles_pillow(image, tile_folder):
    max_level = get_max_level(image.width, image.height)
    for level in range(max_level + 1):
        scale = 0.5 ** (max_level - level)
        new_width = max(1, int(image.width * scale))
        new_height = max(1, int(image.height * scale))
        resized = image.resize((new_width, new_height))
        cols = math.ceil(resized.width / TILE_SIZE)
        rows = math.ceil(resized.height / TILE_SIZE)

        level_dir = os.path.join(tile_folder, str(level))
        os.makedirs(level_dir, exist_ok=True)

        for row in range(rows):
            for col in range(cols):
                left = col * TILE_SIZE
                upper = row * TILE_SIZE
                right = min(left + TILE_SIZE, resized.width)
                lower = min(upper + TILE_SIZE, resized.height)
                tile = resized.crop((left, upper, right, lower))
                tile_path = os.path.join(level_dir, f"{col}_{row}.{TILE_FORMAT}")
                tile.save(tile_path)

        print(f"🧱 Pillow - Level {level}: {cols * rows} tiles")
        
def save_tiles_openslide(slide, dz, tile_folder):
    for level in range(dz.level_count):
        cols, rows = dz.level_tiles[level]
        level_dir = os.path.join(tile_folder, str(level))
        os.makedirs(level_dir, exist_ok=True)
        for row in range(rows):
            for col in range(cols):
                tile = dz.get_tile(level, (col, row))
                tile_path = os.path.join(level_dir, f"{col}_{row}.{TILE_FORMAT}")
                tile.save(tile_path)
        print(f"🧱 OpenSlide - Level {level}: {cols * rows} tiles")

# 🖥️ CLI
parser = argparse.ArgumentParser(description="Convert any supported image (WSI or standard) to DeepZoom (DZI)")
parser.add_argument("--input", "-i", required=True, help="Input image path (e.g. .svs, .jpg, .tif, .png)")
parser.add_argument("--output", "-o", help="Output basename (dzi file + tile folder). Defaults to input name.")
args = parser.parse_args()

input_path = os.path.abspath(args.input)
input_ext = os.path.splitext(input_path)[1].lower()
input_name = os.path.splitext(os.path.basename(input_path))[0]
input_dir = os.path.dirname(input_path)
dzi_dir = os.path.join(input_dir, 'dzi')
os.makedirs(dzi_dir, exist_ok=True)

output_basename = os.path.join(dzi_dir, input_name)
dzi_path = output_basename + '.dzi'
tile_folder = output_basename + '_files'
os.makedirs(tile_folder, exist_ok=True)

# ✅ Try OpenSlide first
try:
    slide = OpenSlide(input_path)
    from openslide import deepzoom
    dz = deepzoom.DeepZoomGenerator(slide, tile_size=TILE_SIZE, overlap=OVERLAP)
    max_level = dz.level_count - 1
    width, height = dz.level_dimensions[max_level]
    generate_dzi_descriptor(width, height, dzi_path)
    save_tiles_openslide(slide, dz, tile_folder)
    print(f"✅ OpenSlide DZI saved to: {dzi_path}")
except OpenSlideUnsupportedFormatError:
    # Fallback to Pillow for standard images
    print("ℹ️ Falling back to Pillow for standard image...")
    image = Image.open(input_path).convert('RGB')
    generate_dzi_descriptor(image.width, image.height, dzi_path)
    save_tiles_pillow(image, tile_folder)
    print(f"✅ Pillow DZI saved to: {dzi_path}")
