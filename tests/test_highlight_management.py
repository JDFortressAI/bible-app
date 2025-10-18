"""
Unit tests for Bible highlight management system.

Tests all highlight operations including adding, merging, searching, and statistics.
"""

import pytest
from src.bible_models import BiblePassage, BibleVerse, BibleHighlight, HighlightPosition
from datetime import datetime


class TestHighlightManagement:
    """Test suite for highlight management functionality."""
    
    @pytest.fixture
    def sample_passage(self):
        """Create a sample passage for testing."""
        verses = [
            BibleVerse(book="John", chapter=3, verse=16, 
                      text="For God so loved the world that He gave His only begotten Son"),
            BibleVerse(book="John", chapter=3, verse=17,
                      text="For God did not send His Son into the world to condemn the world"),
            BibleVerse(book="John", chapter=3, verse=18,
                      text="He who believes in Him is not condemned")
        ]
        return BiblePassage(
            reference="John 3:16-18",
            version="NKJV",
            verses=verses,
            highlights=[]
        )
    
    def test_add_highlight_single_verse(self, sample_passage):
        """Test adding a highlight within a single verse."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=4)
        
        highlight = sample_passage.add_highlight(start_pos, end_pos)
        
        assert len(sample_passage.highlights) == 1
        assert highlight.start_position == start_pos
        assert highlight.end_position == end_pos
        assert highlight.highlight_count == 1
        assert highlight.get_highlighted_text(sample_passage) == "For God so loved the"
    
    def test_add_highlight_multiple_verses(self, sample_passage):
        """Test adding a highlight spanning multiple verses."""
        start_pos = HighlightPosition(verse_index=0, word_index=5)
        end_pos = HighlightPosition(verse_index=1, word_index=3)
        
        highlight = sample_passage.add_highlight(start_pos, end_pos)
        
        assert len(sample_passage.highlights) == 1
        assert highlight.spans_multiple_verses()
        highlighted_text = highlight.get_highlighted_text(sample_passage)
        # Check that it contains text from both verses
        assert "world that He gave His only begotten Son" in highlighted_text
        assert "For God did not" in highlighted_text
    
    def test_add_duplicate_highlight_increments_count(self, sample_passage):
        """Test that adding the same highlight twice increments the count."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=2)
        
        highlight1 = sample_passage.add_highlight(start_pos, end_pos)
        highlight2 = sample_passage.add_highlight(start_pos, end_pos)
        
        assert len(sample_passage.highlights) == 1
        assert highlight1 is highlight2  # Same object returned
        assert highlight1.highlight_count == 2
    
    def test_add_highlight_invalid_positions(self, sample_passage):
        """Test error handling for invalid highlight positions."""
        # Verse index out of bounds
        with pytest.raises(ValueError, match="beyond passage length"):
            sample_passage.add_highlight(
                HighlightPosition(verse_index=5, word_index=0),
                HighlightPosition(verse_index=5, word_index=2)
            )
        
        # Word index out of bounds
        with pytest.raises(ValueError, match="beyond verse length"):
            sample_passage.add_highlight(
                HighlightPosition(verse_index=0, word_index=100),
                HighlightPosition(verse_index=0, word_index=102)
            )
    
    def test_merge_overlapping_highlights(self, sample_passage):
        """Test merging of overlapping highlights."""
        # Add overlapping highlights
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=4)
        )
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=3),
            HighlightPosition(verse_index=0, word_index=7)
        )
        
        assert len(sample_passage.highlights) == 2
        
        sample_passage.merge_overlapping_highlights()
        
        assert len(sample_passage.highlights) == 1
        merged = sample_passage.highlights[0]
        assert merged.start_position == HighlightPosition(verse_index=0, word_index=0)
        assert merged.end_position == HighlightPosition(verse_index=0, word_index=7)
        assert merged.highlight_count == 2
    
    def test_merge_adjacent_highlights(self, sample_passage):
        """Test merging of adjacent highlights."""
        # Add adjacent highlights
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=3),
            HighlightPosition(verse_index=0, word_index=5)
        )
        
        sample_passage.merge_overlapping_highlights()
        
        assert len(sample_passage.highlights) == 1
        merged = sample_passage.highlights[0]
        assert merged.start_position == HighlightPosition(verse_index=0, word_index=0)
        assert merged.end_position == HighlightPosition(verse_index=0, word_index=5)
    
    def test_get_popular_highlights(self, sample_passage):
        """Test getting highlights sorted by popularity."""
        # Add highlights with different counts
        h1 = sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        h2 = sample_passage.add_highlight(
            HighlightPosition(verse_index=1, word_index=0),
            HighlightPosition(verse_index=1, word_index=2)
        )
        
        # Increment counts
        h1.highlight_count = 5
        h2.highlight_count = 10
        
        popular = sample_passage.get_popular_highlights()
        assert len(popular) == 2
        assert popular[0].highlight_count == 10  # Most popular first
        assert popular[1].highlight_count == 5
        
        # Test minimum count filter
        popular_filtered = sample_passage.get_popular_highlights(min_count=8)
        assert len(popular_filtered) == 1
        assert popular_filtered[0].highlight_count == 10
    
    def test_search_highlights_by_text(self, sample_passage):
        """Test searching highlights by text content."""
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=4)  # "For God so loved the"
        )
        sample_passage.add_highlight(
            HighlightPosition(verse_index=1, word_index=0),
            HighlightPosition(verse_index=1, word_index=2)  # "For God did"
        )
        
        # Search for "God"
        results = sample_passage.search_highlights(text_query="God")
        assert len(results) == 2  # Both highlights contain "God"
        
        # Search for "loved"
        results = sample_passage.search_highlights(text_query="loved")
        assert len(results) == 1  # Only first highlight contains "loved"
        
        # Case insensitive search
        results = sample_passage.search_highlights(text_query="GOD")
        assert len(results) == 2
    
    def test_search_highlights_by_count(self, sample_passage):
        """Test searching highlights by minimum count."""
        h1 = sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        h2 = sample_passage.add_highlight(
            HighlightPosition(verse_index=1, word_index=0),
            HighlightPosition(verse_index=1, word_index=2)
        )
        
        h1.highlight_count = 5
        h2.highlight_count = 2
        
        results = sample_passage.search_highlights(min_count=3)
        assert len(results) == 1
        assert results[0].highlight_count == 5
    
    def test_search_highlights_by_verse_range(self, sample_passage):
        """Test searching highlights by verse range."""
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        sample_passage.add_highlight(
            HighlightPosition(verse_index=2, word_index=0),
            HighlightPosition(verse_index=2, word_index=2)
        )
        
        # Search in first verse only
        results = sample_passage.search_highlights(verse_range=(0, 0))
        assert len(results) == 1
        assert results[0].start_position.verse_index == 0
        
        # Search in all verses
        results = sample_passage.search_highlights(verse_range=(0, 2))
        assert len(results) == 2
    
    def test_search_highlights_by_span_type(self, sample_passage):
        """Test searching highlights by span type."""
        # Single verse highlight
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        # Multi-verse highlight
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=5),
            HighlightPosition(verse_index=1, word_index=2)
        )
        
        # Search for single-verse highlights only
        results = sample_passage.search_highlights(spans_multiple=False)
        assert len(results) == 1
        assert not results[0].spans_multiple_verses()
        
        # Search for multi-verse highlights only
        results = sample_passage.search_highlights(spans_multiple=True)
        assert len(results) == 1
        assert results[0].spans_multiple_verses()
    
    def test_get_highlight_statistics(self, sample_passage):
        """Test highlight statistics calculation."""
        # Empty passage
        stats = sample_passage.get_highlight_statistics()
        assert stats['total_highlights'] == 0
        assert stats['coverage_percentage'] == 0.0
        
        # Add some highlights
        h1 = sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        h2 = sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=5),
            HighlightPosition(verse_index=1, word_index=2)
        )
        
        h1.highlight_count = 5
        h2.highlight_count = 3
        
        stats = sample_passage.get_highlight_statistics()
        assert stats['total_highlights'] == 2
        assert stats['total_highlight_count'] == 8
        assert stats['average_popularity'] == 4.0
        assert stats['most_popular_count'] == 5
        assert stats['single_verse_highlights'] == 1
        assert stats['multi_verse_highlights'] == 1
        assert stats['verses_with_highlights'] == 2
        assert stats['coverage_percentage'] > 0
    
    def test_remove_highlight(self, sample_passage):
        """Test removing specific highlights."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=2)
        
        sample_passage.add_highlight(start_pos, end_pos)
        assert len(sample_passage.highlights) == 1
        
        # Remove existing highlight
        removed = sample_passage.remove_highlight(start_pos, end_pos)
        assert removed is True
        assert len(sample_passage.highlights) == 0
        
        # Try to remove non-existent highlight
        removed = sample_passage.remove_highlight(start_pos, end_pos)
        assert removed is False
    
    def test_clear_highlights(self, sample_passage):
        """Test clearing all highlights."""
        # Add multiple highlights
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        sample_passage.add_highlight(
            HighlightPosition(verse_index=1, word_index=0),
            HighlightPosition(verse_index=1, word_index=2)
        )
        
        assert len(sample_passage.highlights) == 2
        
        count = sample_passage.clear_highlights()
        assert count == 2
        assert len(sample_passage.highlights) == 0
    
    def test_get_highlights_by_verse(self, sample_passage):
        """Test getting highlights for a specific verse."""
        # Add highlights affecting different verses
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=5),
            HighlightPosition(verse_index=1, word_index=2)
        )
        sample_passage.add_highlight(
            HighlightPosition(verse_index=2, word_index=0),
            HighlightPosition(verse_index=2, word_index=2)
        )
        
        # Get highlights for verse 0
        verse_0_highlights = sample_passage.get_highlights_by_verse(0)
        assert len(verse_0_highlights) == 2  # Two highlights include verse 0
        
        # Get highlights for verse 1
        verse_1_highlights = sample_passage.get_highlights_by_verse(1)
        assert len(verse_1_highlights) == 1  # One highlight includes verse 1
        
        # Get highlights for verse 2
        verse_2_highlights = sample_passage.get_highlights_by_verse(2)
        assert len(verse_2_highlights) == 1  # One highlight includes verse 2
        
        # Invalid verse index
        invalid_highlights = sample_passage.get_highlights_by_verse(10)
        assert len(invalid_highlights) == 0
    
    def test_get_highlight_coverage(self, sample_passage):
        """Test highlight coverage calculation."""
        # No highlights
        assert sample_passage.get_highlight_coverage() == 0.0
        
        # Add a highlight covering 3 words out of total
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        
        total_words = sample_passage.total_words
        coverage = sample_passage.get_highlight_coverage()
        expected_coverage = (3 / total_words) * 100.0
        assert abs(coverage - expected_coverage) < 0.01
    
    def test_highlight_edge_cases(self, sample_passage):
        """Test edge cases in highlight management."""
        # Single word highlight
        sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=0)
        )
        
        highlight = sample_passage.highlights[0]
        assert highlight.get_highlighted_text(sample_passage) == "For"
        
        # Highlight entire verse
        verse_1_words = len(sample_passage.verses[1].get_words())
        sample_passage.add_highlight(
            HighlightPosition(verse_index=1, word_index=0),
            HighlightPosition(verse_index=1, word_index=verse_1_words - 1)
        )
        
        highlight = sample_passage.highlights[1]
        assert highlight.get_highlighted_text(sample_passage) == sample_passage.verses[1].text
    
    def test_complex_search_combinations(self, sample_passage):
        """Test complex search combinations with multiple filters."""
        # Add various highlights
        h1 = sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=2)
        )
        h2 = sample_passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=5),
            HighlightPosition(verse_index=1, word_index=2)
        )
        h3 = sample_passage.add_highlight(
            HighlightPosition(verse_index=2, word_index=0),
            HighlightPosition(verse_index=2, word_index=2)
        )
        
        h1.highlight_count = 10
        h2.highlight_count = 5
        h3.highlight_count = 2
        
        # Search with multiple criteria
        results = sample_passage.search_highlights(
            text_query="God",
            min_count=3,
            spans_multiple=False
        )
        
        # Should find h1 (contains "God", count >= 3, single verse)
        assert len(results) == 1
        assert results[0] is h1


class TestHighlightValidation:
    """Test highlight validation and error handling."""
    
    def test_highlight_position_validation(self):
        """Test HighlightPosition validation."""
        # Valid position
        pos = HighlightPosition(verse_index=0, word_index=5)
        assert pos.verse_index == 0
        assert pos.word_index == 5
        
        # Invalid negative indices
        with pytest.raises(ValueError):
            HighlightPosition(verse_index=-1, word_index=0)
        
        with pytest.raises(ValueError):
            HighlightPosition(verse_index=0, word_index=-1)
    
    def test_bible_highlight_validation(self):
        """Test BibleHighlight validation."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=5)
        
        # Valid highlight
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        assert highlight.highlight_count == 1  # Default value
        
        # Invalid position order
        with pytest.raises(ValueError, match="End position must be after or equal to start position"):
            BibleHighlight(
                start_position=HighlightPosition(verse_index=1, word_index=0),
                end_position=HighlightPosition(verse_index=0, word_index=5)
            )
        
        # Invalid highlight count
        with pytest.raises(ValueError):
            BibleHighlight(
                start_position=start_pos,
                end_position=end_pos,
                highlight_count=0
            )


if __name__ == "__main__":
    pytest.main([__file__])