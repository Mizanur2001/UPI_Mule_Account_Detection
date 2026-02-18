"""Extract images from reference PDF for use in new PPT."""
import os, sys
try:
    import fitz
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF", "-q"])
    import fitz

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(BASE, "CSIC 1.0 PPT Prototype Developent Format for reference.pdf")
OUT = os.path.join(BASE, "docs", "ref_images")
os.makedirs(OUT, exist_ok=True)

doc = fitz.open(PDF)
# Page 1 has the title slide layout
page = doc[0]

# Extract all images
for idx, img_info in enumerate(page.get_images(full=True)):
    xref = img_info[0]
    base_img = doc.extract_image(xref)
    ext = base_img["ext"]
    data = base_img["image"]
    fname = os.path.join(OUT, f"ref_img_{idx}.{ext}")
    with open(fname, "wb") as f:
        f.write(data)
    print(f"Extracted: {fname} ({len(data)} bytes, {base_img['width']}x{base_img['height']})")

# Also render each page as PNG for visual reference
for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    fname = os.path.join(OUT, f"page_{i+1}.png")
    pix.save(fname)
    print(f"Rendered: {fname} ({os.path.getsize(fname)} bytes)")

print("\nDone!")
