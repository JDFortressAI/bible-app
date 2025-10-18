"""
Unit tests for BibleVerse model.

Tests cover model creation, validation, computed properties, and methods
as specified in requirements 1.3, 2.1, 4.1, and 4.3.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from src.bible_models import BibleVerse, BibleHighlight, HighlightPosition, BiblePassage


class TestBibleVerseCreation:
    """Test BibleVerse model creation and basic validation."""
    
    def test_valid_verse_creation(self):
        """Test creating a valid BibleVerse with all required fields."""
        verse = BibleVerse(
            book="John",
            chapter=3,
            verse=16,
            text="For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
        )
        
        assert verse.book == "John"
        assert verse.chapter == 3
        assert verse.verse == 16
        assert "For God so loved the world" in verse.text
    
    def test_book_name_validation(self):
        """Test book name validation - must be non-empty string."""
        # Valid book names
        verse1 = BibleVerse(book="Genesis", chapter=1, verse=1, text="In the beginning God created the heavens and the earth.")
        assert verse1.book == "Genesis"
        
        verse2 = BibleVerse(book="1 Kings", chapter=1, verse=1, text="Now King David was old, advanced in years.")
        assert verse2.book == "1 Kings"
        
        # Invalid book names
        with pytest.raises(ValidationError) as exc_info:
            BibleVerse(book="", chapter=1, verse=1, text="Some text")
        assert "String should have at least 1 character" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            BibleVerse(book="   ", chapter=1, verse=1, text="Some text")
        assert "Book name cannot be empty" in str(exc_info.value)
    
    def test_chapter_validation(self):
        """Test chapter number validation - must be positive integer."""
        # Valid chapter numbers
        verse1 = BibleVerse(book="Psalms", chapter=1, verse=1, text="Blessed is the man")
        assert verse1.chapter == 1
        
        verse2 = BibleVerse(book="Psalms", chapter=119, verse=1, text="Blessed are the undefiled")
        assert verse2.chapter == 119
        
        # Invalid chapter numbers
        with pytest.raises(ValidationError) as exc_info:
            BibleVerse(book="Genesis", chapter=0, verse=1, text="Some text")
        assert "greater than 0" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            BibleVerse(book="Genesis", chapter=-1, verse=1, text="Some text")
        assert "greater than 0" in str(exc_info.value)
    
    def test_verse_validation(self):
        """Test verse number validation - must be positive integer."""
        # Valid verse numbers
        verse1 = BibleVerse(book="John", chapter=3, verse=1, text="There was a man")
        assert verse1.verse == 1
        
        verse2 = BibleVerse(book="Psalms", chapter=119, verse=176, text="I have gone astray")
        assert verse2.verse == 176
        
        # Invalid verse numbers
        with pytest.raises(ValidationError) as exc_info:
            BibleVerse(book="Genesis", chapter=1, verse=0, text="Some text")
        assert "greater than 0" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            BibleVerse(book="Genesis", chapter=1, verse=-1, text="Some text")
        assert "greater than 0" in str(exc_info.value)
    
    def test_text_validation(self):
        """Test verse text validation - must be non-empty string."""
        # Valid text
        verse = BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept.")
        assert verse.text == "Jesus wept."
        
        # Invalid text
        with pytest.raises(ValidationError) as exc_info:
            BibleVerse(book="Genesis", chapter=1, verse=1, text="")
        assert "String should have at least 1 character" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            BibleVerse(book="Genesis", chapter=1, verse=1, text="   ")
        assert "Verse text cannot be empty" in str(exc_info.value)
    
    def test_whitespace_trimming(self):
        """Test that book name and text are trimmed of leading/trailing whitespace."""
        verse = BibleVerse(
            book="  John  ",
            chapter=3,
            verse=16,
            text="  For God so loved the world.  "
        )
        
        assert verse.book == "John"
        assert verse.text == "For God so loved the world."


class TestBibleVerseProperties:
    """Test computed properties of BibleVerse model."""
    
    def test_word_count_property(self):
        """Test word_count property calculation."""
        # Single word
        verse1 = BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept.")
        assert verse1.word_count == 2
        
        # Multiple words
        verse2 = BibleVerse(
            book="John", 
            chapter=3, 
            verse=16, 
            text="For God so loved the world that He gave His only begotten Son"
        )
        assert verse2.word_count == 13
        
        # Empty after split (edge case)
        verse3 = BibleVerse(book="Test", chapter=1, verse=1, text="Word")
        assert verse3.word_count == 1
    
    def test_char_count_property(self):
        """Test char_count property calculation."""
        verse1 = BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept.")
        assert verse1.char_count == 11  # Including the period
        
        verse2 = BibleVerse(book="Test", chapter=1, verse=1, text="A")
        assert verse2.char_count == 1
        
        verse3 = BibleVerse(book="Test", chapter=1, verse=1, text="Hello, world!")
        assert verse3.char_count == 13
    
    def test_reference_property(self):
        """Test reference property formatting."""
        verse1 = BibleVerse(book="John", chapter=3, verse=16, text="For God so loved")
        assert verse1.reference == "John 3:16"
        
        verse2 = BibleVerse(book="1 Kings", chapter=19, verse=12, text="And after the earthquake")
        assert verse2.reference == "1 Kings 19:12"
        
        verse3 = BibleVerse(book="Psalms", chapter=119, verse=105, text="Your word is a lamp")
        assert verse3.reference == "Psalms 119:105"


class TestBibleVerseMethods:
    """Test methods of BibleVerse model."""
    
    def test_get_words_method(self):
        """Test get_words() method returns correct word list."""
        verse1 = BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept.")
        words1 = verse1.get_words()
        assert words1 == ["Jesus", "wept."]
        assert len(words1) == 2
        
        verse2 = BibleVerse(
            book="John", 
            chapter=3, 
            verse=16, 
            text="For God so loved the world"
        )
        words2 = verse2.get_words()
        assert words2 == ["For", "God", "so", "loved", "the", "world"]
        assert len(words2) == 6
        
        # Single word
        verse3 = BibleVerse(book="Test", chapter=1, verse=1, text="Word")
        words3 = verse3.get_words()
        assert words3 == ["Word"]
        assert len(words3) == 1
    
    def test_get_words_consistency_with_word_count(self):
        """Test that get_words() length matches word_count property."""
        verses = [
            BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept."),
            BibleVerse(book="Genesis", chapter=1, verse=1, text="In the beginning God created the heavens and the earth."),
            BibleVerse(book="Psalms", chapter=23, verse=1, text="The Lord is my shepherd; I shall not want."),
        ]
        
        for verse in verses:
            assert len(verse.get_words()) == verse.word_count


class TestBibleVerseStringRepresentation:
    """Test string representation methods."""
    
    def test_str_representation(self):
        """Test __str__ method returns readable format."""
        verse = BibleVerse(
            book="John", 
            chapter=3, 
            verse=16, 
            text="For God so loved the world."
        )
        
        str_repr = str(verse)
        assert str_repr == "John 3:16: For God so loved the world."
    
    def test_repr_representation(self):
        """Test __repr__ method returns developer-friendly format."""
        verse = BibleVerse(
            book="John", 
            chapter=3, 
            verse=16, 
            text="For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
        )
        
        repr_str = repr(verse)
        assert "BibleVerse(" in repr_str
        assert "book='John'" in repr_str
        assert "chapter=3" in repr_str
        assert "verse=16" in repr_str
        assert "text='For God so loved the world that He gave His only" in repr_str
        assert "...'" in repr_str  # Text should be truncated


class TestBibleVerseEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_long_verse(self):
        """Test handling of very long verse text."""
        long_text = "This is a very long verse text. " * 100  # 3300+ characters
        verse = BibleVerse(book="Test", chapter=1, verse=1, text=long_text)
        
        # Text gets trimmed, so we need to compare with the trimmed version
        trimmed_text = long_text.strip()
        assert verse.char_count == len(trimmed_text)
        assert verse.word_count == len(trimmed_text.split())
        assert len(verse.get_words()) == verse.word_count
    
    def test_verse_with_special_characters(self):
        """Test verse with punctuation and special characters."""
        text = "Jesus said, \"I am the way, the truth, and the life; no one comes to the Father except through Me.\""
        verse = BibleVerse(book="John", chapter=14, verse=6, text=text)
        
        assert verse.text == text
        assert verse.char_count == len(text)
        words = verse.get_words()
        assert "\"I" in words
        assert "Me.\"" in words
    
    def test_verse_with_numbers(self):
        """Test verse containing numbers."""
        verse = BibleVerse(
            book="Numbers", 
            chapter=1, 
            verse=1, 
            text="Now the Lord spoke to Moses in the Wilderness of Sinai, in the tabernacle of meeting, on the first day of the second month, in the second year after they had come out of the land of Egypt, saying:"
        )
        
        assert "first" in verse.get_words()
        assert "second" in verse.get_words()
        assert verse.word_count > 30
    
    def test_book_names_with_numbers(self):
        """Test book names that contain numbers."""
        books_with_numbers = ["1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "1 Corinthians", "2 Corinthians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "1 Peter", "2 Peter", "1 John", "2 John", "3 John"]
        
        for book in books_with_numbers:
            verse = BibleVerse(book=book, chapter=1, verse=1, text="Test verse text.")
            assert verse.book == book
            assert book in verse.reference


class TestBibleHighlightCreation:
    """Test BibleHighlight model creation and validation."""
    
    def test_valid_highlight_creation(self):
        """Test creating a valid BibleHighlight with all required fields."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=3)
        
        highlight = BibleHighlight(
            start_position=start_pos,
            end_position=end_pos,
            highlight_count=5
        )
        
        assert highlight.start_position == start_pos
        assert highlight.end_position == end_pos
        assert highlight.highlight_count == 5
    
    def test_default_highlight_count(self):
        """Test that highlight_count defaults to 1."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=1)
        
        highlight = BibleHighlight(
            start_position=start_pos,
            end_position=end_pos
        )
        
        assert highlight.highlight_count == 1
    
    def test_highlight_count_validation(self):
        """Test highlight_count must be positive."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=1)
        
        # Valid counts
        highlight1 = BibleHighlight(start_position=start_pos, end_position=end_pos, highlight_count=1)
        assert highlight1.highlight_count == 1
        
        highlight2 = BibleHighlight(start_position=start_pos, end_position=end_pos, highlight_count=100)
        assert highlight2.highlight_count == 100
        
        # Invalid counts
        with pytest.raises(ValidationError) as exc_info:
            BibleHighlight(start_position=start_pos, end_position=end_pos, highlight_count=0)
        assert "greater than or equal to 1" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            BibleHighlight(start_position=start_pos, end_position=end_pos, highlight_count=-1)
        assert "greater than or equal to 1" in str(exc_info.value)
    
    def test_position_order_validation(self):
        """Test that end_position must be after or equal to start_position."""
        # Valid: same position (single word)
        pos = HighlightPosition(verse_index=0, word_index=5)
        highlight1 = BibleHighlight(start_position=pos, end_position=pos)
        assert highlight1.start_position == highlight1.end_position
        
        # Valid: end after start in same verse
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=3)
        highlight2 = BibleHighlight(start_position=start_pos, end_position=end_pos)
        assert highlight2.end_position > highlight2.start_position
        
        # Valid: end in later verse
        start_pos = HighlightPosition(verse_index=0, word_index=5)
        end_pos = HighlightPosition(verse_index=1, word_index=2)
        highlight3 = BibleHighlight(start_position=start_pos, end_position=end_pos)
        assert highlight3.end_position > highlight3.start_position
        
        # Invalid: end before start
        start_pos = HighlightPosition(verse_index=1, word_index=5)
        end_pos = HighlightPosition(verse_index=0, word_index=2)
        with pytest.raises(ValidationError) as exc_info:
            BibleHighlight(start_position=start_pos, end_position=end_pos)
        assert "End position must be after or equal to start position" in str(exc_info.value)
        
        # Invalid: end before start in same verse
        start_pos = HighlightPosition(verse_index=0, word_index=5)
        end_pos = HighlightPosition(verse_index=0, word_index=2)
        with pytest.raises(ValidationError) as exc_info:
            BibleHighlight(start_position=start_pos, end_position=end_pos)
        assert "End position must be after or equal to start position" in str(exc_info.value)


class TestBibleHighlightMethods:
    """Test methods of BibleHighlight model."""
    
    def test_spans_multiple_verses_single_verse(self):
        """Test spans_multiple_verses() returns False for single verse highlights."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=5)
        
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        assert not highlight.spans_multiple_verses()
    
    def test_spans_multiple_verses_multi_verse(self):
        """Test spans_multiple_verses() returns True for multi-verse highlights."""
        start_pos = HighlightPosition(verse_index=0, word_index=5)
        end_pos = HighlightPosition(verse_index=2, word_index=3)
        
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        assert highlight.spans_multiple_verses()
    
    def test_spans_multiple_verses_adjacent_verses(self):
        """Test spans_multiple_verses() with adjacent verses."""
        start_pos = HighlightPosition(verse_index=1, word_index=10)
        end_pos = HighlightPosition(verse_index=2, word_index=0)
        
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        assert highlight.spans_multiple_verses()


class TestBibleHighlightTextExtraction:
    """Test get_highlighted_text() method with mock BiblePassage."""
    
    def create_mock_passage(self):
        """Create a mock BiblePassage for testing."""
        # We'll create a simple mock object since BiblePassage isn't implemented yet
        class MockPassage:
            def __init__(self):
                self.verses = [
                    BibleVerse(book="John", chapter=3, verse=16, text="For God so loved the world"),
                    BibleVerse(book="John", chapter=3, verse=17, text="For God did not send His Son"),
                    BibleVerse(book="John", chapter=3, verse=18, text="He who believes in Him is not condemned")
                ]
        
        return MockPassage()
    
    def test_single_verse_highlight_extraction(self):
        """Test extracting text from single verse highlight."""
        passage = self.create_mock_passage()
        
        # Highlight "God so loved" (words 1-3 in verse 0)
        start_pos = HighlightPosition(verse_index=0, word_index=1)
        end_pos = HighlightPosition(verse_index=0, word_index=3)
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        text = highlight.get_highlighted_text(passage)
        assert text == "God so loved"
    
    def test_single_word_highlight_extraction(self):
        """Test extracting single word highlight."""
        passage = self.create_mock_passage()
        
        # Highlight just "God" (word 1 in verse 0)
        pos = HighlightPosition(verse_index=0, word_index=1)
        highlight = BibleHighlight(start_position=pos, end_position=pos)
        
        text = highlight.get_highlighted_text(passage)
        assert text == "God"
    
    def test_full_verse_highlight_extraction(self):
        """Test extracting entire verse."""
        passage = self.create_mock_passage()
        
        # Highlight entire first verse
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=5)  # "world" is word 5
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        text = highlight.get_highlighted_text(passage)
        assert text == "For God so loved the world"
    
    def test_multi_verse_highlight_extraction(self):
        """Test extracting text spanning multiple verses."""
        passage = self.create_mock_passage()
        
        # Highlight from "loved the world" in verse 0 to "God did" in verse 1
        start_pos = HighlightPosition(verse_index=0, word_index=3)  # "loved"
        end_pos = HighlightPosition(verse_index=1, word_index=2)    # "did"
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        text = highlight.get_highlighted_text(passage)
        expected = "loved the world For God did"
        assert text == expected
    
    def test_three_verse_highlight_extraction(self):
        """Test extracting text spanning three verses."""
        passage = self.create_mock_passage()
        
        # Highlight from "world" in verse 0 to "believes" in verse 2
        start_pos = HighlightPosition(verse_index=0, word_index=5)  # "world"
        end_pos = HighlightPosition(verse_index=2, word_index=2)    # "believes"
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        text = highlight.get_highlighted_text(passage)
        expected = "world For God did not send His Son He who believes"
        assert text == expected
    
    def test_highlight_validation_errors(self):
        """Test error handling for invalid highlight positions."""
        passage = self.create_mock_passage()
        
        # Test verse index out of range
        start_pos = HighlightPosition(verse_index=5, word_index=0)  # verse 5 doesn't exist
        end_pos = HighlightPosition(verse_index=5, word_index=1)
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        with pytest.raises(ValueError) as exc_info:
            highlight.get_highlighted_text(passage)
        assert "Passage only has 3 verses" in str(exc_info.value)
        
        # Test word index out of range in single verse
        start_pos = HighlightPosition(verse_index=0, word_index=10)  # word 10 doesn't exist
        end_pos = HighlightPosition(verse_index=0, word_index=11)
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        with pytest.raises(IndexError) as exc_info:
            highlight.get_highlighted_text(passage)
        assert "Start word index 10 is beyond verse length" in str(exc_info.value)
        
        # Test end word index out of range in single verse
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=10)  # word 10 doesn't exist
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        with pytest.raises(IndexError) as exc_info:
            highlight.get_highlighted_text(passage)
        assert "End word index 10 is beyond verse length" in str(exc_info.value)
        
        # Test word index out of range in multi-verse highlight
        start_pos = HighlightPosition(verse_index=0, word_index=10)  # word 10 doesn't exist
        end_pos = HighlightPosition(verse_index=1, word_index=2)
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        with pytest.raises(IndexError) as exc_info:
            highlight.get_highlighted_text(passage)
        assert "Start word index 10 is beyond verse length" in str(exc_info.value)


class TestBibleHighlightStringRepresentation:
    """Test string representation methods for BibleHighlight."""
    
    def test_str_representation(self):
        """Test __str__ method returns readable format."""
        start_pos = HighlightPosition(verse_index=0, word_index=1)
        end_pos = HighlightPosition(verse_index=1, word_index=3)
        highlight = BibleHighlight(
            start_position=start_pos,
            end_position=end_pos,
            highlight_count=42
        )
        
        str_repr = str(highlight)
        expected = "BibleHighlight(HighlightPosition(verse=0, word=1) to HighlightPosition(verse=1, word=3), count=42)"
        assert str_repr == expected
    
    def test_repr_representation(self):
        """Test __repr__ method returns developer-friendly format."""
        start_pos = HighlightPosition(verse_index=2, word_index=5)
        end_pos = HighlightPosition(verse_index=2, word_index=8)
        highlight = BibleHighlight(
            start_position=start_pos,
            end_position=end_pos,
            highlight_count=1
        )
        
        repr_str = repr(highlight)
        assert "BibleHighlight(" in repr_str
        assert "start_position=HighlightPosition(verse_index=2, word_index=5)" in repr_str
        assert "end_position=HighlightPosition(verse_index=2, word_index=8)" in repr_str
        assert "highlight_count=1" in repr_str


class TestBibleHighlightEdgeCases:
    """Test edge cases and boundary conditions for BibleHighlight."""
    
    def create_single_verse_passage(self):
        """Create a passage with just one verse for edge case testing."""
        class MockPassage:
            def __init__(self):
                self.verses = [
                    BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept.")
                ]
        return MockPassage()
    
    def test_highlight_in_single_verse_passage(self):
        """Test highlighting in a passage with only one verse."""
        passage = self.create_single_verse_passage()
        
        # Highlight both words
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=1)
        highlight = BibleHighlight(start_position=start_pos, end_position=end_pos)
        
        text = highlight.get_highlighted_text(passage)
        assert text == "Jesus wept."
        assert not highlight.spans_multiple_verses()
    
    def test_highlight_single_word_in_short_verse(self):
        """Test highlighting single word in very short verse."""
        passage = self.create_single_verse_passage()
        
        # Highlight just "Jesus"
        pos = HighlightPosition(verse_index=0, word_index=0)
        highlight = BibleHighlight(start_position=pos, end_position=pos)
        
        text = highlight.get_highlighted_text(passage)
        assert text == "Jesus"
    
    def test_highlight_with_maximum_count(self):
        """Test highlight with very large count value."""
        start_pos = HighlightPosition(verse_index=0, word_index=0)
        end_pos = HighlightPosition(verse_index=0, word_index=1)
        
        highlight = BibleHighlight(
            start_position=start_pos,
            end_position=end_pos,
            highlight_count=999999
        )
        
        assert highlight.highlight_count == 999999
    
    def test_empty_verse_handling(self):
        """Test behavior with verses that have minimal content."""
        class MockPassage:
            def __init__(self):
                self.verses = [
                    BibleVerse(book="Test", chapter=1, verse=1, text="A")  # Single character
                ]
        
        passage = MockPassage()
        
        # Try to highlight the single word
        pos = HighlightPosition(verse_index=0, word_index=0)
        highlight = BibleHighlight(start_position=pos, end_position=pos)
        
        text = highlight.get_highlighted_text(passage)
        assert text == "A"


class TestBiblePassageCreation:
    """Test BiblePassage model creation and basic validation."""
    
    def create_sample_verses(self):
        """Create sample verses for testing."""
        return [
            BibleVerse(book="John", chapter=3, verse=16, text="For God so loved the world that He gave His only begotten Son"),
            BibleVerse(book="John", chapter=3, verse=17, text="For God did not send His Son into the world to condemn the world"),
            BibleVerse(book="John", chapter=3, verse=18, text="He who believes in Him is not condemned but he who does not believe is condemned already")
        ]
    
    def test_valid_passage_creation(self):
        """Test creating a valid BiblePassage with all required fields."""
        verses = self.create_sample_verses()
        
        passage = BiblePassage(
            reference="John 3:16-18",
            version="NKJV",
            verses=verses
        )
        
        assert passage.reference == "John 3:16-18"
        assert passage.version == "NKJV"
        assert len(passage.verses) == 3
        assert len(passage.highlights) == 0  # Default empty list
        assert isinstance(passage.fetched_at, datetime)
    
    def test_default_values(self):
        """Test default values for optional fields."""
        verses = self.create_sample_verses()
        
        passage = BiblePassage(
            reference="John 3:16-18",
            verses=verses
        )
        
        assert passage.version == "NKJV"  # Default version
        assert passage.highlights == []   # Default empty highlights
        assert isinstance(passage.fetched_at, datetime)
    
    def test_reference_validation(self):
        """Test reference validation - must be non-empty string."""
        verses = self.create_sample_verses()
        
        # Valid references
        passage1 = BiblePassage(reference="John 3:16", verses=verses)
        assert passage1.reference == "John 3:16"
        
        passage2 = BiblePassage(reference="Luke 1:1-38", verses=verses)
        assert passage2.reference == "Luke 1:1-38"
        
        # Invalid references
        with pytest.raises(ValidationError) as exc_info:
            BiblePassage(reference="", verses=verses)
        assert "String should have at least 1 character" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            BiblePassage(reference="   ", verses=verses)
        assert "Reference cannot be empty" in str(exc_info.value)
    
    def test_version_validation(self):
        """Test version validation - must be non-empty string."""
        verses = self.create_sample_verses()
        
        # Valid versions
        passage1 = BiblePassage(reference="John 3:16", verses=verses, version="ESV")
        assert passage1.version == "ESV"
        
        passage2 = BiblePassage(reference="John 3:16", verses=verses, version="New International Version")
        assert passage2.version == "New International Version"
        
        # Invalid versions
        with pytest.raises(ValidationError) as exc_info:
            BiblePassage(reference="John 3:16", verses=verses, version="")
        assert "Version cannot be empty" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            BiblePassage(reference="John 3:16", verses=verses, version="   ")
        assert "Version cannot be empty" in str(exc_info.value)
    
    def test_verses_validation(self):
        """Test verses validation - must have at least one verse."""
        verses = self.create_sample_verses()
        
        # Valid verses list
        passage = BiblePassage(reference="John 3:16-18", verses=verses)
        assert len(passage.verses) == 3
        
        # Invalid: empty verses list
        with pytest.raises(ValidationError) as exc_info:
            BiblePassage(reference="John 3:16", verses=[])
        assert "List should have at least 1 item" in str(exc_info.value)
    
    def test_whitespace_trimming(self):
        """Test that reference and version are trimmed of leading/trailing whitespace."""
        verses = self.create_sample_verses()
        
        passage = BiblePassage(
            reference="  John 3:16-18  ",
            version="  NKJV  ",
            verses=verses
        )
        
        assert passage.reference == "John 3:16-18"
        assert passage.version == "NKJV"


class TestBiblePassageMetadataProperties:
    """Test computed metadata properties of BiblePassage model."""
    
    def create_sample_passage(self):
        """Create a sample passage for testing."""
        verses = [
            BibleVerse(book="John", chapter=3, verse=16, text="For God so loved the world"),  # 6 words, 26 chars
            BibleVerse(book="John", chapter=3, verse=17, text="For God did not send His Son"),  # 7 words, 28 chars
            BibleVerse(book="John", chapter=3, verse=18, text="He who believes in Him")  # 5 words, 22 chars
        ]
        return BiblePassage(reference="John 3:16-18", verses=verses)
    
    def test_total_verses_property(self):
        """Test total_verses property calculation."""
        passage = self.create_sample_passage()
        assert passage.total_verses == 3
        
        # Single verse passage
        single_verse = [BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept.")]
        single_passage = BiblePassage(reference="John 11:35", verses=single_verse)
        assert single_passage.total_verses == 1
    
    def test_total_words_property(self):
        """Test total_words property calculation."""
        passage = self.create_sample_passage()
        # 6 + 7 + 5 = 18 words total
        assert passage.total_words == 18
        
        # Verify by checking individual verse word counts
        expected_total = sum(verse.word_count for verse in passage.verses)
        assert passage.total_words == expected_total
    
    def test_total_characters_property(self):
        """Test total_characters property calculation."""
        passage = self.create_sample_passage()
        # 26 + 28 + 22 = 76 characters total
        assert passage.total_characters == 76
        
        # Verify by checking individual verse character counts
        expected_total = sum(verse.char_count for verse in passage.verses)
        assert passage.total_characters == expected_total
    
    def test_books_property_single_book(self):
        """Test books property with single book passage."""
        passage = self.create_sample_passage()
        assert passage.books == ["John"]
    
    def test_books_property_multiple_books(self):
        """Test books property with multi-book passage."""
        verses = [
            BibleVerse(book="Zechariah", chapter=12, verse=1, text="The burden of the word of the Lord"),
            BibleVerse(book="Zechariah", chapter=12, verse=2, text="Behold I will make Jerusalem"),
            BibleVerse(book="Zechariah", chapter=13, verse=1, text="In that day a fountain shall be opened"),
            BibleVerse(book="Malachi", chapter=1, verse=1, text="The burden of the word of the Lord to Israel")
        ]
        passage = BiblePassage(reference="Zechariah 12:1-Malachi 1:1", verses=verses)
        
        # Should preserve order and uniqueness
        assert passage.books == ["Zechariah", "Malachi"]
    
    def test_books_property_preserves_order(self):
        """Test that books property preserves the order of first appearance."""
        verses = [
            BibleVerse(book="Genesis", chapter=1, verse=1, text="In the beginning"),
            BibleVerse(book="Exodus", chapter=1, verse=1, text="Now these are the names"),
            BibleVerse(book="Genesis", chapter=1, verse=2, text="The earth was without form"),
            BibleVerse(book="Leviticus", chapter=1, verse=1, text="Now the Lord called"),
            BibleVerse(book="Exodus", chapter=1, verse=2, text="Reuben Simeon Levi")
        ]
        passage = BiblePassage(reference="Mixed Books", verses=verses)
        
        # Should be in order of first appearance: Genesis, Exodus, Leviticus
        assert passage.books == ["Genesis", "Exodus", "Leviticus"]
    
    def test_chapter_range_single_verse(self):
        """Test chapter_range property with single verse."""
        verse = [BibleVerse(book="John", chapter=3, verse=16, text="For God so loved")]
        passage = BiblePassage(reference="John 3:16", verses=verse)
        
        assert passage.chapter_range == "3:16"
    
    def test_chapter_range_same_chapter(self):
        """Test chapter_range property with multiple verses in same chapter."""
        verses = [
            BibleVerse(book="John", chapter=3, verse=16, text="For God so loved"),
            BibleVerse(book="John", chapter=3, verse=17, text="For God did not send"),
            BibleVerse(book="John", chapter=3, verse=18, text="He who believes")
        ]
        passage = BiblePassage(reference="John 3:16-18", verses=verses)
        
        assert passage.chapter_range == "3:16-18"
    
    def test_chapter_range_different_chapters(self):
        """Test chapter_range property with verses spanning multiple chapters."""
        verses = [
            BibleVerse(book="Luke", chapter=1, verse=35, text="And the angel answered"),
            BibleVerse(book="Luke", chapter=1, verse=36, text="Now indeed Elizabeth"),
            BibleVerse(book="Luke", chapter=2, verse=1, text="And it came to pass"),
            BibleVerse(book="Luke", chapter=2, verse=2, text="This census first took place")
        ]
        passage = BiblePassage(reference="Luke 1:35-2:2", verses=verses)
        
        assert passage.chapter_range == "1:35-2:2"
    



class TestBiblePassageHighlightManagement:
    """Test highlight management methods of BiblePassage model."""
    
    def create_sample_passage(self):
        """Create a sample passage for highlight testing."""
        verses = [
            BibleVerse(book="John", chapter=3, verse=16, text="For God so loved the world"),  # 6 words
            BibleVerse(book="John", chapter=3, verse=17, text="For God did not send His Son"),  # 7 words
            BibleVerse(book="John", chapter=3, verse=18, text="He who believes in Him")  # 5 words
        ]
        return BiblePassage(reference="John 3:16-18", verses=verses)
    
    def test_add_highlight_new(self):
        """Test adding a new highlight to the passage."""
        passage = self.create_sample_passage()
        
        start_pos = HighlightPosition(verse_index=0, word_index=1)  # "God"
        end_pos = HighlightPosition(verse_index=0, word_index=3)    # "loved"
        
        highlight = passage.add_highlight(start_pos, end_pos)
        
        assert len(passage.highlights) == 1
        assert highlight.start_position == start_pos
        assert highlight.end_position == end_pos
        assert highlight.highlight_count == 1
        assert highlight in passage.highlights
    
    def test_add_highlight_existing(self):
        """Test adding a highlight that already exists (should increment count)."""
        passage = self.create_sample_passage()
        
        start_pos = HighlightPosition(verse_index=0, word_index=1)
        end_pos = HighlightPosition(verse_index=0, word_index=3)
        
        # Add highlight twice
        highlight1 = passage.add_highlight(start_pos, end_pos)
        highlight2 = passage.add_highlight(start_pos, end_pos)
        
        # Should be the same highlight object with incremented count
        assert highlight1 is highlight2
        assert len(passage.highlights) == 1
        assert highlight1.highlight_count == 2
    
    def test_add_highlight_multiple_different(self):
        """Test adding multiple different highlights."""
        passage = self.create_sample_passage()
        
        # First highlight: "God so loved"
        highlight1 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=3)
        )
        
        # Second highlight: "the world"
        highlight2 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=4),
            HighlightPosition(verse_index=0, word_index=5)
        )
        
        assert len(passage.highlights) == 2
        assert highlight1.highlight_count == 1
        assert highlight2.highlight_count == 1
        assert highlight1 != highlight2
    
    def test_add_highlight_multi_verse(self):
        """Test adding a highlight that spans multiple verses."""
        passage = self.create_sample_passage()
        
        # Highlight from "world" in verse 0 to "God" in verse 1
        start_pos = HighlightPosition(verse_index=0, word_index=5)  # "world"
        end_pos = HighlightPosition(verse_index=1, word_index=1)    # "God" in verse 1
        
        highlight = passage.add_highlight(start_pos, end_pos)
        
        assert len(passage.highlights) == 1
        assert highlight.spans_multiple_verses()
        assert highlight.highlight_count == 1
    
    def test_add_highlight_validation_errors(self):
        """Test validation errors when adding highlights."""
        passage = self.create_sample_passage()
        
        # Test verse index out of range
        with pytest.raises(ValueError) as exc_info:
            passage.add_highlight(
                HighlightPosition(verse_index=5, word_index=0),  # verse 5 doesn't exist
                HighlightPosition(verse_index=5, word_index=1)
            )
        assert "Highlight positions reference verses beyond passage length" in str(exc_info.value)
        
        # Test word index out of range
        with pytest.raises(ValueError) as exc_info:
            passage.add_highlight(
                HighlightPosition(verse_index=0, word_index=10),  # word 10 doesn't exist
                HighlightPosition(verse_index=0, word_index=11)
            )
        assert "Start word index 10 is beyond verse length" in str(exc_info.value)
        
        # Test end word index out of range
        with pytest.raises(ValueError) as exc_info:
            passage.add_highlight(
                HighlightPosition(verse_index=0, word_index=0),
                HighlightPosition(verse_index=0, word_index=10)  # word 10 doesn't exist
            )
        assert "End word index 10 is beyond verse length" in str(exc_info.value)
    
    def test_get_popular_highlights_default(self):
        """Test getting popular highlights with default minimum count."""
        passage = self.create_sample_passage()
        
        # Add highlights with different counts
        highlight1 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=1)
        )
        highlight1.highlight_count = 5
        
        highlight2 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=2),
            HighlightPosition(verse_index=0, word_index=3)
        )
        highlight2.highlight_count = 10
        
        highlight3 = passage.add_highlight(
            HighlightPosition(verse_index=1, word_index=0),
            HighlightPosition(verse_index=1, word_index=1)
        )
        highlight3.highlight_count = 3
        
        popular = passage.get_popular_highlights()
        
        # Should be sorted by count descending
        assert len(popular) == 3
        assert popular[0].highlight_count == 10  # highlight2
        assert popular[1].highlight_count == 5   # highlight1
        assert popular[2].highlight_count == 3   # highlight3
    
    def test_get_popular_highlights_with_minimum(self):
        """Test getting popular highlights with minimum count filter."""
        passage = self.create_sample_passage()
        
        # Add highlights with different counts
        highlight1 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=1)
        )
        highlight1.highlight_count = 5
        
        highlight2 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=2),
            HighlightPosition(verse_index=0, word_index=3)
        )
        highlight2.highlight_count = 10
        
        highlight3 = passage.add_highlight(
            HighlightPosition(verse_index=1, word_index=0),
            HighlightPosition(verse_index=1, word_index=1)
        )
        highlight3.highlight_count = 3
        
        # Filter for highlights with count >= 5
        popular = passage.get_popular_highlights(min_count=5)
        
        assert len(popular) == 2
        assert popular[0].highlight_count == 10  # highlight2
        assert popular[1].highlight_count == 5   # highlight1
        
        # Filter for highlights with count >= 8
        very_popular = passage.get_popular_highlights(min_count=8)
        
        assert len(very_popular) == 1
        assert very_popular[0].highlight_count == 10  # highlight2
    
    def test_get_popular_highlights_empty(self):
        """Test getting popular highlights from passage with no highlights."""
        passage = self.create_sample_passage()
        
        popular = passage.get_popular_highlights()
        assert popular == []
        
        popular_filtered = passage.get_popular_highlights(min_count=5)
        assert popular_filtered == []


class TestBiblePassageHighlightCoverage:
    """Test highlight coverage calculation methods."""
    
    def create_sample_passage(self):
        """Create a sample passage for coverage testing."""
        verses = [
            BibleVerse(book="John", chapter=3, verse=16, text="For God so loved"),  # 4 words
            BibleVerse(book="John", chapter=3, verse=17, text="For God did not")    # 4 words
        ]
        return BiblePassage(reference="John 3:16-17", verses=verses)  # Total: 8 words
    
    def test_get_highlight_coverage_no_highlights(self):
        """Test coverage calculation with no highlights."""
        passage = self.create_sample_passage()
        
        coverage = passage.get_highlight_coverage()
        assert coverage == 0.0
    
    def test_get_highlight_coverage_single_word(self):
        """Test coverage calculation with single word highlight."""
        passage = self.create_sample_passage()
        
        # Highlight just "God" (1 word out of 8)
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=1)
        )
        
        coverage = passage.get_highlight_coverage()
        assert coverage == 12.5  # 1/8 * 100 = 12.5%
    
    def test_get_highlight_coverage_multiple_words_same_verse(self):
        """Test coverage calculation with multiple words in same verse."""
        passage = self.create_sample_passage()
        
        # Highlight "God so loved" (3 words out of 8)
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=3)
        )
        
        coverage = passage.get_highlight_coverage()
        assert coverage == 37.5  # 3/8 * 100 = 37.5%
    
    def test_get_highlight_coverage_full_verse(self):
        """Test coverage calculation with full verse highlighted."""
        passage = self.create_sample_passage()
        
        # Highlight entire first verse (4 words out of 8)
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=0, word_index=3)
        )
        
        coverage = passage.get_highlight_coverage()
        assert coverage == 50.0  # 4/8 * 100 = 50%
    
    def test_get_highlight_coverage_multi_verse(self):
        """Test coverage calculation with multi-verse highlight."""
        passage = self.create_sample_passage()
        
        # Highlight from "loved" in verse 0 to "God" in verse 1 (3 words total)
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=3),  # "loved"
            HighlightPosition(verse_index=1, word_index=1)   # "God" in verse 1
        )
        
        coverage = passage.get_highlight_coverage()
        assert coverage == 37.5  # 3/8 * 100 = 37.5%
    
    def test_get_highlight_coverage_overlapping_highlights(self):
        """Test coverage calculation with overlapping highlights (no double counting)."""
        passage = self.create_sample_passage()
        
        # First highlight: "God so" (words 1-2)
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=2)
        )
        
        # Second highlight: "so loved" (words 2-3) - overlaps with first
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=2),
            HighlightPosition(verse_index=0, word_index=3)
        )
        
        coverage = passage.get_highlight_coverage()
        # Should cover words 1, 2, 3 = 3 words out of 8 = 37.5%
        assert coverage == 37.5
    
    def test_get_highlight_coverage_full_passage(self):
        """Test coverage calculation with entire passage highlighted."""
        passage = self.create_sample_passage()
        
        # Highlight entire passage
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=0),
            HighlightPosition(verse_index=1, word_index=3)
        )
        
        coverage = passage.get_highlight_coverage()
        assert coverage == 100.0  # 8/8 * 100 = 100%


class TestBiblePassageHighlightMerging:
    """Test highlight merging functionality."""
    
    def create_sample_passage(self):
        """Create a sample passage for merging tests."""
        verses = [
            BibleVerse(book="John", chapter=3, verse=16, text="For God so loved the world"),  # 6 words
            BibleVerse(book="John", chapter=3, verse=17, text="For God did not send His")     # 6 words
        ]
        return BiblePassage(reference="John 3:16-17", verses=verses)
    
    def test_merge_overlapping_highlights_no_highlights(self):
        """Test merging with no highlights."""
        passage = self.create_sample_passage()
        
        passage.merge_overlapping_highlights()
        assert len(passage.highlights) == 0
    
    def test_merge_overlapping_highlights_single_highlight(self):
        """Test merging with single highlight."""
        passage = self.create_sample_passage()
        
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=3)
        )
        
        passage.merge_overlapping_highlights()
        assert len(passage.highlights) == 1
    
    def test_merge_overlapping_highlights_non_overlapping(self):
        """Test merging with non-overlapping highlights."""
        passage = self.create_sample_passage()
        
        # First highlight: "God so" (words 1-2)
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=2)
        )
        
        # Second highlight: "the world" (words 4-5) - no overlap
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=4),
            HighlightPosition(verse_index=0, word_index=5)
        )
        
        passage.merge_overlapping_highlights()
        assert len(passage.highlights) == 2  # Should remain separate
    
    def test_merge_overlapping_highlights_overlapping(self):
        """Test merging with overlapping highlights."""
        passage = self.create_sample_passage()
        
        # First highlight: "God so loved" (words 1-3)
        highlight1 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=3)
        )
        highlight1.highlight_count = 5
        
        # Second highlight: "so loved the" (words 2-4) - overlaps
        highlight2 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=2),
            HighlightPosition(verse_index=0, word_index=4)
        )
        highlight2.highlight_count = 3
        
        passage.merge_overlapping_highlights()
        
        # Should be merged into one highlight covering words 1-4
        assert len(passage.highlights) == 1
        merged = passage.highlights[0]
        assert merged.start_position == HighlightPosition(verse_index=0, word_index=1)
        assert merged.end_position == HighlightPosition(verse_index=0, word_index=4)
        assert merged.highlight_count == 8  # 5 + 3
    
    def test_merge_adjacent_highlights(self):
        """Test merging adjacent highlights."""
        passage = self.create_sample_passage()
        
        # First highlight: "God so" (words 1-2)
        highlight1 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=2)
        )
        highlight1.highlight_count = 2
        
        # Second highlight: "loved" (word 3) - adjacent to first
        highlight2 = passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=3),
            HighlightPosition(verse_index=0, word_index=3)
        )
        highlight2.highlight_count = 4
        
        passage.merge_overlapping_highlights()
        
        # Should be merged into one highlight covering words 1-3
        assert len(passage.highlights) == 1
        merged = passage.highlights[0]
        assert merged.start_position == HighlightPosition(verse_index=0, word_index=1)
        assert merged.end_position == HighlightPosition(verse_index=0, word_index=3)
        assert merged.highlight_count == 6  # 2 + 4


class TestBiblePassageStringRepresentation:
    """Test string representation methods for BiblePassage."""
    
    def test_str_representation(self):
        """Test __str__ method returns readable format."""
        verses = [
            BibleVerse(book="John", chapter=3, verse=16, text="For God so loved the world"),
            BibleVerse(book="John", chapter=3, verse=17, text="For God did not send His Son")
        ]
        passage = BiblePassage(reference="John 3:16-17", verses=verses)
        
        # Add a highlight
        passage.add_highlight(
            HighlightPosition(verse_index=0, word_index=1),
            HighlightPosition(verse_index=0, word_index=3)
        )
        
        str_repr = str(passage)
        expected = "BiblePassage(John 3:16-17, 2 verses, 1 highlights)"
        assert str_repr == expected
    
    def test_repr_representation(self):
        """Test __repr__ method returns developer-friendly format."""
        verses = [
            BibleVerse(book="John", chapter=3, verse=16, text="For God so loved the world")
        ]
        passage = BiblePassage(reference="John 3:16", version="ESV", verses=verses)
        
        repr_str = repr(passage)
        assert "BiblePassage(" in repr_str
        assert "reference='John 3:16'" in repr_str
        assert "version='ESV'" in repr_str
        assert "verses=1" in repr_str
        assert "highlights=0" in repr_str


class TestBiblePassageEdgeCases:
    """Test edge cases and boundary conditions for BiblePassage."""
    
    def test_single_verse_passage(self):
        """Test passage with single verse."""
        verse = [BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept.")]
        passage = BiblePassage(reference="John 11:35", verses=verse)
        
        assert passage.total_verses == 1
        assert passage.total_words == 2
        assert passage.books == ["John"]
        assert passage.chapter_range == "11:35"
    
    def test_very_long_passage(self):
        """Test passage with many verses."""
        verses = []
        for i in range(1, 101):  # 100 verses
            verses.append(BibleVerse(
                book="Psalms", 
                chapter=119, 
                verse=i, 
                text=f"This is verse {i} with some text content."
            ))
        
        passage = BiblePassage(reference="Psalms 119:1-100", verses=verses)
        
        assert passage.total_verses == 100
        assert passage.total_words == 800  # 8 words per verse * 100 verses
        assert passage.books == ["Psalms"]
        assert passage.chapter_range == "119:1-100"
    
    def test_passage_with_complex_book_names(self):
        """Test passage with complex book names."""
        verses = [
            BibleVerse(book="1 Chronicles", chapter=1, verse=1, text="Adam Seth Enosh"),
            BibleVerse(book="2 Chronicles", chapter=1, verse=1, text="Now Solomon the son of David"),
            BibleVerse(book="Song of Solomon", chapter=1, verse=1, text="The song of songs")
        ]
        passage = BiblePassage(reference="Mixed Chronicles", verses=verses)
        
        assert passage.books == ["1 Chronicles", "2 Chronicles", "Song of Solomon"]
        assert passage.total_verses == 3
    
    def test_passage_with_custom_fetched_time(self):
        """Test passage with custom fetched_at time."""
        verses = [BibleVerse(book="John", chapter=3, verse=16, text="For God so loved")]
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        
        passage = BiblePassage(
            reference="John 3:16",
            verses=verses,
            fetched_at=custom_time
        )
        
        assert passage.fetched_at == custom_time
    
    def test_empty_highlights_list_operations(self):
        """Test operations on passage with empty highlights list."""
        verses = [BibleVerse(book="John", chapter=3, verse=16, text="For God so loved")]
        passage = BiblePassage(reference="John 3:16", verses=verses)
        
        assert passage.get_popular_highlights() == []
        assert passage.get_highlight_coverage() == 0.0
        
        # Merging empty list should not error
        passage.merge_overlapping_highlights()
        assert len(passage.highlights) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])