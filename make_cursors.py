# -*- coding: utf-8 -*-
"""
狗爪子鼠标指针 V3 创意版 -> Windows .cur 生成器
思路：32px 下"原生形状里塞爪子"太挤太丑，改为爪子本体当指针：
  - 默认/链接 = 大号爪印直接做指针（链接加金色星光）
  - 文本 = 狗骨头！(创意替换 I-beam)
  - 其余 = 更粗、更高对比的重绘
16 倍超采样 + LANCZOS 缩小保证边缘平滑。
"""
import math
import os
import struct

from PIL import Image, ImageDraw, ImageFont

SIZE = 32
SS = 16
K = SS

ROOT = r"D:\PC_mouse\paw_cursor"
OUT = os.path.join(ROOT, "cursors")
BUILD = os.path.join(ROOT, "build")
os.makedirs(OUT, exist_ok=True)
os.makedirs(BUILD, exist_ok=True)

# V3 高对比色板（小尺寸下更清晰）
CREAM = (255, 246, 233)   # 奶油白
INK = (43, 29, 18)        # 深可可描边
PAD = (169, 113, 75)      # 肉垫棕
TOE = (196, 138, 95)      # 趾印浅棕
HL = (240, 214, 175)      # 高光
GOLD = (226, 168, 92)     # 金色点缀（链接星光）
SHADOW = (43, 29, 18, 70)


def rot(x, y, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return x * c - y * s, x * s + y * c


def bez(p0, p1, p2, p3, n=12):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
        y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
        pts.append((x, y))
    return pts


def heart_pts(cx, cy, sc, ang=0):
    segs = [((0, 7), (-9, 7), (-11, 2), (-8, -2)),
            ((-8, -2), (-5, -5), (-2, -4), (0, -1)),
            ((0, -1), (2, -4), (5, -5), (8, -2)),
            ((8, -2), (11, 2), (9, 7), (0, 7))]
    out = []
    for s in segs:
        for (x, y) in bez(*s, n=12):
            X, Y = rot(x * sc, y * sc, ang)
            out.append((cx + X, cy + Y))
    return out


def ell_pts(cx, cy, rx, ry, ang=0, n=32):
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        X, Y = rot(rx * math.cos(t), ry * math.sin(t), ang)
        out.append((cx + X, cy + Y))
    return out


def P(pts):
    return [(x * K, y * K) for x, y in pts]


def outline(d, pts, color, w):
    w = max(int(round(w * K)), 1)
    poly = P(pts)
    d.line(poly + [poly[0]], fill=color, width=w, joint="curve")


def line(d, x0, y0, x1, y1, color, w):
    d.line([x0 * K, y0 * K, x1 * K, y1 * K], fill=color,
           width=max(int(round(w * K)), 1), joint="curve")


def draw_paw(d, cx, cy, sc, ang=0, shadow=True, pad=PAD, toe=TOE):
    toes = [(-9, -6, -22), (-3.5, -9, -8), (3.5, -9, 8), (9, -6, 22)]
    if shadow:
        for tx, ty, _ in toes:
            dx, dy = rot(tx * sc, ty * sc, ang)
            d.polygon(P(ell_pts(cx + dx + 1.0, cy + dy + 1.3, 2.5 * sc, 3.5 * sc, ang)), fill=SHADOW)
        d.polygon(P(heart_pts(cx + 1.0, cy + 1.3, sc, ang)), fill=SHADOW)
    for tx, ty, ra in toes:
        dx, dy = rot(tx * sc, ty * sc, ang)
        pts = ell_pts(cx + dx, cy + dy, 2.5 * sc, 3.5 * sc, ang + ra)
        d.polygon(P(pts), fill=toe)
        outline(d, pts, INK, max(1.1 * sc, 0.7))
    hp = heart_pts(cx, cy, sc, ang)
    d.polygon(P(hp), fill=pad)
    outline(d, hp, INK, max(1.3 * sc, 0.8))
    for hx, hy, hr in [(-2.5, 2.5, 1.3), (-8, -4.5, 1.0), (8, -4.5, 1.0)]:
        if hr * sc < 0.5:
            continue
        dx, dy = rot(hx * sc, hy * sc, ang)
        d.polygon(P(ell_pts(cx + dx, cy + dy, hr * sc, hr * sc)), fill=HL)


def sparkle(d, x, y, s):
    q = s * 0.35
    pts = [(x, y - s), (x + q, y - q), (x + s, y), (x + q, y + q),
           (x, y + s), (x - q, y + q), (x - s, y), (x - q, y - q)]
    d.polygon(P(pts), fill=GOLD)
    outline(d, pts, INK, 0.5)


def new_img():
    img = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def write_cur(path, rgba, hotspot):
    w = h = SIZE
    hx, hy = hotspot
    xor = bytearray()
    and_rows = []
    for y in range(h - 1, -1, -1):
        row = bytearray()
        and_row = bytearray()
        acc = 0
        bits = 0
        for x in range(w):
            i = (y * w + x) * 4
            r, g, b, a = rgba[i], rgba[i + 1], rgba[i + 2], rgba[i + 3]
            row += bytes((b, g, r, a))
            acc = (acc << 1) | (1 if a == 0 else 0)
            bits += 1
            if bits == 8:
                and_row.append(acc)
                acc = 0
                bits = 0
        if bits:
            and_row.append(acc << (8 - bits))
        while len(and_row) % 4:
            and_row.append(0)
        and_rows.append(bytes(and_row))
        xor += row
    and_mask = b"".join(and_rows)
    dib = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0,
                      len(xor) + len(and_mask), 0, 0, 0, 0)
    data = dib + bytes(xor) + and_mask
    header = struct.pack("<HHH", 0, 2, 1)
    entry = struct.pack("<BBBBHHII", w, h, 0, 0, hx, hy, len(data), 22)
    with open(path, "wb") as f:
        f.write(header + entry + data)


def finish(img, name, hotspot):
    im = img.resize((SIZE, SIZE), Image.LANCZOS)
    im.save(os.path.join(BUILD, name + ".png"))
    write_cur(os.path.join(OUT, name + ".cur"), im.tobytes(), hotspot)
    return im


# ---------- 01 默认：大爪印直接当指针（热点=左上趾） ----------
def cur_arrow():
    img, d = new_img()
    draw_paw(d, 16.5, 16.5, 1.15, -14, shadow=True)
    return finish(img, "arrow", (5, 8))


# ---------- 02 链接：正爪印 + 金色星光 ----------
def cur_link():
    img, d = new_img()
    draw_paw(d, 16, 16.5, 1.15, 0, shadow=True)
    sparkle(d, 28.2, 4.4, 2.2)
    sparkle(d, 23.6, 2.4, 1.5)
    return finish(img, "link", (6, 9))


# ---------- 03 文本：狗骨头！ ----------
def cur_ibeam():
    img, d = new_img()
    lobes = [(12.4, 8.4), (19.6, 8.4), (12.4, 23.6), (19.6, 23.6)]
    # 阴影
    d.rounded_rectangle([13.9 * K, 8.2 * K, 19.9 * K, 26.2 * K],
                        radius=2 * K, fill=SHADOW)
    for (x, y) in lobes:
        d.polygon(P(ell_pts(x + 0.9, y + 1.2, 3.1, 3.1)), fill=SHADOW)
    # 骨干
    d.rounded_rectangle([13 * K, 7 * K, 19 * K, 25 * K], radius=2 * K,
                        fill=CREAM, outline=INK, width=int(1.5 * K))
    # 四个骨节
    for (x, y) in lobes:
        pts = ell_pts(x, y, 3.1, 3.1)
        d.polygon(P(pts), fill=CREAM)
        outline(d, pts, INK, 1.4)
    # 骨干上盖小肉垫
    hp = heart_pts(16, 16, 0.3)
    d.polygon(P(hp), fill=PAD)
    outline(d, hp, INK, 0.5)
    return finish(img, "ibeam", (16, 16))


# ---------- 04 忙碌：爪印 + 旋转弧 ----------
def cur_busy():
    img, d = new_img()
    draw_paw(d, 16, 16, 0.92, 0, shadow=True)
    bbox = [3.5 * K, 3.5 * K, 28.5 * K, 28.5 * K]
    d.arc(bbox, -90, 0, fill=TOE, width=int(3 * K))
    d.polygon(P([(25.7, 14.5), (31.3, 14.5), (28.5, 19.8)]), fill=PAD)
    d.arc(bbox, 90, 180, fill=TOE, width=int(3 * K))
    d.polygon(P([(0.7, 17.5), (6.3, 17.5), (3.5, 12.2)]), fill=PAD)
    return finish(img, "busy", (16, 16))


# ---------- 05 十字：粗十字 + 中心肉垫 ----------
def cur_cross():
    img, d = new_img()
    for x0, y0, x1, y1 in [(2, 16, 9, 16), (23, 16, 30, 16),
                           (16, 2, 16, 9), (16, 23, 16, 30)]:
        line(d, x0, y0, x1, y1, PAD, 3.2)
    hp = heart_pts(16, 16, 0.55)
    d.polygon(P(hp), fill=PAD)
    outline(d, hp, INK, 0.9)
    return finish(img, "cross", (16, 16))


# ---------- 06 移动 ----------
def cur_move():
    img, d = new_img()
    tris = [[(16, 1), (20, 7.5), (12, 7.5)], [(16, 31), (12, 24.5), (20, 24.5)],
            [(1, 16), (7.5, 12), (7.5, 20)], [(31, 16), (24.5, 12), (24.5, 20)]]
    for pts in tris:
        d.polygon(P(pts), fill=PAD)
        outline(d, pts, INK, 1.0)
    for x0, y0, x1, y1 in [(16, 7.5, 16, 10.5), (16, 21.5, 16, 24.5),
                           (7.5, 16, 10.5, 16), (21.5, 16, 24.5, 16)]:
        line(d, x0, y0, x1, y1, TOE, 2)
    draw_paw(d, 16, 16, 0.5, 0, shadow=False)
    return finish(img, "move", (16, 16))


# ---------- 07 水平调整 ----------
def cur_sizewe():
    img, d = new_img()
    line(d, 6, 16, 26, 16, PAD, 3.2)
    d.polygon(P([(1.5, 16), (7.5, 11.5), (7.5, 20.5)]), fill=PAD)
    outline(d, [(1.5, 16), (7.5, 11.5), (7.5, 20.5)], INK, 1.0)
    d.polygon(P([(30.5, 16), (24.5, 11.5), (24.5, 20.5)]), fill=PAD)
    outline(d, [(30.5, 16), (24.5, 11.5), (24.5, 20.5)], INK, 1.0)
    draw_paw(d, 16, 16, 0.5, 0, shadow=False)
    return finish(img, "sizewe", (16, 16))


# ---------- 08 垂直调整 ----------
def cur_sizens():
    img, d = new_img()
    line(d, 16, 6, 16, 26, PAD, 3.2)
    d.polygon(P([(16, 1.5), (11.5, 7.5), (20.5, 7.5)]), fill=PAD)
    outline(d, [(16, 1.5), (11.5, 7.5), (20.5, 7.5)], INK, 1.0)
    d.polygon(P([(16, 30.5), (11.5, 24.5), (20.5, 24.5)]), fill=PAD)
    outline(d, [(16, 30.5), (11.5, 24.5), (20.5, 24.5)], INK, 1.0)
    draw_paw(d, 16, 16, 0.5, 0, shadow=False)
    return finish(img, "sizens", (16, 16))


# ---------- 09 对角调整 ----------
def cur_sizenwse():
    img, d = new_img()
    line(d, 6, 26, 26, 6, PAD, 3.2)
    tr = [(30.5, 1.5), (21.7, 4.0), (28.0, 10.3)]
    bl = [(1.5, 30.5), (10.3, 28.0), (4.0, 21.7)]
    d.polygon(P(tr), fill=PAD)
    outline(d, tr, INK, 1.0)
    d.polygon(P(bl), fill=PAD)
    outline(d, bl, INK, 1.0)
    draw_paw(d, 16, 16, 0.5, -45, shadow=False)
    return finish(img, "sizenwse", (16, 16))


# ---------- 10 不可用 ----------
def cur_no():
    img, d = new_img()
    d.ellipse([2.5 * K, 2.5 * K, 29.5 * K, 29.5 * K], outline=PAD,
              width=int(3.2 * K))
    draw_paw(d, 16, 16, 0.6, 0, shadow=False)
    line(d, 6.5, 6.5, 25.5, 25.5, PAD, 3.2)
    return finish(img, "no", (16, 16))


# ---------- 11 帮助：爪印 + 问号徽章 ----------
def cur_help():
    img, d = new_img()
    draw_paw(d, 12.5, 17.5, 1.0, 0, shadow=True)
    d.ellipse([18.5 * K, 1 * K, 31 * K, 13.5 * K], fill=CREAM,
              outline=INK, width=int(1.5 * K))
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", int(9 * K))
        d.text((24.75 * K, 7.5 * K), "?", font=font, fill=INK, anchor="mm")
    except Exception:
        pass
    return finish(img, "help", (4, 8))


# ---------- 12 精确选择 ----------
def cur_precision():
    img, d = new_img()
    line(d, 16, 3, 16, 29, INK, 1.3)
    line(d, 3, 16, 29, 16, INK, 1.3)
    draw_paw(d, 16, 16, 0.45, 0, shadow=False)
    return finish(img, "precision", (16, 16))


def preview_sheet(images):
    names = [("arrow", "默认 · 爪印指针"), ("link", "链接 · 星光爪印"),
             ("ibeam", "文本 · 狗骨头"), ("busy", "忙碌 · 旋转"),
             ("cross", "十字"), ("move", "移动"),
             ("sizewe", "水平调整"), ("sizens", "垂直调整"),
             ("sizenwse", "对角调整"), ("no", "不可用"),
             ("help", "帮助 · 问号"), ("precision", "精确选择")]
    CW, CH, cols, rows = 150, 150, 4, 3
    sheet = Image.new("RGB", (cols * CW, rows * CH + 40), (251, 248, 243))
    dd = ImageDraw.Draw(sheet)
    try:
        ft = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
        f = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 15)
    except Exception:
        ft = f = ImageFont.load_default()
    dd.text((10, 6), "狗爪子鼠标指针 V3 创意版 · 32x32 成品（3 倍放大）",
            font=ft, fill=(59, 46, 34))
    for i, (n, label) in enumerate(names):
        r, c = divmod(i, cols)
        x, y = c * CW, r * CH + 40
        big = images[n].resize((96, 96), Image.NEAREST)
        sheet.paste(big, (x + (CW - 96) // 2, y + 4), big)
        dd.text((x + CW // 2, y + 112), label, font=f,
                fill=(107, 93, 79), anchor="mm")
    sheet.save(os.path.join(BUILD, "preview_v3.png"))


def main():
    imgs = {}
    for fn in [cur_arrow, cur_link, cur_ibeam, cur_busy, cur_cross, cur_move,
               cur_sizewe, cur_sizens, cur_sizenwse, cur_no, cur_help,
               cur_precision]:
        imgs[fn.__name__.replace("cur_", "")] = fn()
        print("OK", fn.__name__)
    preview_sheet(imgs)
    print("DONE ->", OUT)


if __name__ == "__main__":
    main()
