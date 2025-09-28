"""
Unit tests for image difference handler utility module.
Tests image comparison using pixelmatch functionality.
"""

import os
from unittest.mock import Mock, patch, MagicMock

import pytest
from PIL import Image

from utils.diff_handler import compare_images


class TestCompareImages:
    """Test cases for compare_images function."""

    @patch('utils.diff_handler.Image.open')
    @patch('utils.diff_handler.pixelmatch')
    def test_compare_images_success(self, mock_pixelmatch, mock_image_open):
        """Test successful image comparison."""
        # Setup mock images
        mock_img1 = Mock()
        mock_img1.size = (100, 100)
        mock_img2 = Mock()
        mock_img2.size = (100, 100)
        mock_image_open.side_effect = [mock_img1, mock_img2]
        
        # Setup mock diff image
        mock_diff_img = Mock()
        
        # Setup pixelmatch to return mismatch count
        mock_pixelmatch.return_value = 42
        
        # Test the function
        with patch('utils.diff_handler.Image.new') as mock_image_new:
            mock_image_new.return_value = mock_diff_img
            
            result = compare_images("image1.png", "image2.png", "diff.png")
        
        # Verify calls
        mock_image_open.assert_any_call("image1.png")
        mock_image_open.assert_any_call("image2.png")
        mock_image_new.assert_called_once_with("RGBA", (100, 100))
        mock_pixelmatch.assert_called_once_with(mock_img1, mock_img2, mock_diff_img, includeAA=True)
        mock_diff_img.save.assert_called_once_with("diff.png")
        
        # Verify result
        assert result == 42

    @patch('utils.diff_handler.Image.open')
    @patch('utils.diff_handler.pixelmatch')
    def test_compare_images_value_error(self, mock_pixelmatch, mock_image_open):
        """Test image comparison with ValueError from pixelmatch."""
        # Setup mock images
        mock_img1 = Mock()
        mock_img1.size = (100, 100)
        mock_img2 = Mock()
        mock_img2.size = (100, 100)
        mock_image_open.side_effect = [mock_img1, mock_img2]
        
        # Setup mock diff image
        mock_diff_img = Mock()
        
        # Setup pixelmatch to raise ValueError
        mock_pixelmatch.side_effect = ValueError("Size mismatch")
        
        # Test the function
        with patch('utils.diff_handler.Image.new') as mock_image_new:
            mock_image_new.return_value = mock_diff_img
            
            result = compare_images("image1.png", "image2.png", "diff.png")
        
        # Verify calls
        mock_image_open.assert_any_call("image1.png")
        mock_image_open.assert_any_call("image2.png")
        mock_image_new.assert_called_once_with("RGBA", (100, 100))
        mock_pixelmatch.assert_called_once_with(mock_img1, mock_img2, mock_diff_img, includeAA=True)
        
        # Should not save diff image on error
        mock_diff_img.save.assert_not_called()
        
        # Verify result (returns 1 on ValueError)
        assert result == 1

    @patch('utils.diff_handler.Image.open')
    def test_compare_images_file_open_error(self, mock_image_open):
        """Test image comparison when image files cannot be opened."""
        # Setup Image.open to raise FileNotFoundError
        mock_image_open.side_effect = FileNotFoundError("Image file not found")
        
        # Test should raise the exception
        with pytest.raises(FileNotFoundError):
            compare_images("nonexistent1.png", "nonexistent2.png", "diff.png")

    @patch('utils.diff_handler.Image.open')
    @patch('utils.diff_handler.pixelmatch')
    def test_compare_images_different_sizes(self, mock_pixelmatch, mock_image_open):
        """Test image comparison with different sized images."""
        # Setup mock images with different sizes
        mock_img1 = Mock()
        mock_img1.size = (100, 100)
        mock_img2 = Mock()
        mock_img2.size = (200, 150)
        mock_image_open.side_effect = [mock_img1, mock_img2]
        
        # Setup mock diff image
        mock_diff_img = Mock()
        
        # Setup pixelmatch to return mismatch count
        mock_pixelmatch.return_value = 15
        
        # Test the function
        with patch('utils.diff_handler.Image.new') as mock_image_new:
            mock_image_new.return_value = mock_diff_img
            
            result = compare_images("small.png", "large.png", "diff.png")
        
        # Verify that diff image is created with the size of the first image
        mock_image_new.assert_called_once_with("RGBA", (100, 100))
        mock_pixelmatch.assert_called_once_with(mock_img1, mock_img2, mock_diff_img, includeAA=True)
        mock_diff_img.save.assert_called_once_with("diff.png")
        
        # Verify result
        assert result == 15

    @patch('utils.diff_handler.Image.open')
    @patch('utils.diff_handler.pixelmatch')
    def test_compare_images_zero_mismatch(self, mock_pixelmatch, mock_image_open):
        """Test image comparison with identical images (zero mismatch)."""
        # Setup mock images
        mock_img1 = Mock()
        mock_img1.size = (100, 100)
        mock_img2 = Mock()
        mock_img2.size = (100, 100)
        mock_image_open.side_effect = [mock_img1, mock_img2]
        
        # Setup mock diff image
        mock_diff_img = Mock()
        
        # Setup pixelmatch to return zero mismatch
        mock_pixelmatch.return_value = 0
        
        # Test the function
        with patch('utils.diff_handler.Image.new') as mock_image_new:
            mock_image_new.return_value = mock_diff_img
            
            result = compare_images("identical1.png", "identical2.png", "diff.png")
        
        # Verify calls
        mock_pixelmatch.assert_called_once_with(mock_img1, mock_img2, mock_diff_img, includeAA=True)
        mock_diff_img.save.assert_called_once_with("diff.png")
        
        # Verify result
        assert result == 0

    @patch('utils.diff_handler.Image.open')
    @patch('utils.diff_handler.pixelmatch')
    @patch('utils.diff_handler.print')
    def test_compare_images_prints_on_value_error(self, mock_print, mock_pixelmatch, mock_image_open):
        """Test that ValueError message is printed."""
        # Setup mock images
        mock_img1 = Mock()
        mock_img1.size = (100, 100)
        mock_img2 = Mock()
        mock_img2.size = (100, 100)
        mock_image_open.side_effect = [mock_img1, mock_img2]
        
        # Setup mock diff image
        mock_diff_img = Mock()
        
        # Setup pixelmatch to raise ValueError
        mock_pixelmatch.side_effect = ValueError("Test error")
        
        # Test the function
        with patch('utils.diff_handler.Image.new') as mock_image_new:
            mock_image_new.return_value = mock_diff_img
            
            result = compare_images("image1.png", "image2.png", "diff.png")
        
        # Verify that "ValueError" was printed
        mock_print.assert_called_once_with("ValueError")
        
        # Verify result
        assert result == 1


class TestCompareImagesIntegration:
    """Integration-style tests for compare_images function behavior."""

    @patch('utils.diff_handler.Image.open')
    @patch('utils.diff_handler.pixelmatch')
    def test_function_signature_and_parameters(self, mock_pixelmatch, mock_image_open):
        """Test that the function accepts the expected parameters."""
        # Setup basic mocks
        mock_img = Mock()
        mock_img.size = (10, 10)
        mock_image_open.return_value = mock_img
        mock_pixelmatch.return_value = 0
        
        with patch('utils.diff_handler.Image.new') as mock_image_new:
            mock_image_new.return_value = Mock()
            
            # Test that function can be called with three string parameters
            result = compare_images("path1", "path2", "diff_path")
            
            # Should return an integer
            assert isinstance(result, int)

    @patch('utils.diff_handler.Image.open')
    @patch('utils.diff_handler.pixelmatch')
    def test_return_value_types(self, mock_pixelmatch, mock_image_open):
        """Test that function returns expected types in different scenarios."""
        # Setup basic mocks
        mock_img = Mock()
        mock_img.size = (10, 10)
        mock_image_open.return_value = mock_img
        
        with patch('utils.diff_handler.Image.new') as mock_image_new:
            mock_image_new.return_value = Mock()
            
            # Test normal case
            mock_pixelmatch.return_value = 42
            result = compare_images("img1", "img2", "diff")
            assert isinstance(result, int)
            assert result == 42
            
            # Test ValueError case
            mock_pixelmatch.side_effect = ValueError()
            result = compare_images("img1", "img2", "diff")
            assert isinstance(result, int)
            assert result == 1