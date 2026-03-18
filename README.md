# img-to-base64

Convert images to Base64 — from the command line or a desktop GUI.

---

## Why would I use this?

Base64 encoding lets you **embed images directly into text-based files** — no separate image files, no broken links, no hosting required. Here's where that actually matters:

### You're building a web page and want self-contained HTML
Instead of `<img src="logo.png">` (which breaks the moment `logo.png` moves), you can embed the image directly:
```html
<img src="data:image/png;base64,iVBORw0KGgoAAAANS...">
```
The entire image lives inside the HTML file. Send it to anyone, open it anywhere — it just works.

### You're sending image data through an API
Most REST APIs and AI APIs (including Anthropic's) don't accept raw binary image uploads. They expect Base64-encoded strings in a JSON payload. This tool gives you that string instantly.

### You're writing CSS with background images baked in
Same idea — embed a texture, icon, or background directly in your stylesheet so it ships as a single `.css` file.

### You need to store an image in a database or config file
Databases store text, not binary blobs (well, not conveniently). Base64 lets you shove an image into a VARCHAR, a JSON config, a YAML file, or an environment variable.

### You're debugging or inspecting Base64 image data
Already have a Base64 string and want to sanity-check what image it came from? Working backwards is easy — paste it into a browser's address bar as a data URI.

---

## Features

- Converts any common image format: PNG, JPEG, GIF, BMP, WebP, SVG, ICO, TIFF
- Outputs plain Base64 or a ready-to-use **data URI** (`data:image/png;base64,...`)
- Optional **line wrapping** (e.g. 76-char MIME-standard lines)
- **CLI** for scripting and automation
- **GUI** for point-and-click use — no terminal required
- Clipboard copy support (with `pyperclip`)
- Zero dependencies beyond Python's standard library

---

## Files

| File | Purpose |
|------|---------|
| `img_to_base64.py` | Desktop GUI (tkinter) |

---

## Quickstart

### GUI
```bash
python img_to_base64.py
```
Browse or drag-and-drop an image, choose your options, hit **Convert**.

### CLI
```bash
# Print Base64 to terminal
python img_to_base64.py photo.png

# Save to a file
python img_to_base64.py photo.png -o photo.b64

# Output as a data URI (paste straight into HTML)
python img_to_base64.py photo.png --data-uri

# Wrap at 76 chars per line (standard for email/MIME)
python img_to_base64.py photo.png -w 76

# Copy to clipboard
python img_to_base64.py photo.png --copy
```

### As a module
```python
from img_to_base64 import image_to_base64
from pathlib import Path

uri = image_to_base64(Path("logo.png"), data_uri=True)
# → "data:image/png;base64,iVBORw0KGgo..."
```

---

## Optional dependencies

```bash
# Clipboard copy support
pip install pyperclip

# Drag-and-drop support in the GUI
pip install tkinterdnd2
```

Neither is required — the tool works fine without them.

---

## Requirements

- Python 3.8+
- `tkinter` (included with most Python installations)
