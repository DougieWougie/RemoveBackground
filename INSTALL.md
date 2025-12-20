# Installation Guide for RemoveBG (Rust)

This guide provides detailed installation instructions for the Rust version of RemoveBG.

## Prerequisites

### System Requirements

- **Rust**: 1.70 or higher
- **Operating System**: Linux, macOS, or Windows
- **Disk Space**: ~200MB for model and dependencies
- **RAM**: Minimum 2GB recommended
- **Internet**: Required for initial model download

### Required System Libraries

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y libssl-dev pkg-config
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install openssl-devel pkg-config
```

#### Linux (Arch)

```bash
sudo pacman -S openssl pkg-config
```

#### macOS

OpenSSL should be available via Homebrew:

```bash
brew install openssl pkg-config
```

If you encounter issues, you may need to set the PKG_CONFIG_PATH:

```bash
export PKG_CONFIG_PATH="/opt/homebrew/opt/openssl@3/lib/pkgconfig"
```

#### Windows

On Windows, the dependencies should be automatically handled. If you encounter issues:

1. Install Visual Studio Build Tools
2. Install OpenSSL from: https://slproweb.com/products/Win32OpenSSL.html

## Installation Methods

### Method 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/removebg
cd removebg

# Build and install
cargo install --path .
```

The `removebg` binary will be installed to `~/.cargo/bin/` (ensure this is in your PATH).

### Method 2: Build for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/removebg
cd removebg

# Build in release mode
cargo build --release

# Binary will be at target/release/removebg
./target/release/removebg input.jpg
```

### Method 3: Build Without Installing

```bash
# Run directly with cargo
cargo run --release -- input.jpg -o output.png
```

## Troubleshooting

### OpenSSL Not Found

If you see an error like:

```
error: failed to run custom build command for `openssl-sys`
Could not find directory of OpenSSL installation
```

**Solution**: Install the OpenSSL development libraries for your system (see prerequisites above).

### ONNX Runtime Issues

The `ort` crate should automatically download ONNX Runtime. If you encounter issues:

1. Ensure you have a stable internet connection
2. Check that you have write permissions to cargo's cache directory
3. Try cleaning and rebuilding:

```bash
cargo clean
cargo build --release
```

### Model Download Fails

If the U2-Net model fails to download on first run:

```bash
# Manually download the model
mkdir -p ~/.u2net
wget https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx \
     -O ~/.u2net/u2net.onnx
```

Or using curl:

```bash
mkdir -p ~/.u2net
curl -L https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx \
     -o ~/.u2net/u2net.onnx
```

### Rust Version Too Old

```bash
# Update Rust to the latest version
rustup update stable
rustup default stable
```

### Permission Errors

If you get permission errors when installing:

```bash
# Make sure ~/.cargo/bin is in your PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Verification

After installation, verify it works:

```bash
# Check version
removebg --version

# Check help
removebg --help

# Test with an image (will download model on first run)
removebg test_image.jpg
```

## Uninstallation

```bash
# If installed with cargo install
cargo uninstall removebg

# Remove the model cache
rm -rf ~/.u2net
```

## Building for Distribution

### Static Binary (Linux)

For a fully static binary that doesn't require system OpenSSL:

```bash
# Add musl target
rustup target add x86_64-unknown-linux-musl

# Build static binary
cargo build --release --target x86_64-unknown-linux-musl
```

Note: This requires musl-tools:

```bash
sudo apt-get install musl-tools  # Ubuntu/Debian
```

### Cross-Compilation

To build for other platforms:

```bash
# Install cross
cargo install cross

# Build for Windows from Linux
cross build --release --target x86_64-pc-windows-gnu

# Build for macOS from Linux (requires macOS SDK)
cross build --release --target x86_64-apple-darwin
```

## Development Setup

For development work:

```bash
# Install development tools
cargo install cargo-watch cargo-edit

# Run tests
cargo test

# Run with auto-reload
cargo watch -x 'run -- input.jpg'

# Check code without building
cargo check

# Format code
cargo fmt

# Lint code
cargo clippy
```

## Performance Optimization

The release build includes these optimizations in Cargo.toml:

```toml
[profile.release]
opt-level = 3              # Maximum optimization
lto = true                 # Link-time optimization
codegen-units = 1          # Better optimization (slower compile)
```

To optimize for size instead:

```toml
[profile.release]
opt-level = 'z'            # Optimize for size
lto = true
codegen-units = 1
strip = true               # Remove debug symbols
```

## Docker Installation (Alternative)

If you prefer using Docker:

```dockerfile
FROM rust:1.75 as builder
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y libssl-dev pkg-config
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y libssl3 ca-certificates
COPY --from=builder /app/target/release/removebg /usr/local/bin/
ENTRYPOINT ["removebg"]
```

Build and run:

```bash
docker build -t removebg .
docker run -v $(pwd):/data removebg /data/input.jpg
```

## Need Help?

If you encounter issues not covered here:

1. Check the main README-RUST.md for general information
2. Open an issue on GitHub with:
   - Your OS and version
   - Rust version (`rustc --version`)
   - Full error message
   - Steps to reproduce
