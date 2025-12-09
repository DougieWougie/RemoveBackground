# RemoveBG - AI-Powered Background Removal Tool

A Python package and command-line tool for removing backgrounds from images using deep learning. This tool leverages the U2-Net neural network model to accurately detect and remove backgrounds, producing clean transparent PNG images.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Python API](#python-api)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Implementation Details](#implementation-details)
- [Testing](#testing)
- [Requirements](#requirements)
- [License](#license)

## Features

- **AI-Powered Segmentation**: Uses the U2-Net deep learning model for accurate subject detection
- **Multiple Format Support**: Works with JPEG, PNG, BMP, TIFF, and other common image formats
- **Transparent Output**: Automatically generates PNG files with alpha channel transparency
- **Simple CLI**: Easy-to-use command-line interface with sensible defaults
- **Python API**: Clean programmatic interface for integration into other projects
- **Automatic Model Download**: Downloads the required AI model (~170MB) on first use
- **Error Handling**: Comprehensive validation and error reporting
- **Well-Tested**: Extensive unit test coverage

## Installation

### Option 1: Install as Package

```bash
# Clone or download the project
cd removebg

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

After installation, you can use the `removebg` command directly:

```bash
removebg input.jpg
```

### Option 2: Install Dependencies Only

```bash
pip install -r requirements.txt
```

Then use the CLI script directly:

```bash
python -m removebg.cli input.jpg
```

## Quick Start

```bash
# Remove background from an image (creates input_nobg.png)
removebg photo.jpg

# Specify custom output path
removebg photo.jpg -o result.png

# Use verbose mode to see processing details
removebg photo.jpg -v
```

## Usage

### Command Line Interface

The CLI provides a simple interface for background removal:

```bash
# Basic usage - output saved as <input>_nobg.png
removebg input.jpg

# Custom output path
removebg input.jpg -o output.png
removebg input.jpg --output transparent.png

# Verbose mode for debugging
removebg input.jpg -v

# Help
removebg --help
```

**Exit Codes:**
- `0`: Success
- `1`: File not found
- `2`: Invalid input (not a valid image or directory provided)
- `3`: Unexpected error

### Python API

You can also use RemoveBG in your Python code:

```python
from removebg import remove_background

# Basic usage - auto-generates output filename
output_path = remove_background('photo.jpg')
print(f"Saved to: {output_path}")
# Output: Saved to: photo_nobg.png

# Custom output path
output_path = remove_background('photo.jpg', 'result.png')
print(f"Saved to: {output_path}")
# Output: Saved to: result.png

# Handle errors
try:
    output_path = remove_background('nonexistent.jpg')
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid image: {e}")
```

## How It Works

### Overview

RemoveBG uses the **rembg** library, which implements the **U2-Net** (U-square Net) deep learning architecture for salient object detection. Here's the complete process:

1. **Input Validation**: Verifies the input file exists and is readable
2. **Image Loading**: Reads the image data into memory
3. **Model Processing**: Passes the image through the U2-Net model
4. **Alpha Mask Generation**: The model outputs a segmentation mask identifying the subject
5. **Transparency Application**: Combines the original image with the alpha mask
6. **Output Generation**: Saves the result as a PNG with transparency

### The U2-Net Model

U2-Net is a two-level nested U-structure architecture designed for salient object detection:

- **Architecture**: Encoder-decoder structure with nested U-blocks
- **Input**: RGB images of various sizes (automatically resized)
- **Output**: Binary mask indicating foreground (subject) vs background
- **Model Size**: ~176 MB (downloaded automatically on first use)
- **Accuracy**: High precision in detecting subjects with complex boundaries (hair, fur, etc.)

### Processing Pipeline

```
Input Image (JPEG/PNG/etc.)
        ↓
    Validation
        ↓
    Load Image Data
        ↓
    U2-Net Model Processing
    ├─ Image Normalization
    ├─ Forward Pass Through Network
    └─ Generate Alpha Mask (0-255)
        ↓
    Combine RGB + Alpha
        ↓
    Save as PNG
        ↓
    Output Image (Transparent PNG)
```

### Model Caching

On first run, rembg downloads the U2-Net model to:
- **Linux/Mac**: `~/.u2net/`
- **Windows**: `%USERPROFILE%\.u2net\`

Subsequent runs use the cached model, making processing faster.

## Project Structure

```
removebg/
├── removebg/                  # Main package directory
│   ├── __init__.py           # Package initialization, exports main API
│   ├── core.py               # Core background removal logic
│   └── cli.py                # Command-line interface implementation
│
├── tests/                    # Test suite
│   ├── __init__.py          # Test package initialization
│   └── test_removebg.py     # Unit tests for all functionality
│
├── setup.py                  # Package installation configuration
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── .gitignore               # Git ignore patterns
```

### Module Responsibilities

#### `removebg/__init__.py`
- Package initialization
- Exports the main `remove_background` function
- Defines package version and metadata

#### `removebg/core.py`
- Contains the `remove_background()` function
- Handles input validation and path processing
- Manages image I/O operations
- Invokes the rembg library for background removal
- Implements comprehensive error handling

#### `removebg/cli.py`
- Implements command-line argument parsing
- Provides user-friendly error messages
- Handles exit codes for different error scenarios
- Supports verbose output mode

#### `tests/test_removebg.py`
- Unit tests for core functionality
- Tests for error conditions
- Integration tests for CLI
- Uses temporary files for safe testing

## Implementation Details

### Key Design Decisions

1. **PNG Output Only**: Transparency requires an alpha channel, which is best supported by PNG format. Even if users specify another extension, it's automatically converted to `.png`.

2. **Automatic Output Naming**: If no output path is provided, files are saved with `_nobg` suffix in the same directory as the input, preventing accidental overwrites.

3. **Path Handling**: Uses `pathlib.Path` for cross-platform compatibility and cleaner path manipulation.

4. **Error Types**: Different exceptions for different error conditions:
   - `FileNotFoundError`: Input file doesn't exist
   - `ValueError`: Invalid input (directory, corrupted image, etc.)

5. **Memory Efficiency**: Processes images in memory using BytesIO instead of saving temporary files.

### Dependencies

The project relies on three main dependencies:

1. **rembg** (>=2.0.50): Provides the U2-Net model and background removal algorithm
2. **Pillow** (>=10.0.0): Python Imaging Library for image I/O operations
3. **onnxruntime** (>=1.15.0): Runtime for executing the ONNX model (required by rembg)

### Performance Considerations

- **First Run**: Slower due to model download (~170MB, one-time)
- **Subsequent Runs**: Faster with cached model
- **Processing Time**: Depends on image size and hardware (typically 1-5 seconds)
- **Memory Usage**: Peak memory usage depends on image size (typically 200-500MB)
- **GPU Acceleration**: Automatically uses GPU if available (via onnxruntime)

## Testing

The project includes comprehensive unit tests covering:

- Default output path generation
- Custom output paths
- Automatic PNG extension handling
- File not found errors
- Invalid input handling (directories, non-image files)
- Multiple input formats (JPEG, PNG)
- Transparency verification

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=removebg --cov-report=html

# Or use unittest directly
python -m unittest tests/test_removebg.py
python -m unittest tests/test_removebg.py -v
```

### Test Coverage

The test suite provides:
- **Function Coverage**: All public functions tested
- **Error Path Coverage**: All error conditions verified
- **Edge Cases**: Directory inputs, missing files, invalid images
- **Format Support**: Multiple input/output format combinations

## Requirements

- **Python**: 3.7 or higher
- **Operating System**: Linux, macOS, or Windows
- **Disk Space**: ~200MB for model and dependencies
- **RAM**: Minimum 2GB recommended
- **Internet**: Required for initial model download

## Advanced Usage

### Batch Processing

Process multiple images programmatically:

```python
from removebg import remove_background
from pathlib import Path

input_dir = Path('input_images')
output_dir = Path('output_images')
output_dir.mkdir(exist_ok=True)

for image_file in input_dir.glob('*.jpg'):
    output_file = output_dir / f"{image_file.stem}_nobg.png"
    try:
        remove_background(str(image_file), str(output_file))
        print(f"Processed: {image_file.name}")
    except Exception as e:
        print(f"Failed to process {image_file.name}: {e}")
```

### Integration Example

Integrate into a web application:

```python
from flask import Flask, request, send_file
from removebg import remove_background
import tempfile

app = Flask(__name__)

@app.route('/remove-bg', methods=['POST'])
def remove_bg_endpoint():
    if 'image' not in request.files:
        return {'error': 'No image provided'}, 400

    image = request.files['image']

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_input:
        image.save(temp_input.name)

        # Process the image
        output_path = remove_background(temp_input.name)

        # Send the result
        return send_file(output_path, mimetype='image/png')
```

## Troubleshooting

### Model Download Issues

If the model fails to download:
```bash
# Manually download the model
python -c "from rembg import remove; remove(b'')"
```

### Memory Errors

For very large images:
- Resize the image before processing
- Close other applications to free up RAM
- Consider using a machine with more memory

### Import Errors

If you get import errors:
```bash
# Ensure package is installed
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## License

This project uses the rembg library, which is licensed under the MIT License. The U2-Net model is also available under an open-source license. Please refer to the respective projects for detailed license information:

- [rembg License](https://github.com/danielgatis/rembg/blob/main/LICENSE.txt)
- [U2-Net License](https://github.com/xuebinqin/U-2-Net/blob/master/LICENSE)

## Contributing

Contributions are welcome! Areas for improvement:

- Support for additional output formats (WebP with transparency)
- Batch processing CLI mode
- Progress indicators for large images
- Alternative model options for speed vs quality tradeoffs
- GUI interface

## Acknowledgments

- **rembg**: The excellent background removal library by Daniel Gatis
- **U2-Net**: The deep learning model by Xuebin Qin et al.
- **ONNX Runtime**: For efficient model execution

## Contact

For issues, questions, or contributions, please open an issue on the project repository.
