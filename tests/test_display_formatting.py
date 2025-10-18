#!/usr/bin/env python3
"""
Tests for Bible data models display and formatting methods.

This module tests the display formatting functionality for BibleVerse, BibleHighlight,
and BiblePassage objects, ensuring proper rendering and visualization.
"""

import unittest
from datetime import datetime
from src.bible_models import BibleVerse, BibleHighlight, BiblePassage, HighlightPosition


class TestBibleVerseDisplay(unittest.TestCase):
    """Test display formatting for BibleVerse objects."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.verse = BibleVerse(
            book="John",
            chapter=3,
            verse=16,
            text="For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
        )
        
        self.short_verse = BibleVerse(
            book="John",
            chapter=11,
            verse=35,
            text="Jesus wept."
        )
    
    def test_format_display_with_reference(self):
        """Test verse display formatting with reference."""
        result = self.verse.format_display(show_reference=True, max_width=80)
        
        # Should include reference
        self.assertIn("John 3:16:", result)
        # Should contain the verse text
        self.assertIn("For God so loved", result)
        # Should handle line wrapping
        lines = result.split('\n')
        self.assertTrue(all(len(line) <= 80 for line in lines))
    
    def test_format_display_without_reference(self):
        """Test verse display formatting without reference."""
        result = self.verse.format_display(show_reference=False, max_width=80)
        
        # Should not include reference
        self.assertNotIn("John 3:16:", result)
        # Should contain the verse text
        self.assertIn("For God so loved", result)
    
    def test_format_display_word_wrapping(self):
        """Test word wrapping in verse display."""
        result = self.verse.format_display(show_reference=True, max_width=40)
        
        lines = result.split('\n')
        # Should have multiple lines due to wrapping
        self.assertGreater(len(lines), 1)
        # All lines should respect max width
        self.assertTrue(all(len(line) <= 40 for line in lines))
        # Subsequent lines should be indented
        if len(lines) > 1:
            self.assertTrue(lines[1].startswith(' '))
    
    def test_format_compact(self):
        """Test compact verse formatting."""
        result = self.verse.format_compact()
        
        # Should include reference
        self.assertIn("John 3:16:", result)
        # Should truncate long text
        self.assertIn("...", result)
        # Should be reasonably short
        self.assertLessEqual(len(result), 70)
    
    def test_format_compact_short_verse(self):
        """Test compact formatting with short verse."""
        result = self.short_verse.format_compact()
        
        # Should include reference
        self.assertIn("John 11:35:", result)
        # Should include full text
        self.assertIn("Jesus wept.", result)
        # Should not truncate
        self.assertNotIn("...", result)


class TestBibleHighlightDisplay(unittest.TestCase):
    """Test display formatting for BibleHighlight objects."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.verse1 = BibleVerse(
            book="John", chapter=3, verse=16,
            text="For God so loved the world that He gave His only begotten Son"
        )
        self.verse2 = BibleVerse(
            book="John", chapter=3, verse=17,
            text="For God did not send His Son into the world to condemn the world"
        )
        
        self.passage = BiblePassage(
            reference="John 3:16-17",
            version="NKJV",
            verses=[self.verse1, self.verse2]
        )
        
        # Single verse highlight
        self.single_highlight = BibleHighlight(
            start_position=HighlightPosition(verse_index=0, word_index=0),
            end_position=HighlightPosition(verse_index=0, word_index=4),
            highlight_count=42
        )
        
        # Multi-verse highlight
        self.multi_highlight = BibleHighlight(
            start_position=HighlightPosition(verse_index=0, word_index=8),
            end_position=HighlightPosition(verse_index=1, word_index=3),
            highlight_count=15
        )
    
    def test_format_display_single_verse(self):
        """Test highlight display for single verse highlight."""
        result = self.single_highlight.format_display(self.passage, show_context=True)
        
        # Should include highlight count
        self.assertIn("42 users", result)
        # Should include verse reference
        self.assertIn("John 3:16", result)
        # Should show highlighted text
        self.assertIn("For God so loved the", result)
        # Should have highlight marker
        self.assertIn("✨", result)
    
    def test_format_display_multi_verse(self):
        """Test highlight display for multi-verse highlight."""
        result = self.multi_highlight.format_display(self.passage, show_context=True)
        
        # Should include highlight count
        self.assertIn("15 users", result)
        # Should show verse range
        self.assertIn("John 3:16-John 3:17", result)
        # Should have highlight marker
        self.assertIn("✨", result)
    
    def test_format_display_without_context(self):
        """Test highlight display without context."""
        result = self.single_highlight.format_display(self.passage, show_context=False)
        
        # Should include highlight count
        self.assertIn("42 users", result)
        # Should show highlighted text
        self.assertIn("For God so loved the", result)
        # Should have highlight marker
        self.assertIn("✨", result)
    
    def test_format_compact(self):
        """Test compact highlight formatting."""
        result = self.single_highlight.format_compact()
        
        # Should include verse index
        self.assertIn("Verse 0", result)
        # Should include word indices
        self.assertIn("words 0-4", result)
        # Should include user count
        self.assertIn("42 users", result)
        # Should have highlight marker
        self.assertIn("✨", result)
    
    def test_get_position_description(self):
        """Test position description generation."""
        result = self.single_highlight.get_position_description(self.passage)
        
        # Should include verse reference
        self.assertIn("John 3:16", result)
        # Should include word positions
        self.assertIn("words 1-5", result)  # 1-indexed for display
    
    def test_spans_multiple_verses(self):
        """Test multi-verse span detection."""
        self.assertFalse(self.single_highlight.spans_multiple_verses())
        self.assertTrue(self.multi_highlight.spans_multiple_verses())


class TestBiblePassageDisplay(unittest.TestCase):
    """Test display formatting for BiblePassage objects."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.verses = [
            BibleVerse(book="John", chapter=3, verse=16,
                      text="For God so loved the world that He gave His only begotten Son"),
            BibleVerse(book="John", chapter=3, verse=17,
                      text="For God did not send His Son into the world to condemn the world"),
            BibleVerse(book="John", chapter=3, verse=18,
                      text="He who believes in Him is not condemned")
        ]
        
        self.passage = BiblePassage(
            reference="John 3:16-18",
            version="NKJV",
            verses=self.verses
        )
        
        # Add some highlights
        self.highlight1 = BibleHighlight(
            start_position=HighlightPosition(verse_index=0, word_index=0),
            end_position=HighlightPosition(verse_index=0, word_index=4),
            highlight_count=100
        )
        self.highlight2 = BibleHighlight(
            start_position=HighlightPosition(verse_index=1, word_index=0),
            end_position=HighlightPosition(verse_index=1, word_index=2),
            highlight_count=50
        )
        
        self.passage.highlights = [self.highlight1, self.highlight2]
    
    def test_format_display_full(self):
        """Test full passage display formatting."""
        result = self.passage.format_display(
            show_metadata=True,
            show_highlights=True,
            max_verses=0,
            max_width=80
        )
        
        # Should include header
        self.assertIn("📖 John 3:16-18 (NKJV)", result)
        # Should include metadata
        self.assertIn("3 verses", result)
        self.assertIn("words", result)
        self.assertIn("characters", result)
        # Should include all verses
        self.assertIn("John 3:16:", result)
        self.assertIn("John 3:17:", result)
        self.assertIn("John 3:18:", result)
        # Should include highlights section
        self.assertIn("HIGHLIGHTS:", result)
        self.assertIn("100 users", result)
    
    def test_format_display_limited_verses(self):
        """Test passage display with verse limit."""
        result = self.passage.format_display(
            show_metadata=True,
            show_highlights=True,
            max_verses=2,
            max_width=80
        )
        
        # Should include first two verses
        self.assertIn("John 3:16:", result)
        self.assertIn("John 3:17:", result)
        # Should show truncation message
        self.assertIn("1 more verses", result)
        # Should not include third verse
        self.assertNotIn("John 3:18:", result)
    
    def test_format_display_no_metadata(self):
        """Test passage display without metadata."""
        result = self.passage.format_display(
            show_metadata=False,
            show_highlights=False,
            max_verses=0,
            max_width=80
        )
        
        # Should include header
        self.assertIn("📖 John 3:16-18 (NKJV)", result)
        # Should not include metadata
        self.assertNotIn("3 verses", result)
        # Should not include highlights
        self.assertNotIn("HIGHLIGHTS:", result)
        # Should include verses
        self.assertIn("John 3:16:", result)
    
    def test_format_compact(self):
        """Test compact passage formatting."""
        result = self.passage.format_compact()
        
        # Should include reference
        self.assertIn("John 3:16-18", result)
        # Should include verse count
        self.assertIn("3 verses", result)
        # Should include highlight count
        self.assertIn("2 highlights", result)
        # Should have book emoji
        self.assertIn("📖", result)
    
    def test_format_metadata_summary(self):
        """Test metadata summary formatting."""
        result = self.passage.format_metadata_summary()
        
        # Should include all metadata fields
        self.assertIn("Reference: John 3:16-18", result)
        self.assertIn("Version: NKJV", result)
        self.assertIn("Verses: 3", result)
        self.assertIn("Words:", result)
        self.assertIn("Characters:", result)
        self.assertIn("Chapter range:", result)
        self.assertIn("Highlights: 2", result)
    
    def test_format_verses_with_highlights(self):
        """Test verse formatting with highlight visualization."""
        result = self.passage.format_verses_with_highlights(max_width=80)
        
        # Should include all verses
        self.assertIn("John 3:16:", result)
        self.assertIn("John 3:17:", result)
        self.assertIn("John 3:18:", result)
        # Should include highlight indicators
        self.assertIn("✨", result)
        self.assertIn("100 users", result)
        self.assertIn("50 users", result)
    
    def test_format_highlights_summary(self):
        """Test highlights summary formatting."""
        result = self.passage.format_highlights_summary()
        
        # Should include summary header
        self.assertIn("HIGHLIGHTS SUMMARY", result)
        self.assertIn("2 total", result)
        # Should include individual highlights
        self.assertIn("100 users", result)
        self.assertIn("50 users", result)
        # Should include coverage statistics
        self.assertIn("Total coverage:", result)
    
    def test_format_highlights_summary_no_highlights(self):
        """Test highlights summary with no highlights."""
        passage_no_highlights = BiblePassage(
            reference="John 3:16",
            version="NKJV",
            verses=[self.verses[0]]
        )
        
        result = passage_no_highlights.format_highlights_summary()
        
        # Should indicate no highlights
        self.assertIn("No highlights", result)


class TestDisplayIntegration(unittest.TestCase):
    """Test integration of display methods with real-world scenarios."""
    
    def setUp(self):
        """Set up complex test scenario."""
        # Multi-chapter passage
        self.verses = [
            BibleVerse(book="Luke", chapter=1, verse=1,
                      text="Inasmuch as many have taken in hand to set in order a narrative"),
            BibleVerse(book="Luke", chapter=1, verse=2,
                      text="just as those who from the beginning were eyewitnesses"),
            BibleVerse(book="Luke", chapter=2, verse=1,
                      text="And it came to pass in those days that a decree went out")
        ]
        
        self.multi_chapter_passage = BiblePassage(
            reference="Luke 1:1-2, 2:1",
            version="NKJV",
            verses=self.verses
        )
        
        # Add cross-chapter highlight
        self.cross_chapter_highlight = BibleHighlight(
            start_position=HighlightPosition(verse_index=1, word_index=5),
            end_position=HighlightPosition(verse_index=2, word_index=3),
            highlight_count=25
        )
        
        self.multi_chapter_passage.highlights = [self.cross_chapter_highlight]
    
    def test_multi_chapter_display(self):
        """Test display of multi-chapter passages."""
        result = self.multi_chapter_passage.format_display()
        
        # Should handle multiple chapters
        self.assertIn("Luke 1:1", result)
        self.assertIn("Luke 2:1", result)
        # Should show chapter range
        self.assertIn("1:1-2:1", result)
        # Should handle cross-chapter highlights
        self.assertIn("✨", result)
        self.assertIn("25 users", result)
    
    def test_highlight_visualization_cross_chapter(self):
        """Test highlight visualization across chapters."""
        result = self.multi_chapter_passage.format_verses_with_highlights()
        
        # Should show highlight start and end indicators
        self.assertIn("Highlight starts here", result)
        self.assertIn("Highlight ends here", result)
        # Should include user count
        self.assertIn("25 users", result)
    
    def test_empty_passage_handling(self):
        """Test handling of edge cases."""
        # Test with minimal passage
        minimal_verse = BibleVerse(book="Ps", chapter=1, verse=1, text="Test")
        minimal_passage = BiblePassage(
            reference="Psalm 1:1",
            version="NKJV",
            verses=[minimal_verse]
        )
        
        result = minimal_passage.format_display()
        
        # Should handle minimal data gracefully
        self.assertIn("Psalm 1:1", result)
        self.assertIn("1 verses", result)
        self.assertIn("Test", result)


if __name__ == '__main__':
    unittest.main()