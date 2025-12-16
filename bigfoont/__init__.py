"""bigfoont - Render text as braille using bitmap fonts."""

__version__ = "0.1.0"

from .braille import text_to_braille, bdf_text_to_braille, BDFFont, get_preset, list_presets
