#!/usr/bin/env python3
"""
Tests for M'Cheyne reader display methods.

This module tests the display functionality in the McCheyneReader class,
including the updated display_readings method and new display options.
"""

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from datetime import datetime

from src.mccheyne import McCheyneReader
from src.bible_models import BibleVerse, BibleHighlight, BiblePassage, HighlightPosition


class TestMcCheyneDisplay(unittest.TestCase):
    """Test display methods in McCheyneReader."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = McCheyneReader()
        
        # Create test verses
        self.verse1 = BibleVerse(
            book="John", chapter=3, verse=16,
            text="For God so loved the world that He gave His only begotten Son"
        )
        self.verse2 = BibleVerse(
            book="John", chapter=3, verse=17,
            text="For God did not send His Son into the world to condemn the world"
        )
        
        # Create test passage with highlights
        self.passage = BiblePassage(
            reference="John 3:16-17",
            version="NKJV",
            verses=[self.verse1, self.verse2]
        )
        
        # Add highlights
        highlight = BibleHighlight(
            start_position=HighlightPosition(verse_index=0, word_index=0),
            end_position=HighlightPosition(verse_index=0, word_index=4),
            highlight_count=50
        )
        self.passage.highlights = [highlight]
        
        # Test readings data
        self.structured_readings = {
            "Family": [self.passage],
            "Secret": [self.passage]
        }
        
        self.legacy_readings = {
            "Family": ["📖 John 3:16 (NKJV)\n──────────────────────────────────────────────────\nFor God so loved..."],
            "Secret": ["📖 John 3:17 (NKJV)\n──────────────────────────────────────────────────\nFor God did not send..."]
        }
    
    def capture_output(self, func, *args, **kwargs):
        """Capture stdout output from a function."""
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        try:
            func(*args, **kwargs)
            return captured_output.getvalue()
        finally:
            sys.stdout = old_stdout
    
    def test_display_readings_structured_default(self):
        """Test display_readings with structured BiblePassage objects."""
        output = self.capture_output(
            self.reader.display_readings, 
            self.structured_readings
        )
        
        # Should include header
        self.assertIn("M'CHEYNE BIBLE READING PLAN", output)
        self.assertIn(datetime.now().strftime('%B %d, %Y'), output)
        
        # Should include both categories
        self.assertIn("FAMILY READINGS:", output)
        self.assertIn("SECRET READINGS:", output)
        
        # Should include passage information
        self.assertIn("John 3:16-17", output)
        self.assertIn("NKJV", output)
        
        # Should include metadata
        self.assertIn("2 verses", output)
        self.assertIn("words", output)
        
        # Should include highlights by default
        self.assertIn("1 highlights", output)
    
    def test_display_readings_structured_detailed(self):
        """Test display_readings with detailed mode."""
        output = self.capture_output(
            self.reader.display_readings, 
            self.structured_readings,
            detailed=True
        )
        
        # Should show all verses in detailed mode
        self.assertIn("John 3:16:", output)
        self.assertIn("John 3:17:", output)
        
        # Should include full verse text
        self.assertIn("For God so loved the world", output)
        self.assertIn("For God did not send His Son", output)
    
    def test_display_readings_no_highlights(self):
        """Test display_readings with highlights disabled."""
        output = self.capture_output(
            self.reader.display_readings, 
            self.structured_readings,
            show_highlights=False
        )
        
        # Should not include highlight information
        self.assertNotIn("highlights", output)
        self.assertNotIn("✨", output)
    
    def test_display_readings_legacy_format(self):
        """Test display_readings with legacy string format."""
        output = self.capture_output(
            self.reader.display_readings, 
            self.legacy_readings
        )
        
        # Should handle legacy format
        self.assertIn("FAMILY READINGS:", output)
        self.assertIn("SECRET READINGS:", output)
        
        # Should display legacy strings
        self.assertIn("📖 John 3:16 (NKJV)", output)
        self.assertIn("For God so loved...", output)
    
    def test_display_readings_compact(self):
        """Test compact display mode."""
        output = self.capture_output(
            self.reader.display_readings_compact, 
            self.structured_readings
        )
        
        # Should include compact header
        self.assertIn("COMPACT", output)
        
        # Should show compact format
        self.assertIn("John 3:16-17", output)
        self.assertIn("2 verses", output)
        
        # Should be more concise than full display
        self.assertNotIn("For God so loved the world", output)
    
    def test_display_metadata_summary(self):
        """Test metadata summary display."""
        output = self.capture_output(
            self.reader.display_metadata_summary, 
            self.structured_readings
        )
        
        # Should include metadata header
        self.assertIn("READING PLAN METADATA", output)
        
        # Should show detailed metadata
        self.assertIn("Reference: John 3:16-17", output)
        self.assertIn("Version: NKJV", output)
        self.assertIn("Verses: 2", output)
        
        # Should include daily totals
        self.assertIn("DAILY TOTALS:", output)
        self.assertIn("Total verses: 4", output)  # 2 passages × 2 verses each
    
    def test_display_highlights_only(self):
        """Test highlights-only display mode."""
        output = self.capture_output(
            self.reader.display_highlights_only, 
            self.structured_readings
        )
        
        # Should include highlights header
        self.assertIn("HIGHLIGHTS SUMMARY", output)
        
        # Should show highlight information
        self.assertIn("John 3:16-17", output)
        self.assertIn("50 users", output)
        self.assertIn("✨", output)
    
    def test_display_highlights_only_no_highlights(self):
        """Test highlights display with no highlights."""
        # Create passage without highlights
        passage_no_highlights = BiblePassage(
            reference="John 3:16",
            version="NKJV",
            verses=[self.verse1]
        )
        
        readings_no_highlights = {
            "Family": [passage_no_highlights],
            "Secret": []
        }
        
        output = self.capture_output(
            self.reader.display_highlights_only, 
            readings_no_highlights
        )
        
        # Should indicate no highlights
        self.assertIn("No highlights found", output)
        self.assertIn("Popular highlights help identify", output)
    
    def test_display_empty_readings(self):
        """Test display with empty readings."""
        empty_readings = {"Family": [], "Secret": []}
        
        output = self.capture_output(
            self.reader.display_readings, 
            empty_readings
        )
        
        # Should handle empty readings gracefully
        self.assertIn("No readings found for this category", output)
    
    def test_display_mixed_formats(self):
        """Test display with mixed structured and legacy formats."""
        mixed_readings = {
            "Family": [self.passage],  # Structured
            "Secret": ["📖 Legacy format passage"]  # Legacy string
        }
        
        output = self.capture_output(
            self.reader.display_readings, 
            mixed_readings
        )
        
        # Should handle both formats
        self.assertIn("John 3:16-17", output)  # Structured
        self.assertIn("📖 Legacy format passage", output)  # Legacy


class TestMcCheyneMainFunction(unittest.TestCase):
    """Test the main function with various command line options."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = McCheyneReader()
        
        # Mock readings data
        self.mock_verse = BibleVerse(
            book="Genesis", chapter=1, verse=1,
            text="In the beginning God created the heavens and the earth"
        )
        self.mock_passage = BiblePassage(
            reference="Genesis 1:1",
            version="NKJV",
            verses=[self.mock_verse]
        )
        self.mock_structured_readings = {
            "Family": [self.mock_passage],
            "Secret": [self.mock_passage]
        }
        self.mock_legacy_readings = {
            "Family": ["📖 Genesis 1:1 (NKJV)\nIn the beginning..."],
            "Secret": ["📖 Genesis 1:2 (NKJV)\nThe earth was..."]
        }
    
    @patch('src.mccheyne.McCheyneReader')
    @patch('sys.argv')
    def test_main_default_mode(self, mock_argv, mock_reader_class):
        """Test main function with default settings."""
        mock_argv.__getitem__.return_value = []
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_todays_readings.return_value = self.mock_legacy_readings
        mock_reader.get_todays_date.return_value = (10, 16)
        
        from src.mccheyne import main
        
        with patch('builtins.print'):
            main()
        
        # Should use legacy format by default
        mock_reader.get_todays_readings.assert_called_once()
        mock_reader.display_readings.assert_called_once()
    
    @patch('src.mccheyne.McCheyneReader')
    @patch('sys.argv', ['script', '--structured'])
    def test_main_structured_mode(self, mock_reader_class):
        """Test main function with structured mode."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_todays_readings_structured.return_value = self.mock_structured_readings
        mock_reader.get_todays_date.return_value = (10, 16)
        
        from src.mccheyne import main
        
        with patch('builtins.print'):
            main()
        
        # Should use structured format
        mock_reader.get_todays_readings_structured.assert_called_once()
        mock_reader.display_readings.assert_called_once()
    
    @patch('src.mccheyne.McCheyneReader')
    @patch('sys.argv', ['script', '--compact'])
    def test_main_compact_mode(self, mock_reader_class):
        """Test main function with compact mode."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_todays_readings.return_value = self.mock_legacy_readings
        mock_reader.get_todays_date.return_value = (10, 16)
        
        from src.mccheyne import main
        
        with patch('builtins.print'):
            main()
        
        # Should use compact display
        mock_reader.display_readings_compact.assert_called_once()
    
    @patch('src.mccheyne.McCheyneReader')
    @patch('sys.argv', ['script', '--metadata'])
    def test_main_metadata_mode(self, mock_reader_class):
        """Test main function with metadata mode."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_todays_readings_structured.return_value = self.mock_structured_readings
        mock_reader.get_todays_date.return_value = (10, 16)
        
        from src.mccheyne import main
        
        with patch('builtins.print'):
            main()
        
        # Should force structured format and use metadata display
        mock_reader.get_todays_readings_structured.assert_called_once()
        mock_reader.display_metadata_summary.assert_called_once()
    
    @patch('src.mccheyne.McCheyneReader')
    @patch('sys.argv', ['script', '--highlights'])
    def test_main_highlights_mode(self, mock_reader_class):
        """Test main function with highlights mode."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_todays_readings_structured.return_value = self.mock_structured_readings
        mock_reader.get_todays_date.return_value = (10, 16)
        
        from src.mccheyne import main
        
        with patch('builtins.print'):
            main()
        
        # Should force structured format and use highlights display
        mock_reader.get_todays_readings_structured.assert_called_once()
        mock_reader.display_highlights_only.assert_called_once()
    
    @patch('src.mccheyne.McCheyneReader')
    @patch('sys.argv', ['script', '--detailed'])
    def test_main_detailed_mode(self, mock_reader_class):
        """Test main function with detailed mode."""
        mock_reader = MagicMock()
        mock_reader_class.return_value = mock_reader
        mock_reader.get_todays_readings_structured.return_value = self.mock_structured_readings
        mock_reader.get_todays_date.return_value = (10, 16)
        
        from src.mccheyne import main
        
        with patch('builtins.print'):
            main()
        
        # Should force structured format and use detailed display
        mock_reader.get_todays_readings_structured.assert_called_once()
        args, kwargs = mock_reader.display_readings.call_args
        self.assertTrue(kwargs.get('detailed', False))
    
    def test_print_usage_help(self):
        """Test usage help printing."""
        from src.mccheyne import print_usage_help
        
        output = StringIO()
        with patch('sys.stdout', output):
            print_usage_help()
        
        help_text = output.getvalue()
        
        # Should include usage information
        self.assertIn("USAGE OPTIONS:", help_text)
        self.assertIn("--structured", help_text)
        self.assertIn("--compact", help_text)
        self.assertIn("--detailed", help_text)
        self.assertIn("Examples:", help_text)


class TestDisplayErrorHandling(unittest.TestCase):
    """Test error handling in display methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = McCheyneReader()
    
    def test_display_with_invalid_highlight(self):
        """Test display handling of invalid highlights."""
        # Create passage with invalid highlight
        verse = BibleVerse(book="John", chapter=3, verse=16, text="Short text")
        passage = BiblePassage(reference="John 3:16", version="NKJV", verses=[verse])
        
        # Add highlight with invalid word index
        invalid_highlight = BibleHighlight(
            start_position=HighlightPosition(verse_index=0, word_index=10),  # Beyond verse length
            end_position=HighlightPosition(verse_index=0, word_index=15),
            highlight_count=1
        )
        passage.highlights = [invalid_highlight]
        
        readings = {"Family": [passage], "Secret": []}
        
        # Should handle gracefully without crashing
        try:
            output = StringIO()
            with patch('sys.stdout', output):
                self.reader.display_readings(readings)
            
            result = output.getvalue()
            # Should still display the passage
            self.assertIn("John 3:16", result)
            
        except Exception as e:
            self.fail(f"Display method should handle invalid highlights gracefully: {e}")
    
    def test_display_with_empty_verse_text(self):
        """Test display with edge case data."""
        # This should be caught by validation, but test display robustness
        try:
            verse = BibleVerse(book="Test", chapter=1, verse=1, text="A")  # Minimal valid text
            passage = BiblePassage(reference="Test 1:1", version="NKJV", verses=[verse])
            readings = {"Family": [passage], "Secret": []}
            
            output = StringIO()
            with patch('sys.stdout', output):
                self.reader.display_readings(readings)
            
            result = output.getvalue()
            self.assertIn("Test 1:1", result)
            
        except Exception as e:
            self.fail(f"Display should handle minimal data gracefully: {e}")


if __name__ == '__main__':
    unittest.main()