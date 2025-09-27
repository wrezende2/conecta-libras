#!/usr/bin/env python3
"""
Conecta Libras banner generator

Creates a 1200x630 image with a blue→purple gradient background, centered text:
- Title: "Conecta Libras"
- Subtitle: "Comunicação inclusiva sem barreiras"

Places the WSS Studio Art logo in the bottom-right corner with margin.

Usage examples:
  python make_banner.py --logo path/to/wss_logo.png
  python make_banner.py --output banner_conecta_libras.png --logo wss.png --title "Conecta Libras" --subtitle "Comunicação inclusiva sem barreiras"

If no --logo is provided, the banner is created without a logo.
"""
from __future__ import annotations

import argparse
import math
import os
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import piexif
import shutil
from pathlib import Path


SIZE = (1200, 630)  # Facebook/LinkedIn/Twitter OG size
BG_GRADIENT_START = (34, 110, 255)  # default blue
BG_GRADIENT_END = (136, 58, 255)    # default purple
TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0, 90)
DEFAULT_MARGIN = 36


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def make_linear_gradient(size: Tuple[int, int], start: Tuple[int, int, int], end: Tuple[int, int, int], dark: bool = False) -> Image.Image:
    w, h = size
    # Diagonal gradient left->right with slight vertical variation
    base = Image.new("RGB", size, start)
    grad = Image.new("RGB", (w, 1))
    for x in range(w):
        t = x / max(1, (w - 1))
        grad.putpixel((x, 0), lerp_color(start, end, t))
    grad = grad.resize((w, h))
    # Add a subtle radial light to add depth
    vignette = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vignette)
    cx, cy = int(w * 0.2), int(h * 0.3)
    max_r = int(math.hypot(w, h) * 0.6)
    for r in range(max_r, 0, -8):
        alpha = int(255 * (1 - r / max_r) ** 2)
        vd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=alpha)
    vignette = vignette.filter(ImageFilter.GaussianBlur(60))

    grad = Image.composite(grad, base, Image.new("L", (w, h), 255))
    highlight = Image.new("RGB", (w, h), (255, 255, 255))
    grad = Image.composite(highlight, grad, vignette)
    if dark:
        # Darken overall and reduce highlight for dark theme
        overlay = Image.new("RGB", (w, h), (0, 0, 0))
        # 35% black overlay
        mask = Image.new("L", (w, h), int(255 * 0.35))
        grad = Image.composite(overlay, grad, mask)
    return grad


def _color_distance(c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def _is_grayish(c: Tuple[int, int, int], thresh: int = 12) -> bool:
    r, g, b = c
    return max(r, g, b) - min(r, g, b) < thresh


def derive_gradient_from_logo(logo_path: str) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]] | None:
    """Pick two distinct dominant colors from the logo to use as gradient endpoints.
    Returns (start, end) in RGB or None on failure.
    """
    if not logo_path or not os.path.isfile(logo_path):
        return None
    try:
        img = Image.open(logo_path).convert("RGBA")
    except Exception:
        return None

    # Remove transparent pixels and dark borders by compositing over white
    if img.mode == "RGBA":
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img)
    img = img.convert("RGB")
    # Reduce for speed and quantize to get a small palette
    thumb = img.copy()
    thumb.thumbnail((256, 256), Image.LANCZOS)
    quant = thumb.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
    palette = quant.getpalette()
    colors = []
    if palette:
        for i in range(0, min(8, quant.getcolors().__len__() if quant.getcolors() else 8)):
            r, g, b = palette[3 * i: 3 * i + 3]
            colors.append((r, g, b))
    # Fallback: sample pixels if palette failed
    if not colors:
        colors = [thumb.getpixel((int(thumb.width * x / 5), int(thumb.height * y / 5)))
                  for x in range(1, 5) for y in range(1, 5)]

    # Filter near-gray and very dark/very light extremes
    filtered = []
    for c in colors:
        if _is_grayish(c):
            continue
        if sum(c) < 80 or sum(c) > 720:  # remove almost black/white
            continue
        filtered.append(c)
    if not filtered:
        filtered = colors or [(34, 110, 255), (136, 58, 255)]

    # Choose the pair with max distance
    best_pair = None
    best_d = -1.0
    for i in range(len(filtered)):
        for j in range(i + 1, len(filtered)):
            d = _color_distance(filtered[i], filtered[j])
            if d > best_d:
                best_d = d
                best_pair = (filtered[i], filtered[j])
    if not best_pair:
        return None

    # Prefer cooler color as start (left) and warmer as end (right)
    def warmness(c):
        r, g, b = c
        return r - b
    c1, c2 = best_pair
    return (c1, c2) if warmness(c1) < warmness(c2) else (c2, c1)


def find_font(preferences: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    # Try user-specified paths first
    for p in preferences:
        if p and os.path.isfile(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass

    # Common system fonts
    candidates = [
        # Windows
        r"C:\\Windows\\Fonts\\SegoeUI-Semibold.ttf",
        r"C:\\Windows\\Fonts\\SegoeUI-Bold.ttf",
        r"C:\\Windows\\Fonts\\arialbd.ttf",
        r"C:\\Windows\\Fonts\\arial.ttf",
        # DejaVu (often available in many environments)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    # Fallback PIL bitmap font
    return ImageFont.load_default()


def draw_text_with_shadow(draw: ImageDraw.ImageDraw, position: Tuple[int, int], text: str, font: ImageFont.ImageFont, fill: Tuple[int, int, int], shadow_offset=(2, 2)):
    x, y = position
    # Shadow
    if isinstance(fill, tuple) and len(fill) == 3:
        shadow_fill = (0, 0, 0)
    else:
        shadow_fill = (0, 0, 0, 128)
    draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=shadow_fill)
    # Text
    draw.text((x, y), text, font=font, fill=fill)


def fit_text(draw: ImageDraw.ImageDraw, text: str, target_width: int, base_font_paths: list[str], max_size: int, min_size: int = 18) -> ImageFont.ImageFont:
    size = max_size
    while size >= min_size:
        font = find_font(base_font_paths, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        if width <= target_width:
            return font
        size -= 2
    return find_font(base_font_paths, min_size)


def place_logo(canvas: Image.Image, logo_path: Optional[str], margin: int, scale_width: Optional[int] = None, allow_upscale: bool = True) -> None:
    if not logo_path or not os.path.isfile(logo_path):
        return

    try:
        logo = Image.open(logo_path).convert("RGBA")
    except Exception:
        return

    # Scale logo
    if scale_width is None:
        scale_width = max(140, int(canvas.width * 0.16))  # responsive but bounded
    # Optionally avoid upscaling; when allow_upscale is False, clamp to original width
    if not allow_upscale:
        scale_width = min(scale_width, logo.width)
    w_percent = scale_width / logo.width
    new_size = (scale_width, max(1, int(logo.height * w_percent)))
    logo = logo.resize(new_size, Image.LANCZOS)

    # Slight drop shadow for the logo
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", logo.size, SHADOW_COLOR)
    shadow = Image.alpha_composite(shadow, sh)
    shadow = shadow.filter(ImageFilter.GaussianBlur(6))

    x = canvas.width - logo.width - margin
    y = canvas.height - logo.height - margin

    # Paste shadow first
    canvas.alpha_composite(shadow, dest=(x + 4, y + 4))
    # Then the logo
    canvas.alpha_composite(logo, dest=(x, y))


def build_banner(
    title: str,
    subtitle: str,
    logo_path: Optional[str] = None,
    output: str = "banner_conecta_libras.png",
    size: Tuple[int, int] = SIZE,
    margin: int = DEFAULT_MARGIN,
    title_font_paths: Optional[list[str]] = None,
    subtitle_font_paths: Optional[list[str]] = None,
    palette_from_logo: bool = True,
    jpg_output: Optional[str] = None,
    logo_scale: float = 1.0,
    subtitle_gap_factor: float = 1.35,
    allow_upscale_logo: bool = True,
    text_shift_ratio: float = 0.0,
    dark_theme: bool = False,
    exif_artist: Optional[str] = None,
    exif_copyright: Optional[str] = None,
    exif_description: Optional[str] = None,
):
    if title_font_paths is None:
        title_font_paths = []
    if subtitle_font_paths is None:
        subtitle_font_paths = []

    # Optional: derive gradient from logo palette
    grad_start, grad_end = BG_GRADIENT_START, BG_GRADIENT_END
    if palette_from_logo and logo_path:
        pair = derive_gradient_from_logo(logo_path)
        if pair:
            grad_start, grad_end = pair

    bg = make_linear_gradient(size, grad_start, grad_end, dark=dark_theme)
    canvas = bg.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # Compute text layout
    safe_w = size[0] - margin * 2

    # Title
    title_font = fit_text(draw, title, safe_w, [*title_font_paths], max_size=112, min_size=32)
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]

    # Subtitle smaller relative to title
    subtitle_font = fit_text(draw, subtitle, safe_w, [*subtitle_font_paths], max_size=int(max(28, 0.35 * (title_font.size))), min_size=18)
    sub_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_h = sub_bbox[3] - sub_bbox[1]

    total_h = title_h + int(sub_h * 1.6)
    start_y = (size[1] - total_h) // 2
    # Apply vertical shift (ratio of canvas height). Negative moves up.
    start_y = int(start_y + text_shift_ratio * size[1])

    title_x = (size[0] - title_w) // 2
    sub_x = (size[0] - sub_w) // 2

    # Draw with subtle shadow for legibility
    draw_text_with_shadow(draw, (title_x, start_y), title, title_font, TEXT_COLOR, shadow_offset=(2, 3))
    draw_text_with_shadow(draw, (sub_x, start_y + int(title_h * subtitle_gap_factor)), subtitle, subtitle_font, TEXT_COLOR, shadow_offset=(1, 2))

    # Place logo bottom-right
    # Base width heuristic (16% of canvas width), then apply user scale
    base_logo_w = int(size[0] * 0.16)
    # Allow much smaller logos; keep a tiny lower bound for safety
    scaled_logo_w = max(16, int(base_logo_w * max(0.02, logo_scale)))
    place_logo(canvas, logo_path, margin=margin, scale_width=scaled_logo_w, allow_upscale=allow_upscale_logo)

    canvas.save(output)
    # Export JPG if requested
    if jpg_output:
        rgb = canvas.convert("RGB")
        # Embed EXIF metadata if provided
        exif_bytes = None
        if any([exif_artist, exif_copyright, exif_description]):
            zeroth = {piexif.ImageIFD.Software: "make_banner.py"}
            if exif_artist:
                zeroth[piexif.ImageIFD.Artist] = exif_artist
            if exif_copyright:
                zeroth[piexif.ImageIFD.Copyright] = exif_copyright
            exif = {"0th": zeroth, "Exif": {}}
            if exif_description:
                exif["0th"][piexif.ImageIFD.ImageDescription] = exif_description
            exif_bytes = piexif.dump(exif)
        if exif_bytes is not None:
            rgb.save(jpg_output, format="JPEG", quality=92, optimize=True, subsampling=1, exif=exif_bytes)
        else:
            rgb.save(jpg_output, format="JPEG", quality=92, optimize=True, subsampling=1)
    return output


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate the Conecta Libras social banner (1200x630)")
    p.add_argument("--title", default="Conecta Libras", help="Main title text")
    p.add_argument("--subtitle", default="Comunicação inclusiva sem barreiras", help="Subtitle text")
    p.add_argument("--logo", default=None, help="Path to WSS Studio Art logo PNG/JPG (optional)")
    p.add_argument("--output", default="banner_conecta_libras.png", help="Output image path (PNG recommended)")
    p.add_argument("--jpg", dest="jpg", default=None, help="Optional JPG output path; if set, a JPEG will also be saved")
    p.add_argument("--width", type=int, default=SIZE[0], help="Banner width (default 1200)")
    p.add_argument("--height", type=int, default=SIZE[1], help="Banner height (default 630)")
    p.add_argument("--margin", type=int, default=DEFAULT_MARGIN, help="Outer margin in pixels")
    p.add_argument("--title-font", action="append", default=[], help="Custom title font path(s). You can pass multiple --title-font entries; first usable is picked.")
    p.add_argument("--subtitle-font", action="append", default=[], help="Custom subtitle font path(s). You can pass multiple --subtitle-font entries; first usable is picked.")
    p.add_argument("--no-palette-from-logo", action="store_true", help="Disable deriving gradient colors from logo palette")
    p.add_argument("--logo-scale", type=float, default=1.0, help="Scale multiplier for logo width relative to default (default=1.0). For 1/4 size use 0.25")
    p.add_argument("--subtitle-gap", type=float, default=1.35, help="Gap factor between title and subtitle relative to title height (default=1.35)")
    p.add_argument("--no-upscale-logo", action="store_true", help="Prevent the logo from being upscaled beyond its original size")
    p.add_argument("--text-shift", type=float, default=0.0, help="Vertical shift ratio for the text block (negative moves up). Example: -0.08")
    p.add_argument("--dark", dest="dark", action="store_true", help="Enable dark theme (darker gradient background)")
    # EXIF metadata for JPG
    p.add_argument("--exif-artist", default=None, help="EXIF Artist field for JPG outputs")
    p.add_argument("--exif-copyright", default=None, help="EXIF Copyright field for JPG outputs")
    p.add_argument("--exif-description", default=None, help="EXIF ImageDescription for JPG outputs")
    # Presets
    p.add_argument("--preset", choices=["all_social", "final_kit"], default=None, help="Generate a set of social sizes into an output directory")
    p.add_argument("--outdir", default=None, help="Output directory for preset exports (default: ./Exports_<timestamp>)")
    p.add_argument("--zip", dest="zip_outputs", action="store_true", help="Zip the preset outputs into a single archive")
    return p.parse_args()


def main():
    args = parse_args()
    # Determine default jpg path if user passed --jpg as empty or wants auto-name
    jpg_path = args.jpg
    if jpg_path is not None and jpg_path.strip() == "":
        base, _ = os.path.splitext(args.output)
        jpg_path = base + ".jpg"

    if args.preset == "all_social":
        # Define common social sizes (name, width, height)
        # (name, width, height, text_shift_ratio)
        sizes = [
            # Instagram
            ("IG_1080x1080", 1080, 1080, 0.0),
            ("IG_1080x1350", 1080, 1350, -0.02),
            ("IG_1080x1920", 1080, 1920, -0.08),  # Stories/Reels: subir um pouco
            # Facebook
            ("FacebookPost_1200x1200", 1200, 1200, 0.0),
            ("FacebookEvent_1200x628", 1200, 628, 0.0),
            ("FacebookCover_1640x924", 1640, 924, 0.0),
            # LinkedIn
            ("LinkedIn_1200x627", 1200, 627, 0.0),
            ("LinkedInCover_1584x396", 1584, 396, 0.0),
            # Twitter/X
            ("Twitter_1600x900", 1600, 900, 0.0),
            ("TwitterHeader_1500x500", 1500, 500, 0.0),
            # YouTube
            ("YouTube_1280x720", 1280, 720, 0.0),
            ("YouTubeBanner_2560x1440", 2560, 1440, 0.0),
            ("YouTubeSafe_2048x1152", 2048, 1152, 0.0),
            # Pinterest
            ("Pinterest_1000x1500", 1000, 1500, -0.02),
            ("PinterestSquare_1000x1000", 1000, 1000, 0.0),
            # TikTok / Stories generic
            ("TikTok_1080x1920", 1080, 1920, -0.08),
            # Open Graph generic
            ("OG_1200x630", 1200, 630, 0.0),
        ]
        outdir = Path(args.outdir) if args.outdir else Path.cwd() / f"Exports_{int(__import__('time').time())}"
        outdir.mkdir(parents=True, exist_ok=True)

        made = []
        for name, w, h, shift in sizes:
            png_path = outdir / f"{name}.png"
            jpg_path2 = outdir / f"{name}.jpg"
            outp = build_banner(
                title=args.title,
                subtitle=args.subtitle,
                logo_path=args.logo,
                output=str(png_path),
                size=(w, h),
                margin=args.margin,
                title_font_paths=args.title_font,
                subtitle_font_paths=args.subtitle_font,
                palette_from_logo=not args.__dict__.get("no_palette_from_logo", False),
                jpg_output=str(jpg_path2),
                logo_scale=args.logo_scale,
                subtitle_gap_factor=args.subtitle_gap,
                allow_upscale_logo=not args.__dict__.get("no_upscale_logo", False),
                text_shift_ratio=args.text_shift if args.text_shift else shift,
                dark_theme=args.dark,
                exif_artist=args.exif_artist,
                exif_copyright=args.exif_copyright,
                exif_description=args.exif_description,
            )
            print(f"Saved preset: {outp} and {jpg_path2}")
            made.append(str(png_path))
            made.append(str(jpg_path2))

        if args.zip_outputs:
            zip_base = outdir.with_suffix("")
            archive_path = shutil.make_archive(str(zip_base), "zip", root_dir=str(outdir))
            print(f"Zipped preset outputs to {archive_path}")
        return

    if args.preset == "final_kit":
        # Curated formats to ship as final kit
        sizes = [
            ("Master_4800x2520", 4800, 2520, 0.0),
            ("Master_2400x1260", 2400, 1260, 0.0),
            ("IG_1080x1350", 1080, 1350, -0.02),
            ("IG_1080x1080", 1080, 1080, 0.0),
            ("IG_1080x1920", 1080, 1920, -0.08),
            ("LinkedIn_1200x627", 1200, 627, 0.0),
            ("LinkedInCover_1584x396", 1584, 396, 0.0),
            ("Twitter_1600x900", 1600, 900, 0.0),
            ("TwitterHeader_1500x500", 1500, 500, 0.0),
            ("FacebookPost_1200x1200", 1200, 1200, 0.0),
            ("FacebookCover_1640x924", 1640, 924, 0.0),
            ("YouTube_1280x720", 1280, 720, 0.0),
            ("YouTubeBanner_2560x1440", 2560, 1440, 0.0),
            ("YouTubeSafe_2048x1152", 2048, 1152, 0.0),
            ("OG_1200x630", 1200, 630, 0.0),
        ]
        outdir = Path(args.outdir) if args.outdir else Path.cwd() / "Exports_Final"
        outdir.mkdir(parents=True, exist_ok=True)

        for name, w, h, shift in sizes:
            png_path = outdir / f"{name}.png"
            jpg_path2 = outdir / f"{name}.jpg"
            outp = build_banner(
                title=args.title,
                subtitle=args.subtitle,
                logo_path=args.logo,
                output=str(png_path),
                size=(w, h),
                margin=args.margin,
                title_font_paths=args.title_font,
                subtitle_font_paths=args.subtitle_font,
                palette_from_logo=not args.__dict__.get("no_palette_from_logo", False),
                jpg_output=str(jpg_path2),
                logo_scale=args.logo_scale,
                subtitle_gap_factor=args.subtitle_gap,
                allow_upscale_logo=not args.__dict__.get("no_upscale_logo", False),
                text_shift_ratio=args.text_shift if args.text_shift else shift,
            )
            print(f"Saved preset: {outp} and {jpg_path2}")

        if args.zip_outputs:
            archive_path = shutil.make_archive(str(outdir), "zip", root_dir=str(outdir))
            print(f"Zipped preset outputs to {archive_path}")
        return

    # Single image path (default behavior)
    out = build_banner(
        title=args.title,
        subtitle=args.subtitle,
        logo_path=args.logo,
        output=args.output,
        size=(args.width, args.height),
        margin=args.margin,
        title_font_paths=args.title_font,
        subtitle_font_paths=args.subtitle_font,
        palette_from_logo=not args.__dict__.get("no_palette_from_logo", False),
        jpg_output=jpg_path,
        logo_scale=args.logo_scale,
        subtitle_gap_factor=args.subtitle_gap,
        allow_upscale_logo=not args.__dict__.get("no_upscale_logo", False),
        text_shift_ratio=args.text_shift,
        dark_theme=args.dark,
        exif_artist=args.exif_artist,
        exif_copyright=args.exif_copyright,
        exif_description=args.exif_description,
    )
    print(f"Saved banner to {out}")
    if jpg_path:
        print(f"Saved JPG to {jpg_path}")


if __name__ == "__main__":
    main()
