# RemoveBG - AI-Powered Background Removal Tool (Rust)

A high-performance Rust implementation of an AI-powered background removal tool using the U2-Net deep learning model. This tool leverages ONNX Runtime to accurately detect and remove backgrounds, producing clean transparent PNG images.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Line Interface](#command-line-interface)
  - [Rust API](#rust-api)
- [How It Works](#how-it-works)
- [Building from Source](#building-from-source)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Performance](#performance)

## Features

- **AI-Powered Segmentation**: Uses the U2-Net deep learning model via ONNX Runtime for accurate subject detection
- **High Performance**: Native Rust implementation for maximum speed and efficiency
- **Multiple Format Support**: Works with JPEG, PNG, BMP, TIFF, and other common image formats
- **Transparent Output**: Automatically generates PNG files with alpha channel transparency
- **Simple CLI**: Easy-to-use command-line interface with sensible defaults
- **Rust Library**: Clean API for integration into other Rust projects
- **Automatic Model Download**: Downloads the required AI model (~176MB) on first use
- **Comprehensive Error Handling**: Type-safe error handling with detailed error messages
- **Memory Safe**: Leverages Rust's memory safety guarantees

## Installation

### Prerequisites

Before building, ensure you have the required system libraries installed:

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install libssl-dev pkg-config
```

**Linux (Fedora/RHEL)**:
```bash
sudo dnf install openssl-devel pkg-config
```

**macOS**:
```bash
brew install openssl pkg-config
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions and troubleshooting.

### Option 1: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/removebg
cd removebg

# Build and install
cargo install --path .
```

After installation, you can use the `removebg` command directly:

```bash
removebg input.jpg
```

### Option 2: Build Only

```bash
# Build in release mode for optimal performance
cargo build --release

# Binary will be at target/release/removebg
./target/release/removebg input.jpg
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

### Rust API

You can also use RemoveBG as a library in your Rust projects:

#### Add to Cargo.toml

```toml
[dependencies]
removebg = { path = "../removebg" }
```

#### Example Usage

```rust
use removebg::remove_background;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Basic usage - auto-generates output filename
    let output_path = remove_background("photo.jpg", None)?;
    println!("Saved to: {}", output_path);
    // Output: Saved to: photo_nobg.png

    // Custom output path
    let output_path = remove_background("photo.jpg", Some("result.png"))?;
    println!("Saved to: {}", output_path);
    // Output: Saved to: result.png

    Ok(())
}
```

#### Error Handling

```rust
use removebg::{remove_background, RemoveBgError};

match remove_background("photo.jpg", None) {
    Ok(path) => println!("Success: {}", path),
    Err(RemoveBgError::FileNotFound(path)) => {
        eprintln!("File not found: {}", path);
    }
    Err(RemoveBgError::NotAFile(path)) => {
        eprintln!("Not a file: {}", path);
    }
    Err(e) => eprintln!("Error: {}", e),
}
```

## How It Works

### Overview

RemoveBG uses the **U2-Net** (U-square Net) deep learning architecture via ONNX Runtime for salient object detection. Here's the complete process:

1. **Input Validation**: Verifies the input file exists and is readable
2. **Image Loading**: Reads the image data using the `image` crate
3. **Preprocessing**: Resizes image to 320x320 and normalizes pixel values
4. **Model Inference**: Passes the image through the U2-Net ONNX model
5. **Mask Generation**: The model outputs a segmentation mask identifying the subject
6. **Mask Application**: Applies the alpha mask to create transparency
7. **Output Generation**: Saves the result as a PNG with transparency

### The U2-Net Model

U2-Net is a two-level nested U-structure architecture designed for salient object detection:

- **Architecture**: Encoder-decoder structure with nested U-blocks
- **Input**: RGB images (resized to 320x320)
- **Output**: Binary mask indicating foreground (subject) vs background
- **Model Size**: ~176 MB (downloaded automatically on first use)
- **Accuracy**: High precision in detecting subjects with complex boundaries (hair, fur, etc.)

### Processing Pipeline

```
Input Image (JPEG/PNG/etc.)
        ↓
    Validation
        ↓
    Load Image (image crate)
        ↓
    Preprocessing (resize + normalize)
        ↓
    ONNX Runtime Inference
    ├─ Convert to tensor (ndarray)
    ├─ Forward pass through U2-Net
    └─ Generate alpha mask (0-255)
        ↓
    Apply mask to create RGBA
        ↓
    Save as PNG
        ↓
    Output Image (Transparent PNG)
```

### Model Caching

On first run, the model is downloaded to:
- **Linux/Mac**: `~/.u2net/u2net.onnx`
- **Windows**: `%USERPROFILE%\.u2net\u2net.onnx`

Subsequent runs use the cached model, making processing much faster.

## Building from Source

### Prerequisites

- Rust 1.70 or higher
- Cargo (comes with Rust)
- ONNX Runtime (automatically linked via `ort` crate)

### Build Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/removebg
cd removebg

# Build in debug mode (faster compilation, slower runtime)
cargo build

# Build in release mode (optimized for performance)
cargo build --release

# Run tests
cargo test

# Run the CLI
cargo run -- input.jpg -o output.png

# Install globally
cargo install --path .
```

### Development

```bash
# Run with verbose output for debugging
cargo run -- input.jpg -v

# Check for issues without building
cargo check

# Format code
cargo fmt

# Lint code
cargo clippy
```

## Project Structure

```
removebg/
├── Cargo.toml              # Rust package configuration
├── src/
│   ├── lib.rs             # Library root, public API exports
│   ├── main.rs            # CLI binary entry point
│   ├── core.rs            # Core background removal logic
│   └── error.rs           # Error types and handling
│
├── README-RUST.md         # This file
└── README.md              # Original Python version README
```

### Module Responsibilities

#### `src/lib.rs`
- Library root module
- Re-exports public API (`remove_background`, error types)
- Package metadata and version

#### `src/core.rs`
- Core background removal implementation
- Model loading and initialization
- Image preprocessing and postprocessing
- ONNX Runtime inference
- Alpha mask generation and application

#### `src/error.rs`
- Custom error types using `thiserror`
- Type-safe error handling
- Detailed error messages for different failure scenarios

#### `src/main.rs`
- CLI implementation using `clap`
- Argument parsing
- User-friendly error messages
- Exit code handling

## Requirements

- **Rust**: 1.70 or higher
- **Operating System**: Linux, macOS, or Windows
- **Disk Space**: ~200MB for model and dependencies
- **RAM**: Minimum 2GB recommended
- **Internet**: Required for initial model download

## Performance

The Rust implementation offers significant performance improvements over Python:

### Benchmarks (approximate)

- **Startup Time**: ~50-100ms (vs ~500-1000ms for Python)
- **Memory Usage**: Lower baseline memory usage due to no interpreter overhead
- **Processing Speed**: Comparable to Python for inference (bottleneck is model, not language)
- **Binary Size**: ~10-20MB (release build with optimizations)

### Optimizations

The release build includes several optimizations:
- **LTO (Link-Time Optimization)**: Enabled for smaller binary and better performance
- **Single codegen unit**: Better optimization at the cost of longer compile time
- **Opt-level 3**: Maximum optimization level

## Dependencies

The project uses the following key Rust crates:

1. **ort** (2.0): ONNX Runtime bindings for running the U2-Net model
2. **image** (0.25): Image loading, manipulation, and saving
3. **ndarray** (0.16): N-dimensional array support for tensors
4. **clap** (4.5): Command-line argument parsing
5. **thiserror** (1.0): Ergonomic error type definitions
6. **reqwest** (0.12): HTTP client for model downloads
7. **dirs** (5.0): Platform-specific directory utilities

## Advantages over Python Version

1. **Performance**: Faster startup, lower memory overhead
2. **Type Safety**: Compile-time guarantees prevent many runtime errors
3. **Memory Safety**: No garbage collection pauses, no memory leaks
4. **Single Binary**: Easy deployment, no Python runtime needed
5. **Cross-compilation**: Build for different platforms easily
6. **Dependency Management**: Cargo handles all dependencies automatically

## Troubleshooting

### Model Download Issues

If the model fails to download:
```bash
# Check internet connection and manually download
wget https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx
mkdir -p ~/.u2net
mv u2net.onnx ~/.u2net/
```

### ONNX Runtime Issues

If you encounter ONNX Runtime errors:
```bash
# Make sure you have the necessary system libraries
# On Ubuntu/Debian:
sudo apt-get install libgomp1

# On macOS:
# ONNX Runtime should work out of the box

# On Windows:
# Visual C++ Redistributable may be required
```

### Build Errors

```bash
# Update Rust to the latest version
rustup update

# Clean build artifacts and rebuild
cargo clean
cargo build --release
```

## License

This project uses ONNX Runtime and the U2-Net model. Please refer to their respective licenses:

- [ONNX Runtime License](https://github.com/microsoft/onnxruntime/blob/main/LICENSE)
- [U2-Net License](https://github.com/xuebinqin/U-2-Net/blob/master/LICENSE)

## Contributing

Contributions are welcome! Areas for improvement:

- Support for additional models (U2-Net-Lite for faster processing)
- GPU acceleration via CUDA/TensorRT
- Batch processing mode
- Progress indicators for long operations
- WebAssembly support for browser usage
- Additional image format support (WebP, AVIF)

## Acknowledgments

- **U2-Net**: The deep learning model by Xuebin Qin et al.
- **ONNX Runtime**: For efficient cross-platform model execution
- **rembg**: Inspiration from the Python implementation by Daniel Gatis
- **image-rs**: Excellent Rust image processing library

## Contact

For issues, questions, or contributions, please open an issue on the project repository.
