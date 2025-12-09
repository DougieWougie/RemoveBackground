"""Core background removal functionality.

This module provides the main background removal functionality using the rembg library,
which leverages the U2-Net deep learning model for accurate background segmentation.
"""
from io import BytesIO
from pathlib import Path
from typing import Optional
from PIL import Image
from rembg import remove


def remove_background(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Remove background from an image and save as transparent PNG.

    This function uses the rembg library with the U2-Net model to perform accurate
    background segmentation and removal. The model automatically detects the main
    subject in the image and removes everything else, replacing it with transparency.

    Process flow:
    1. Validate input file exists and is readable
    2. Read image data into memory
    3. Process with rembg's U2-Net model to generate alpha mask
    4. Combine original image with alpha mask
    5. Save result as PNG with transparency

    Args:
        input_path: Path to the input image file. Supports common formats like
                   JPEG, PNG, BMP, TIFF, etc.
        output_path: Optional path to save the output image. If not provided,
                    saves to the same directory as input with "_nobg" suffix.
                    Extension is forced to .png regardless of specified extension.

    Returns:
        str: Absolute path to the output file that was created

    Raises:
        FileNotFoundError: If the input file doesn't exist at the specified path
        ValueError: If the input path is not a file (e.g., it's a directory) or
                   if the file cannot be processed as a valid image

    Examples:
        >>> # Basic usage with auto-generated output path
        >>> output = remove_background('photo.jpg')
        >>> print(output)
        '/path/to/photo_nobg.png'

        >>> # Custom output path
        >>> output = remove_background('photo.jpg', 'result.png')
        >>> print(output)
        '/path/to/result.png'

        >>> # Extension is automatically corrected to PNG
        >>> output = remove_background('photo.jpg', 'result.jpg')
        >>> print(output)
        '/path/to/result.png'
    """
    input_file = Path(input_path)

    # Validate input file exists
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Ensure input is a file, not a directory
    if not input_file.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")

    # Generate output path if not provided
    if output_path is None:
        output_path = str(input_file.parent / f"{input_file.stem}_nobg.png")
    else:
        # Ensure output has .png extension since transparency requires PNG
        output_file = Path(output_path)
        if output_file.suffix.lower() != '.png':
            output_path = str(output_file.with_suffix('.png'))

    try:
        # Read image data
        with open(input_path, 'rb') as input_file:
            input_data = input_file.read()

        # Remove background using rembg's U2-Net model
        # This returns image data with alpha channel for transparency
        output_data = remove(input_data)

        # Open the result and save as PNG
        output_image = Image.open(BytesIO(output_data))
        output_image.save(output_path, 'PNG')

        return output_path

    except Exception as e:
        raise ValueError(f"Failed to process image: {str(e)}")
