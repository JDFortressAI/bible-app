#!/usr/bin/env python3
"""
Tests for typography improvements in Bible text.
"""

import unittest
from src.bible_parser import apply_proper_typography, clean_verse_text


class TestTypography(unittest.TestCase):
    """Test typography improvements."""
    
    def test_double_quotes_conversion(self):
        """Test conversion of straight double quotes to proper typographic quotes."""
        input_text = 'He said, "Hello world."'  # Straight quotes
        result = apply_proper_typography(input_text)
        # Should have proper opening and closing quotes
        self.assertIn(chr(8220), result)  # Left double quote "
        self.assertIn(chr(8221), result)  # Right double quote "
        self.assertNotEqual(input_text, result)  # Should be different
    
    def test_apostrophes_conversion(self):
        """Test conversion of apostrophes in contractions."""
        input_text = "I don't understand."
        result = apply_proper_typography(input_text)
        # Should have proper apostrophe
        self.assertIn(chr(8217), result)  # Right single quote/apostrophe '
        
        # Test possessive
        input_text = "The Lord's blessing."
        result = apply_proper_typography(input_text)
        self.assertIn(chr(8217), result)  # Right single quote/apostrophe '
    
    def test_escaped_quotes_conversion(self):
        """Test conversion of escaped quotes."""
        # Test escaped double quotes
        input_text = 'He said, \\"Hello world.\\"'
        result = apply_proper_typography(input_text)
        # Should not have escaped quotes
        self.assertNotIn('\\"', result)
        self.assertIn(chr(8220), result)  # Left double quote "
        
        # Test escaped apostrophe
        input_text = "I don\\'t understand."
        result = apply_proper_typography(input_text)
        self.assertNotIn("\\'", result)
        self.assertIn(chr(8217), result)  # Right single quote/apostrophe '
    
    def test_em_dashes_conversion(self):
        """Test conversion of double hyphens to em dashes."""
        input_text = "He said--and this is important--that we should go."
        result = apply_proper_typography(input_text)
        # Should not have double hyphens
        self.assertNotIn("--", result)
        # Should have em dash (we'll check length changed)
        self.assertNotEqual(len(input_text), len(result))
    
    def test_ellipses_conversion(self):
        """Test conversion of multiple periods to proper ellipses."""
        input_text = "And then..."
        result = apply_proper_typography(input_text)
        # Should not have three periods
        self.assertNotIn("...", result)
        # Should be shorter (ellipsis is one character)
        self.assertLess(len(result), len(input_text))
    
    def test_clean_verse_text_with_typography(self):
        """Test that clean_verse_text applies typography improvements."""
        input_text = '1 He said, "I don\'t understand."'
        result = clean_verse_text(input_text)
        
        # Should remove verse number
        self.assertNotIn("1 ", result)
        # Should have proper quotes
        self.assertIn(chr(8220), result)  # Left double quote "
        self.assertIn(chr(8217), result)  # Right single quote/apostrophe '
    
    def test_yhwh_typography_basic(self):
        """Test YHWH divine name typography for basic cases."""
        from src.bible_parser import apply_yhwh_typography
        
        # Test primary cases
        input_text = "the Lord said to Moses"
        result = apply_yhwh_typography(input_text)
        self.assertIn("Lᴏʀᴅ", result)
        self.assertNotIn("Lord", result)
        
        # Test O Lord case
        input_text = "O Lord, hear my prayer"
        result = apply_yhwh_typography(input_text)
        self.assertIn("O Lᴏʀᴅ", result)
    
    def test_yhwh_typography_compound(self):
        """Test YHWH typography for compound names."""
        from src.bible_parser import apply_yhwh_typography
        
        # Test Lord God
        input_text = "O Lord God of Israel"
        result = apply_yhwh_typography(input_text)
        self.assertIn("O Lᴏʀᴅ God", result)
        
        # Test Lord of hosts
        input_text = "the Lord of hosts"
        result = apply_yhwh_typography(input_text)
        self.assertIn("Lᴏʀᴅ of hosts", result)
    
    def test_yhwh_typography_possessive(self):
        """Test YHWH typography with possessives."""
        from src.bible_parser import apply_yhwh_typography
        
        input_text = "the Lord's covenant"
        result = apply_yhwh_typography(input_text)
        self.assertIn("Lᴏʀᴅ's", result)
    
    def test_yhwh_typography_html(self):
        """Test YHWH typography with HTML markup."""
        from src.bible_parser import apply_yhwh_typography
        
        input_text = "the Lord said"
        result = apply_yhwh_typography(input_text, use_html=True)
        self.assertIn('<span class="small-caps">ORD</span>', result)
        self.assertIn('L<span class="small-caps">ORD</span>', result)
    
    def test_yhwh_typography_sentence_start(self):
        """Test YHWH typography at sentence beginnings."""
        from src.bible_parser import apply_yhwh_typography
        
        # Beginning of text
        input_text = "Lord, have mercy on us"
        result = apply_yhwh_typography(input_text)
        self.assertIn("Lᴏʀᴅ,", result)
        
        # After period
        input_text = "He prayed. Lord, help us."
        result = apply_yhwh_typography(input_text)
        self.assertIn(". Lᴏʀᴅ,", result)


if __name__ == '__main__':
    unittest.main()