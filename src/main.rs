//! Command-line interface for the RemoveBG background removal tool.
//!
//! This binary provides a user-friendly CLI for removing backgrounds from images,
//! with support for custom output paths and verbose logging.

use clap::Parser;
use removebg::{remove_background, RemoveBgError};
use std::process;

/// AI-powered background removal tool using U2-Net deep learning model
#[derive(Parser, Debug)]
#[command(name = "removebg")]
#[command(author, version, about, long_about = None)]
#[command(after_help = "EXAMPLES:
    removebg input.jpg
    removebg input.jpg -o output.png
    removebg photo.png --output result.png
    removebg image.jpg -v")]
struct Args {
    /// Path to the input image file
    #[arg(value_name = "INPUT")]
    input: String,

    /// Path to save the output image (default: <input>_nobg.png)
    #[arg(short, long, value_name = "OUTPUT")]
    output: Option<String>,

    /// Print verbose output
    #[arg(short, long)]
    verbose: bool,
}

fn main() {
    let args = Args::parse();

    // Run the background removal and handle errors
    match run(args) {
        Ok(()) => process::exit(0),
        Err(code) => process::exit(code),
    }
}

/// Main execution logic with error handling.
///
/// Returns exit codes:
/// - 0: Success
/// - 1: File not found
/// - 2: Invalid input (not a valid image or is a directory)
/// - 3: Unexpected error
fn run(args: Args) -> Result<(), i32> {
    if args.verbose {
        println!("Processing: {}", args.input);
    }

    match remove_background(&args.input, args.output.as_deref()) {
        Ok(output_path) => {
            println!("Background removed successfully!");
            println!("Saved to: {}", output_path);
            Ok(())
        }
        Err(e) => {
            match &e {
                RemoveBgError::FileNotFound(_) => {
                    eprintln!("Error: {}", e);
                    Err(1)
                }
                RemoveBgError::NotAFile(_) => {
                    eprintln!("Error: {}", e);
                    Err(2)
                }
                RemoveBgError::ImageError(_) => {
                    eprintln!("Error: {}", e);
                    Err(2)
                }
                _ => {
                    eprintln!("Unexpected error: {}", e);
                    if args.verbose {
                        eprintln!("Error details: {:?}", e);
                    }
                    Err(3)
                }
            }
        }
    }
}
