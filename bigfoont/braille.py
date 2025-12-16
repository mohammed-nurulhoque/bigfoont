"""Render text as braille using bitmap fonts."""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import re

# Braille: 2x4 dots per character, encoded as bits in U+2800-U+28FF
# Dot positions: 1,2,3,7 (left column), 4,5,6,8 (right column)
BRAILLE_BASE = 0x2800
BRAILLE_DOTS = [
    (0, 0, 0x01), (0, 1, 0x02), (0, 2, 0x04), (0, 3, 0x40),
    (1, 0, 0x08), (1, 1, 0x10), (1, 2, 0x20), (1, 3, 0x80),
]

# Presets: (braille_w, braille_h) -> (pixel_w, pixel_h, description)
PRESETS = {
    (4, 2): (8, 8, "8x8 - tiny"),
    (4, 4): (8, 16, "8x16 - compact"),
    (8, 4): (16, 16, "16x16 - standard"),
    (8, 6): (16, 24, "16x24 - tall"),
    (12, 6): (24, 24, "24x24 - large"),
    (16, 8): (32, 32, "32x32 - extra large"),
}


def get_preset(braille_w: int, braille_h: int) -> tuple[int, int]:
    """Get pixel size for braille output size. Returns (width*2, height*4) if not in presets."""
    return PRESETS.get((braille_w, braille_h), (None,))[:2] or (braille_w * 2, braille_h * 4)


def list_presets() -> dict:
    """Return {(braille_w, braille_h): description}."""
    return {k: v[2] for k, v in PRESETS.items()}


def _bitmap_to_braille(bitmap: list[list[bool]]) -> str:
    """Convert 2D bool bitmap to braille string."""
    if not bitmap or not bitmap[0]:
        return ""
    height, width = len(bitmap), len(bitmap[0])
    lines = []
    for y in range(0, height, 4):
        line = []
        for x in range(0, width, 2):
            code = BRAILLE_BASE
            for dx, dy, bit in BRAILLE_DOTS:
                if y + dy < height and x + dx < width and bitmap[y + dy][x + dx]:
                    code |= bit
            line.append(chr(code))
        lines.append(''.join(line))
    return '\n'.join(lines)


def text_to_braille(
    text: str,
    font_path: str | Path,
    char_size: tuple[int, int] = (16, 16),
    font_size: int | None = None,
    threshold: int = 128,
) -> str:
    """Render text to braille using a TTF/OTF font."""
    if not text:
        return ""
    
    char_w, char_h = char_size
    font_size = font_size or max(char_w, char_h)
    
    try:
        font = ImageFont.truetype(str(font_path), size=font_size)
    except OSError:
        font = ImageFont.load_default()
    
    img = Image.new('L', (char_w * len(text), char_h), color=255)
    draw = ImageDraw.Draw(img)
    for i, char in enumerate(text):
        draw.text((i * char_w, 0), char, font=font, fill=0)
    
    # Convert to bitmap (dark pixels = True)
    bitmap = [[img.getpixel((x, y)) < threshold 
               for x in range(img.width)] 
              for y in range(img.height)]
    return _bitmap_to_braille(bitmap)


class BDFFont:
    """Simple BDF font parser."""
    
    def __init__(self, path: str | Path):
        self.glyphs: dict[int, tuple[int, int, list[list[bool]]]] = {}  # ord -> (w, h, bitmap)
        self.width = 4
        self.height = 8
        self._parse(Path(path))
    
    def _parse(self, path: Path):
        content = path.read_text()
        
        if m := re.search(r'FONTBOUNDINGBOX\s+(\d+)\s+(\d+)', content):
            self.width, self.height = int(m.group(1)), int(m.group(2))
        
        for m in re.finditer(
            r'ENCODING\s+(\d+)\s*\n.*?BBX\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(-?\d+)\s*\n.*?BITMAP\s*\n(.*?)\nENDCHAR',
            content, re.DOTALL
        ):
            enc, w, h = int(m.group(1)), int(m.group(2)), int(m.group(3))
            x_off, y_off = int(m.group(4)), int(m.group(5))
            bitmap = []
            for line in m.group(6).strip().split('\n'):
                if line.strip():
                    val = int(line.strip(), 16)
                    bitmap.append([bool(val & (1 << (7 - bit))) for bit in range(w)])
            self.glyphs[enc] = (w, h, x_off, y_off, bitmap)
    
    def render(self, text: str, spacing: int = 0) -> list[list[bool]]:
        """Render text to 2D bitmap."""
        # Calculate height from actual glyphs
        max_ascent = max_descent = 0
        for ch in text:
            if g := self.glyphs.get(ord(ch)):
                _, h, _, y_off, _ = g
                max_ascent = max(max_ascent, h + y_off)
                max_descent = max(max_descent, -y_off if y_off < 0 else 0)
        
        total_h = max_ascent + max_descent or self.height
        total_w = len(text) * self.width + max(0, len(text) - 1) * spacing
        bitmap = [[False] * total_w for _ in range(total_h)]
        
        x = 0
        for ch in text:
            if g := self.glyphs.get(ord(ch)):
                w, h, x_off, y_off, glyph = g
                y_start = max_ascent - h - y_off
                for row_i, row in enumerate(glyph):
                    y = y_start + row_i
                    if 0 <= y < total_h:
                        for col_i, pixel in enumerate(row):
                            px = x + x_off + col_i
                            if pixel and 0 <= px < total_w:
                                bitmap[y][px] = True
            x += self.width + spacing
        return bitmap


def bdf_text_to_braille(text: str, font_path: str | Path, spacing: int = 0) -> str:
    """Render text to braille using a BDF font."""
    return _bitmap_to_braille(BDFFont(font_path).render(text, spacing))
