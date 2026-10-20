# -*- coding: utf-8 -*-
# 生成道观风应用图标：朱红底 + 描金回纹边框 + 居中金色「签」字
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'icons')
os.makedirs(OUT, exist_ok=True)

GOLD = (232, 205, 116)
GOLD_D = (201, 162, 39)
RED_T = (164, 36, 36)      # 顶部亮红
RED_B = (87, 14, 14)       # 底部深红
TEXT = (252, 240, 200)     # 金字主体
TEXT_SH = (96, 44, 24)     # 字阴影

FONT_CANDIDATES = [
    r'C:\Windows\Fonts\simhei.ttf',
    r'C:\Windows\Fonts\msyhbd.ttc',
    r'C:\Windows\Fonts\msyh.ttc',
    r'C:\Windows\Fonts\simsun.ttc',
]


def vgrad(size):
    img = Image.new('RGB', (size, size))
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        c = tuple(int(RED_T[i] + (RED_B[i] - RED_T[i]) * t) for i in range(3))
        for x in range(size):
            px[x, y] = c
    return img


def load_font(size):
    for fp in FONT_CANDIDATES:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw(size, radius, glyph_scale=0.56, border_inset=0.05):
    img = vgrad(size)
    if radius > 0:
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
        img = Image.composite(img, Image.new('RGB', (size, size), (0, 0, 0)), mask)

    d = ImageDraw.Draw(img)
    bw = max(2, size // 40)
    inset = int(size * border_inset)
    r1 = max(1, radius - inset)
    r2 = max(1, radius - inset - bw * 2)

    # 双层描金边框（外金 + 内暗金，仿回纹勾边）
    if radius > 0:
        d.rounded_rectangle([inset, inset, size - 1 - inset, size - 1 - inset], radius=r1, outline=GOLD, width=bw)
        d.rounded_rectangle([inset + bw * 2, inset + bw * 2, size - 1 - inset - bw * 2, size - 1 - inset - bw * 2],
                            radius=r2, outline=GOLD_D, width=max(1, bw // 2))
    else:
        d.rectangle([inset, inset, size - 1 - inset, size - 1 - inset], outline=GOLD, width=bw)
        d.rectangle([inset + bw * 2, inset + bw * 2, size - 1 - inset - bw * 2, size - 1 - inset - bw * 2],
                    outline=GOLD_D, width=max(1, bw // 2))

    # 中央金字「签」
    font = load_font(int(size * glyph_scale))
    txt = '签'
    bbox = d.textbbox((0, 0), txt, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) / 2 - bbox[0]
    y = (size - h) / 2 - bbox[1]
    sh = max(1, size // 48)
    d.text((x, y + sh), txt, font=font, fill=TEXT_SH)   # 阴影
    d.text((x, y), txt, font=font, fill=TEXT)            # 主体
    return img


def main():
    draw(512, int(512 * 0.22)).save(os.path.join(OUT, 'icon-512.png'))
    draw(192, int(192 * 0.22)).save(os.path.join(OUT, 'icon-192.png'))
    draw(180, 0).save(os.path.join(OUT, 'apple-touch-icon.png'))                     # iOS 自行圆角，需满幅不透明
    draw(512, 0, glyph_scale=0.46, border_inset=0.10).save(os.path.join(OUT, 'icon-maskable-512.png'))  # 安全区更靠内
    print('icons ->', OUT)


if __name__ == '__main__':
    main()
