"""Background removal module for removing backgrounds from images."""
import sys
from io import BytesIO
from pathlib import Path
from typing import Optional
from PIL import Image
from rembg import remove


def remove_background(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Remove background from an image and save as transparent PNG.

    Args:
        input_path: Path to the input image file
        output_path: Path to save the output image (optional)

    Returns:
        Path to the output file

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is not a valid image
    """
    input_file = Path(input_path)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_file.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    # Generate output path if not provided
    if output_path is None:
        output_path = str(input_file.parent / f"{input_file.stem}_nobg.png")
    else:
        # Ensure output has .png extension
        output_file = Path(output_path)
        if output_file.suffix.lower() != '.png':
            output_path = str(output_file.with_suffix('.png'))

    try:
        # Open and process the image
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()

        # Remove background
        output_data = remove(input_data)

        # Save the result
        output_image = Image.open(BytesIO(output_data))
        output_image.save(output_path, 'PNG')

        return output_path

    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python removebg.py <input_image> [output_image]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = remove_background(input_path, output_path)
        print(f"Background removed successfully! Saved to: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
