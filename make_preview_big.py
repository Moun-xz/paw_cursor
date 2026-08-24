# -*- coding: utf-8 -*-
"""从 build/ 下已生成的 32px 成品 PNG 生成一张大尺寸全套预览图。
用 NEAREST 放大 = 忠实还原真实像素效果（所见即所得）。"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = r"D:\PC_mouse\paw_cursor"
BUILD = os.path.join(ROOT, "build")

names = [
    ("arrow", "默认指针", "整只斜置狗爪 · 爪尖是热点"),
    ("link", "链接选择", "直立爪印 + 金色星光"),
    ("ibeam", "文本编辑", "狗骨头 · 骨杆上一颗肉垫"),
    ("busy", "忙碌加载", "爪印 + 环绕旋转弧"),
    ("cross", "十字选择", "粗十字 + 中心肉垫"),
    ("move", "窗口移动", "四向箭头 + 小爪印"),
    ("sizewe", "水平调整", "左右箭头 + 小爪印"),
    ("sizens", "垂直调整", "上下箭头 + 小爪印"),
    ("sizenwse", "对角调整", "斜向箭头 + 斜置小爪"),
    ("no", "不可用", "禁止圆环 + 肉垫"),
    ("help", "帮助", "爪印 + 问号徽章"),
    ("precision", "精确选择", "细十字 + 小爪印"),
]

COLS, ROWS = 3, 4
CW, CH = 340, 300
TITLE = 70
sheet = Image.new("RGB", (COLS * CW, ROWS * CH + TITLE), (250, 247, 242))
dd = ImageDraw.Draw(sheet)

try:
    ft = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 26)
    f1 = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 20)
    f2 = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
except Exception:
    try:
        ft = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
        f1 = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
        f2 = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
    except Exception:
        ft = f1 = f2 = ImageFont.load_default()

dd.text((24, 18), "狗爪子鼠标指针 V3 创意版 · 全套效果预览（32px 成品 5 倍放大）",
        font=ft, fill=(59, 46, 34))
dd.line([(24, 58), (COLS * CW - 24, 58)], fill=(226, 216, 202), width=2)

for i, (n, label, desc) in enumerate(names):
    r, c = divmod(i, COLS)
    x, y = c * CW, r * CH + TITLE
    # 卡片
    dd.rounded_rectangle([x + 14, y + 14, x + CW - 14, y + CH - 14],
                         radius=16, fill=(255, 255, 255),
                         outline=(226, 216, 202), width=2)
    # 棋盘格背景模拟透明（在光标本体区域）
    img = Image.open(os.path.join(BUILD, n + ".png")).convert("RGBA")
    big = img.resize((160, 160), Image.NEAREST)
    bx, by = x + (CW - 160) // 2, y + 22
    # 半透明白底 + 细网格提示透明区域
    grid = Image.new("RGB", (160, 160), (255, 255, 255))
    gd = ImageDraw.Draw(grid)
    for gy in range(0, 160, 20):
        for gx in range(0, 160, 20):
            if (gx // 20 + gy // 20) % 2 == 0:
                gd.rectangle([gx, gy, gx + 19, gy + 19],
                             fill=(244, 240, 233))
    grid.paste(big, (0, 0), big)
    sheet.paste(grid, (bx, by))
    # 名称 + 说明
    dd.text((x + CW // 2, y + 200), label, font=f1,
            fill=(59, 46, 34), anchor="mm")
    dd.text((x + CW // 2, y + 228), desc, font=f2,
            fill=(140, 124, 106), anchor="mm")
    # 序号
    dd.text((x + 30, y + 34), f"{i + 1:02d}", font=f2,
            fill=(200, 188, 170), anchor="mm")

out = os.path.join(BUILD, "preview_v3_big.png")
sheet.save(out)
print("saved", out, sheet.size)
