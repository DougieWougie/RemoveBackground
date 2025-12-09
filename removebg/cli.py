"""Command-line interface for background removal tool.

This module provides a user-friendly CLI for the background removal functionality,
with support for custom output paths and verbose logging.
"""
import argparse
import sys
from pathlib import Path
from removebg.core import remove_background


def main():
    """
    Main CLI entry point.

    Parses command-line arguments and invokes the background removal function.
    Handles errors gracefully and provides appropriate exit codes.

    Exit codes:
        0: Success
        1: File not found
        2: Invalid input (e.g., not a valid image)
        3: Unexpected error

    Returns:
        int: Exit code indicating success or type of failure
    """
    parser = argparse.ArgumentParser(
        description="Remove backgrounds from images and save as transparent PNG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.jpg
  %(prog)s input.jpg -o output.png
  %(prog)s photo.png --output result.png
  %(prog)s image.jpg -v
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
