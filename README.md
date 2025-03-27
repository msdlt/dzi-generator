# 🧭 DeepZoom Image Converter

This Python script converts standard images or **Whole Slide Images (WSI)** into **DeepZoom (DZI)** format, compatible with viewers like [OpenSeadragon](https://openseadragon.github.io/). It supports `.svs`, `.tif`, `.jpg`, `.png`, and other formats via OpenSlide and Pillow.

---

## 📦 Features

- 🧠 Automatically detects whether to use **OpenSlide** or **Pillow**
- 🔍 Generates DeepZoom image pyramids with custom tile size and overlap
- 📁 Outputs DZI `.dzi` descriptor and tiled image folder
- 🖼️ Supports both medical WSI and regular images

---

## 🛠 Requirements

Install dependencies using pip:

```
pip install openslide-python Pillow
```

> **Note:** You must also have [OpenSlide](https://openslide.org/download/) installed on your system (e.g. `libopenslide` on Linux/macOS).

---

## 🚀 Usage

```
python dzi_converter.py --input path/to/image.svs
```

### Optional:

```
--output, -o    Output base name (defaults to input file name)
```

### Example:

```
python dzi_converter.py -i slides/sample.svs -o output/my_slide
```

This will produce:

```
output/
├── my_slide.dzi
└── my_slide_files/
    ├── 0/
    ├── 1/
    ├── ...
    └── N/
```

---

## 📂 Output Structure

- **`.dzi`** file: XML descriptor with tile layout and metadata
- **`_files/`** folder: DeepZoom tiles organized by zoom level

Each level contains JPEG tiles named as `{col}_{row}.jpeg`.

---

## 🧪 Supported Formats

| Format              | Library Used |
|---------------------|--------------|
| `.svs`, `.tif` (WSI) | OpenSlide     |
| `.jpg`, `.png`, `.tif` | Pillow       |

---

## ⚙️ Configuration

These values are hardcoded in the script but can be modified:

```python
TILE_SIZE = 254       # Tile size in pixels
OVERLAP = 1           # Overlap between tiles
TILE_FORMAT = 'jpeg'  # Output tile format
```

---

## 🧠 Internals

- **OpenSlide path**: Uses `DeepZoomGenerator` for tiled pyramid generation
- **Fallback path**: Uses Pillow to manually create tiles and descriptor
- **Multi-resolution tiling**: Based on power-of-two scaling

---

## 📝 License

This script is provided under the MIT License.

---

## 🙌 Acknowledgements

- [OpenSlide](https://openslide.org/)
- [Pillow (PIL)](https://python-pillow.org/)
- [OpenSeadragon](https://openseadragon.github.io/)
