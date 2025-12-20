//! Core background removal functionality.
//!
//! This module provides the main background removal functionality using the U2-Net
//! deep learning model via ONNX Runtime for accurate background segmentation.

use crate::error::{RemoveBgError, Result};
use image::{DynamicImage, ImageBuffer, Rgba, RgbaImage};
use ndarray::{Array, Array4};
use ort::{Session, SessionOutputs, Value};
use std::io::Read;
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

/// U2-Net model URL for download
const MODEL_URL: &str = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx";

/// Singleton session holder for the ONNX model
static MODEL_SESSION: OnceLock<Session> = OnceLock::new();

/// Initialize the ONNX Runtime environment and load the U2-Net model.
///
/// This function downloads the model if not present and initializes the ONNX session.
/// The model is cached in memory for subsequent uses.
fn get_or_init_model() -> Result<&'static Session> {
    MODEL_SESSION.get_or_try_init(|| {
        // Initialize ORT environment
        ort::init()
            .with_name("removebg")
            .commit()
            .map_err(|e| RemoveBgError::ModelInitError(e.to_string()))?;

        let model_path = get_model_path()?;

        // Download model if it doesn't exist
        if !model_path.exists() {
            download_model(&model_path)?;
        }

        // Load the ONNX model
        Session::builder()
            .map_err(|e| RemoveBgError::ModelInitError(e.to_string()))?
            .commit_from_file(&model_path)
            .map_err(|e| RemoveBgError::ModelInitError(e.to_string()))
    })
}

/// Get the path where the model should be stored.
fn get_model_path() -> Result<PathBuf> {
    let home = dirs::home_dir()
        .ok_or_else(|| RemoveBgError::ModelInitError("Could not determine home directory".into()))?;

    let model_dir = home.join(".u2net");
    std::fs::create_dir_all(&model_dir)?;

    Ok(model_dir.join("u2net.onnx"))
}

/// Download the U2-Net model from the official repository.
fn download_model(path: &Path) -> Result<()> {
    println!("Downloading U2-Net model (~176 MB)...");

    let response = ureq::get(MODEL_URL)
        .call()
        .map_err(|e| RemoveBgError::ModelInitError(format!("Failed to download model: {}", e)))?;

    let mut bytes = Vec::new();
    response.into_reader()
        .read_to_end(&mut bytes)
        .map_err(|e| RemoveBgError::ModelInitError(format!("Failed to read model data: {}", e)))?;

    std::fs::write(path, bytes)?;
    println!("Model downloaded successfully!");

    Ok(())
}

/// Preprocess image for U2-Net model inference.
///
/// Resizes image to 320x320 and normalizes pixel values.
fn preprocess_image(image: &DynamicImage) -> Array4<f32> {
    // Resize to 320x320 (U2-Net input size)
    let resized = image.resize_exact(320, 320, image::imageops::FilterType::Lanczos3);
    let rgb = resized.to_rgb8();

    // Convert to float array and normalize
    let mut input = Array::zeros((1, 3, 320, 320));

    for (y, row) in rgb.rows().enumerate() {
        for (x, pixel) in row.enumerate() {
            // Normalize to [0, 1] and convert to CHW format
            input[[0, 0, y, x]] = pixel[0] as f32 / 255.0;
            input[[0, 1, y, x]] = pixel[1] as f32 / 255.0;
            input[[0, 2, y, x]] = pixel[2] as f32 / 255.0;
        }
    }

    input
}

/// Run inference on the U2-Net model to generate an alpha mask.
fn generate_mask(image: &DynamicImage) -> Result<DynamicImage> {
    let session = get_or_init_model()?;

    // Preprocess the image
    let input_tensor = preprocess_image(image);

    // Run inference
    let outputs: SessionOutputs = session
        .run(ort::inputs!["input" => Value::from_array(input_tensor)
            .map_err(|e| RemoveBgError::ModelError(e.to_string()))?]?)
        .map_err(|e| RemoveBgError::ModelError(e.to_string()))?;

    // Extract the output tensor
    let output = outputs[0]
        .try_extract_tensor::<f32>()
        .map_err(|e| RemoveBgError::ModelError(e.to_string()))?;

    // Get dimensions
    let shape = output.shape();
    let height = shape[2];
    let width = shape[3];

    // Create mask image
    let mut mask = ImageBuffer::new(width as u32, height as u32);

    for y in 0..height {
        for x in 0..width {
            let value = output[[0, 0, y, x]];
            let pixel_value = (value.max(0.0).min(1.0) * 255.0) as u8;
            mask.put_pixel(x as u32, y as u32, image::Luma([pixel_value]));
        }
    }

    // Resize mask back to original image size
    let mask_resized = image::DynamicImage::ImageLuma8(mask)
        .resize_exact(image.width(), image.height(), image::imageops::FilterType::Lanczos3);

    Ok(mask_resized)
}

/// Apply alpha mask to image to create transparent background.
fn apply_alpha_mask(image: &DynamicImage, mask: &DynamicImage) -> RgbaImage {
    let rgb = image.to_rgba8();
    let mask_gray = mask.to_luma8();

    let mut output = RgbaImage::new(image.width(), image.height());

    for (x, y, pixel) in rgb.enumerate_pixels() {
        let alpha = mask_gray.get_pixel(x, y)[0];
        output.put_pixel(x, y, Rgba([pixel[0], pixel[1], pixel[2], alpha]));
    }

    output
}

/// Remove background from an image and save as transparent PNG.
///
/// This function uses the U2-Net model to perform accurate background segmentation
/// and removal. The model automatically detects the main subject in the image and
/// removes everything else, replacing it with transparency.
///
/// # Process Flow
/// 1. Validate input file exists and is readable
/// 2. Load image data
/// 3. Process with U2-Net model to generate alpha mask
/// 4. Apply mask to create transparency
/// 5. Save result as PNG
///
/// # Arguments
/// * `input_path` - Path to the input image file. Supports common formats like JPEG, PNG, BMP, TIFF, etc.
/// * `output_path` - Optional path to save the output image. If not provided, saves to the same
///   directory as input with "_nobg" suffix. Extension is forced to .png regardless of specified extension.
///
/// # Returns
/// The absolute path to the output file that was created.
///
/// # Errors
/// * `FileNotFound` - If the input file doesn't exist
/// * `NotAFile` - If the input path is not a file (e.g., it's a directory)
/// * `ImageError` - If the file cannot be processed as a valid image
/// * `ModelError` - If model inference fails
///
/// # Examples
/// ```no_run
/// use removebg::remove_background;
///
/// // Basic usage with auto-generated output path
/// let output = remove_background("photo.jpg", None)?;
/// println!("Saved to: {}", output);
///
/// // Custom output path
/// let output = remove_background("photo.jpg", Some("result.png"))?;
/// println!("Saved to: {}", output);
/// # Ok::<(), removebg::error::RemoveBgError>(())
/// ```
pub fn remove_background(input_path: &str, output_path: Option<&str>) -> Result<String> {
    let input_file = Path::new(input_path);

    // Validate input file exists
    if !input_file.exists() {
        return Err(RemoveBgError::FileNotFound(input_path.to_string()));
    }

    // Ensure input is a file, not a directory
    if !input_file.is_file() {
        return Err(RemoveBgError::NotAFile(input_path.to_string()));
    }

    // Generate output path if not provided
    let output_path = match output_path {
        Some(path) => {
            let p = Path::new(path);
            // Ensure .png extension
            if p.extension().and_then(|s| s.to_str()) != Some("png") {
                p.with_extension("png")
            } else {
                p.to_path_buf()
            }
        }
        None => {
            let stem = input_file.file_stem()
                .ok_or_else(|| RemoveBgError::ProcessingError("Invalid input filename".into()))?;
            let parent = input_file.parent().unwrap_or(Path::new("."));
            parent.join(format!("{}_nobg.png", stem.to_string_lossy()))
        }
    };

    // Load the input image
    let image = image::open(input_path)
        .map_err(|e| RemoveBgError::ProcessingError(format!("Failed to load image: {}", e)))?;

    // Generate alpha mask using U2-Net
    let mask = generate_mask(&image)?;

    // Apply mask to create transparent image
    let output_image = apply_alpha_mask(&image, &mask);

    // Save as PNG
    output_image.save(&output_path)?;

    Ok(output_path.to_string_lossy().to_string())
}
