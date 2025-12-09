"""Unit tests for background removal functionality."""
import unittest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import removebg


class TestRemoveBackground(unittest.TestCase):
    """Test cases for remove_background function."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_dir_path = Path(self.test_dir)

        # Create a simple test image (100x100 red square)
        self.test_image_path = self.test_dir_path / "test_image.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.test_image_path, 'JPEG')

        # Create a PNG test image
        self.test_png_path = self.test_dir_path / "test_image.png"
        img.save(self.test_png_path, 'PNG')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_remove_background_default_output(self):
        """Test background removal with default output path."""
        output_path = removebg.remove_background(str(self.test_image_path))

        # Check that output file was created
        self.assertTrue(Path(output_path).exists())

        # Check that output is PNG
        self.assertTrue(output_path.endswith('.png'))

        # Check that output has expected name
        expected_name = "test_image_nobg.png"
        self.assertEqual(Path(output_path).name, expected_name)

        # Verify the output is a valid PNG image
        with Image.open(output_path) as img:
            self.assertEqual(img.format, 'PNG')
            # PNG with transparency should have RGBA mode
            self.assertIn(img.mode, ['RGBA', 'LA', 'PA'])

    def test_remove_background_custom_output(self):
        """Test background removal with custom output path."""
        output_path = self.test_dir_path / "custom_output.png"
        result = removebg.remove_background(
            str(self.test_image_path),
            str(output_path)
        )

        # Check that output file was created at specified location
        self.assertTrue(Path(result).exists())
        self.assertEqual(Path(result), output_path)

        # Verify the output is a valid PNG image
        with Image.open(result) as img:
            self.assertEqual(img.format, 'PNG')

    def test_remove_background_auto_png_extension(self):
        """Test that output is forced to .png extension."""
        output_path = self.test_dir_path / "output.jpg"
        result = removebg.remove_background(
            str(self.test_image_path),
            str(output_path)
        )

        # Check that extension was changed to .png
        self.assertTrue(result.endswith('.png'))
        self.assertEqual(Path(result).suffix, '.png')

    def test_remove_background_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        non_existent = self.test_dir_path / "does_not_exist.jpg"

        with self.assertRaises(FileNotFoundError) as context:
            removebg.remove_background(str(non_existent))

        self.assertIn("not found", str(context.exception).lower())

    def test_remove_background_directory_input(self):
        """Test that ValueError is raised when input is a directory."""
        with self.assertRaises(ValueError) as context:
            removebg.remove_background(str(self.test_dir_path))

        self.assertIn("not a file", str(context.exception).lower())

    def test_remove_background_invalid_image(self):
        """Test that ValueError is raised for invalid image file."""
        # Create a non-image file
        invalid_file = self.test_dir_path / "not_an_image.txt"
        invalid_file.write_text("This is not an image")

        with self.assertRaises(ValueError) as context:
            removebg.remove_background(str(invalid_file))

        self.assertIn("failed to process", str(context.exception).lower())

    def test_remove_background_png_input(self):
        """Test background removal with PNG input."""
        output_path = removebg.remove_background(str(self.test_png_path))

        # Check that output file was created
        self.assertTrue(Path(output_path).exists())

        # Verify the output is a valid PNG image
        with Image.open(output_path) as img:
            self.assertEqual(img.format, 'PNG')

    def test_output_has_transparency(self):
        """Test that output image has transparency channel."""
        output_path = removebg.remove_background(str(self.test_image_path))

        with Image.open(output_path) as img:
            # Image should have alpha channel for transparency
            self.assertIn('A', img.mode, "Output image should have alpha channel")


class TestCLI(unittest.TestCase):
    """Test cases for CLI interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_dir_path = Path(self.test_dir)

        # Create a simple test image
        self.test_image_path = self.test_dir_path / "test_image.jpg"
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(self.test_image_path, 'JPEG')

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_cli_import(self):
        """Test that CLI module can be imported."""
        import cli
        self.assertTrue(hasattr(cli, 'main'))


if __name__ == '__main__':
    unittest.main()
