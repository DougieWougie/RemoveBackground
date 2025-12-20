//! RemoveBG - AI-powered background removal tool
//!
//! This library provides functionality to remove backgrounds from images using
//! deep learning models. It uses the U2-Net model via ONNX Runtime for accurate
//! semantic segmentation, which can identify and isolate the main subject(s) in
//! an image while removing the background.
//!
//! # Features
//! - AI-powered background removal using U2-Net model
//! - Automatic model download on first use
//! - Support for multiple image formats (JPEG, PNG, BMP, TIFF, etc.)
//! - Transparent PNG output
//! - Simple API and CLI interface
//!
//! # Examples
//!
//! ```no_run
//! use removebg::remove_background;
//!
//! // Basic usage - auto-generates output filename
//! let output = remove_background("photo.jpg", None)?;
//! println!("Saved to: {}", output);
//!
//! // Custom output path
//! let output = remove_background("photo.jpg", Some("result.png"))?;
//! println!("Saved to: {}", output);
//! # Ok::<(), removebg::error::RemoveBgError>(())
//! ```

pub mod core;
pub mod error;

// Re-export main API
pub use core::remove_background;
pub use error::{RemoveBgError, Result};

/// Library version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
