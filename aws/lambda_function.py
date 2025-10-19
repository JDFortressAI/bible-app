#!/usr/bin/env python3
"""
AWS Lambda function for weekly M'Cheyne Bible readings update.

This function runs weekly to fetch fresh Bible passages for the next 1-8 days
and store them in S3 for the Streamlit application to use. This ensures there's
always at least 1 day of readings available ahead of time.
"""

import json
import boto3
import os
import requests
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Union
import re
from bs4 import BeautifulSoup
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class McCheyneUpdater:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.ecs_client = boto3.client('ecs')
        self.bucket_name = os.environ['S3_BUCKET']
        self.ecs_service_arn = os.environ.get('ECS_SERVICE_ARN')
        self.ecs_cluster_arn = os.environ.get('ECS_CLUSTER_ARN')
        
        # Web scraping setup - use same URLs as working mccheyne.py
        self.base_url = "https://bibleplan.org/plans/mcheyne/"
        self.bible_url = "https://www.biblestudytools.com/nkjv/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_todays_date(self) -> tuple:
        """Get today's month and day in GMT"""
        now = datetime.now(timezone.utc)
        return now.month, now.day
    
    def get_date_range(self, start_days_ahead: int = 1, end_days_ahead: int = 8, base_date: Optional[datetime] = None) -> List[Tuple[int, int]]:
        """
        Get a range of dates (month, day) from start_days_ahead to end_days_ahead from base_date.
        
        Args:
            start_days_ahead: How many days ahead to start (default: 1 = tomorrow)
            end_days_ahead: How many days ahead to end (default: 8 = 8 days from now)
            base_date: Base date to calculate from (default: now)
        
        Returns:
            List of (month, day) tuples
        """
        if base_date is None:
            base_date = datetime.now(timezone.utc)
        
        dates = []
        for days_ahead in range(start_days_ahead, end_days_ahead + 1):
            target_date = base_date + timedelta(days=days_ahead)
            dates.append((target_date.month, target_date.day))
        
        return dates
    
    def s3_file_exists(self, key: str) -> bool:
        """Check if a file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception as e:
            logger.error(f"Error checking S3 file existence: {e}")
            return False
    
    def fetch_reading_plan(self, month: int, day: int) -> Dict[str, List[str]]:
        """Fetch reading passages from M'Cheyne plan - using exact logic from mccheyne.py"""
        try:
            # The main M'Cheyne plan page
            url = "https://bibleplan.org/plans/mcheyne/"
            logger.info(f"Fetching reading plan from: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Retry logic with exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    timeout = 60 + (attempt * 30)  # 60s, 90s, 120s
                    logger.info(f"Attempt {attempt + 1}/{max_retries} - Timeout: {timeout}s")
                    response = requests.get(url, headers=headers, timeout=timeout)
                    response.raise_for_status()
                    break
                except requests.exceptions.Timeout as e:
                    logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2 ** attempt)  # Exponential backoff
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2 ** attempt)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            readings = {"Family": [], "Secret": []}
            
            # Create specific date patterns to search for
            # Create the specific date string with ordinal suffix
            if day in [1, 21, 31]:
                ordinal = f"{day}st"
            elif day in [2, 22]:
                ordinal = f"{day}nd"
            elif day in [3, 23]:
                ordinal = f"{day}rd"
            else:
                ordinal = f"{day}th"
            
            date_patterns = [
                f"October {ordinal}:",  # "October 12th:"
                f"Oct {ordinal}:",      # "Oct 12th:"
                f"{month}/{day}",
                f"{month:02d}/{day:02d}",
            ]
            
            logger.info(f"Looking for date patterns: {date_patterns}")
            
            # Look for the reading plan table
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    row_text = row.get_text(strip=True)
                    
                    # Check if this row contains today's date
                    date_found = False
                    for pattern in date_patterns:
                        if pattern in row_text:
                            date_found = True
                            logger.info(f"Found date pattern '{pattern}' in row")
                            break
                    
                    if date_found:
                        cells = row.find_all(['td', 'th'])
                        
                        # Extract text from each cell
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # Look for the specific date pattern in the cells
                        target_date = f"October {day}"
                        if day in [1, 21, 31]:
                            target_date += "st"
                        elif day in [2, 22]:
                            target_date += "nd"
                        elif day in [3, 23]:
                            target_date += "rd"
                        else:
                            target_date += "th"
                        
                        # Find the index of the cell containing our target date
                        target_index = -1
                        for i, cell_text in enumerate(cell_texts):
                            if target_date in cell_text:
                                target_index = i
                                break
                        
                        if target_index >= 0:
                            # Look for Family and Secret readings in the next few cells
                            family_refs = []
                            secret_refs = []
                            
                            # Check the next 3 cells after the date cell
                            for i in range(target_index + 1, min(target_index + 4, len(cell_texts))):
                                if i < len(cell_texts):
                                    cell_text = cell_texts[i]
                                    
                                    if 'Family:' in cell_text:
                                        family_refs = self.extract_bible_references(cell_text)
                                        logger.info(f"Found Family readings: {family_refs}")
                                    elif 'Secret:' in cell_text:
                                        secret_refs = self.extract_bible_references(cell_text)
                                        logger.info(f"Found Secret readings: {secret_refs}")
                            
                            if family_refs and secret_refs:
                                readings["Family"] = family_refs
                                readings["Secret"] = secret_refs
                                return readings
            
            return readings
            
        except Exception as e:
            logger.error(f"Error fetching reading plan: {e}")
            return {"Family": [], "Secret": []}
    
    def extract_bible_references(self, text: str) -> List[str]:
        """Extract Bible references from formatted text like 'Family:1 Kings 15|Colossians 2'"""
        if not text:
            return []
        
        # Remove prefixes like "Family:" or "Secret:"
        text = re.sub(r'^(Family|Secret):\s*', '', text, flags=re.IGNORECASE)
        
        # Split by | or similar separators
        parts = re.split(r'[|,;]', text)
        
        references = []
        for part in parts:
            part = part.strip()
            if part and self.is_bible_reference(part):
                references.append(part)
        
        return references

    def is_bible_reference(self, text: str) -> bool:
        """Check if text looks like a Bible reference"""
        if not text or len(text) > 50:  # Too long to be a simple reference
            return False
        
        # Clean the text
        text = text.strip()
        
        # Skip common non-Bible text (but allow if it's part of a longer reference)
        skip_words = ['old testament', 'new testament', 'bible in', 'days', 'plan', 'reading', 'testament in']
        if any(skip.lower() in text.lower() for skip in skip_words):
            return False
        
        # Pattern for Bible references
        # Examples: "Genesis 1", "1 Kings 15", "Psalm 99-101", "Matthew 1:1-10", "Colossians 2"
        patterns = [
            r'^\d*\s*[A-Za-z]+\s+\d+(?:\s*-\s*\d+)?(?::\d+(?:\s*-\s*\d+)?)?$',  # "1 Kings 15" or "Psalm 99-101"
            r'^[A-Za-z]+\s+\d+(?:\s*-\s*\d+)?(?::\d+(?:\s*-\s*\d+)?)?$',        # "Genesis 1" or "Matthew 1:1-10"
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def parse_bible_reference(self, reference: str) -> Tuple[str, str, str]:
        """Parse a Bible reference into book, chapter, and verses"""
        # Clean up the reference
        reference = reference.strip()
        
        # Handle ranges like "Psalm 99-101" - take the first chapter for URL
        if '-' in reference and ':' not in reference:
            # This is a chapter range like "Psalm 99-101"
            parts = reference.split('-')
            if len(parts) == 2:
                # Extract book and first chapter
                first_part = parts[0].strip()
                pattern = r'(\d?\s*[A-Za-z]+)\s+(\d+)'
                match = re.match(pattern, first_part)
                if match:
                    book = match.group(1).strip()
                    chapter = match.group(2)
                    return book, chapter, f"chapters {reference.split()[-1]}"  # Keep original range info
        
        # Pattern to match: "Book Chapter:Verse-Verse" or "Book Chapter"
        pattern = r'(\d?\s*[A-Za-z]+)\s+(\d+)(?::(\d+(?:-\d+)?))?'
        match = re.match(pattern, reference)
        
        if match:
            book = match.group(1).strip()
            chapter = match.group(2)
            verses = match.group(3) if match.group(3) else ""
            return book, chapter, verses
        
        return "", "", ""
    
    def format_book_name(self, book: str) -> str:
        """Format book name for URL (e.g., '1 Kings' -> '1-kings')"""
        # Handle numbered books
        book = book.lower().strip()
        
        # Special case for Psalms - fix the key issue!
        if book.startswith('psalm'):
            book = 'psalms'  # biblestudytools.com uses 'psalms' not 'psalm'
        
        book = re.sub(r'\s+', '-', book)  # Replace spaces with hyphens
        book = re.sub(r'[^\w\-]', '', book)  # Remove special characters
        return book
    
    def fetch_passage_text(self, reference: str) -> Dict:
        """Fetch the actual Bible text for a given reference and return structured data"""
        try:
            # Check if this is a chapter range (e.g., "Psalm 110-111")
            if '-' in reference and ':' not in reference:
                return self.fetch_chapter_range(reference)
            
            book, chapter, verses = self.parse_bible_reference(reference)
            if not book or not chapter:
                logger.error(f"Could not parse reference: {reference}")
                return None
            
            return self.fetch_single_chapter(reference, book, chapter)
            
        except Exception as e:
            logger.error(f"Error fetching passage {reference}: {e}")
            return None
    
    def fetch_chapter_range(self, reference: str) -> Dict:
        """Fetch multiple chapters for a range like 'Psalm 110-111'"""
        try:
            # Parse the range
            parts = reference.split('-')
            if len(parts) != 2:
                logger.error(f"Invalid range format: {reference}")
                return None
            
            # Extract book and chapter numbers
            first_part = parts[0].strip()
            last_chapter = parts[1].strip()
            
            # Parse first part to get book and starting chapter
            pattern = r'(\d?\s*[A-Za-z]+)\s+(\d+)'
            match = re.match(pattern, first_part)
            if not match:
                logger.error(f"Could not parse range start: {first_part}")
                return None
            
            book = match.group(1).strip()
            start_chapter = int(match.group(2))
            end_chapter = int(last_chapter)
            
            logger.info(f"Fetching chapters {start_chapter}-{end_chapter} of {book}")
            
            # Fetch all chapters in the range
            all_verses = []
            for chapter_num in range(start_chapter, end_chapter + 1):
                chapter_ref = f"{book} {chapter_num}"
                chapter_data = self.fetch_single_chapter(chapter_ref, book, str(chapter_num))
                
                if chapter_data and chapter_data.get('verses'):
                    all_verses.extend(chapter_data['verses'])
                    time.sleep(0.5)  # Be respectful to the server
            
            if all_verses:
                return {
                    "reference": reference,
                    "version": "NKJV",
                    "verses": all_verses,
                    "highlights": [],
                    "fetched_at": datetime.now().isoformat()
                }
            
            logger.error(f"No verses found for range {reference}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching chapter range {reference}: {e}")
            return None
    
    def fetch_single_chapter(self, reference: str, book: str, chapter: str) -> Dict:
        """Fetch a single chapter of Bible text"""
        try:
            # Format book name for URL
            book_url = self.format_book_name(book)
            
            # Construct URL
            url = f"{self.bible_url}{book_url}/{chapter}.html"
            logger.info(f"Fetching passage from: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    timeout = 45 + (attempt * 15)  # 45s, 60s
                    response = requests.get(url, headers=headers, timeout=timeout)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request error for {url} on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(1 + attempt)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for verse content using HTML structure - biblestudytools.com specific
            verses_data = []
            
            # Try to find verses using data-verse-id attribute (most reliable)
            verse_elements = soup.select('div[data-verse-id]')
            
            if verse_elements:
                logger.info(f"Found {len(verse_elements)} verses with data-verse-id")
                
                for verse_elem in verse_elements:
                    verse_id = verse_elem.get('data-verse-id')
                    if verse_id:
                        try:
                            verse_num = int(verse_id)
                            
                            # Get the verse text, excluding the verse number link
                            verse_text = ""
                            
                            # Get all text nodes, but skip the verse number link
                            for node in verse_elem.contents:
                                if hasattr(node, 'get_text'):
                                    # Skip verse number links
                                    if node.name == 'a' and 'text-blue-600' in node.get('class', []):
                                        continue
                                    verse_text += node.get_text()
                                elif hasattr(node, 'strip'):
                                    # Text node
                                    verse_text += str(node)
                            
                            # Clean up the text
                            verse_text = verse_text.strip()
                            verse_text = re.sub(r'\s+', ' ', verse_text)
                            
                            # Apply proper typography
                            verse_text = self.apply_proper_typography(verse_text, book)
                            
                            if verse_text and len(verse_text) > 5:
                                verses_data.append({
                                    "book": book,
                                    "chapter": int(chapter),
                                    "verse": verse_num,
                                    "text": verse_text
                                })
                                
                        except ValueError:
                            continue
                
                if verses_data:
                    # Sort by verse number to ensure correct order
                    verses_data.sort(key=lambda x: x['verse'])
                    
                    return {
                        "reference": reference,
                        "version": "NKJV",
                        "verses": verses_data,
                        "highlights": [],
                        "fetched_at": datetime.now().isoformat()
                    }
            
            logger.error(f"No verses found for {reference}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching single chapter {reference}: {e}")
            return None
    
    def update_readings_for_date(self, month: int, day: int) -> Dict:
        """Update readings for a specific date"""
        date_str = f"{month:02d}/{day:02d}"
        s3_key = f"mcheyne_structured_{month:02d}_{day:02d}.json"
        
        logger.info(f"Updating M'Cheyne readings for {date_str}")
        
        # Check if file already exists
        if self.s3_file_exists(s3_key):
            logger.info(f"Readings for {date_str} already exist, skipped")
            return {
                "success": True,
                "message": f"Readings for {date_str} already exist, skipped",
                "date": date_str,
                "family_count": 0,
                "secret_count": 0,
                "s3_key": s3_key,
                "skipped": True
            }
        
        # Fetch reading plan
        readings = self.fetch_reading_plan(month, day)
        
        if not readings["Family"] and not readings["Secret"]:
            logger.warning(f"No readings found for {date_str}")
            return {
                "success": False,
                "message": f"No readings found for {date_str}",
                "date": date_str,
                "family_count": 0,
                "secret_count": 0,
                "s3_key": s3_key
            }
        
        # Fetch actual Bible text for each passage
        structured_data = {
            "format_version": "1.0",
            "date": date_str,
            "cached_at": datetime.now().isoformat(),
            "Family": [],
            "Secret": []
        }
        
        family_count = 0
        secret_count = 0
        
        for category in ["Family", "Secret"]:
            for reference in readings[category]:
                passage_data = self.fetch_passage_text(reference)
                if passage_data:
                    structured_data[category].append(passage_data)
                    if category == "Family":
                        family_count += 1
                    else:
                        secret_count += 1
                    logger.info(f"Successfully fetched {category}: {reference}")
                else:
                    logger.warning(f"Failed to fetch {category}: {reference}")
        
        # Save to S3
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(structured_data, indent=2),
                ContentType='application/json'
            )
            logger.info(f"Successfully saved data to S3: {s3_key}")
            
            return {
                "success": True,
                "message": f"Successfully updated readings for {date_str}",
                "date": date_str,
                "family_count": family_count,
                "secret_count": secret_count,
                "s3_key": s3_key
            }
            
        except Exception as e:
            logger.error(f"Error saving to S3: {e}")
            return {
                "success": False,
                "message": f"Error saving to S3: {e}",
                "date": date_str,
                "family_count": family_count,
                "secret_count": secret_count,
                "s3_key": s3_key
            }
    
    def apply_proper_typography(self, text: str, book: str = None) -> str:
        """Apply proper typographic quotes and punctuation to text"""
        if not text:
            return ""
        
        # Replace escaped quotes first
        text = text.replace('\\"', '"')
        text = text.replace("\\'", "'")
        
        # Handle apostrophes first (before quote processing)
        apostrophe_patterns = [
            (r"\b(\w+)'(s|t|re|ve|ll|d|m)\b", r"\1" + chr(8217) + r"\2"),  # it's, don't, we're, I've, I'll, I'd, I'm
            (r"\b(\w+)'(\w+)\b", r"\1" + chr(8217) + r"\2"),  # general contractions
            (r"(\w+)n't\b", r"\1n" + chr(8217) + r"t"),  # won't, can't, etc.
            (r"(\w+)s'\b", r"\1s" + chr(8217)),  # possessive plural: boys', wits'
        ]
        
        for pattern, replacement in apostrophe_patterns:
            text = re.sub(pattern, replacement, text)
        
        # Convert straight double quotes to proper typographic quotes
        text = self.convert_double_quotes(text)
        
        # Convert remaining straight single quotes to proper typographic quotes
        text = self.convert_single_quotes(text)
        
        # Handle em dashes (replace double hyphens)
        text = text.replace('--', '—')
        
        # Handle ellipses
        text = re.sub(r'\.{3,}', '…', text)
        
        # Handle YHWH divine name typography (Old Testament only)
        text = self.apply_yhwh_typography(text, book)
        
        return text
    
    def convert_double_quotes(self, text: str) -> str:
        """Convert straight double quotes to proper typographic quotes"""
        if '"' not in text:
            return text
        
        result = ""
        i = 0
        quote_stack = []
        
        while i < len(text):
            char = text[i]
            
            if char == '"':
                prev_char = text[i-1] if i > 0 else ' '
                next_char = text[i+1] if i < len(text) - 1 else ' '
                
                is_opening = (
                    prev_char.isspace() or 
                    prev_char in '([{-—' or 
                    i == 0 or
                    (prev_char in '.,;:!?' and next_char.isalnum())
                )
                
                is_closing = (
                    next_char.isspace() or 
                    next_char in ')]}.,;:!?-—' or 
                    i == len(text) - 1 or
                    prev_char.isalnum()
                )
                
                if is_opening and not is_closing:
                    result += chr(8220)  # Left double quote "
                    quote_stack.append('double')
                elif is_closing and not is_opening:
                    result += chr(8221)  # Right double quote "
                    if quote_stack and quote_stack[-1] == 'double':
                        quote_stack.pop()
                else:
                    if not quote_stack or quote_stack[-1] != 'double':
                        result += chr(8220)  # Left double quote "
                        quote_stack.append('double')
                    else:
                        result += chr(8221)  # Right double quote "
                        quote_stack.pop()
            else:
                result += char
            
            i += 1
        
        return result
    
    def convert_single_quotes(self, text: str) -> str:
        """Convert remaining straight single quotes to proper typographic quotes"""
        if "'" not in text:
            return text
        
        result = ""
        i = 0
        quote_stack = []
        
        while i < len(text):
            char = text[i]
            
            if char == "'":
                prev_char = text[i-1] if i > 0 else ' '
                next_char = text[i+1] if i < len(text) - 1 else ' '
                
                if prev_char.isalpha() and (next_char.isspace() or next_char in '.,;:!?)]}'):
                    result += chr(8217)  # Right single quote/apostrophe '
                elif prev_char.isalpha() and next_char.isalpha():
                    result += chr(8217)  # Right single quote/apostrophe '
                else:
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
    
    def is_old_testament_book(self, book: str) -> bool:
        """Determine if a Bible book is from the Old Testament"""
        if not book:
            return False
        
        book_lower = book.lower().strip()
        
        old_testament_books = {
            'genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy',
            'joshua', 'judges', 'ruth', '1 samuel', '2 samuel', '1 kings', '2 kings',
            '1 chronicles', '2 chronicles', 'ezra', 'nehemiah', 'esther',
            'job', 'psalms', 'psalm', 'proverbs', 'ecclesiastes', 'song of solomon', 'song of songs',
            'isaiah', 'jeremiah', 'lamentations', 'ezekiel', 'daniel',
            'hosea', 'joel', 'amos', 'obadiah', 'jonah', 'micah', 'nahum', 'habakkuk',
            'zephaniah', 'haggai', 'zechariah', 'malachi'
        }
        
        return book_lower in old_testament_books
    
    def apply_yhwh_typography(self, text: str, book: str = None) -> str:
        """Apply proper typography for the divine name YHWH (rendered as "Lord" in most translations)"""
        if not text:
            return ""
        
        # Only apply YHWH typography to Old Testament books
        if book and not self.is_old_testament_book(book):
            return text
        
        # Define YHWH patterns - these represent the tetragrammaton YHWH
        yhwh_patterns = [
            (r'\b(the|The) Lord\b', r'\1 Lᴏʀᴅ'),
            (r'\b(O|o) Lord\b', r'\1 Lᴏʀᴅ'),
            (r'\b(the|The) Lord God\b', r'\1 Lᴏʀᴅ God'),
            (r'\b(O|o) Lord God\b', r'\1 Lᴏʀᴅ God'),
            (r'\bLord God\b', 'Lᴏʀᴅ God'),
            (r'\b(the|The) Lord of hosts\b', r'\1 Lᴏʀᴅ of hosts'),
            (r'\b(O|o) Lord of hosts\b', r'\1 Lᴏʀᴅ of hosts'),
            (r'\bLord of hosts\b', 'Lᴏʀᴅ of hosts'),
            (r'\b(the|The) Lord\'s\b', r'\1 Lᴏʀᴅ\'s'),
            (r'\bLord\'s\b', 'Lᴏʀᴅ\'s'),
            (r'^Lord\b', 'Lᴏʀᴅ'),
            (r'(?<=\. )Lord\b', 'Lᴏʀᴅ'),
            (r'(?<=\! )Lord\b', 'Lᴏʀᴅ'),
            (r'(?<=\? )Lord\b', 'Lᴏʀᴅ'),
        ]
        
        # Apply patterns using Unicode small caps characters
        for pattern, replacement in yhwh_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text

    def run_weekly_update(self, base_date: Optional[datetime] = None) -> Dict:
        """Run weekly update for next 1-8 days"""
        if base_date is None:
            base_date = datetime.now(timezone.utc)
        
        logger.info(f"Starting weekly M'Cheyne readings update for next 1-8 days from {base_date.strftime('%Y-%m-%d')}")
        
        # Get date range (tomorrow through next 8 days)
        dates = self.get_date_range(1, 8, base_date)
        
        results = []
        successful_updates = 0
        skipped_updates = 0
        failed_updates = 0
        total_family_passages = 0
        total_secret_passages = 0
        
        for month, day in dates:
            result = self.update_readings_for_date(month, day)
            results.append(result)
            
            if result["success"]:
                if result.get("skipped", False):
                    skipped_updates += 1
                else:
                    successful_updates += 1
                    total_family_passages += result["family_count"]
                    total_secret_passages += result["secret_count"]
            else:
                failed_updates += 1
        
        # Create summary
        start_date = base_date + timedelta(days=1)
        end_date = base_date + timedelta(days=8)
        date_range = f"{start_date.strftime('%m/%d')} to {end_date.strftime('%m/%d')}"
        
        summary = {
            "success": True,
            "message": f"Weekly update completed: {successful_updates} new, {skipped_updates} skipped, {failed_updates} failed",
            "successful_updates": successful_updates,
            "skipped_updates": skipped_updates,
            "failed_updates": failed_updates,
            "total_days_processed": len(dates),
            "total_family_passages": total_family_passages,
            "total_secret_passages": total_secret_passages,
            "date_range": date_range,
            "detailed_results": results
        }
        
        logger.info(f"Weekly update summary: {summary['message']}")
        return summary

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    try:
        logger.info("Starting M'Cheyne readings update")
        
        # Check for test mode
        test_mode = event.get('test_mode', False)
        base_date = None
        
        if test_mode and 'base_date' in event:
            try:
                base_date = datetime.fromisoformat(event['base_date'].replace('Z', '+00:00'))
                logger.info(f"Test mode: using base date {base_date}")
            except Exception as e:
                logger.warning(f"Invalid base_date format: {e}, using current time")
        
        # Create updater and run
        updater = McCheyneUpdater()
        result = updater.run_weekly_update(base_date)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda function error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }