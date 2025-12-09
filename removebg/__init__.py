"""RemoveBG - AI-powered background removal tool.

This package provides functionality to remove backgrounds from images using
deep learning models. It wraps the rembg library with a clean API and CLI.

The core functionality uses the U2-Net model for accurate semantic segmentation,
which can identify and isolate the main subject(s) in an image while removing
the background.

Main exports:
    remove_background: Main function to remove background from an image

Example:
    >>> from removebg import remove_background
    >>> output_path = remove_background('input.jpg', 'output.png')
    >>> print(f"Saved to: {output_path}")
"""

from removebg.core import remove_background

__version__ = '1.0.0'
__all__ = ['remove_background']
