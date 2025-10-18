"""
Unit tests for Bible text parser functionality.

Tests various M'Cheyne passage formats and edge cases for the Bible text parsing system.
"""

import pytest
from datetime import datetime
from src.bible_parser import (
    parse_bible_reference,
    normalize_book_name,
    clean_verse_text,
    extract_verses_from_text,
    parse_bible_text,
    parse_mcheyne_passage_list
)
from src.bible_models import BibleVerse, BiblePassage


class TestParseBibleReference:
    """Test Bible reference parsing functionality."""
    
    def test_single_verse_reference(self):
        """Test parsing single verse references."""
        book, chapter, verse, end_verse = parse_bible_reference("John 3:16")
        assert book == "John"
        assert chapter == 3
        assert verse == 16
        assert end_verse is None
    
    def test_verse_range_reference(self):
        """Test parsing verse range references."""
        book, chapter, start_verse, end_verse = parse_bible_reference("Luke 1:1-38")
        assert book == "Luke"
        assert chapter == 1
        assert start_verse == 1
        assert end_verse == 38
    
    def test_cross_chapter_reference(self):
        """Test parsing cross-chapter references."""
        book, chapter, verse, end_verse = parse_bible_reference("Zechariah 12:1-13:1")
        assert book == "Zechariah"
        assert chapter == 12
        assert verse == 1
        assert end_verse is None  # Cross-chapter ranges return None for end_verse
    
    def test_whole_chapter_reference(self):
        """Test parsing whole chapter references."""
        book, chapter, verse, end_verse = parse_bible_reference("Genesis 1")
        assert book == "Genesis"
        assert chapter == 1
        assert verse == 1
        assert end_verse is None
    
    def test_numbered_book_reference(self):
        """Test parsing references with numbered books."""
        book, chapter, verse, end_verse = parse_bible_reference("1 Kings 15")
        assert book == "1 Kings"
        assert chapter == 15
        assert verse == 1
        assert end_verse is None
    
    def test_psalm_range_reference(self):
        """Test parsing Psalm range references."""
        book, chapter, verse, end_verse = parse_bible_reference("Psalm 119:1-24")
        assert book == "Psalm"
        assert chapter == 119
        assert verse == 1
        assert end_verse == 24
    
    def test_invalid_reference(self):
        """Test handling of invalid references."""
        with pytest.raises(ValueError, match="Could not parse Bible reference"):
            parse_bible_reference("Invalid Reference")
    
    def test_empty_reference(self):
        """Test handling of empty references."""
        with pytest.raises(ValueError, match="Could not parse Bible reference"):
            parse_bible_reference("")


class TestNormalizeBookName:
    """Test book name normalization functionality."""
    
    def test_common_abbreviations(self):
        """Test common book abbreviations."""
        assert normalize_book_name("gen") == "Genesis"
        assert normalize_book_name("matt") == "Matthew"
        assert normalize_book_name("ps") == "Psalms"
        assert normalize_book_name("rev") == "Revelation"
    
    def test_numbered_books(self):
        """Test numbered book normalization."""
        assert normalize_book_name("1kings") == "1 Kings"
        assert normalize_book_name("1 sam") == "1 Samuel"
        assert normalize_book_name("2cor") == "2 Corinthians"
        assert normalize_book_name("1 john") == "1 John"
    
    def test_case_insensitive(self):
        """Test case insensitive normalization."""
        assert normalize_book_name("GENESIS") == "Genesis"
        assert normalize_book_name("Matthew") == "Matthew"
        assert normalize_book_name("psalms") == "Psalms"
    
    def test_unknown_book(self):
        """Test handling of unknown book names."""
        result = normalize_book_name("unknown book")
        assert result == "Unknown Book"  # Should return title case
    
    def test_whitespace_handling(self):
        """Test whitespace handling in book names."""
        assert normalize_book_name("  genesis  ") == "Genesis"
        assert normalize_book_name("1  kings") == "1 Kings"


class TestCleanVerseText:
    """Test verse text cleaning functionality."""
    
    def test_remove_verse_numbers(self):
        """Test removal of leading verse numbers."""
        text = "16 For God so loved the world..."
        result = clean_verse_text(text)
        assert result == "For God so loved the world..."
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "For   God\tso\nloved   the world"
        result = clean_verse_text(text)
        assert result == "For God so loved the world"
    
    def test_remove_web_artifacts(self):
        """Test removal of web artifacts."""
        text = "For God so loved [See note] the world (cf. John 1:1)"
        result = clean_verse_text(text)
        # Should remove bracketed notes but keep legitimate parentheses
        assert "[See note]" not in result
        assert "For God so loved the world" in result
    
    def test_empty_text(self):
        """Test handling of empty text."""
        assert clean_verse_text("") == ""
        assert clean_verse_text("   ") == ""
    
    def test_preserve_punctuation(self):
        """Test preservation of legitimate punctuation."""
        text = "Jesus said, \"I am the way, the truth, and the life.\""
        result = clean_verse_text(text)
        assert "\"" in result
        assert "," in result
        assert "." in result


class TestExtractVersesFromText:
    """Test verse extraction from text blocks."""
    
    def test_numbered_verses(self):
        """Test extraction of numbered verses."""
        text = "1 In the beginning God created the heavens and the earth. 2 The earth was without form, and void."
        verses = extract_verses_from_text(text, "Genesis", 1, 1, 2)
        
        assert len(verses) == 2
        assert verses[0].verse == 1
        assert verses[0].text == "In the beginning God created the heavens and the earth."
        assert verses[1].verse == 2
        assert verses[1].text == "The earth was without form, and void."
    
    def test_single_verse_text(self):
        """Test extraction of single verse without numbers."""
        text = "For God so loved the world that He gave His only begotten Son."
        verses = extract_verses_from_text(text, "John", 3, 16)
        
        assert len(verses) == 1
        assert verses[0].book == "John"
        assert verses[0].chapter == 3
        assert verses[0].verse == 16
        assert verses[0].text == text
    
    def test_verse_range_splitting(self):
        """Test intelligent splitting of verse ranges."""
        text = "Blessed is the man who walks not in the counsel of the ungodly. Nor stands in the path of sinners. Nor sits in the seat of the scornful."
        verses = extract_verses_from_text(text, "Psalms", 1, 1, 3)
        
        assert len(verses) >= 1  # Should create at least one verse
        assert verses[0].book == "Psalms"
        assert verses[0].chapter == 1
    
    def test_empty_text(self):
        """Test handling of empty text."""
        verses = extract_verses_from_text("", "Genesis", 1, 1)
        assert len(verses) == 0
    
    def test_book_name_normalization(self):
        """Test that book names are normalized during extraction."""
        text = "In the beginning God created the heavens and the earth."
        verses = extract_verses_from_text(text, "gen", 1, 1)
        
        assert len(verses) == 1
        assert verses[0].book == "Genesis"


class TestParseBibleText:
    """Test complete Bible text parsing functionality."""
    
    def test_simple_passage_parsing(self):
        """Test parsing a simple passage."""
        text = "16 For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
        passage = parse_bible_text(text, "John 3:16")
        
        assert passage.reference == "John 3:16"
        assert passage.version == "NKJV"
        assert len(passage.verses) == 1
        assert passage.verses[0].book == "John"
        assert passage.verses[0].chapter == 3
        assert passage.verses[0].verse == 16
        assert "For God so loved the world" in passage.verses[0].text
    
    def test_verse_range_parsing(self):
        """Test parsing a verse range."""
        text = "1 Inasmuch as many have taken in hand to set in order a narrative. 2 Just as those who from the beginning were eyewitnesses."
        passage = parse_bible_text(text, "Luke 1:1-2")
        
        assert passage.reference == "Luke 1:1-2"
        assert len(passage.verses) >= 1
        assert passage.verses[0].book == "Luke"
        assert passage.verses[0].chapter == 1
    
    def test_cross_chapter_reference(self):
        """Test parsing cross-chapter references."""
        text = "The burden of the word of the Lord against Israel. In that day a fountain shall be opened."
        passage = parse_bible_text(text, "Zechariah 12:1-13:1")
        
        assert passage.reference == "Zechariah 12:1-13:1"
        assert len(passage.verses) >= 1
        assert passage.verses[0].book == "Zechariah"
    
    def test_custom_version(self):
        """Test parsing with custom Bible version."""
        text = "For God so loved the world..."
        passage = parse_bible_text(text, "John 3:16", "ESV")
        
        assert passage.version == "ESV"
    
    def test_empty_text_error(self):
        """Test error handling for empty text."""
        with pytest.raises(ValueError, match="Raw text cannot be empty"):
            parse_bible_text("", "John 3:16")
    
    def test_empty_reference_error(self):
        """Test error handling for empty reference."""
        with pytest.raises(ValueError, match="Reference cannot be empty"):
            parse_bible_text("Some text", "")
    
    def test_invalid_reference_error(self):
        """Test error handling for invalid reference."""
        with pytest.raises(ValueError, match="Invalid Bible reference"):
            parse_bible_text("Some text", "Invalid Reference")
    
    def test_passage_metadata(self):
        """Test that passage metadata is properly set."""
        text = "For God so loved the world..."
        passage = parse_bible_text(text, "John 3:16")
        
        assert isinstance(passage.fetched_at, datetime)
        assert passage.total_verses == 1
        assert passage.total_words > 0
        assert passage.books == ["John"]


class TestParseMcheynePassageList:
    """Test M'Cheyne passage list parsing functionality."""
    
    def test_multiple_passages(self):
        """Test parsing multiple passages."""
        passage_texts = {
            "John 3:16": "For God so loved the world...",
            "Genesis 1:1": "In the beginning God created the heavens and the earth.",
            "Psalm 23:1": "The Lord is my shepherd; I shall not want."
        }
        
        passages = parse_mcheyne_passage_list(passage_texts)
        
        assert len(passages) == 3
        assert "John 3:16" in passages
        assert "Genesis 1:1" in passages
        assert "Psalm 23:1" in passages
        
        # Check that each passage is properly parsed
        john_passage = passages["John 3:16"]
        assert john_passage.verses[0].book == "John"
        assert john_passage.verses[0].chapter == 3
        assert john_passage.verses[0].verse == 16
    
    def test_custom_version(self):
        """Test parsing with custom version."""
        passage_texts = {"John 3:16": "For God so loved the world..."}
        passages = parse_mcheyne_passage_list(passage_texts, "ESV")
        
        assert passages["John 3:16"].version == "ESV"
    
    def test_invalid_passage_fallback(self):
        """Test fallback handling for invalid passages."""
        passage_texts = {
            "John 3:16": "For God so loved the world...",
            "Invalid Reference": "Some text that can't be parsed properly"
        }
        
        passages = parse_mcheyne_passage_list(passage_texts)
        
        # Should still parse the valid passage
        assert "John 3:16" in passages
        assert passages["John 3:16"].verses[0].book == "John"
        
        # Should create fallback for invalid reference if possible
        # (This depends on implementation - might skip invalid ones)
    
    def test_empty_input(self):
        """Test handling of empty input."""
        passages = parse_mcheyne_passage_list({})
        assert len(passages) == 0


class TestComplexMcheyneFormats:
    """Test complex M'Cheyne reading formats."""
    
    def test_luke_1_1_38_format(self):
        """Test Luke 1:1-38 format (long verse range)."""
        # Simulate a long passage with multiple verses
        text = """1 Inasmuch as many have taken in hand to set in order a narrative of those things which have been fulfilled among us, 2 just as those who from the beginning were eyewitnesses and ministers of the word delivered them to us, 3 it seemed good to me also, having had perfect understanding of all things from the very first, to write to you an orderly account, most excellent Theophilus."""
        
        passage = parse_bible_text(text, "Luke 1:1-38")
        
        assert passage.reference == "Luke 1:1-38"
        assert len(passage.verses) >= 1
        assert passage.verses[0].book == "Luke"
        assert passage.verses[0].chapter == 1
        assert passage.total_words > 20  # Should have substantial content
    
    def test_zechariah_12_1_13_1_format(self):
        """Test Zechariah 12:1-13:1 format (cross-chapter range)."""
        text = "The burden of the word of the Lord against Israel. Thus says the Lord, who stretches out the heavens, lays the foundation of the earth, and forms the spirit of man within him. In that day a fountain shall be opened for the house of David and for the inhabitants of Jerusalem, for sin and for uncleanness."
        
        passage = parse_bible_text(text, "Zechariah 12:1-13:1")
        
        assert passage.reference == "Zechariah 12:1-13:1"
        assert len(passage.verses) >= 1
        assert passage.verses[0].book == "Zechariah"
        assert passage.verses[0].chapter == 12
    
    def test_psalm_119_1_24_format(self):
        """Test Psalm 119:1-24 format (long psalm section)."""
        text = """1 Blessed are the undefiled in the way, Who walk in the law of the Lord! 2 Blessed are those who keep His testimonies, Who seek Him with the whole heart! 3 They also do no iniquity; They walk in His ways."""
        
        passage = parse_bible_text(text, "Psalm 119:1-24")
        
        assert passage.reference == "Psalm 119:1-24"
        assert len(passage.verses) >= 1
        assert passage.verses[0].book == "Psalms"  # Should normalize to "Psalms"
        assert passage.verses[0].chapter == 119
    
    def test_whole_chapter_format(self):
        """Test whole chapter format like 'Genesis 1'."""
        text = """1 In the beginning God created the heavens and the earth. 2 The earth was without form, and void; and darkness was on the face of the deep. And the Spirit of God was hovering over the face of the waters. 3 Then God said, "Let there be light"; and there was light."""
        
        passage = parse_bible_text(text, "Genesis 1")
        
        assert passage.reference == "Genesis 1"
        assert len(passage.verses) >= 1
        assert passage.verses[0].book == "Genesis"
        assert passage.verses[0].chapter == 1
    
    def test_numbered_book_format(self):
        """Test numbered book format like '1 Kings 15'."""
        text = "Now in the eighteenth year of King Jeroboam the son of Nebat, Abijam became king over Judah."
        
        passage = parse_bible_text(text, "1 Kings 15")
        
        assert passage.reference == "1 Kings 15"
        assert len(passage.verses) >= 1
        assert passage.verses[0].book == "1 Kings"
        assert passage.verses[0].chapter == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])