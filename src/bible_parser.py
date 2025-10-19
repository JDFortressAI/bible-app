"""
Bible Text Parser for M'Cheyne Integration

This module provides functions to parse raw Bible text into structured BibleVerse objects,
handling complex verse ranges and text normalization for the M'Cheyne reading system.
"""

import re
from typing import List, Tuple, Optional, Dict
from bible_models import BibleVerse, BiblePassage
from datetime import datetime


def parse_bible_reference(reference: str) -> Tuple[str, int, int, Optional[int]]:
    """
    Parse a Bible reference into its components.
    
    Args:
        reference: Bible reference string (e.g., "Luke 1:1-38", "Genesis 1", "Psalm 119:1")
        
    Returns:
        Tuple of (book, start_chapter, start_verse, end_verse)
        end_verse is None for single verse or chapter references
        
    Examples:
        "Luke 1:1-38" -> ("Luke", 1, 1, 38)
        "Genesis 1" -> ("Genesis", 1, 1, None)  # Whole chapter
        "John 3:16" -> ("John", 3, 16, None)   # Single verse
        "Zechariah 12:1-13:1" -> ("Zechariah", 12, 1, None)  # Cross-chapter range
    """
    reference = reference.strip()
    
    # Pattern for complex references like "Zechariah 12:1-13:1"
    cross_chapter_pattern = r'(\d?\s*[A-Za-z]+)\s+(\d+):(\d+)-(\d+):(\d+)'
    match = re.match(cross_chapter_pattern, reference)
    if match:
        book = match.group(1).strip()
        start_chapter = int(match.group(2))
        start_verse = int(match.group(3))
        # For cross-chapter ranges, we'll handle them specially
        return book, start_chapter, start_verse, None
    
    # Pattern for verse ranges within a chapter like "Luke 1:1-38"
    verse_range_pattern = r'(\d?\s*[A-Za-z]+)\s+(\d+):(\d+)-(\d+)'
    match = re.match(verse_range_pattern, reference)
    if match:
        book = match.group(1).strip()
        chapter = int(match.group(2))
        start_verse = int(match.group(3))
        end_verse = int(match.group(4))
        return book, chapter, start_verse, end_verse
    
    # Pattern for single verse like "John 3:16"
    single_verse_pattern = r'(\d?\s*[A-Za-z]+)\s+(\d+):(\d+)'
    match = re.match(single_verse_pattern, reference)
    if match:
        book = match.group(1).strip()
        chapter = int(match.group(2))
        verse = int(match.group(3))
        return book, chapter, verse, None
    
    # Pattern for whole chapter like "Genesis 1"
    chapter_pattern = r'(\d?\s*[A-Za-z]+)\s+(\d+)'
    match = re.match(chapter_pattern, reference)
    if match:
        book = match.group(1).strip()
        chapter = int(match.group(2))
        return book, chapter, 1, None  # Start from verse 1
    
    raise ValueError(f"Could not parse Bible reference: {reference}")


def normalize_book_name(book: str) -> str:
    """
    Normalize book names to standard format.
    
    Args:
        book: Raw book name from text
        
    Returns:
        Standardized book name
        
    Examples:
        "1kings" -> "1 Kings"
        "psalm" -> "Psalms"
        "matt" -> "Matthew"
    """
    book = book.strip()
    
    # Common book name mappings
    book_mappings = {
        # Old Testament
        'gen': 'Genesis', 'genesis': 'Genesis',
        'ex': 'Exodus', 'exod': 'Exodus', 'exodus': 'Exodus',
        'lev': 'Leviticus', 'leviticus': 'Leviticus',
        'num': 'Numbers', 'numbers': 'Numbers',
        'deut': 'Deuteronomy', 'deuteronomy': 'Deuteronomy',
        'josh': 'Joshua', 'joshua': 'Joshua',
        'judg': 'Judges', 'judges': 'Judges',
        'ruth': 'Ruth',
        '1sam': '1 Samuel', '1 sam': '1 Samuel', '1samuel': '1 Samuel',
        '2sam': '2 Samuel', '2 sam': '2 Samuel', '2samuel': '2 Samuel',
        '1kings': '1 Kings', '1 kings': '1 Kings', '1kgs': '1 Kings',
        '2kings': '2 Kings', '2 kings': '2 Kings', '2kgs': '2 Kings',
        '1chr': '1 Chronicles', '1 chr': '1 Chronicles', '1chronicles': '1 Chronicles',
        '2chr': '2 Chronicles', '2 chr': '2 Chronicles', '2chronicles': '2 Chronicles',
        'ezra': 'Ezra',
        'neh': 'Nehemiah', 'nehemiah': 'Nehemiah',
        'esth': 'Esther', 'esther': 'Esther',
        'job': 'Job',
        'ps': 'Psalms', 'psalm': 'Psalms', 'psalms': 'Psalms', 'psa': 'Psalms',
        'prov': 'Proverbs', 'proverbs': 'Proverbs',
        'eccl': 'Ecclesiastes', 'ecclesiastes': 'Ecclesiastes', 'ecc': 'Ecclesiastes',
        'song': 'Song of Solomon', 'songs': 'Song of Solomon', 'sos': 'Song of Solomon',
        'isa': 'Isaiah', 'isaiah': 'Isaiah',
        'jer': 'Jeremiah', 'jeremiah': 'Jeremiah',
        'lam': 'Lamentations', 'lamentations': 'Lamentations',
        'ezek': 'Ezekiel', 'ezekiel': 'Ezekiel',
        'dan': 'Daniel', 'daniel': 'Daniel',
        'hos': 'Hosea', 'hosea': 'Hosea',
        'joel': 'Joel',
        'amos': 'Amos',
        'obad': 'Obadiah', 'obadiah': 'Obadiah',
        'jonah': 'Jonah',
        'mic': 'Micah', 'micah': 'Micah',
        'nah': 'Nahum', 'nahum': 'Nahum',
        'hab': 'Habakkuk', 'habakkuk': 'Habakkuk',
        'zeph': 'Zephaniah', 'zephaniah': 'Zephaniah',
        'hag': 'Haggai', 'haggai': 'Haggai',
        'zech': 'Zechariah', 'zechariah': 'Zechariah',
        'mal': 'Malachi', 'malachi': 'Malachi',
        
        # New Testament
        'matt': 'Matthew', 'matthew': 'Matthew', 'mt': 'Matthew',
        'mark': 'Mark', 'mk': 'Mark',
        'luke': 'Luke', 'lk': 'Luke',
        'john': 'John', 'jn': 'John',
        'acts': 'Acts',
        'rom': 'Romans', 'romans': 'Romans',
        '1cor': '1 Corinthians', '1 cor': '1 Corinthians', '1corinthians': '1 Corinthians',
        '2cor': '2 Corinthians', '2 cor': '2 Corinthians', '2corinthians': '2 Corinthians',
        'gal': 'Galatians', 'galatians': 'Galatians',
        'eph': 'Ephesians', 'ephesians': 'Ephesians',
        'phil': 'Philippians', 'philippians': 'Philippians',
        'col': 'Colossians', 'colossians': 'Colossians',
        '1thess': '1 Thessalonians', '1 thess': '1 Thessalonians', '1thessalonians': '1 Thessalonians',
        '2thess': '2 Thessalonians', '2 thess': '2 Thessalonians', '2thessalonians': '2 Thessalonians',
        '1tim': '1 Timothy', '1 tim': '1 Timothy', '1timothy': '1 Timothy',
        '2tim': '2 Timothy', '2 tim': '2 Timothy', '2timothy': '2 Timothy',
        'titus': 'Titus',
        'philem': 'Philemon', 'philemon': 'Philemon',
        'heb': 'Hebrews', 'hebrews': 'Hebrews',
        'jas': 'James', 'james': 'James',
        '1pet': '1 Peter', '1 pet': '1 Peter', '1peter': '1 Peter',
        '2pet': '2 Peter', '2 pet': '2 Peter', '2peter': '2 Peter',
        '1john': '1 John', '1 john': '1 John', '1jn': '1 John',
        '2john': '2 John', '2 john': '2 John', '2jn': '2 John',
        '3john': '3 John', '3 john': '3 John', '3jn': '3 John',
        'jude': 'Jude',
        'rev': 'Revelation', 'revelation': 'Revelation'
    }
    
    # Try exact match first
    book_lower = book.lower()
    if book_lower in book_mappings:
        return book_mappings[book_lower]
    
    # Handle numbered books with spaces
    numbered_book_pattern = r'^(\d+)\s*([a-z]+)$'
    match = re.match(numbered_book_pattern, book_lower)
    if match:
        number = match.group(1)
        book_name = match.group(2)
        full_key = f"{number}{book_name}"
        if full_key in book_mappings:
            return book_mappings[full_key]
    
    # If no mapping found, return title case version
    return book.title()


def clean_verse_text(text: str, book: str = None) -> str:
    """
    Clean and normalize verse text.
    
    Args:
        text: Raw verse text from web scraping
        book: Bible book name (used for YHWH typography context)
        
    Returns:
        Cleaned verse text with proper typography
    """
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove verse numbers at the beginning ONLY if this is already an isolated verse
    # (Don't remove them if we're still parsing the full text)
    if not re.search(r'\d+\s+.*?\d+\s+', text):  # Only if no multiple verse numbers
        text = re.sub(r'^\d+\s*', '', text)
    
    # Normalize whitespace (replace multiple spaces/tabs/newlines with single space)
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common web artifacts but be conservative
    web_artifacts = [
        r'\[a\]',  # Remove footnote markers like [a]
        r'\[b\]',  # Remove footnote markers like [b]
        r'\[c\]',  # Remove footnote markers like [c]
    ]
    
    for pattern in web_artifacts:
        text = re.sub(pattern, '', text)
    
    # Remove bracketed content only if it looks like a note
    bracketed_content = re.findall(r'\[.*?\]', text)
    for match in bracketed_content:
        if any(word in match.lower() for word in ['note', 'see', 'cf', 'compare', 'lit', 'or']):
            text = text.replace(match, '')
    
    # Clean up any double spaces created by removals
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Apply proper typography (with book context for YHWH typography)
    text = apply_proper_typography(text, book)
    
    return text


def apply_proper_typography(text: str, book: str = None) -> str:
    """
    Apply proper typographic quotes and punctuation to text.
    
    Args:
        text: Text with straight quotes and basic punctuation
        book: Bible book name (used for YHWH typography context)
        
    Returns:
        Text with proper typographic quotes and punctuation
    """
    if not text:
        return ""
    
    # Replace escaped quotes first
    text = text.replace('\\"', '"')
    text = text.replace("\\'", "'")
    
    # Handle apostrophes first (before quote processing)
    # This prevents apostrophes from being treated as quotes
    apostrophe_patterns = [
        (r"\b(\w+)'(s|t|re|ve|ll|d|m)\b", r"\1" + chr(8217) + r"\2"),  # it's, don't, we're, I've, I'll, I'd, I'm
        (r"\b(\w+)'(\w+)\b", r"\1" + chr(8217) + r"\2"),  # general contractions
        (r"(\w+)n't\b", r"\1n" + chr(8217) + r"t"),  # won't, can't, etc.
        (r"(\w+)s'\b", r"\1s" + chr(8217)),  # possessive plural: boys', wits'
    ]
    
    for pattern, replacement in apostrophe_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Convert straight double quotes to proper typographic quotes
    # Use a more sophisticated approach that considers context
    text = convert_double_quotes(text)
    
    # Convert remaining straight single quotes to proper typographic quotes
    text = convert_single_quotes(text)
    
    # Handle em dashes (replace double hyphens)
    text = text.replace('--', '—')
    
    # Handle ellipses
    text = re.sub(r'\.{3,}', '…', text)
    
    # Handle YHWH divine name typography (Old Testament only)
    text = apply_yhwh_typography(text, book)
    
    return text


def convert_double_quotes(text: str) -> str:
    """
    Convert straight double quotes to proper typographic quotes using context.
    
    Args:
        text: Text with straight double quotes
        
    Returns:
        Text with proper typographic double quotes
    """
    if '"' not in text:
        return text
    
    result = ""
    i = 0
    quote_stack = []  # Stack to track nested quotes
    
    while i < len(text):
        char = text[i]
        
        if char == '"':
            # Determine if this should be an opening or closing quote
            # Look at the character before and after
            prev_char = text[i-1] if i > 0 else ' '
            next_char = text[i+1] if i < len(text) - 1 else ' '
            
            # Rules for opening quotes:
            # 1. After whitespace, punctuation, or start of string
            # 2. Not immediately after a letter (unless it's after punctuation)
            is_opening = (
                prev_char.isspace() or 
                prev_char in '([{-—' or 
                i == 0 or
                (prev_char in '.,;:!?' and next_char.isalnum())
            )
            
            # Rules for closing quotes:
            # 1. Before whitespace, punctuation, or end of string
            # 2. After a letter or punctuation
            is_closing = (
                next_char.isspace() or 
                next_char in ')]}.,;:!?-—' or 
                i == len(text) - 1 or
                prev_char.isalnum()
            )
            
            # Handle nested quotes by using the stack
            if is_opening and not is_closing:
                result += chr(8220)  # Left double quote "
                quote_stack.append('double')
            elif is_closing and not is_opening:
                result += chr(8221)  # Right double quote "
                if quote_stack and quote_stack[-1] == 'double':
                    quote_stack.pop()
            else:
                # Ambiguous case - use stack to decide
                if not quote_stack or quote_stack[-1] != 'double':
                    # No open quote, so this is opening
                    result += chr(8220)  # Left double quote "
                    quote_stack.append('double')
                else:
                    # There's an open quote, so this is closing
                    result += chr(8221)  # Right double quote "
                    quote_stack.pop()
        else:
            result += char
        
        i += 1
    
    return result


def convert_single_quotes(text: str) -> str:
    """
    Convert remaining straight single quotes to proper typographic quotes.
    
    Args:
        text: Text with straight single quotes (after apostrophes have been handled)
        
    Returns:
        Text with proper typographic single quotes
    """
    if "'" not in text:
        return text
    
    result = ""
    i = 0
    quote_stack = []
    
    while i < len(text):
        char = text[i]
        
        if char == "'":
            # Check if this is likely an apostrophe that wasn't caught earlier
            prev_char = text[i-1] if i > 0 else ' '
            next_char = text[i+1] if i < len(text) - 1 else ' '
            
            # Additional apostrophe patterns
            if prev_char.isalpha() and (next_char.isspace() or next_char in '.,;:!?)]}'):
                # This is likely a possessive or contraction at word end
                result += chr(8217)  # Right single quote/apostrophe '
            elif prev_char.isalpha() and next_char.isalpha():
                # This is likely an apostrophe within a word
                result += chr(8217)  # Right single quote/apostrophe '
            else:
                # This is likely a quotation mark
                # Use similar logic as double quotes
                is_opening = (
                    prev_char.isspace() or 
                    prev_char in '([{-—"' or 
                    i == 0
                )
                
                is_closing = (
                    next_char.isspace() or 
                    next_char in ')]}.,;:!?-—"' or 
                    i == len(text) - 1
                )
                
                if is_opening and not is_closing:
                    result += chr(8216)  # Left single quote '
                    quote_stack.append('single')
                elif is_closing and not is_opening:
                    result += chr(8217)  # Right single quote '
                    if quote_stack and quote_stack[-1] == 'single':
                        quote_stack.pop()
                else:
                    # Use stack to decide
                    if not quote_stack or quote_stack[-1] != 'single':
                        result += chr(8216)  # Left single quote '
                        quote_stack.append('single')
                    else:
                        result += chr(8217)  # Right single quote '
                        quote_stack.pop()
        else:
            result += char
        
        i += 1
    
    return result


def is_old_testament_book(book: str) -> bool:
    """
    Determine if a Bible book is from the Old Testament.
    
    Args:
        book: Bible book name
        
    Returns:
        True if Old Testament, False if New Testament
    """
    if not book:
        return False
    
    book_lower = book.lower().strip()
    
    # Old Testament books
    old_testament_books = {
        # Torah/Pentateuch
        'genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy',
        
        # Historical Books
        'joshua', 'judges', 'ruth', '1 samuel', '2 samuel', '1 kings', '2 kings',
        '1 chronicles', '2 chronicles', 'ezra', 'nehemiah', 'esther',
        
        # Wisdom Literature
        'job', 'psalms', 'psalm', 'proverbs', 'ecclesiastes', 'song of solomon', 'song of songs',
        
        # Major Prophets
        'isaiah', 'jeremiah', 'lamentations', 'ezekiel', 'daniel',
        
        # Minor Prophets
        'hosea', 'joel', 'amos', 'obadiah', 'jonah', 'micah', 'nahum', 'habakkuk',
        'zephaniah', 'haggai', 'zechariah', 'malachi'
    }
    
    return book_lower in old_testament_books


def apply_yhwh_typography(text: str, book: str = None, use_html: bool = False) -> str:
    """
    Apply proper typography for the divine name YHWH (rendered as "Lord" in most translations).
    
    In Hebrew Bible tradition, YHWH (the tetragrammaton) is typically rendered in English
    translations as "LORD" in small caps to distinguish it from Adonai ("Lord").
    
    This function only applies YHWH typography to Old Testament passages, as "Lord" in the
    New Testament typically refers to Jesus Christ, not the tetragrammaton.
    
    Args:
        text: Text containing potential YHWH references
        book: Bible book name (used to determine Old vs New Testament)
        use_html: If True, use HTML markup; if False, use Unicode small caps
        
    Returns:
        Text with proper YHWH typography applied (Old Testament only)
    """
    if not text:
        return ""
    
    # Only apply YHWH typography to Old Testament books
    if book and not is_old_testament_book(book):
        return text
    
    # Define YHWH patterns - these represent the tetragrammaton YHWH
    # Most English translations render YHWH as "LORD" in small caps
    # Use case-insensitive patterns with capture groups to preserve original case
    yhwh_patterns = [
        # Primary patterns (99.9% of cases) - preserve case of "the/The"
        (r'\b(the|The) Lord\b', r'\1 L{small_caps}ORD{/small_caps}'),
        (r'\b(O|o) Lord\b', r'\1 L{small_caps}ORD{/small_caps}'),
        
        # Complex compound patterns
        (r'\b(the|The) Lord God\b', r'\1 L{small_caps}ORD{/small_caps} God'),
        (r'\b(O|o) Lord God\b', r'\1 L{small_caps}ORD{/small_caps} God'),
        (r'\bLord God\b', 'L{small_caps}ORD{/small_caps} God'),
        
        # Additional YHWH compound names
        (r'\b(the|The) Lord of hosts\b', r'\1 L{small_caps}ORD{/small_caps} of hosts'),
        (r'\b(O|o) Lord of hosts\b', r'\1 L{small_caps}ORD{/small_caps} of hosts'),
        (r'\bLord of hosts\b', 'L{small_caps}ORD{/small_caps} of hosts'),
        
        # YHWH with possessive
        (r'\b(the|The) Lord\'s\b', r'\1 L{small_caps}ORD{/small_caps}\'s'),
        (r'\bLord\'s\b', 'L{small_caps}ORD{/small_caps}\'s'),
        
        # Standalone Lord at sentence beginning (likely YHWH in most contexts)
        (r'^Lord\b', 'L{small_caps}ORD{/small_caps}'),
        (r'(?<=\. )Lord\b', 'L{small_caps}ORD{/small_caps}'),
        (r'(?<=\! )Lord\b', 'L{small_caps}ORD{/small_caps}'),
        (r'(?<=\? )Lord\b', 'L{small_caps}ORD{/small_caps}'),
    ]
    
    # Apply patterns (now with case preservation through capture groups)
    for pattern, replacement in yhwh_patterns:
        if use_html:
            # Use HTML markup for web display
            html_replacement = replacement.replace(
                '{small_caps}', '<span class="small-caps">'
            ).replace('{/small_caps}', '</span>')
            text = re.sub(pattern, html_replacement, text)
        else:
            # Use Unicode small caps characters for plain text
            # Unicode small caps: ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ
            small_caps_replacement = replacement.replace(
                '{small_caps}ORD{/small_caps}', 'ᴏʀᴅ'
            )
            text = re.sub(pattern, small_caps_replacement, text)
    
    return text


def extract_verses_from_text(text: str, book: str, chapter: int, start_verse: int = 1, end_verse: Optional[int] = None) -> List[BibleVerse]:
    """
    Extract individual verses from a block of Bible text.
    
    Args:
        text: Raw Bible text containing multiple verses
        book: Book name
        chapter: Chapter number
        start_verse: Starting verse number
        end_verse: Ending verse number (None for single verse or unknown end)
        
    Returns:
        List of BibleVerse objects
    """
    verses = []
    
    if not text.strip():
        return verses
    
    # Normalize the text first
    text = text.strip()
    
    # Try multiple verse number patterns to handle different formats
    verse_patterns = [
        r'(\d+)\s+([^0-9]+?)(?=\s*\d+\s+|$)',  # "1 Text here 2 More text"
        r'(\d+)\.\s*([^0-9]+?)(?=\s*\d+\.|$)',  # "1. Text here 2. More text"
        r'(\d+):\s*([^0-9]+?)(?=\s*\d+:|$)',   # "1: Text here 2: More text"
    ]
    
    verses_found = False
    
    for pattern in verse_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        if matches and len(matches) > 1:  # Only use if we find multiple verses
            verses_found = True
            print(f"Found {len(matches)} verses using pattern: {pattern}")
            
            for verse_num_str, verse_text in matches:
                try:
                    verse_num = int(verse_num_str)
                    cleaned_text = clean_verse_text(verse_text, book)
                    
                    if cleaned_text and len(cleaned_text) > 10:  # Filter out very short text
                        verses.append(BibleVerse(
                            book=normalize_book_name(book),
                            chapter=chapter,
                            verse=verse_num,
                            text=cleaned_text
                        ))
                except ValueError:
                    continue
            
            if verses:
                # Sort verses by verse number to ensure correct order
                verses.sort(key=lambda v: v.verse)
                return verses
    
    # If no clear verse patterns found, try splitting by line breaks and looking for verse numbers
    if not verses_found:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            # Look for lines that start with a number
            match = re.match(r'^(\d+)\s+(.+)', line)
            if match:
                verse_num_str, verse_text = match.groups()
                try:
                    verse_num = int(verse_num_str)
                    cleaned_text = clean_verse_text(verse_text, book)
                    
                    if cleaned_text and len(cleaned_text) > 10:
                        verses.append(BibleVerse(
                            book=normalize_book_name(book),
                            chapter=chapter,
                            verse=verse_num,
                            text=cleaned_text
                        ))
                        verses_found = True
                except ValueError:
                    continue
        
        if verses_found:
            verses.sort(key=lambda v: v.verse)
            return verses
    
    # If still no verses found, try a more aggressive approach
    # Look for any numbers in the text that could be verse numbers
    if not verses_found:
        # Split by any standalone numbers
        parts = re.split(r'\s+(\d+)\s+', text)
        
        if len(parts) > 2:  # We have at least one number split
            current_verse_num = start_verse
            
            # Skip the first part (text before first number)
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    verse_num_str = parts[i]
                    verse_text = parts[i + 1].strip()
                    
                    try:
                        parsed_verse_num = int(verse_num_str)
                        # Use the parsed verse number if it makes sense
                        if parsed_verse_num >= current_verse_num and parsed_verse_num <= 200:  # Reasonable verse number
                            current_verse_num = parsed_verse_num
                        else:
                            # If the number doesn't make sense as a verse number, use sequential numbering
                            current_verse_num += 1
                    except ValueError:
                        current_verse_num += 1
                    
                    if verse_text:
                        cleaned_text = clean_verse_text(verse_text, book)
                        if cleaned_text and len(cleaned_text) > 10:
                            verses.append(BibleVerse(
                                book=normalize_book_name(book),
                                chapter=chapter,
                                verse=current_verse_num,
                                text=cleaned_text
                            ))
                            verses_found = True
            
            if verses_found:
                return verses
    
    # Last resort: if no verse numbers found, treat as single verse or split by sentences
    cleaned_text = clean_verse_text(text, book)
    if cleaned_text:
        # If we have an end_verse hint, try to split the text intelligently
        if end_verse and end_verse > start_verse:
            # Try to split by sentences or natural breaks
            sentences = re.split(r'[.!?]+\s+', cleaned_text)
            verses_needed = end_verse - start_verse + 1
            
            if len(sentences) >= verses_needed:
                # Distribute sentences among verses
                sentences_per_verse = max(1, len(sentences) // verses_needed)
                
                sentence_idx = 0
                for verse_num in range(start_verse, end_verse + 1):
                    if sentence_idx >= len(sentences):
                        break
                    
                    # Take a reasonable number of sentences for this verse
                    end_idx = min(sentence_idx + sentences_per_verse, len(sentences))
                    verse_sentences = sentences[sentence_idx:end_idx]
                    
                    if verse_sentences:
                        verse_text = '. '.join(verse_sentences)
                        if not verse_text.endswith('.'):
                            verse_text += '.'
                        
                        verses.append(BibleVerse(
                            book=normalize_book_name(book),
                            chapter=chapter,
                            verse=verse_num,
                            text=verse_text.strip()
                        ))
                        
                        sentence_idx = end_idx
            else:
                # Not enough sentences to split meaningfully, create single verse
                verses.append(BibleVerse(
                    book=normalize_book_name(book),
                    chapter=chapter,
                    verse=start_verse,
                    text=cleaned_text
                ))
        else:
            # Single verse or unknown range
            verses.append(BibleVerse(
                book=normalize_book_name(book),
                chapter=chapter,
                verse=start_verse,
                text=cleaned_text
            ))
    
    return verses


def parse_bible_text(raw_text: str, reference: str, version: str = "NKJV") -> BiblePassage:
    """
    Parse raw Bible text into a structured BiblePassage object.
    
    Args:
        raw_text: Raw Bible text from web scraping or other sources
        reference: Bible reference string (e.g., "Luke 1:1-38")
        version: Bible version (default: "NKJV")
        
    Returns:
        BiblePassage object with structured verses
        
    Raises:
        ValueError: If reference cannot be parsed or text is invalid
        
    Examples:
        >>> text = "1 In the beginning God created the heavens and the earth. 2 The earth was without form..."
        >>> passage = parse_bible_text(text, "Genesis 1:1-2")
        >>> len(passage.verses)
        2
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Raw text cannot be empty")
    
    if not reference or not reference.strip():
        raise ValueError("Reference cannot be empty")
    
    # Parse the reference
    try:
        book, chapter, start_verse, end_verse = parse_bible_reference(reference)
    except ValueError as e:
        raise ValueError(f"Invalid Bible reference '{reference}': {e}")
    
    # Handle cross-chapter ranges (like "Zechariah 12:1-13:1")
    if '-' in reference and ':' in reference:
        # Check if this is a cross-chapter range
        cross_chapter_match = re.match(r'(\d?\s*[A-Za-z]+)\s+(\d+):(\d+)-(\d+):(\d+)', reference)
        if cross_chapter_match:
            # This is a complex cross-chapter range
            # For now, we'll parse it as starting from the first chapter/verse
            # The actual implementation would need to handle fetching multiple chapters
            book = cross_chapter_match.group(1).strip()
            start_chapter = int(cross_chapter_match.group(2))
            start_verse_num = int(cross_chapter_match.group(3))
            end_chapter = int(cross_chapter_match.group(4))
            end_verse_num = int(cross_chapter_match.group(5))
            
            # For this implementation, we'll create verses assuming the text contains
            # verses from multiple chapters in sequence
            verses = []
            
            # Split the text and try to identify chapter boundaries
            # This is a simplified approach - real implementation might need more sophisticated parsing
            cleaned_text = clean_verse_text(raw_text, book)
            
            # Create a single verse for now (this would need enhancement for real cross-chapter parsing)
            verses.append(BibleVerse(
                book=normalize_book_name(book),
                chapter=start_chapter,
                verse=start_verse_num,
                text=cleaned_text
            ))
            
            return BiblePassage(
                reference=reference,
                version=version,
                verses=verses,
                highlights=[],
                fetched_at=datetime.now()
            )
    
    # Extract verses from the text
    verses = extract_verses_from_text(raw_text, book, chapter, start_verse, end_verse)
    
    if not verses:
        raise ValueError(f"No verses could be extracted from text for reference '{reference}'")
    
    # Create and return the passage
    return BiblePassage(
        reference=reference,
        version=version,
        verses=verses,
        highlights=[],
        fetched_at=datetime.now()
    )


def parse_mcheyne_passage_list(passage_texts: Dict[str, str], version: str = "NKJV") -> Dict[str, List[BiblePassage]]:
    """
    Parse multiple M'Cheyne passages from a dictionary of reference -> text mappings.
    
    Args:
        passage_texts: Dictionary mapping Bible references to their text content
        version: Bible version (default: "NKJV")
        
    Returns:
        Dictionary mapping references to BiblePassage objects
        
    Example:
        >>> texts = {
        ...     "Luke 1:1-38": "1 Inasmuch as many have taken in hand...",
        ...     "Genesis 1": "1 In the beginning God created..."
        ... }
        >>> passages = parse_mcheyne_passage_list(texts)
        >>> len(passages)
        2
    """
    parsed_passages = {}
    
    for reference, text in passage_texts.items():
        try:
            passage = parse_bible_text(text, reference, version)
            parsed_passages[reference] = passage
        except ValueError as e:
            print(f"Warning: Could not parse passage '{reference}': {e}")
            # Create a minimal passage with the raw text as a single verse
            try:
                book, chapter, start_verse, _ = parse_bible_reference(reference)
                fallback_verse = BibleVerse(
                    book=normalize_book_name(book),
                    chapter=chapter,
                    verse=start_verse,
                    text=clean_verse_text(text, book) or "Text unavailable"
                )
                parsed_passages[reference] = BiblePassage(
                    reference=reference,
                    version=version,
                    verses=[fallback_verse],
                    highlights=[],
                    fetched_at=datetime.now()
                )
            except Exception:
                print(f"Error: Could not create fallback passage for '{reference}'")
    
    return parsed_passages