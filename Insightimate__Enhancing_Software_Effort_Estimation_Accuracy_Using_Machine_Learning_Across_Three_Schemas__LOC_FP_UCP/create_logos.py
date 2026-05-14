#!/usr/bin/env python3
"""Create IEEE Access logo images matching the official template style."""
from PIL import Image, ImageDraw, ImageFont
import os, subprocess

WORKDIR = "/home/dtu/AI-Project/AI-Project/Insightimate__Enhancing_Software_Effort_Estimation_Accuracy_Using_Machine_Learning_Across_Three_Schemas__LOC_FP_UCP"

# IEEE Access brand colors
# PANTONE 3015 C = roughly RGB(0, 114, 188)
IEEE_BLUE = (0, 114, 188)
DARK_GREY = (51, 51, 51)
MID_GREY = (102, 102, 102)
WHITE = (255, 255, 255)
LIGHT_GREY = (180, 180, 180)

# DPI and dimensions
DPI = 300
# 10pc = 10 * 12pt = 120pt. At 300dpi: 120/72 * 300 = 500px wide
LOGO_W = 500
LOGO_H = 110  # logo height for standard logo

def get_font(size, bold=False):
    """Try to find a suitable font."""
    candidates = [
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold else
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf' if bold else
        '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return ImageFont.load_default()

def create_logo_with_tagline():
    """Create logo.png - IEEE Access logo WITH tagline (for title page header).
    Looks like:  [IEEE] [Access*]
                 Rapid Review | Open Access Journal
    """
    W, H = LOGO_W, LOGO_H
    img = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Fonts
    ieee_font = get_font(42, bold=True)
    access_font = get_font(42, bold=False)
    tm_font = get_font(16, bold=False)
    tagline_font = get_font(14, bold=False)
    bullet_font = get_font(16, bold=False)

    # Draw "IEEE" in blue bold
    draw.text((2, 5), "IEEE", font=ieee_font, fill=IEEE_BLUE)
    ieee_bbox = draw.textbbox((2, 5), "IEEE", font=ieee_font)
    ieee_w = ieee_bbox[2] - ieee_bbox[0]

    # Draw "Access" in blue (thinner weight after)
    x_access = ieee_w + 6
    draw.text((x_access, 5), "Access", font=access_font, fill=IEEE_BLUE)
    access_bbox = draw.textbbox((x_access, 5), "Access", font=access_font)
    access_right = access_bbox[2]

    # Draw superscript ® or * after Access  (use ® symbol)
    draw.text((access_right + 1, 4), "\u00ae", font=tm_font, fill=IEEE_BLUE)

    # Draw tagline below
    # Three bullet points separated by vertical bars
    tagline_y = 50
    tagline_parts = [
        ("\u25cf", bullet_font, DARK_GREY),  # bullet
        (" Rapid Review  ", tagline_font, DARK_GREY),
        ("|", tagline_font, LIGHT_GREY),
        ("  Peer-Reviewed  ", tagline_font, DARK_GREY),
        ("|", tagline_font, LIGHT_GREY),
        ("  Open Access Journal", tagline_font, DARK_GREY),
    ]
    tx = 2
    for text, font, color in tagline_parts:
        draw.text((tx, tagline_y), text, font=font, fill=color)
        bbox = draw.textbbox((tx, tagline_y), text, font=font)
        tx = bbox[2]

    return img

def create_logo_no_tagline():
    """Create notaglinelogo.png - IEEE Access logo WITHOUT tagline (for regular page headers)."""
    W, H = LOGO_W, 70
    img = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    ieee_font = get_font(42, bold=True)
    access_font = get_font(42, bold=False)
    tm_font = get_font(16, bold=False)

    # Draw "IEEE" in blue bold
    draw.text((2, 8), "IEEE", font=ieee_font, fill=IEEE_BLUE)
    ieee_bbox = draw.textbbox((2, 8), "IEEE", font=ieee_font)
    ieee_w = ieee_bbox[2] - ieee_bbox[0]

    # Draw "Access" in blue
    x_access = ieee_w + 6
    draw.text((x_access, 8), "Access", font=access_font, fill=IEEE_BLUE)
    access_bbox = draw.textbbox((x_access, 8), "Access", font=access_font)
    access_right = access_bbox[2]

    # Draw superscript ®
    draw.text((access_right + 1, 7), "\u00ae", font=tm_font, fill=IEEE_BLUE)

    return img

def create_bullet():
    """Create bullet.png - small blue filled circle (used before abstract)."""
    SIZE = 30
    img = Image.new('RGBA', (SIZE, SIZE), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    margin = 4
    draw.ellipse([margin, margin, SIZE-margin, SIZE-margin], fill=IEEE_BLUE, outline=IEEE_BLUE)
    return img

# Create and save all three images
logo = create_logo_with_tagline()
logo_rgb = Image.new('RGB', logo.size, WHITE)
logo_rgb.paste(logo, mask=logo.split()[3])
logo_rgb.save(os.path.join(WORKDIR, 'logo.png'), 'PNG', dpi=(DPI, DPI))
print(f"logo.png: {logo.size}")

notagline = create_logo_no_tagline()
notagline_rgb = Image.new('RGB', notagline.size, WHITE)
notagline_rgb.paste(notagline, mask=notagline.split()[3])
notagline_rgb.save(os.path.join(WORKDIR, 'notaglinelogo.png'), 'PNG', dpi=(DPI, DPI))
print(f"notaglinelogo.png: {notagline.size}")

bullet = create_bullet()
bullet_rgb = Image.new('RGB', bullet.size, WHITE)
bullet_rgb.paste(bullet, mask=bullet.split()[3])
bullet_rgb.save(os.path.join(WORKDIR, 'bullet.png'), 'PNG', dpi=(DPI, DPI))
print(f"bullet.png: {bullet.size}")

print("Done creating logo images.")
