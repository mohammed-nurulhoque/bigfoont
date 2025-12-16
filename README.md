# bigfoont

Render text as braille unicode art using bitmap fonts.

```
⣆⡆⣤⡄⢸⠀⢸⠀⡤⡄⠀⠀⣆⡆⡤⡄⡤⠄⢸⠀⡤⡇⢰⠀
⠃⠃⠓⠂⠘⠂⠘⠂⠓⠃⠀⠀⠛⠃⠓⠃⠃⠀⠘⠂⠓⠃⠐⠀
```

> **Note:** Output must be viewed in a **monospace font** with Unicode braille support for correct alignment.

## Installation

```bash
pip install -e .
```

## Usage

```bash
# BDF font (compact 2-line output)
bigfoont fonts/miniwi.bdf "Hello World!"

# TTF font (default 8x4 braille = 16x16 pixels)
bigfoont fonts/PressStart2P.ttf "Hello"

# Custom size
bigfoont -s 4x2 fonts/PressStart2P.ttf "Hi!"

# With spacing
bigfoont --spacing 1 fonts/miniwi.bdf "Hello"

# List presets
bigfoont --list-presets
```

### Size Presets

| Braille | Pixels | Description |
|---------|--------|-------------|
| 4x2 | 8x8 | Tiny |
| 4x4 | 8x16 | Compact |
| **8x4** | **16x16** | **Default** |
| 12x6 | 24x24 | Large |
| 16x8 | 32x32 | Extra large |

## How It Works

Text is rendered to a bitmap, then converted to braille by mapping 2×4 pixel blocks to Unicode braille patterns (U+2800-U+28FF):

```
⡇ = dot positions:    1 4     ● ·
                       2 5  →  ● ·
                       3 6     ● ·
                       7 8     · ·
```

## Python API

```python
from bigfoont import text_to_braille, bdf_text_to_braille

# TTF font
print(text_to_braille("Hello", "font.ttf", char_size=(16, 16)))

# BDF font
print(bdf_text_to_braille("Hello", "fonts/miniwi.bdf"))
```
