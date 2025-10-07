from hamcrest import (
    assert_that,
    equal_to,
)

"""
Real Unit Tests for Image Diff Handler
Testing actual image comparison logic.
"""

from unittest.mock import Mock, patch

import pytest

from utils.diff_handler import compare_images


class TestImageDiffHandler:
    """Test compare_images function."""

    @patch("utils.diff_handler.Image.open")
    @patch("utils.diff_handler.Image.new")
    @patch("utils.diff_handler.pixelmatch")
    def test_compare_images_success(
            self,
            mock_pixelmatch,
            mock_new,
            mock_open):
        """Test successful image comparison."""
        # Setup mocks
        mock_img1 = Mock()
        mock_img2 = Mock()
        mock_img_diff = Mock()
        mock_img1.size = (100, 100)

        mock_open.side_effect = [mock_img1, mock_img2]
        mock_new.return_value = mock_img_diff
        mock_pixelmatch.return_value = 42  # Number of mismatched pixels

        result = compare_images("img1.png", "img2.png", "diff.png")

        assert_that(result, equal_to(42))
        mock_open.assert_any_call("img1.png")
        mock_open.assert_any_call("img2.png")
        mock_new.assert_called_once_with("RGBA", (100, 100))
        mock_pixelmatch.assert_called_once_with(
            mock_img1, mock_img2, mock_img_diff, includeAA=True
        )
        mock_img_diff.save.assert_called_once_with("diff.png")

    @patch("utils.diff_handler.Image.open")
    @patch("utils.diff_handler.Image.new")
    @patch("utils.diff_handler.pixelmatch")
    def test_compare_images_value_error(
            self, mock_pixelmatch, mock_new, mock_open):
        """Test compare_images handles ValueError from pixelmatch."""
        # Setup mocks
        mock_img1 = Mock()
        mock_img2 = Mock()
        mock_img_diff = Mock()
        mock_img1.size = (100, 100)

        mock_open.side_effect = [mock_img1, mock_img2]
        mock_new.return_value = mock_img_diff
        mock_pixelmatch.side_effect = ValueError("Image size mismatch")

        with patch("builtins.print") as mock_print:
            result = compare_images("img1.png", "img2.png", "diff.png")

        # Function returns 1 on ValueError
        assert_that(result, equal_to(1))
        mock_print.assert_called_once_with("ValueError")
        # Save should NOT be called when ValueError occurs before save
        mock_img_diff.save.assert_not_called()

    @patch("utils.diff_handler.Image.open")
    def test_compare_images_file_not_found(self, mock_open):
        """Test compare_images handles file not found error."""
        mock_open.side_effect = FileNotFoundError("Image file not found")

        with pytest.raises(FileNotFoundError):
            compare_images("nonexistent1.png", "nonexistent2.png", "diff.png")

    @patch("utils.diff_handler.Image.open")
    @patch("utils.diff_handler.Image.new")
    @patch("utils.diff_handler.pixelmatch")
    def test_compare_images_save_error(
            self, mock_pixelmatch, mock_new, mock_open):
        """Test compare_images handles save error."""
        # Setup mocks
        mock_img1 = Mock()
        mock_img2 = Mock()
        mock_img_diff = Mock()
        mock_img1.size = (100, 100)

        mock_open.side_effect = [mock_img1, mock_img2]
        mock_new.return_value = mock_img_diff
        mock_pixelmatch.return_value = 0  # No mismatch but save fails
        mock_img_diff.save.side_effect = OSError("Cannot save image")

        with pytest.raises(OSError, match="Cannot save image"):
            compare_images("img1.png", "img2.png", "/invalid/path/diff.png")

    @patch("utils.diff_handler.Image.open")
    @patch("utils.diff_handler.Image.new")
    @patch("utils.diff_handler.pixelmatch")
    def test_compare_images_zero_mismatch(
            self, mock_pixelmatch, mock_new, mock_open):
        """Test compare_images when images are identical."""
        # Setup mocks
        mock_img1 = Mock()
        mock_img2 = Mock()
        mock_img_diff = Mock()
        mock_img1.size = (200, 150)

        mock_open.side_effect = [mock_img1, mock_img2]
        mock_new.return_value = mock_img_diff
        mock_pixelmatch.return_value = 0  # No differences

        result = compare_images(
            "identical1.png",
            "identical2.png",
            "no_diff.png")

        assert_that(result, equal_to(0))
        mock_new.assert_called_once_with("RGBA", (200, 150))

    @patch("utils.diff_handler.Image.open")
    @patch("utils.diff_handler.Image.new")
    @patch("utils.diff_handler.pixelmatch")
    def test_compare_images_large_mismatch(
            self, mock_pixelmatch, mock_new, mock_open):
        """Test compare_images with large number of mismatched pixels."""
        # Setup mocks
        mock_img1 = Mock()
        mock_img2 = Mock()
        mock_img_diff = Mock()
        mock_img1.size = (1000, 1000)

        mock_open.side_effect = [mock_img1, mock_img2]
        mock_new.return_value = mock_img_diff
        mock_pixelmatch.return_value = 50000  # Large difference

        result = compare_images(
            "very_different1.png", "very_different2.png", "big_diff.png"
        )

        assert_that(result, equal_to(50000))
        mock_new.assert_called_once_with("RGBA", (1000, 1000))

    @patch("utils.diff_handler.Image.open")
    def test_compare_images_invalid_image_format(self, mock_open):
        """Test compare_images handles invalid image format."""
        mock_open.side_effect = OSError("cannot identify image file")

        with pytest.raises(OSError, match="cannot identify image file"):
            compare_images("invalid.txt", "img2.png", "diff.png")
