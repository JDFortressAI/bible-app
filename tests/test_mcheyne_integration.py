#!/usr/bin/env python3
"""
Integration tests for M'Cheyne fetcher with structured models.

Tests the integration between the M'Cheyne fetcher and the new BiblePassage models.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
from datetime import datetime
from src.mccheyne import McCheyneReader
from src.bible_models import BiblePassage, BibleVerse


class TestMcCheyneIntegration(unittest.TestCase):
    """Test M'Cheyne fetcher integration with structured models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = McCheyneReader()
        
        # Sample HTML content for mocking
        self.sample_html = """
        <html>
            <body>
                <div class="bible-text">
                    <p class="verse">1 In the beginning God created the heavens and the earth.</p>
                    <p class="verse">2 The earth was without form, and void; and darkness was on the face of the deep.</p>
                </div>
            </body>
        </html>
        """
        
        # Sample passage data
        self.sample_verses = [
            BibleVerse(book="Genesis", chapter=1, verse=1, text="In the beginning God created the heavens and the earth."),
            BibleVerse(book="Genesis", chapter=1, verse=2, text="The earth was without form, and void; and darkness was on the face of the deep.")
        ]
        
        self.sample_passage = BiblePassage(
            reference="Genesis 1:1-2",
            version="NKJV",
            verses=self.sample_verses,
            highlights=[],
            fetched_at=datetime.now()
        )
    
    def tearDown(self):
        """Clean up test files."""
        # Remove any test cache files
        test_files = [f for f in os.listdir('.') if f.startswith('mcheyne_') and 'test' in f]
        for file in test_files:
            try:
                os.remove(file)
            except OSError:
                pass
    
    @patch('src.mccheyne.requests.Session.get')
    def test_fetch_passage_text_structured(self, mock_get):
        """Test fetching passage text as structured BiblePassage object."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.content = self.sample_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test structured format
        result = self.reader.fetch_passage_text("Genesis 1:1-2", return_structured=True)
        
        # Verify it returns a BiblePassage object
        self.assertIsInstance(result, BiblePassage)
        self.assertEqual(result.reference, "Genesis 1:1-2")
        self.assertEqual(result.version, "NKJV")
        self.assertGreater(len(result.verses), 0)
        
        # Verify verse structure
        first_verse = result.verses[0]
        self.assertIsInstance(first_verse, BibleVerse)
        self.assertEqual(first_verse.book, "Genesis")
        self.assertEqual(first_verse.chapter, 1)
        self.assertGreater(len(first_verse.text), 0)
    
    @patch('src.mccheyne.requests.Session.get')
    def test_fetch_passage_text_legacy(self, mock_get):
        """Test fetching passage text as legacy string format."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.content = self.sample_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test legacy format (default)
        result = self.reader.fetch_passage_text("Genesis 1:1-2", return_structured=False)
        
        # Verify it returns a string
        self.assertIsInstance(result, str)
        self.assertIn("Genesis 1:1-2", result)
        self.assertIn("NKJV", result)
    
    def test_structured_cache_save_and_load(self):
        """Test saving and loading structured readings from cache."""
        month, day = 10, 16
        
        # Create test readings
        test_readings = {
            "Family": [self.sample_passage],
            "Secret": [self.sample_passage]
        }
        
        # Save to cache
        self.reader.save_structured_readings_to_cache(month, day, test_readings)
        
        # Verify cache file exists
        cache_file = self.reader.get_structured_cache_filename(month, day)
        self.assertTrue(os.path.exists(cache_file))
        
        # Load from cache
        loaded_readings = self.reader.load_cached_structured_readings(month, day)
        
        # Verify loaded data
        self.assertEqual(len(loaded_readings["Family"]), 1)
        self.assertEqual(len(loaded_readings["Secret"]), 1)
        
        family_passage = loaded_readings["Family"][0]
        self.assertIsInstance(family_passage, BiblePassage)
        self.assertEqual(family_passage.reference, "Genesis 1:1-2")
        self.assertEqual(family_passage.version, "NKJV")
        self.assertEqual(len(family_passage.verses), 2)
    
    def test_fallback_passage_creation(self):
        """Test creation of fallback passages when parsing fails."""
        reference = "John 3:16"
        raw_text = "For God so loved the world that He gave His only begotten Son..."
        
        fallback_passage = self.reader._create_fallback_passage(reference, raw_text)
        
        self.assertIsInstance(fallback_passage, BiblePassage)
        self.assertEqual(fallback_passage.reference, reference)
        self.assertEqual(fallback_passage.version, "NKJV")
        self.assertEqual(len(fallback_passage.verses), 1)
        
        verse = fallback_passage.verses[0]
        self.assertEqual(verse.book, "John")
        self.assertEqual(verse.chapter, 3)
        self.assertEqual(verse.verse, 16)
        self.assertIn("For God so loved", verse.text)
    
    def test_error_passage_creation(self):
        """Test creation of error passages when fetching fails."""
        reference = "Invalid Reference"
        error_msg = "Could not parse reference"
        
        error_passage = self.reader._create_error_passage(reference, error_msg)
        
        self.assertIsInstance(error_passage, BiblePassage)
        self.assertEqual(error_passage.reference, reference)
        self.assertEqual(len(error_passage.verses), 1)
        
        verse = error_passage.verses[0]
        self.assertIn("Error:", verse.text)
        self.assertIn(error_msg, verse.text)
    
    @patch('src.mccheyne.McCheyneReader.load_cached_structured_readings')
    @patch('src.mccheyne.McCheyneReader.fetch_reading_plan')
    @patch('src.mccheyne.McCheyneReader.fetch_passage_text')
    def test_get_todays_readings_structured(self, mock_fetch_passage, mock_fetch_plan, mock_load_cache):
        """Test getting today's readings as structured objects."""
        # Mock cache to return empty (force fresh fetch)
        mock_load_cache.return_value = {"Family": [], "Secret": []}
        
        # Mock the reading plan
        mock_fetch_plan.return_value = {
            "Family": ["Genesis 1:1-2", "Matthew 1:1"],
            "Secret": ["Psalm 1", "Romans 1:1"]
        }
        
        # Mock passage fetching to return structured objects
        mock_fetch_passage.side_effect = [
            self.sample_passage,  # Genesis 1:1-2
            BiblePassage(reference="Matthew 1:1", version="NKJV", verses=[
                BibleVerse(book="Matthew", chapter=1, verse=1, text="The book of the genealogy of Jesus Christ...")
            ]),
            BiblePassage(reference="Psalm 1", version="NKJV", verses=[
                BibleVerse(book="Psalms", chapter=1, verse=1, text="Blessed is the man who walks not...")
            ]),
            BiblePassage(reference="Romans 1:1", version="NKJV", verses=[
                BibleVerse(book="Romans", chapter=1, verse=1, text="Paul, a bondservant of Jesus Christ...")
            ])
        ]
        
        # Get structured readings
        readings = self.reader.get_todays_readings_structured()
        
        # Verify structure
        self.assertIn("Family", readings)
        self.assertIn("Secret", readings)
        self.assertEqual(len(readings["Family"]), 2)
        self.assertEqual(len(readings["Secret"]), 2)
        
        # Verify all are BiblePassage objects
        for category in ["Family", "Secret"]:
            for passage in readings[category]:
                self.assertIsInstance(passage, BiblePassage)
                self.assertGreater(len(passage.verses), 0)
    
    def test_backward_compatibility(self):
        """Test that legacy methods still work."""
        # Test that old cache format can still be loaded
        month, day = 10, 16
        
        # Create legacy cache data
        legacy_data = {
            "date": f"{month:02d}/{day:02d}/2025",
            "cached_at": datetime.now().isoformat(),
            "Family": ["📖 Genesis 1:1-2 (NKJV)\n" + "─" * 50 + "\nIn the beginning..."],
            "Secret": ["📖 Psalm 1 (NKJV)\n" + "─" * 50 + "\nBlessed is the man..."]
        }
        
        # Save legacy cache
        cache_file = self.reader.get_cache_filename(month, day)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(legacy_data, f, indent=2)
        
        # Load legacy cache
        loaded_readings = self.reader.load_cached_readings(month, day)
        
        # Verify legacy format still works
        self.assertEqual(len(loaded_readings["Family"]), 1)
        self.assertEqual(len(loaded_readings["Secret"]), 1)
        self.assertIsInstance(loaded_readings["Family"][0], str)
        self.assertIn("Genesis 1:1-2", loaded_readings["Family"][0])
    
    def test_cache_migration_compatibility(self):
        """Test that both cache formats can coexist."""
        month, day = 10, 16
        
        # Create both cache types
        legacy_cache = self.reader.get_cache_filename(month, day)
        structured_cache = self.reader.get_structured_cache_filename(month, day)
        
        # Verify they have different names
        self.assertNotEqual(legacy_cache, structured_cache)
        self.assertIn("mcheyne_readings_", legacy_cache)
        self.assertIn("mcheyne_structured_", structured_cache)
    
    def test_display_structured_readings(self):
        """Test displaying structured readings."""
        readings = {
            "Family": [self.sample_passage],
            "Secret": []
        }
        
        # This should not raise an exception
        try:
            self.reader.display_readings(readings)
        except Exception as e:
            self.fail(f"display_readings raised an exception: {e}")
    
    def test_complex_reference_parsing(self):
        """Test handling of complex Bible references."""
        complex_references = [
            "Luke 1:1-38",
            "Zechariah 12:1-13:1", 
            "Psalm 119:1-24",
            "1 Kings 15",
            "2 Corinthians 5:17"
        ]
        
        for reference in complex_references:
            try:
                # Test that parse_bible_reference doesn't crash
                book, chapter, verse = self.reader.parse_bible_reference(reference)
                self.assertIsInstance(book, str)
                self.assertIsInstance(chapter, str)
                self.assertIsInstance(verse, str)
            except Exception as e:
                self.fail(f"Failed to parse reference '{reference}': {e}")


class TestMcCheyneErrorHandling(unittest.TestCase):
    """Test error handling in M'Cheyne integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = McCheyneReader()
    
    @patch('src.mccheyne.requests.Session.get')
    def test_network_error_handling(self, mock_get):
        """Test handling of network errors."""
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        # Test structured format error handling
        result = self.reader.fetch_passage_text("Genesis 1:1", return_structured=True)
        
        self.assertIsInstance(result, BiblePassage)
        self.assertEqual(result.reference, "Genesis 1:1")
        self.assertIn("Error:", result.verses[0].text)
    
    def test_invalid_reference_handling(self):
        """Test handling of invalid Bible references."""
        invalid_references = [
            "",
            "Invalid Book 999:999",
            "Not A Reference",
            "123 456 789"
        ]
        
        for reference in invalid_references:
            result = self.reader.fetch_passage_text(reference, return_structured=True)
            self.assertIsInstance(result, BiblePassage)
            # Should create error passage without crashing
    
    def test_malformed_cache_handling(self):
        """Test handling of malformed cache files."""
        month, day = 10, 16
        cache_file = self.reader.get_structured_cache_filename(month, day)
        
        # Create malformed cache file
        with open(cache_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle gracefully and return empty readings
        readings = self.reader.load_cached_structured_readings(month, day)
        self.assertEqual(readings["Family"], [])
        self.assertEqual(readings["Secret"], [])


if __name__ == '__main__':
    unittest.main()