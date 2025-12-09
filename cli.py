#!/usr/bin/env python3
"""Command-line interface for background removal tool."""
import argparse
import sys
from pathlib import Path
from removebg import remove_background


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Remove backgrounds from images and save as transparent PNG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.jpg
  %(prog)s input.jpg -o output.png
  %(prog)s photo.png --output result.png
        """
    )

    parser.add_argument(
        'input',
        help='Path to the input image file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Path to save the output image (default: <input>_nobg.png)',
        default=None
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print verbose output'
    )

    args = parser.parse_args()

    try:
        if args.verbose:
            print(f"Processing: {args.input}")

        output_path = remove_background(args.input, args.output)

        print(f"Background removed successfully!")
        print(f"Saved to: {output_path}")

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main())
