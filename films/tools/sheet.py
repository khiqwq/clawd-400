"""python sheet.py out.png img1 img2 ... — 2-column contact sheet at half size, labelled."""
import os, sys
from PIL import Image, ImageDraw
out, files = sys.argv[1], sys.argv[2:]
ims = [Image.open(f).convert('RGB') for f in files]
w, h = ims[0].width // 2, ims[0].height // 2
cols = 2
rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (w * cols + 8 * (cols - 1), h * rows + 8 * (rows - 1)), (60, 60, 60))
d = ImageDraw.Draw(S)
for k, (im, f) in enumerate(zip(ims, files)):
    x, y = (k % cols) * (w + 8), (k // cols) * (h + 8)
    S.paste(im.resize((w, h)), (x, y))
    d.rectangle([x, y, x + 150, y + 22], fill=(0, 0, 0)); d.text((x + 4, y + 5), os.path.basename(f), fill=(255, 255, 0))
S.save(out)
