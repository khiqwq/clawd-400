"""Title art for the short: CLAWD in a 5x7 pixel font (Clawd orange) and 末班车 in a 12 px bitmap font."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tools'))
from pixfilm import canvas_image  # noqa: E402
from engine import Canvas  # noqa: E402

FONT = {
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'],
    'D': ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
}


def word(w, scale, out):
    c = Canvas(len(w) * 6 - 1, 7)
    for k, ch in enumerate(w):
        c.art([r.replace('#', 'O') for r in FONT[ch]], k * 6, 0)
    canvas_image(c).resize((c.w * scale, c.h * scale), Image.NEAREST).save(out)


def cjk(s, scale, out, rgb=(230, 226, 220)):
    font = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 12)
    im = Image.new('L', (int(font.getlength(s)) + 2, 14), 0)
    ImageDraw.Draw(im).text((0, 0), s, font=font, fill=255)
    rgba = Image.new('RGBA', im.size, (0, 0, 0, 0))
    rgba.putdata([rgb + (255,) if v > 110 else (0, 0, 0, 0) for v in im.getdata()])
    rgba = rgba.crop(rgba.getbbox())
    rgba.resize((rgba.width * scale, rgba.height * scale), Image.NEAREST).save(out)


if __name__ == '__main__':
    os.makedirs(os.path.join(HERE, 'assets'), exist_ok=True)
    word('CLAWD', 16, os.path.join(HERE, 'assets', 'title_en.png'))
    cjk('末班车', 8, os.path.join(HERE, 'assets', 'title_zh.png'))
    print('ok')
