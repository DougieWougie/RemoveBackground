//! Error types for the removebg library.
//!
//! This module defines custom error types for background removal operations,
//! providing detailed error information for different failure scenarios.

use thiserror::Error;

/// Main error type for background removal operations.
#[derive(Error, Debug)]
pub enum RemoveBgError {
    /// Input file was not found at the specified path.
    #[error("Input file not found: {0}")]
    FileNotFound(String),

    /// Input path exists but is not a file (e.g., it's a directory).
    #[error("Input path is not a file: {0}")]
    NotAFile(String),

    /// Failed to read the input image file.
    #[error("Failed to read input file: {0}")]
    IoError(#[from] std::io::Error),

    /// Failed to decode or process the image.
    #[error("Failed to process image: {0}")]
    ImageError(#[from] image::ImageError),

    /// ONNX model execution failed.
    #[error("Model inference failed: {0}")]
    ModelError(String),

    /// Model download or initialization failed.
    #[error("Model initialization failed: {0}")]
    ModelInitError(String),

    /// Generic processing error.
    #[error("Failed to process image: {0}")]
    ProcessingError(String),
}

/// Result type alias for RemoveBG operations.
pub type Result<T> = std::result::Result<T, RemoveBgError>;
