# -*- coding: utf-8 -*-
# 生成道观风「扫码求签」二维码卡片（盖章版 + 纯净版）
# 背景用「雕梁画栋」：红渐变 + 顶部藻井回纹 + 左右朱红柱 + 底部回纹 + 云纹
import os
from PIL import Image, ImageDraw, ImageFont
import qrcode

URL = 'https://sanqing-qian.netlify.app'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '二维码')
os.makedirs(OUT, exist_ok=True)

# 道观配色
DARK = (74, 13, 13)          # 深红码点
CREAM = (247, 236, 205)      # 米色底
GOLD = (201, 162, 39)
GOLD_LIGHT = (232, 205, 116)
GOLD_PALE = (216, 192, 138)
LACQUER = (46, 22, 9)        # 牌匾底
INK = (252, 240, 200)        # 说明文字
SEAL_RED = (164, 36, 36)     # 中央「签」印

FONT_CANDIDATES = [
    r'C:\Windows\Fonts\simhei.ttf',
    r'C:\Windows\Fonts\msyhbd.ttc',
    r'C:\Windows\Fonts\msyh.ttc',
    r'C:\Windows\Fonts\simsun.ttc',
]


def load_font(size):
    for fp in FONT_CANDIDATES:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def grad_at(stops, t):
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t0 <= t <= t1:
            return lerp(c0, c1, (t - t0) / (t1 - t0))
    return stops[-1][1]


def vgrad(w, h, stops):
    img = Image.new('RGB', (w, h))
    px = img.load()
    for y in range(h):
        c = grad_at(stops, y / (h - 1))
        for x in range(w):
            px[x, y] = c
    return img


# 红底渐变，对应网页 .temple 背景
BG_STOPS = [(0.0, (107, 18, 18)), (0.30, (140, 26, 26)), (0.70, (95, 15, 15)), (1.0, (61, 8, 8))]
# 朱红柱横向渐变（明暗交替）
PILLAR_STOPS = [(0.0, (61, 8, 8)), (0.35, (140, 26, 26)), (0.6, (164, 36, 36)), (1.0, (61, 8, 8))]


def draw_hui(od, x0, y0, x1, y1, cell=18, color=GOLD_LIGHT, alpha=150, w=2):
    """回纹：嵌套小方框网格"""
    c = color + (alpha,)
    for yy in range(y0, y1, cell):
        for xx in range(x0, x1, cell):
            od.rectangle([xx + 3, yy + 3, xx + cell - 3, yy + cell - 3], outline=c, width=w)
            od.rectangle([xx + 7, yy + 7, xx + cell - 7, yy + cell - 7], outline=c, width=1)


def draw_pillar(d, x0, y0, x1, y1, cap=16):
    for x in range(x0, x1):
        c = grad_at(PILLAR_STOPS, (x - x0) / max(1, x1 - x0 - 1))
        d.line([x, y0, x, y1], fill=c)
    d.rectangle([x0, y0, x1, y1], outline=GOLD_LIGHT, width=2)
    # 上下金色柱础
    d.rectangle([x0 - 3, y0 - cap, x1 + 3, y0], fill=GOLD_LIGHT)
    d.rectangle([x0 - 3, y1, x1 + 3, y1 + cap], fill=GOLD_LIGHT)


def cloud(od, x, y, s, color=GOLD_LIGHT, alpha=90, w=5):
    c = color + (alpha,)
    od.arc([x - 1.8 * s, y - 1.2 * s, x - 0.2 * s, y], 180, 360, fill=c, width=w)
    od.arc([x - 0.6 * s, y - 1.7 * s, x + 0.6 * s, y], 180, 360, fill=c, width=w)
    od.arc([x + 0.2 * s, y - 1.2 * s, x + 1.8 * s, y], 180, 360, fill=c, width=w)
    od.line([x - 1.8 * s, y, x + 1.8 * s, y], fill=c, width=w)


def temple_bg(w, h):
    """雕梁画栋背景：红渐变 + 顶部藻井回纹 + 左右朱红柱 + 底部回纹 + 四角云纹"""
    base = vgrad(w, h, BG_STOPS).convert('RGBA')
    d = ImageDraw.Draw(base)

    band = 92           # 顶部/底部回纹带高度
    strip = 8           # 金色分隔条
    # 顶部藻井回纹 + 金色条
    d.rectangle([0, 0, w - 1, band - 1], outline=GOLD_LIGHT, width=3)
    d.rectangle([0, band, w - 1, band + strip - 1], fill=GOLD_LIGHT)
    # 底部回纹 + 金色条
    d.rectangle([0, h - band - strip, w - 1, h - band - 1], fill=GOLD_LIGHT)
    d.rectangle([0, h - band, w - 1, h - 1], outline=GOLD_LIGHT, width=3)

    # 左右朱红柱（贯穿中部）
    pw = 44
    draw_pillar(d, 28, band + strip, 28 + pw, h - band - strip)
    draw_pillar(d, w - 28 - pw, band + strip, w - 28, h - band - strip)

    # 回纹图案（藻井带与底部带内）
    ov = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    draw_hui(od, 0, 0, w, band, cell=20)
    draw_hui(od, 0, h - band, w, h, cell=20)

    # 四角云纹 + 上下空档的淡云
    cloud(od, 120, 170, 30)
    cloud(od, w - 120, 170, 30)
    cloud(od, 120, h - 170, 30)
    cloud(od, w - 120, h - 170, 30)
    cloud(od, w // 2, 300, 34, alpha=50)
    cloud(od, w // 2, h - 300, 34, alpha=50)

    base = Image.alpha_composite(base, ov)
    return base.convert('RGB')


def make_qr_img(target_px):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=4, box_size=10)
    qr.add_data(URL)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    count = len(matrix)
    module = max(1, target_px // count)
    size = count * module
    img = Image.new('RGB', (size, size), CREAM)
    d = ImageDraw.Draw(img)
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val:
                d.rectangle([c * module, r * module, (c + 1) * module - 1, (r + 1) * module - 1], fill=DARK)
    return img


def stamp(img):
    s = img.size[0]
    d = ImageDraw.Draw(img)
    cx = cy = s // 2
    white_m = int(s * 0.26)
    seal_m = int(s * 0.17)
    d.rounded_rectangle([cx - white_m // 2, cy - white_m // 2, cx + white_m // 2, cy + white_m // 2],
                        radius=white_m // 6, fill=CREAM)
    d.rounded_rectangle([cx - seal_m // 2, cy - seal_m // 2, cx + seal_m // 2, cy + seal_m // 2],
                        radius=seal_m // 5, fill=SEAL_RED, outline=GOLD_LIGHT, width=max(2, seal_m // 20))
    font = load_font(int(seal_m * 0.62))
    d.text((cx, cy), '签', font=font, fill=(252, 240, 200), anchor='mm')


def compose(qr_img, path):
    W, H = 1080, 1500
    canvas = temple_bg(W, H)
    d = ImageDraw.Draw(canvas)

    # 金色外框（双线）
    d.rounded_rectangle([20, 20, W - 20, H - 20], radius=28, outline=GOLD, width=5)
    d.rounded_rectangle([32, 32, W - 32, H - 32], radius=20, outline=GOLD_LIGHT, width=2)

    # 顶部牌匾标题
    plaque_w, plaque_h = 780, 208
    px, py = (W - plaque_w) // 2, 120
    d.rounded_rectangle([px, py, px + plaque_w, py + plaque_h], radius=14, fill=LACQUER, outline=GOLD, width=3)
    d.rounded_rectangle([px + 8, py + 8, px + plaque_w - 8, py + plaque_h - 8], radius=10, outline=GOLD_LIGHT, width=1)
    d.text((W // 2, py + 84), '三弘道长求签', font=load_font(104), fill=GOLD_LIGHT, anchor='mm')
    d.text((W // 2, py + 156), '吕 祖 灵 签 · 扫 码 摇 签 问 卜', font=load_font(34), fill=GOLD_PALE, anchor='mm')

    # 米色纸卡（含二维码）
    qr_size = qr_img.size[0]
    pad = 58
    paper = qr_size + 2 * pad
    paper_x = (W - paper) // 2
    paper_y = 382
    d.rounded_rectangle([paper_x - 6, paper_y - 6, paper_x + paper + 6, paper_y + paper + 6],
                        radius=28, fill=GOLD, outline=None)
    d.rounded_rectangle([paper_x, paper_y, paper_x + paper, paper_y + paper], radius=22, fill=CREAM, outline=GOLD_LIGHT, width=2)
    canvas.paste(qr_img, (paper_x + pad, paper_y + pad))

    # 底部说明
    bottom = paper_y + paper
    d.text((W // 2, bottom + 52), '手机扫码，直接求签', font=load_font(46), fill=INK, anchor='mm')
    d.text((W // 2, bottom + 116), 'sanqing-qian.netlify.app', font=load_font(30), fill=GOLD_PALE, anchor='mm')

    canvas.save(path, dpi=(300, 300))
    print('已生成:', path, canvas.size)


qr = make_qr_img(672)

stamped = qr.copy()
stamp(stamped)
compose(stamped, os.path.join(OUT, '求签二维码.png'))

compose(qr.copy(), os.path.join(OUT, '求签二维码_纯净.png'))
