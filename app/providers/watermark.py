import io, os, requests
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from io import BytesIO

BRAND_GREEN = os.getenv("BRAND_GREEN", "#10B981")

def _load_logo_from_source(logo_path: Optional[str], logo_url: Optional[str]):
    if logo_path and os.path.exists(logo_path):
        return Image.open(logo_path).convert("RGBA")
    if logo_url:
        resp = requests.get(logo_url, timeout=20)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content)).convert("RGBA")
    return None

def apply_watermark(image: Image.Image, logo_path: Optional[str] = None, logo_url: Optional[str] = None, footer_text: Optional[str] = None) -> Image.Image:
    img = image.convert("RGBA")
    W, H = img.size
    draw = ImageDraw.Draw(img)
    footer_h = int(H * 0.10)
    footer_color = (255, 255, 255, 220)
    footer_y0 = H - footer_h
    draw.rectangle([0, footer_y0, W, H], fill=footer_color)
    footer_text = footer_text or os.getenv("BRAND_FOOTER", "ChatRefill • Top-up worldwide")

    try:
        font_path = os.getenv("BRAND_FONT_PATH", "")
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, int(footer_h * 0.45))
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    text_color = tuple(int(BRAND_GREEN.strip("#")[i:i+2], 16) for i in (0,2,4)) + (255,)
    tb = draw.textbbox((0,0), footer_text, font=font)
    text_x = int(W * 0.04)
    text_y = footer_y0 + (footer_h - (tb[3]-tb[1]))//2
    draw.text((text_x, text_y), footer_text, fill=text_color, font=font)

    logo = _load_logo_from_source(logo_path, logo_url)
    if logo:
        target_w = int(W * 0.18)
        logo = logo.resize((target_w, int(target_w * (logo.height / logo.width))), Image.LANCZOS)
        padding = int(W * 0.02)
        lx = W - logo.width - padding
        ly = min(H - logo.height - padding, footer_y0 + (footer_h - logo.height)//2)
        img.alpha_composite(logo, dest=(lx, ly))
    return img
