"""
Simple test script for BibleVerse model without pytest dependency.
"""

from src.bible_models import BibleVerse
from pydantic import ValidationError


def test_basic_functionality():
    """Test basic BibleVerse functionality."""
    print("Testing BibleVerse basic functionality...")
    
    # Test valid verse creation
    verse = BibleVerse(
        book="John",
        chapter=3,
        verse=16,
        text="For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
    )
    
    print(f"✓ Created verse: {verse.reference}")
    print(f"✓ Word count: {verse.word_count}")
    print(f"✓ Character count: {verse.char_count}")
    print(f"✓ Words: {verse.get_words()[:5]}...")  # First 5 words
    
    # Test validation
    try:
        invalid_verse = BibleVerse(book="", chapter=1, verse=1, text="Some text")
        print("✗ Should have failed validation for empty book")
        return False
    except ValidationError:
        print("✓ Correctly rejected empty book name")
    
    try:
        invalid_verse = BibleVerse(book="John", chapter=0, verse=1, text="Some text")
        print("✗ Should have failed validation for zero chapter")
        return False
    except ValidationError:
        print("✓ Correctly rejected zero chapter number")
    
    try:
        invalid_verse = BibleVerse(book="John", chapter=1, verse=0, text="Some text")
        print("✗ Should have failed validation for zero verse")
        return False
    except ValidationError:
        print("✓ Correctly rejected zero verse number")
    
    try:
        invalid_verse = BibleVerse(book="John", chapter=1, verse=1, text="")
        print("✗ Should have failed validation for empty text")
        return False
    except ValidationError:
        print("✓ Correctly rejected empty text")
    
    # Test properties
    short_verse = BibleVerse(book="John", chapter=11, verse=35, text="Jesus wept.")
    assert short_verse.word_count == 2, f"Expected 2 words, got {short_verse.word_count}"
    assert short_verse.char_count == 11, f"Expected 11 chars, got {short_verse.char_count}"
    assert short_verse.reference == "John 11:35", f"Expected 'John 11:35', got '{short_verse.reference}'"
    assert short_verse.get_words() == ["Jesus", "wept."], f"Expected ['Jesus', 'wept.'], got {short_verse.get_words()}"
    
    print("✓ All property calculations correct")
    
    # Test whitespace trimming
    trimmed_verse = BibleVerse(
        book="  John  ",
        chapter=3,
        verse=16,
        text="  For God so loved the world.  "
    )
    assert trimmed_verse.book == "John", f"Expected 'John', got '{trimmed_verse.book}'"
    assert trimmed_verse.text == "For God so loved the world.", f"Expected trimmed text, got '{trimmed_verse.text}'"
    
    print("✓ Whitespace trimming works correctly")
    
    # Test string representations
    str_repr = str(verse)
    expected_str = "John 3:16: For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
    assert str_repr == expected_str, f"String representation mismatch"
    print("✓ String representation correct")
    
    repr_str = repr(verse)
    assert "BibleVerse(" in repr_str, "Repr should contain 'BibleVerse('"
    assert "book='John'" in repr_str, "Repr should contain book info"
    assert "chapter=3" in repr_str, "Repr should contain chapter info"
    print("✓ Repr representation correct")
    
    print("\n🎉 All tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        if success:
            print("\nBibleVerse implementation is working correctly!")
        else:
            print("\nSome tests failed!")
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()