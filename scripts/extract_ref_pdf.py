"""Extract styling info from reference PDF using PyMuPDF."""
import sys
try:
    import fitz
except ImportError:
    print("Installing PyMuPDF...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF", "-q"])
    import fitz

doc = fitz.open("CSIC 1.0 PPT Prototype Developent Format for reference.pdf")
for i, page in enumerate(doc):
    print(f"\n{'='*60}")
    print(f"PAGE {i+1}")
    print(f"{'='*60}")
    print(f"Size: {page.rect.width:.1f} x {page.rect.height:.1f}")
    
    # Images
    imgs = page.get_images()
    print(f"Images: {len(imgs)}")
    
    # Text with styling
    blocks = page.get_text("dict")["blocks"]
    for b in blocks:
        if b["type"] == 0:
            for line in b["lines"]:
                for span in line["spans"]:
                    t = span["text"].strip()
                    if t:
                        print(f'  "{t[:70]}" | Font={span["font"]} Size={span["size"]:.1f} Color=#{span["color"]:06x} Pos=({span["origin"][0]:.0f},{span["origin"][1]:.0f})')
        elif b["type"] == 1:
            x0, y0, x1, y1 = b["bbox"]
            print(f"  [IMAGE] at ({x0:.0f},{y0:.0f}) size {x1-x0:.0f}x{y1-y0:.0f}")

    # Extract drawings/shapes for color analysis
    drawings = page.get_drawings()
    if drawings:
        print(f"  Shapes/drawings: {len(drawings)}")
        for j, d in enumerate(drawings[:8]):
            fill = d.get("fill")
            stroke = d.get("color")
            rect = d.get("rect")
            if fill or stroke:
                print(f"    Shape {j}: fill={fill} stroke={stroke} rect={rect}")
