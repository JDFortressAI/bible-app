#!/usr/bin/env python3
"""
Tests for Bible data models JSON serialization and caching functionality.

Tests serialization round-trip accuracy, cache migration, and validation.
"""

import unittest
import json
import os
import tempfile
from datetime import datetime
from src.bible_models import BiblePassage, BibleVerse, BibleHighlight, HighlightPosition
from src.mccheyne import McCheyneReader


class TestBibleModelsSerialization(unittest.TestCase):
    """Test JSON serialization for all Bible data models."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample data for testing
        self.sample_position = HighlightPosition(verse_index=0, word_index=5)
        
        self.sample_verse = BibleVerse(
            book="Genesis",
            chapter=1,
            verse=1,
            text="In the beginning God created the heavens and the earth."
        )
        
        self.sample_highlight = BibleHighlight(
            start_position=HighlightPosition(verse_index=0, word_index=0),
            end_position=HighlightPosition(verse_index=0, word_index=4),
            highlight_count=42
        )
        
        self.sample_passage = BiblePassage(
            reference="Genesis 1:1-2",
            version="NKJV",
            verses=[
                BibleVerse(book="Genesis", chapter=1, verse=1, text="In the beginning God created the heavens and the earth."),
                BibleVerse(book="Genesis", chapter=1, verse=2, text="The earth was without form, and void; and darkness was on the face of the deep.")
            ],
            highlights=[self.sample_highlight],
            fetched_at=datetime(2025, 10, 16, 10, 30, 0)
        )
    
    def test_highlight_position_serialization(self):
        """Test HighlightPosition JSON serialization round-trip."""
        # Test to_json and from_json
        json_str = self.sample_position.to_json()
        self.assertIsInstance(json_str, str)
        
        restored_position = HighlightPosition.from_json(json_str)
        self.assertEqual(restored_position.verse_index, self.sample_position.verse_index)
        self.assertEqual(restored_position.word_index, self.sample_position.word_index)
        self.assertEqual(restored_position, self.sample_position)
        
        # Test to_dict and from_dict
        data_dict = self.sample_position.to_dict()
        self.assertIsInstance(data_dict, dict)
        self.assertIn('verse_index', data_dict)
        self.assertIn('word_index', data_dict)
        
        restored_from_dict = HighlightPosition.from_dict(data_dict)
        self.assertEqual(restored_from_dict, self.sample_position)
    
    def test_bible_verse_serialization(self):
        """Test BibleVerse JSON serialization round-trip."""
        # Test to_json and from_json
        json_str = self.sample_verse.to_json()
        self.assertIsInstance(json_str, str)
        
        restored_verse = BibleVerse.from_json(json_str)
        self.assertEqual(restored_verse.book, self.sample_verse.book)
        self.assertEqual(restored_verse.chapter, self.sample_verse.chapter)
        self.assertEqual(restored_verse.verse, self.sample_verse.verse)
        self.assertEqual(restored_verse.text, self.sample_verse.text)
        
        # Test computed properties are preserved
        self.assertEqual(restored_verse.word_count, self.sample_verse.word_count)
        self.assertEqual(restored_verse.char_count, self.sample_verse.char_count)
        self.assertEqual(restored_verse.reference, self.sample_verse.reference)
        
        # Test to_dict and from_dict
        data_dict = self.sample_verse.to_dict()
        self.assertIsInstance(data_dict, dict)
        required_fields = ['book', 'chapter', 'verse', 'text']
        for field in required_fields:
            self.assertIn(field, data_dict)
        
        restored_from_dict = BibleVerse.from_dict(data_dict)
        self.assertEqual(restored_from_dict.book, self.sample_verse.book)
        self.assertEqual(restored_from_dict.text, self.sample_verse.text)
    
    def test_bible_highlight_serialization(self):
        """Test BibleHighlight JSON serialization round-trip."""
        # Test to_json and from_json
        json_str = self.sample_highlight.to_json()
        self.assertIsInstance(json_str, str)
        
        restored_highlight = BibleHighlight.from_json(json_str)
        self.assertEqual(restored_highlight.start_position, self.sample_highlight.start_position)
        self.assertEqual(restored_highlight.end_position, self.sample_highlight.end_position)
        self.assertEqual(restored_highlight.highlight_count, self.sample_highlight.highlight_count)
        
        # Test to_dict and from_dict
        data_dict = self.sample_highlight.to_dict()
        self.assertIsInstance(data_dict, dict)
        required_fields = ['start_position', 'end_position', 'highlight_count']
        for field in required_fields:
            self.assertIn(field, data_dict)
        
        restored_from_dict = BibleHighlight.from_dict(data_dict)
        self.assertEqual(restored_from_dict.highlight_count, self.sample_highlight.highlight_count)
    
    def test_bible_passage_serialization(self):
        """Test BiblePassage JSON serialization round-trip."""
        # Test to_json and from_json
        json_str = self.sample_passage.to_json()
        self.assertIsInstance(json_str, str)
        
        restored_passage = BiblePassage.from_json(json_str)
        self.assertEqual(restored_passage.reference, self.sample_passage.reference)
        self.assertEqual(restored_passage.version, self.sample_passage.version)
        self.assertEqual(len(restored_passage.verses), len(self.sample_passage.verses))
        self.assertEqual(len(restored_passage.highlights), len(self.sample_passage.highlights))
        
        # Test verses are properly restored
        for i, verse in enumerate(restored_passage.verses):
            original_verse = self.sample_passage.verses[i]
            self.assertEqual(verse.book, original_verse.book)
            self.assertEqual(verse.chapter, original_verse.chapter)
            self.assertEqual(verse.verse, original_verse.verse)
            self.assertEqual(verse.text, original_verse.text)
        
        # Test highlights are properly restored
        for i, highlight in enumerate(restored_passage.highlights):
            original_highlight = self.sample_passage.highlights[i]
            self.assertEqual(highlight.start_position, original_highlight.start_position)
            self.assertEqual(highlight.end_position, original_highlight.end_position)
            self.assertEqual(highlight.highlight_count, original_highlight.highlight_count)
        
        # Test computed properties work after deserialization
        self.assertEqual(restored_passage.total_verses, self.sample_passage.total_verses)
        self.assertEqual(restored_passage.total_words, self.sample_passage.total_words)
        self.assertEqual(restored_passage.books, self.sample_passage.books)
        
        # Test to_dict and from_dict
        data_dict = self.sample_passage.to_dict()
        self.assertIsInstance(data_dict, dict)
        required_fields = ['reference', 'version', 'verses', 'highlights', 'fetched_at']
        for field in required_fields:
            self.assertIn(field, data_dict)
        
        restored_from_dict = BiblePassage.from_dict(data_dict)
        self.assertEqual(restored_from_dict.reference, self.sample_passage.reference)
        self.assertEqual(len(restored_from_dict.verses), len(self.sample_passage.verses))
    
    def test_bible_passage_file_operations(self):
        """Test BiblePassage file save/load operations."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test saving to file
            self.sample_passage.to_json_file(temp_path)
            self.assertTrue(os.path.exists(temp_path))
            
            # Test loading from file
            restored_passage = BiblePassage.from_json_file(temp_path)
            self.assertEqual(restored_passage.reference, self.sample_passage.reference)
            self.assertEqual(restored_passage.version, self.sample_passage.version)
            self.assertEqual(len(restored_passage.verses), len(self.sample_passage.verses))
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_serialization_with_datetime(self):
        """Test that datetime fields are properly serialized and deserialized."""
        # Create passage with specific datetime
        test_datetime = datetime(2025, 10, 16, 14, 30, 45)
        passage = BiblePassage(
            reference="Test Reference",
            version="NKJV",
            verses=[self.sample_verse],
            fetched_at=test_datetime
        )
        
        # Serialize and deserialize
        json_str = passage.to_json()
        restored_passage = BiblePassage.from_json(json_str)
        
        # Check datetime is preserved (allowing for microsecond precision differences)
        self.assertEqual(restored_passage.fetched_at.replace(microsecond=0), 
                        test_datetime.replace(microsecond=0))
    
    def test_serialization_error_handling(self):
        """Test error handling in serialization methods."""
        # Test invalid JSON
        with self.assertRaises(ValueError):
            BibleVerse.from_json("invalid json")
        
        # Test missing required fields
        with self.assertRaises(ValueError):
            BibleVerse.from_dict({"book": "Genesis"})  # Missing chapter, verse, text
        
        # Test invalid data types
        with self.assertRaises(ValueError):
            BibleVerse.from_dict({
                "book": "Genesis",
                "chapter": "not_a_number",  # Should be int
                "verse": 1,
                "text": "Some text"
            })
    
    def test_large_passage_serialization(self):
        """Test serialization performance with large passages."""
        # Create a large passage with many verses and highlights
        large_verses = []
        large_highlights = []
        
        for i in range(100):  # 100 verses
            verse = BibleVerse(
                book="Psalms",
                chapter=119,
                verse=i + 1,
                text=f"This is verse {i + 1} with some sample text that is reasonably long to test performance."
            )
            large_verses.append(verse)
            
            # Add some highlights
            if i % 10 == 0:  # Every 10th verse
                highlight = BibleHighlight(
                    start_position=HighlightPosition(verse_index=i, word_index=0),
                    end_position=HighlightPosition(verse_index=i, word_index=5),
                    highlight_count=i + 1
                )
                large_highlights.append(highlight)
        
        large_passage = BiblePassage(
            reference="Psalm 119:1-100",
            version="NKJV",
            verses=large_verses,
            highlights=large_highlights
        )
        
        # Test serialization doesn't crash and completes in reasonable time
        start_time = datetime.now()
        json_str = large_passage.to_json()
        serialize_time = (datetime.now() - start_time).total_seconds()
        
        self.assertLess(serialize_time, 1.0)  # Should complete in under 1 second
        self.assertGreater(len(json_str), 1000)  # Should produce substantial JSON
        
        # Test deserialization
        start_time = datetime.now()
        restored_passage = BiblePassage.from_json(json_str)
        deserialize_time = (datetime.now() - start_time).total_seconds()
        
        self.assertLess(deserialize_time, 1.0)  # Should complete in under 1 second
        self.assertEqual(len(restored_passage.verses), 100)
        self.assertEqual(len(restored_passage.highlights), 10)


class TestMcCheyneCaching(unittest.TestCase):
    """Test M'Cheyne caching functionality with structured models."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.reader = McCheyneReader()
        self.test_month = 10
        self.test_day = 16
        
        # Sample structured readings
        self.sample_readings = {
            "Family": [
                BiblePassage(
                    reference="Genesis 1:1-2",
                    version="NKJV",
                    verses=[
                        BibleVerse(book="Genesis", chapter=1, verse=1, text="In the beginning God created the heavens and the earth."),
                        BibleVerse(book="Genesis", chapter=1, verse=2, text="The earth was without form, and void.")
                    ]
                )
            ],
            "Secret": [
                BiblePassage(
                    reference="Psalm 1:1",
                    version="NKJV",
                    verses=[
                        BibleVerse(book="Psalms", chapter=1, verse=1, text="Blessed is the man who walks not in the counsel of the ungodly.")
                    ]
                )
            ]
        }
    
    def tearDown(self):
        """Clean up test cache files."""
        cache_files = [
            self.reader.get_cache_filename(self.test_month, self.test_day),
            self.reader.get_structured_cache_filename(self.test_month, self.test_day)
        ]
        
        for cache_file in cache_files:
            if os.path.exists(cache_file):
                try:
                    os.unlink(cache_file)
                except OSError:
                    pass
    
    def test_structured_cache_save_and_load(self):
        """Test saving and loading structured cache."""
        # Save structured readings
        self.reader.save_structured_readings_to_cache(
            self.test_month, self.test_day, self.sample_readings
        )
        
        # Verify cache file exists
        cache_file = self.reader.get_structured_cache_filename(self.test_month, self.test_day)
        self.assertTrue(os.path.exists(cache_file))
        
        # Load structured readings
        loaded_readings = self.reader.load_cached_structured_readings(self.test_month, self.test_day)
        
        # Verify loaded data matches original
        self.assertEqual(len(loaded_readings["Family"]), 1)
        self.assertEqual(len(loaded_readings["Secret"]), 1)
        
        family_passage = loaded_readings["Family"][0]
        self.assertIsInstance(family_passage, BiblePassage)
        self.assertEqual(family_passage.reference, "Genesis 1:1-2")
        self.assertEqual(len(family_passage.verses), 2)
        
        secret_passage = loaded_readings["Secret"][0]
        self.assertIsInstance(secret_passage, BiblePassage)
        self.assertEqual(secret_passage.reference, "Psalm 1:1")
        self.assertEqual(len(secret_passage.verses), 1)
    
    def test_cache_validation_errors(self):
        """Test cache validation with invalid data."""
        cache_file = self.reader.get_structured_cache_filename(self.test_month, self.test_day)
        
        # Test invalid JSON
        with open(cache_file, 'w') as f:
            f.write("invalid json content")
        
        loaded_readings = self.reader.load_cached_structured_readings(self.test_month, self.test_day)
        self.assertEqual(loaded_readings["Family"], [])
        self.assertEqual(loaded_readings["Secret"], [])
        
        # Test missing required keys
        with open(cache_file, 'w') as f:
            json.dump({"invalid": "structure"}, f)
        
        loaded_readings = self.reader.load_cached_structured_readings(self.test_month, self.test_day)
        self.assertEqual(loaded_readings["Family"], [])
        self.assertEqual(loaded_readings["Secret"], [])
        
        # Test invalid passage data
        invalid_cache_data = {
            "format_version": "1.0",
            "Family": [{"invalid": "passage_data"}],
            "Secret": []
        }
        
        with open(cache_file, 'w') as f:
            json.dump(invalid_cache_data, f)
        
        loaded_readings = self.reader.load_cached_structured_readings(self.test_month, self.test_day)
        self.assertEqual(loaded_readings["Family"], [])  # Invalid passage should be skipped
        self.assertEqual(loaded_readings["Secret"], [])
    
    def test_cache_migration(self):
        """Test migration from legacy cache to structured cache."""
        # Create legacy cache data
        legacy_cache_data = {
            "date": f"{self.test_month:02d}/{self.test_day:02d}/2025",
            "cached_at": datetime.now().isoformat(),
            "Family": [
                "📖 Genesis 1:1 (NKJV)\n" + "─" * 50 + "\nIn the beginning God created the heavens and the earth."
            ],
            "Secret": [
                "📖 Psalm 1:1 (NKJV)\n" + "─" * 50 + "\nBlessed is the man who walks not in the counsel of the ungodly."
            ]
        }
        
        # Save legacy cache
        legacy_cache_file = self.reader.get_cache_filename(self.test_month, self.test_day)
        with open(legacy_cache_file, 'w') as f:
            json.dump(legacy_cache_data, f)
        
        # Ensure no structured cache exists
        structured_cache_file = self.reader.get_structured_cache_filename(self.test_month, self.test_day)
        if os.path.exists(structured_cache_file):
            os.unlink(structured_cache_file)
        
        # Attempt to load structured readings (should trigger migration)
        loaded_readings = self.reader.load_cached_structured_readings(self.test_month, self.test_day)
        
        # Verify migration occurred and structured cache was created
        self.assertTrue(os.path.exists(structured_cache_file))
        
        # Verify migrated data
        self.assertGreater(len(loaded_readings["Family"]), 0)
        self.assertGreater(len(loaded_readings["Secret"]), 0)
        
        family_passage = loaded_readings["Family"][0]
        self.assertIsInstance(family_passage, BiblePassage)
        self.assertIn("Genesis", family_passage.reference)
        
        secret_passage = loaded_readings["Secret"][0]
        self.assertIsInstance(secret_passage, BiblePassage)
        self.assertIn("Psalm", secret_passage.reference)
    
    def test_cache_format_versioning(self):
        """Test cache format version handling."""
        # Create cache with unsupported version
        unsupported_cache_data = {
            "format_version": "2.0",  # Unsupported version
            "Family": [],
            "Secret": []
        }
        
        cache_file = self.reader.get_structured_cache_filename(self.test_month, self.test_day)
        with open(cache_file, 'w') as f:
            json.dump(unsupported_cache_data, f)
        
        # Should return empty readings for unsupported version
        loaded_readings = self.reader.load_cached_structured_readings(self.test_month, self.test_day)
        self.assertEqual(loaded_readings["Family"], [])
        self.assertEqual(loaded_readings["Secret"], [])
    
    def test_save_validation_errors(self):
        """Test validation errors when saving cache."""
        # Test invalid readings structure
        invalid_readings = {"invalid": "structure"}
        
        # Should handle gracefully without crashing
        try:
            self.reader.save_structured_readings_to_cache(
                self.test_month, self.test_day, invalid_readings
            )
        except Exception as e:
            # Should catch validation errors
            self.assertIn("Invalid readings structure", str(e))
        
        # Test non-BiblePassage objects
        invalid_readings_with_wrong_types = {
            "Family": ["not_a_bible_passage"],
            "Secret": []
        }
        
        try:
            self.reader.save_structured_readings_to_cache(
                self.test_month, self.test_day, invalid_readings_with_wrong_types
            )
        except Exception as e:
            # Should catch type validation errors
            self.assertIn("must be BiblePassage object", str(e))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)