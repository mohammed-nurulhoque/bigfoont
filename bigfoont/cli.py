"""Command-line interface for bigfoont."""

import argparse
import sys

from .braille import text_to_braille, bdf_text_to_braille, get_preset, list_presets


def main():
    parser = argparse.ArgumentParser(
        prog='bigfoont',
        description='Render text as braille unicode art using bitmap fonts',
    )
    
    parser.add_argument('font', nargs='?', help='Path to font file (TTF/OTF or BDF)')
    parser.add_argument('text', nargs='*', help='Text to render')
    parser.add_argument('-s', '--size', 
                       help='Output size in braille chars WxH (e.g., 8x4, 4x2)')
    parser.add_argument('-f', '--font-size', type=int,
                       help='Font size in points (default: auto)')
    parser.add_argument('-t', '--threshold', type=int, default=128,
                       help='Binarization threshold 0-255 (default: 128)')
    parser.add_argument('--spacing', type=int, default=0,
                       help='Extra spacing between characters in pixels')
    parser.add_argument('--list-presets', action='store_true',
                       help='List available size presets')
    
    args = parser.parse_args()
    
    # List presets mode
    if args.list_presets:
        print("Available presets (braille WxH -> pixel WxH):")
        for (bw, bh), desc in list_presets().items():
            pw, ph = bw * 2, bh * 4
            print(f"  {bw}x{bh} -> {pw}x{ph} pixels: {desc}")
        return
    
    # Need font and text
    if not args.font:
        parser.print_help()
        sys.exit(1)
    
    text = ' '.join(args.text) if args.text else "Hello"
    
    # Check if font is a BDF file
    if args.font.lower().endswith('.bdf'):
        output = bdf_text_to_braille(text, args.font, spacing=args.spacing)
        print(output)
        return
    
    # TTF/OTF font - determine character size
    if args.size:
        try:
            w, h = args.size.lower().split('x')
            braille_w, braille_h = int(w), int(h)
        except ValueError:
            print(f"Invalid size format: {args.size}. Use WxH (e.g., 8x4)", file=sys.stderr)
            sys.exit(1)
        char_size = get_preset(braille_w, braille_h)
    else:
        # Default: 8x4 braille chars = 16x16 pixels
        char_size = (16, 16)
    
    output = text_to_braille(
        text,
        args.font,
        char_size=char_size,
        font_size=args.font_size,
        threshold=args.threshold,
    )
    print(output)


if __name__ == '__main__':
    main()
