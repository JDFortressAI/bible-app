#!/usr/bin/env python3
"""
M'Cheyne Bible Reading Plan Fetcher

This script fetches today's Bible reading passages from the M'Cheyne reading plan
and retrieves the actual NKJV text for each passage.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from typing import List, Dict, Tuple, Optional, Union
import time
import json
import os
from bible_models import BiblePassage, BibleVerse
from bible_parser import parse_bible_text

class McCheyneReader:
    def __init__(self):
        self.base_url = "https://bibleplan.org/plans/mcheyne/"
        self.bible_url = "https://www.biblestudytools.com/nkjv/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        # Fallback: Try alternative M'Cheyne sources
        self.alternative_sources = [
            "https://www.blueletterbible.org/mcheyne/",
            "https://www.esv.org/resources/reading-plans/mcheyne/",
            "https://www.crossway.org/articles/mcheyne-bible-reading-plan/"
        ]
    
    def get_todays_date(self) -> Tuple[int, int]:
        """Get today's month and day"""
        today = datetime.now()
        return today.month, today.day
    
    def fetch_reading_plan(self, month: int, day: int) -> Dict[str, List[str]]:
        """Fetch today's reading passages from M'Cheyne plan"""
        try:
            # The main M'Cheyne plan page
            url = "https://bibleplan.org/plans/mcheyne/"
            print(f"Fetching reading plan from: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            readings = {"Family": [], "Secret": []}
            
            # Create specific date patterns to search for
            current_date = datetime(2024, month, day)  # Use 2024 as reference
            
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
            
            print(f"Looking for date patterns: {date_patterns}")
            
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
                            print(f"Found date pattern '{pattern}' in row: {row_text[:100]}...")
                            break
                    
                    if date_found:
                        cells = row.find_all(['td', 'th'])
                        print(f"Row has {len(cells)} cells")
                        
                        # Extract text from each cell
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        print(f"Cell contents: {cell_texts}")
                        
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
                        
                        print(f"Looking for specific date: {target_date}")
                        
                        # Find the index of the cell containing our target date
                        target_index = -1
                        for i, cell_text in enumerate(cell_texts):
                            if target_date in cell_text:
                                target_index = i
                                print(f"Found target date at index {i}: {cell_text}")
                                break
                        
                        if target_index >= 0:
                            # Look for Family and Secret readings in the next few cells
                            family_refs = []
                            secret_refs = []
                            
                            # Check the next 3 cells after the date cell
                            for i in range(target_index + 1, min(target_index + 4, len(cell_texts))):
                                if i < len(cell_texts):
                                    cell_text = cell_texts[i]
                                    print(f"Checking cell {i}: {cell_text}")
                                    
                                    if 'Family:' in cell_text:
                                        family_refs = self.extract_bible_references(cell_text)
                                        print(f"Found Family readings: {family_refs}")
                                    elif 'Secret:' in cell_text:
                                        secret_refs = self.extract_bible_references(cell_text)
                                        print(f"Found Secret readings: {secret_refs}")
                            
                            if family_refs and secret_refs:
                                readings["Family"] = family_refs
                                readings["Secret"] = secret_refs
                                return readings
                        
                        # Fallback: extract all references and try to match by position
                        bible_refs = []
                        for i, cell_text in enumerate(cell_texts):
                            if i > 0:  # Skip first cell
                                extracted_refs = self.extract_bible_references(cell_text)
                                bible_refs.extend(extracted_refs)
                        
                        print(f"Found Bible references: {bible_refs}")
                        
                        # If we have many references, this might be the full month table
                        # Don't use it as fallback
                        if len(bible_refs) > 10:
                            print("Too many references found, this seems to be the full month table")
                            continue
            
            # Alternative approach: Look for specific M'Cheyne structure
            # Sometimes the plan is in divs or other elements
            print("Table approach failed, trying alternative parsing...")
            
            # Look for elements containing "Family" and "Secret"
            family_elements = soup.find_all(string=re.compile(r'Family.*:', re.I))
            secret_elements = soup.find_all(string=re.compile(r'Secret.*:', re.I))
            
            for family_elem in family_elements:
                parent = family_elem.parent
                if parent:
                    # Look for Bible references after "Family:"
                    text = parent.get_text()
                    # Extract references after "Family:"
                    family_match = re.search(r'Family.*?:(.*?)(?:Secret|$)', text, re.IGNORECASE | re.DOTALL)
                    if family_match:
                        family_text = family_match.group(1)
                        family_refs = re.findall(r'[A-Za-z0-9\s]+\s+\d+(?::\d+)?(?:\s*-\s*\d+)?', family_text)
                        readings["Family"] = [ref.strip() for ref in family_refs if self.is_bible_reference(ref.strip())][:2]
            
            for secret_elem in secret_elements:
                parent = secret_elem.parent
                if parent:
                    # Look for Bible references after "Secret:"
                    text = parent.get_text()
                    secret_match = re.search(r'Secret.*?:(.*?)(?:Family|$)', text, re.IGNORECASE | re.DOTALL)
                    if secret_match:
                        secret_text = secret_match.group(1)
                        secret_refs = re.findall(r'[A-Za-z0-9\s]+\s+\d+(?::\d+)?(?:\s*-\s*\d+)?', secret_text)
                        readings["Secret"] = [ref.strip() for ref in secret_refs if self.is_bible_reference(ref.strip())][:2]
            
            return readings
            
        except Exception as e:
            print(f"Error fetching reading plan: {e}")
            return {"Family": [], "Secret": []}
    
    def get_day_of_year(self, month: int, day: int) -> int:
        """Calculate day of year for given month/day"""
        date = datetime(2024, month, day)  # Use 2024 as reference year
        return date.timetuple().tm_yday
    
    def get_cache_filename(self, month: int, day: int) -> str:
        """Generate cache filename for today's readings"""
        current_year = datetime.now().year
        return f"mcheyne_readings_{current_year}_{month:02d}_{day:02d}.json"
    
    def get_structured_cache_filename(self, month: int, day: int) -> str:
        """Generate cache filename for today's structured readings"""
        current_year = datetime.now().year
        return f"mcheyne_structured_{current_year}_{month:02d}_{day:02d}.json"
    
    def load_cached_readings(self, month: int, day: int) -> Dict[str, List[str]]:
        """Load readings from local cache if available"""
        cache_file = self.get_cache_filename(month, day)
        
        if os.path.exists(cache_file):
            try:
                print(f"📁 Loading cached readings from: {cache_file}")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Validate the cached data structure
                if (isinstance(cached_data, dict) and 
                    'Family' in cached_data and 'Secret' in cached_data and
                    isinstance(cached_data['Family'], list) and 
                    isinstance(cached_data['Secret'], list)):
                    
                    print(f"✅ Successfully loaded {len(cached_data['Family'])} Family and {len(cached_data['Secret'])} Secret readings from cache")
                    return cached_data
                else:
                    print("⚠️ Cached data format is invalid, will fetch fresh data")
                    
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error reading cache file: {e}, will fetch fresh data")
        
        return {"Family": [], "Secret": []}
    
    def load_cached_structured_readings(self, month: int, day: int) -> Dict[str, List[BiblePassage]]:
        """Load structured readings from local cache with validation and migration support"""
        cache_file = self.get_structured_cache_filename(month, day)
        
        if os.path.exists(cache_file):
            try:
                print(f"📁 Loading cached structured readings from: {cache_file}")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Validate basic structure
                if not isinstance(cached_data, dict):
                    print("⚠️ Cached data is not a dictionary, will fetch fresh data")
                    return {"Family": [], "Secret": []}
                
                # Check for required keys
                if 'Family' not in cached_data or 'Secret' not in cached_data:
                    print("⚠️ Cached data missing required keys, will fetch fresh data")
                    return {"Family": [], "Secret": []}
                
                # Check format version for future migration compatibility
                format_version = cached_data.get('format_version', '1.0')
                if format_version != '1.0':
                    print(f"⚠️ Unsupported cache format version {format_version}, will fetch fresh data")
                    return {"Family": [], "Secret": []}
                
                # Validate that Family and Secret are lists
                if (not isinstance(cached_data['Family'], list) or 
                    not isinstance(cached_data['Secret'], list)):
                    print("⚠️ Family or Secret data is not a list, will fetch fresh data")
                    return {"Family": [], "Secret": []}
                
                # Deserialize BiblePassage objects from JSON with validation
                structured_readings = {"Family": [], "Secret": []}
                validation_errors = []
                
                for category in ["Family", "Secret"]:
                    for i, passage_data in enumerate(cached_data[category]):
                        try:
                            # Validate that passage_data is a dictionary
                            if not isinstance(passage_data, dict):
                                validation_errors.append(f"{category}[{i}]: Not a dictionary")
                                continue
                            
                            # Validate required fields exist
                            required_fields = ['reference', 'version', 'verses']
                            missing_fields = [field for field in required_fields if field not in passage_data]
                            if missing_fields:
                                validation_errors.append(f"{category}[{i}]: Missing fields {missing_fields}")
                                continue
                            
                            # Attempt to deserialize
                            passage = BiblePassage.from_dict(passage_data)
                            
                            # Additional validation
                            if not passage.verses:
                                validation_errors.append(f"{category}[{i}]: No verses in passage")
                                continue
                            
                            structured_readings[category].append(passage)
                            
                        except Exception as e:
                            validation_errors.append(f"{category}[{i}]: {str(e)}")
                
                # Report validation errors if any
                if validation_errors:
                    print(f"⚠️ Cache validation errors found:")
                    for error in validation_errors[:5]:  # Show first 5 errors
                        print(f"   - {error}")
                    if len(validation_errors) > 5:
                        print(f"   ... and {len(validation_errors) - 5} more errors")
                
                # Return results if we have any valid passages
                if structured_readings["Family"] or structured_readings["Secret"]:
                    print(f"✅ Successfully loaded {len(structured_readings['Family'])} Family and {len(structured_readings['Secret'])} Secret structured readings from cache")
                    if validation_errors:
                        print(f"   (Note: {len(validation_errors)} passages failed validation and were skipped)")
                    return structured_readings
                else:
                    print("⚠️ No valid structured passages found in cache after validation")
                    
            except json.JSONDecodeError as e:
                print(f"⚠️ Invalid JSON in cache file: {e}, will fetch fresh data")
            except IOError as e:
                print(f"⚠️ Error reading structured cache file: {e}, will fetch fresh data")
            except Exception as e:
                print(f"⚠️ Unexpected error loading cache: {e}, will fetch fresh data")
        else:
            # No structured cache exists, try to migrate from legacy cache
            if self.migrate_legacy_cache_to_structured(month, day):
                # Recursively call this method to load the newly migrated cache
                return self.load_cached_structured_readings(month, day)
        
        return {"Family": [], "Secret": []}

    def save_structured_readings_to_cache(self, month: int, day: int, readings: Dict[str, List[BiblePassage]]) -> None:
        """Save structured readings to local cache with validation"""
        cache_file = self.get_structured_cache_filename(month, day)
        
        try:
            # Create cache directory if it doesn't exist
            cache_dir = os.path.dirname(cache_file) if os.path.dirname(cache_file) else '.'
            os.makedirs(cache_dir, exist_ok=True)
            
            # Validate input data
            if not isinstance(readings, dict) or "Family" not in readings or "Secret" not in readings:
                raise ValueError("Invalid readings structure: must contain 'Family' and 'Secret' keys")
            
            # Validate that all items are BiblePassage objects
            for category in ["Family", "Secret"]:
                if not isinstance(readings[category], list):
                    raise ValueError(f"Invalid {category} readings: must be a list")
                for i, passage in enumerate(readings[category]):
                    if not isinstance(passage, BiblePassage):
                        raise ValueError(f"Invalid {category} reading at index {i}: must be BiblePassage object")
            
            # Prepare cache data with metadata - serialize BiblePassage objects
            cache_data = {
                "format_version": "1.0",  # For future migration compatibility
                "date": f"{month:02d}/{day:02d}/{datetime.now().year}",
                "cached_at": datetime.now().isoformat(),
                "Family": [passage.to_dict() for passage in readings["Family"]],
                "Secret": [passage.to_dict() for passage in readings["Secret"]]
            }
            
            print(f"💾 Saving structured readings to cache: {cache_file}")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"✅ Successfully cached {len(readings['Family'])} Family and {len(readings['Secret'])} Secret structured readings for {month}/{day}")
            
        except (IOError, ValueError) as e:
            print(f"⚠️ Error saving structured readings to cache: {e}")
    
    def migrate_legacy_cache_to_structured(self, month: int, day: int) -> bool:
        """
        Migrate legacy string-based cache to structured BiblePassage format.
        
        Args:
            month: Month of the readings
            day: Day of the readings
            
        Returns:
            True if migration was successful, False otherwise
        """
        legacy_cache_file = self.get_cache_filename(month, day)
        structured_cache_file = self.get_structured_cache_filename(month, day)
        
        # Skip if structured cache already exists or legacy cache doesn't exist
        if os.path.exists(structured_cache_file) or not os.path.exists(legacy_cache_file):
            return False
        
        try:
            print(f"🔄 Migrating legacy cache to structured format...")
            
            # Load legacy cache
            legacy_readings = self.load_cached_readings(month, day)
            if not legacy_readings["Family"] and not legacy_readings["Secret"]:
                print("⚠️ No legacy readings to migrate")
                return False
            
            # Convert legacy string format to structured format
            structured_readings = {"Family": [], "Secret": []}
            
            for category in ["Family", "Secret"]:
                for legacy_text in legacy_readings[category]:
                    try:
                        # Extract reference from legacy format
                        # Legacy format: "📖 Genesis 1:1-2 (NKJV)\n──────────────────────────────────────────────────\nIn the beginning..."
                        lines = legacy_text.split('\n')
                        if len(lines) >= 1:
                            # Parse the header line
                            header = lines[0].replace('📖 ', '').strip()
                            if '(' in header and ')' in header:
                                reference = header.split('(')[0].strip()
                                version_match = header.split('(')[1].split(')')[0]
                                version = version_match if version_match else "NKJV"
                            else:
                                reference = header
                                version = "NKJV"
                            
                            # Get the text content (skip header and separator lines)
                            text_lines = []
                            for i, line in enumerate(lines[1:], 1):
                                # Skip separator lines (lines with only dashes or similar)
                                if line.strip() and not all(c in '─-_=' for c in line.strip()):
                                    text_lines.append(line)
                            
                            text_content = '\n'.join(text_lines).strip()
                            
                            if reference and text_content:
                                # Try to parse into structured format using the parser
                                try:
                                    structured_passage = parse_bible_text(reference, text_content, version)
                                    if structured_passage and isinstance(structured_passage, BiblePassage):
                                        structured_readings[category].append(structured_passage)
                                        print(f"✅ Migrated {category}: {reference}")
                                        continue
                                except Exception as parse_error:
                                    print(f"⚠️ Parse error for {reference}: {parse_error}")
                                
                                # Fallback: create simple passage directly
                                try:
                                    fallback_passage = self._create_fallback_passage(reference, text_content)
                                    if version != "NKJV":
                                        # Update version if different
                                        fallback_passage.version = version
                                    structured_readings[category].append(fallback_passage)
                                    print(f"⚠️ Migrated {category} with fallback: {reference}")
                                except Exception as fallback_error:
                                    print(f"⚠️ Fallback creation failed for {reference}: {fallback_error}")
                            else:
                                print(f"⚠️ Could not extract reference or text from legacy format: {lines[0][:50]}...")
                        
                    except Exception as e:
                        print(f"⚠️ Error migrating {category} reading: {e}")
            
            # Save migrated structured readings
            if structured_readings["Family"] or structured_readings["Secret"]:
                self.save_structured_readings_to_cache(month, day, structured_readings)
                print(f"✅ Successfully migrated {len(structured_readings['Family'])} Family and {len(structured_readings['Secret'])} Secret readings")
                return True
            else:
                print("⚠️ No readings were successfully migrated")
                return False
                
        except Exception as e:
            print(f"⚠️ Error during cache migration: {e}")
            return False

    def save_readings_to_cache(self, month: int, day: int, readings: Dict[str, List[str]]) -> None:
        """Save readings to local cache"""
        cache_file = self.get_cache_filename(month, day)
        
        try:
            # Create cache directory if it doesn't exist
            cache_dir = os.path.dirname(cache_file) if os.path.dirname(cache_file) else '.'
            os.makedirs(cache_dir, exist_ok=True)
            
            # Prepare cache data with metadata
            cache_data = {
                "date": f"{month:02d}/{day:02d}/{datetime.now().year}",
                "cached_at": datetime.now().isoformat(),
                "Family": readings["Family"],
                "Secret": readings["Secret"]
            }
            
            print(f"💾 Saving readings to cache: {cache_file}")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully cached readings for {month}/{day}")
            
        except IOError as e:
            print(f"⚠️ Error saving to cache: {e}")
    
    def clear_old_cache_files(self, days_to_keep: int = 7) -> None:
        """Clean up old cache files to prevent disk bloat"""
        try:
            current_time = datetime.now()
            cache_patterns = ["mcheyne_readings_", "mcheyne_structured_"]
            
            # Get all cache files in current directory
            for filename in os.listdir('.'):
                if any(filename.startswith(pattern) for pattern in cache_patterns) and filename.endswith('.json'):
                    file_path = os.path.join('.', filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Delete files older than specified days
                    if (current_time - file_time).days > days_to_keep:
                        os.remove(file_path)
                        print(f"🗑️ Removed old cache file: {filename}")
                        
        except Exception as e:
            print(f"⚠️ Error cleaning cache: {e}")
    
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
        skip_words = ['old testament', 'new testament', 'bible in', 'years', 'days', 'plan', 'reading', 'testament in']
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
        
        # Special case for Psalms
        if book.startswith('psalm'):
            book = 'psalms'
        
        book = re.sub(r'\s+', '-', book)  # Replace spaces with hyphens
        book = re.sub(r'[^\w\-]', '', book)  # Remove special characters
        return book
    
    def fetch_passage_text(self, reference: str, return_structured: bool = False) -> Union[str, BiblePassage]:
        """
        Fetch the actual Bible text for a given reference.
        
        Args:
            reference: Bible reference string (e.g., "Luke 1:1-38")
            return_structured: If True, return BiblePassage object; if False, return formatted string
            
        Returns:
            Either a formatted string (legacy) or BiblePassage object (new structured format)
        """
        try:
            book, chapter, verses = self.parse_bible_reference(reference)
            if not book or not chapter:
                error_msg = f"Could not parse reference: {reference}"
                if return_structured:
                    return self._create_error_passage(reference, error_msg)
                return error_msg
            
            # Format book name for URL
            book_url = self.format_book_name(book)
            
            # Construct URL
            url = f"{self.bible_url}{book_url}/{chapter}.html"
            print(f"Fetching passage from: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for verse content using HTML structure - biblestudytools.com specific
            verses_data = []
            
            # Try to find verses using data-verse-id attribute (most reliable)
            verse_elements = soup.select('div[data-verse-id]')
            
            if verse_elements:
                print(f"Found {len(verse_elements)} verses with data-verse-id")
                
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
                            from .bible_parser import apply_proper_typography
                            verse_text = apply_proper_typography(verse_text)
                            
                            if verse_text and len(verse_text) > 5:
                                verses_data.append((verse_num, verse_text))
                                
                        except ValueError:
                            continue
                
                if verses_data:
                    # Sort by verse number to ensure correct order
                    verses_data.sort(key=lambda x: x[0])
                    
                    if return_structured:
                        # Create BibleVerse objects directly
                        verses = []
                        for verse_num, verse_text in verses_data:
                            verses.append(BibleVerse(
                                book=book,
                                chapter=int(chapter),
                                verse=verse_num,
                                text=verse_text
                            ))
                        
                        return BiblePassage(
                            reference=reference,
                            version="NKJV",
                            verses=verses,
                            highlights=[],
                            fetched_at=datetime.now()
                        )
                    else:
                        # Create legacy formatted string
                        formatted_text = f"\n📖 {reference} (NKJV)\n" + "─" * 50 + "\n"
                        for verse_num, verse_text in verses_data:
                            formatted_text += f"{verse_num} {verse_text}\n"
                        return formatted_text
            
            # Fallback: Try other selectors if data-verse-id not found
            passage_text = []
            verse_selectors = [
                'p.verse',  # Main verse paragraphs
                '.verse-text',
                '.bible-text p',
                'div.bible-text',
                'span.text',
                '.passage p'
            ]
            
            for selector in verse_selectors:
                verses_found = soup.select(selector)
                if verses_found:
                    print(f"Fallback: Found {len(verses_found)} verses with selector: {selector}")
                    for verse in verses_found:
                        # Get text and clean it up
                        text = verse.get_text(strip=True)
                        
                        # Skip website headers, navigation, and footer content
                        skip_patterns = [
                            'bible study tools', 'get your bible minute', 'your browser does not support',
                            'nkjv -', 'inbox every morning', 'bible minute', 'study tools',
                            'how to use highlighting', 'save to highlights', 'save to bookmarks',
                            'commentary', 'matthew henry', 'people\'s new testament',
                            'select text in the bible', 'bookmark your selection',
                            'commentaries', 'concise', 'complete'
                        ]
                        
                        if any(skip in text.lower() for skip in skip_patterns):
                            continue
                        
                        # Normalize whitespace
                        text = re.sub(r'\s+', ' ', text)
                        
                        if text and len(text) > 10:  # Filter out very short text
                            passage_text.append(text)
                    
                    if passage_text:
                        break
            
            # Alternative approach: look for the main content area
            if not passage_text:
                print("Trying alternative content extraction...")
                
                # Look for common content containers
                content_selectors = [
                    'div.bible-text',
                    'div.passage-text',
                    'div.content',
                    'div.bible-content',
                    'main',
                    'article'
                ]
                
                for selector in content_selectors:
                    content_div = soup.select_one(selector)
                    if content_div:
                        # Look for verse elements within this container first
                        verse_elements = content_div.select('div[data-verse-id]')
                        if verse_elements:
                            print(f"Found {len(verse_elements)} verses in {selector}")
                            verses_data = []
                            
                            for verse_elem in verse_elements:
                                verse_id = verse_elem.get('data-verse-id')
                                if verse_id:
                                    try:
                                        verse_num = int(verse_id)
                                        
                                        # Get verse text excluding verse number link
                                        verse_text = ""
                                        for node in verse_elem.contents:
                                            if hasattr(node, 'get_text'):
                                                if node.name == 'a' and 'text-blue-600' in node.get('class', []):
                                                    continue
                                                verse_text += node.get_text()
                                            elif hasattr(node, 'strip'):
                                                verse_text += str(node)
                                        
                                        verse_text = verse_text.strip()
                                        verse_text = re.sub(r'\s+', ' ', verse_text)
                                        
                                        # Apply proper typography
                                        from .bible_parser import apply_proper_typography
                                        verse_text = apply_proper_typography(verse_text)
                                        
                                        if verse_text and len(verse_text) > 5:
                                            verses_data.append((verse_num, verse_text))
                                            
                                    except ValueError:
                                        continue
                            
                            if verses_data:
                                verses_data.sort(key=lambda x: x[0])
                                
                                if return_structured:
                                    verses = []
                                    for verse_num, verse_text in verses_data:
                                        verses.append(BibleVerse(
                                            book=book,
                                            chapter=int(chapter),
                                            verse=verse_num,
                                            text=verse_text
                                        ))
                                    
                                    return BiblePassage(
                                        reference=reference,
                                        version="NKJV",
                                        verses=verses,
                                        highlights=[],
                                        fetched_at=datetime.now()
                                    )
                                else:
                                    formatted_text = f"\n📖 {reference} (NKJV)\n" + "─" * 50 + "\n"
                                    for verse_num, verse_text in verses_data:
                                        formatted_text += f"{verse_num} {verse_text}\n"
                                    return formatted_text
                        
                        # Fallback to paragraph extraction if no verse elements found
                        paragraphs = content_div.find_all('p')
                        for p in paragraphs:
                            text = p.get_text(strip=True)
                            text = re.sub(r'\s+', ' ', text)
                            
                            if text and len(text) > 20 and not any(skip in text.lower() for skip in ['copyright', 'version', 'translation']):
                                passage_text.append(text)
                        
                        if passage_text:
                            break
            
            # If still no content, try getting all text and filtering more aggressively
            if not passage_text:
                print("Trying full page text extraction with better filtering...")
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                
                # More comprehensive skip patterns
                skip_patterns = [
                    'bible study tools', 'get your bible minute', 'your browser does not support',
                    'menu', 'search', 'copyright', 'version', 'navigation', 'subscribe', 
                    'advertisement', 'nkjv -', 'inbox every morning', 'bible minute',
                    'study tools', 'does not support', 'browser does not'
                ]
                
                # Find the start of actual Bible content
                bible_start_found = False
                for i, line in enumerate(lines):
                    # Skip website headers and navigation
                    if any(skip in line.lower() for skip in skip_patterns):
                        continue
                    
                    # Look for the actual start of Bible text
                    # Usually starts with verse content, not titles
                    if (len(line) > 30 and len(line) < 1000 and 
                        not line.isupper() and  # Skip all-caps headers
                        not line.endswith(':') and  # Skip section headers
                        any(char.islower() for char in line)):  # Must have lowercase (actual content)
                        
                        bible_start_found = True
                        
                        # Clean up the line but preserve verse numbers for parsing
                        line = re.sub(r'\s+', ' ', line)     # Normalize whitespace
                        # Don't remove verse numbers here - let the parser handle them
                        
                        if len(line) > 20:
                            passage_text.append(line)
                    
                    elif bible_start_found and len(passage_text) > 0:
                        # Stop conditions - end of Bible content indicators
                        end_patterns = [
                            'how to use highlighting', 'save to highlights', 'save to bookmarks',
                            'commentary', 'footnote', 'study note', 'matthew henry',
                            'people\'s new testament', 'concise', 'complete', 'commentaries',
                            'select text in the bible', 'bookmark your selection',
                            'quick access later', 'highlighting and bookmarking'
                        ]
                        
                        if any(end_pattern in line.lower() for end_pattern in end_patterns):
                            print(f"Stopping at end pattern: {line[:50]}...")
                            break
                        
                        # Continue collecting until we hit obvious non-Bible content
                        if (len(line) > 20 and len(line) < 1000 and
                            not any(skip in line.lower() for skip in skip_patterns)):
                            
                            line = re.sub(r'\s+', ' ', line)
                            # Don't remove verse numbers here - let the parser handle them
                            
                            if len(line) > 20:
                                passage_text.append(line)
                
                # If we got too much, trim it down
                if len(passage_text) > 50:
                    passage_text = passage_text[:50]
            
            if passage_text:
                # Clean up the passage text further
                cleaned_text = []
                for line in passage_text:
                    # Skip obvious website content (headers and footers)
                    skip_patterns = [
                        'bible study tools', 'get your bible minute', 'browser does not',
                        'nkjv -', 'study tools', 'inbox every morning',
                        'how to use highlighting', 'save to highlights', 'save to bookmarks',
                        'commentary', 'matthew henry', 'people\'s new testament',
                        'select text in the bible', 'bookmark your selection',
                        'quick access later', 'highlighting and bookmarking',
                        'commentaries', 'concise', 'complete'
                    ]
                    
                    # Stop processing if we hit end-of-content patterns
                    if any(skip in line.lower() for skip in skip_patterns):
                        print(f"Stopping at footer content: {line[:50]}...")
                        break
                    
                    if len(line) > 15:
                        cleaned_text.append(line)
                
                if cleaned_text:
                    # Join the cleaned text for parsing
                    raw_text = "\n".join(cleaned_text[:25])
                    
                    if return_structured:
                        # Return structured BiblePassage object
                        try:
                            return parse_bible_text(raw_text, reference, "NKJV")
                        except Exception as e:
                            print(f"Warning: Could not parse structured text for {reference}: {e}")
                            # Return a minimal structured passage as fallback
                            return self._create_fallback_passage(reference, raw_text)
                    else:
                        # Return legacy formatted string
                        formatted_text = f"\n📖 {reference} (NKJV)\n" + "─" * 50 + "\n"
                        formatted_text += raw_text
                        return formatted_text
                else:
                    error_msg = f"❌ Could not extract clean text for: {reference}\n(URL: {url})"
                    if return_structured:
                        return self._create_error_passage(reference, error_msg)
                    return error_msg
            else:
                error_msg = f"❌ Could not fetch text for: {reference}\n(URL: {url})"
                if return_structured:
                    return self._create_error_passage(reference, error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"❌ Error fetching {reference}: {str(e)}"
            if return_structured:
                return self._create_error_passage(reference, error_msg)
            return error_msg
    
    def try_alternative_sources(self, month: int, day: int) -> Dict[str, List[str]]:
        """Try alternative M'Cheyne reading plan sources"""
        for source_url in self.alternative_sources:
            try:
                print(f"Trying alternative source: {source_url}")
                response = self.session.get(source_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for today's readings in different formats
                date_str = f"{month}/{day}"
                
                # Try to find table or list with readings
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        if date_str in row.get_text():
                            cells = row.find_all(['td', 'th'])
                            refs = []
                            for cell in cells:
                                text = cell.get_text(strip=True)
                                if self.is_bible_reference(text):
                                    refs.append(text)
                            
                            if len(refs) >= 4:
                                return {
                                    "Family": refs[:2],
                                    "Secret": refs[2:4]
                                }
                
            except Exception as e:
                print(f"Failed to fetch from {source_url}: {e}")
                continue
        
        return {"Family": [], "Secret": []}
    
    def _create_fallback_passage(self, reference: str, raw_text: str) -> BiblePassage:
        """Create a fallback BiblePassage when parsing fails."""
        try:
            # Try to extract basic info from reference
            book, chapter, verse = self.parse_bible_reference(reference)
            
            # Create a single verse with the raw text
            fallback_verse = BibleVerse(
                book=book,
                chapter=int(chapter),
                verse=int(verse),
                text=raw_text[:500] if raw_text else "Text unavailable"  # Limit text length
            )
            
            return BiblePassage(
                reference=reference,
                version="NKJV",
                verses=[fallback_verse],
                highlights=[],
                fetched_at=datetime.now()
            )
        except Exception:
            # Ultimate fallback
            return BiblePassage(
                reference=reference,
                version="NKJV",
                verses=[BibleVerse(
                    book="Unknown",
                    chapter=1,
                    verse=1,
                    text=raw_text[:500] if raw_text else "Text unavailable"
                )],
                highlights=[],
                fetched_at=datetime.now()
            )
    
    def _create_error_passage(self, reference: str, error_msg: str) -> BiblePassage:
        """Create an error BiblePassage when fetching fails."""
        try:
            book, chapter, verse = self.parse_bible_reference(reference)
            chapter, verse = int(chapter), int(verse)
        except Exception:
            book, chapter, verse = "Unknown", 1, 1
        
        # Ensure reference is not empty for Pydantic validation
        safe_reference = reference if reference and reference.strip() else "Unknown Reference"
        
        error_verse = BibleVerse(
            book=book,
            chapter=chapter,
            verse=verse,
            text=f"Error: {error_msg}"
        )
        
        return BiblePassage(
            reference=safe_reference,
            version="NKJV",
            verses=[error_verse],
            highlights=[],
            fetched_at=datetime.now()
        )

    def get_sample_readings_for_date(self, month: int, day: int) -> Dict[str, List[str]]:
        """Generate sample readings based on the date (fallback)"""
        # Simple algorithm to generate different readings based on date
        day_of_year = self.get_day_of_year(month, day)
        
        # Sample readings that change based on day of year
        books = ["Genesis", "Exodus", "Matthew", "Mark", "Psalms", "Proverbs", "Romans", "1 Corinthians"]
        
        family_books = [books[day_of_year % len(books)], books[(day_of_year + 1) % len(books)]]
        secret_books = [books[(day_of_year + 2) % len(books)], books[(day_of_year + 3) % len(books)]]
        
        return {
            "Family": [f"{family_books[0]} {(day_of_year % 30) + 1}", f"{family_books[1]} {(day_of_year % 25) + 1}"],
            "Secret": [f"{secret_books[0]} {(day_of_year % 20) + 1}", f"{secret_books[1]} {(day_of_year % 15) + 1}"]
        }

    def get_todays_readings_structured(self) -> Dict[str, List[BiblePassage]]:
        """Get today's complete readings as structured BiblePassage objects (with caching)"""
        month, day = self.get_todays_date()
        print(f"Getting M'Cheyne readings for {month}/{day}")
        
        # Clean up old cache files first
        self.clear_old_cache_files()
        
        # Try to load structured cache first
        cached_readings = self.load_cached_structured_readings(month, day)
        if cached_readings["Family"] or cached_readings["Secret"]:
            print("📖 Using cached structured readings")
            return cached_readings
        
        print("🌐 No structured cache found, fetching fresh readings from web...")
        
        # Try main source first
        readings = self.fetch_reading_plan(month, day)
        print(f"Parsed readings: Family={readings['Family']}, Secret={readings['Secret']}")
        
        # If main source fails, try alternatives
        if not readings["Family"] and not readings["Secret"]:
            print("Main source failed, trying alternatives...")
            readings = self.try_alternative_sources(month, day)
        
        # If all sources fail, use sample readings based on date
        if not readings["Family"] and not readings["Secret"]:
            print("All sources failed. Using date-based sample readings.")
            readings = self.get_sample_readings_for_date(month, day)
        
        # Fetch the actual text for each passage as structured objects
        complete_readings = {"Family": [], "Secret": []}
        
        for category in ["Family", "Secret"]:
            print(f"\nFetching {category} readings:")
            for reference in readings[category]:
                print(f"  - {reference}")
                passage = self.fetch_passage_text(reference, return_structured=True)
                complete_readings[category].append(passage)
                time.sleep(1)  # Be respectful to the server
        
        # Save to structured cache for future use
        if complete_readings["Family"] or complete_readings["Secret"]:
            self.save_structured_readings_to_cache(month, day, complete_readings)
        
        return complete_readings

    def get_todays_readings(self) -> Dict[str, List[str]]:
        """Get today's complete readings with text (with caching)"""
        month, day = self.get_todays_date()
        print(f"Getting M'Cheyne readings for {month}/{day}")
        
        # Clean up old cache files first
        self.clear_old_cache_files()
        
        # Try to load from cache first
        cached_readings = self.load_cached_readings(month, day)
        if cached_readings["Family"] or cached_readings["Secret"]:
            print("📖 Using cached readings (already includes full text)")
            return cached_readings
        
        print("🌐 No cache found, fetching fresh readings from web...")
        
        # Try main source first
        readings = self.fetch_reading_plan(month, day)
        print(f"Parsed readings: Family={readings['Family']}, Secret={readings['Secret']}")
        
        # If main source fails, try alternatives
        if not readings["Family"] and not readings["Secret"]:
            print("Main source failed, trying alternatives...")
            readings = self.try_alternative_sources(month, day)
        
        # If all sources fail, use sample readings based on date
        if not readings["Family"] and not readings["Secret"]:
            print("All sources failed. Using date-based sample readings.")
            readings = self.get_sample_readings_for_date(month, day)
        
        # Fetch the actual text for each passage
        complete_readings = {"Family": [], "Secret": []}
        
        for category in ["Family", "Secret"]:
            print(f"\nFetching {category} readings:")
            for reference in readings[category]:
                print(f"  - {reference}")
                text = self.fetch_passage_text(reference)
                complete_readings[category].append(text)
                time.sleep(1)  # Be respectful to the server
        
        # Save to cache for future use
        if complete_readings["Family"] or complete_readings["Secret"]:
            self.save_readings_to_cache(month, day, complete_readings)
        
        return complete_readings
    
    def display_readings(self, readings: Union[Dict[str, List[str]], Dict[str, List[BiblePassage]]], 
                        detailed: bool = False, show_highlights: bool = True):
        """
        Display the readings in a formatted way (supports both string and structured formats).
        
        Args:
            readings: Dictionary containing Family and Secret readings
            detailed: Whether to show detailed formatting with all verses
            show_highlights: Whether to display highlight information
        """
        print("\n" + "="*60)
        print(f"M'CHEYNE BIBLE READING PLAN - {datetime.now().strftime('%B %d, %Y')}")
        print("="*60)
        
        for category in ["Family", "Secret"]:
            print(f"\n📖 {category.upper()} READINGS:")
            print("-" * 40)
            
            if readings[category]:
                for i, passage in enumerate(readings[category], 1):
                    if isinstance(passage, BiblePassage):
                        # Display structured passage using new formatting methods
                        print(f"\n{i}. ", end="")
                        
                        if detailed:
                            # Show full detailed format
                            formatted_passage = passage.format_display(
                                show_metadata=True,
                                show_highlights=show_highlights,
                                max_verses=0,  # Show all verses
                                max_width=80
                            )
                            print(formatted_passage)
                        else:
                            # Show compact format with limited verses
                            formatted_passage = passage.format_display(
                                show_metadata=True,
                                show_highlights=show_highlights,
                                max_verses=5,  # Limit to 5 verses for readability
                                max_width=80
                            )
                            print(formatted_passage)
                    else:
                        # Display legacy string format
                        print(f"\n{i}. {passage}")
                    print("-" * 40)
            else:
                print("No readings found for this category.")
    
    def display_readings_compact(self, readings: Union[Dict[str, List[str]], Dict[str, List[BiblePassage]]]):
        """
        Display readings in compact format for quick overview.
        
        Args:
            readings: Dictionary containing Family and Secret readings
        """
        print("\n" + "="*60)
        print(f"M'CHEYNE READING PLAN - {datetime.now().strftime('%B %d, %Y')} (COMPACT)")
        print("="*60)
        
        for category in ["Family", "Secret"]:
            print(f"\n📖 {category.upper()}:")
            
            if readings[category]:
                for i, passage in enumerate(readings[category], 1):
                    if isinstance(passage, BiblePassage):
                        compact_format = passage.format_compact()
                        print(f"  {i}. {compact_format}")
                    else:
                        # Extract reference from legacy format
                        lines = passage.split('\n')
                        if lines:
                            header = lines[0].replace('📖 ', '').strip()
                            print(f"  {i}. 📖 {header}")
            else:
                print("  No readings found.")
    
    def display_metadata_summary(self, readings: Dict[str, List[BiblePassage]]):
        """
        Display metadata summary for structured readings.
        
        Args:
            readings: Dictionary containing structured BiblePassage readings
        """
        print("\n" + "="*60)
        print(f"READING PLAN METADATA - {datetime.now().strftime('%B %d, %Y')}")
        print("="*60)
        
        total_verses = 0
        total_words = 0
        total_highlights = 0
        all_books = set()
        
        for category in ["Family", "Secret"]:
            print(f"\n📖 {category.upper()} READINGS SUMMARY:")
            print("-" * 30)
            
            if readings[category]:
                for i, passage in enumerate(readings[category], 1):
                    if isinstance(passage, BiblePassage):
                        print(f"\n{i}. {passage.reference}")
                        metadata = passage.format_metadata_summary()
                        # Indent metadata
                        indented_metadata = '\n'.join(f"   {line}" for line in metadata.split('\n'))
                        print(indented_metadata)
                        
                        # Accumulate totals
                        total_verses += passage.total_verses
                        total_words += passage.total_words
                        total_highlights += len(passage.highlights)
                        all_books.update(passage.books)
            else:
                print("   No readings found.")
        
        # Overall summary
        print("\n" + "="*60)
        print("DAILY TOTALS:")
        print(f"📊 Total verses: {total_verses}")
        print(f"📊 Total words: {total_words}")
        print(f"📚 Books covered: {len(all_books)} ({', '.join(sorted(all_books))})")
        if total_highlights > 0:
            print(f"✨ Total highlights: {total_highlights}")
    
    def display_highlights_only(self, readings: Dict[str, List[BiblePassage]]):
        """
        Display only the highlights from structured readings.
        
        Args:
            readings: Dictionary containing structured BiblePassage readings
        """
        print("\n" + "="*60)
        print(f"HIGHLIGHTS SUMMARY - {datetime.now().strftime('%B %d, %Y')}")
        print("="*60)
        
        has_highlights = False
        
        for category in ["Family", "Secret"]:
            category_highlights = []
            
            for passage in readings[category]:
                if isinstance(passage, BiblePassage) and passage.highlights:
                    category_highlights.append(passage)
            
            if category_highlights:
                has_highlights = True
                print(f"\n📖 {category.upper()} READING HIGHLIGHTS:")
                print("-" * 40)
                
                for passage in category_highlights:
                    print(f"\n📖 {passage.reference}:")
                    highlights_summary = passage.format_highlights_summary()
                    # Indent the summary
                    indented_summary = '\n'.join(f"   {line}" for line in highlights_summary.split('\n'))
                    print(indented_summary)
        
        if not has_highlights:
            print("\nNo highlights found in today's readings.")
            print("Highlights are created when users mark important passages.")
            print("Popular highlights help identify key verses across the community.")

    def display_structured_readings(self, readings: Dict[str, List[BiblePassage]]):
        """Display structured readings with enhanced formatting"""
        self.display_readings(readings)

def main():
    """Main function to run the M'Cheyne reader with enhanced display options"""
    import sys
    
    reader = McCheyneReader()
    
    try:
        print("📖 M'Cheyne Bible Reading Plan Fetcher")
        print("=" * 50)
        
        # Parse command line arguments for display options
        args = sys.argv[1:] if len(sys.argv) > 1 else []
        
        # Display mode options
        compact_mode = '--compact' in args or '-c' in args
        detailed_mode = '--detailed' in args or '-d' in args
        metadata_only = '--metadata' in args or '-m' in args
        highlights_only = '--highlights' in args or '-h' in args
        no_highlights = '--no-highlights' in args
        
        # Check if user wants structured format
        use_structured = (os.getenv('MCHEYNE_STRUCTURED', 'false').lower() == 'true' or 
                         '--structured' in args or '-s' in args)
        
        # Force structured mode for advanced display options
        if metadata_only or highlights_only or detailed_mode:
            use_structured = True
        
        if use_structured:
            print("Using structured BiblePassage format")
            readings = reader.get_todays_readings_structured()
            
            # Display based on mode
            if compact_mode:
                reader.display_readings_compact(readings)
            elif metadata_only:
                reader.display_metadata_summary(readings)
            elif highlights_only:
                reader.display_highlights_only(readings)
            else:
                # Standard or detailed display
                reader.display_readings(
                    readings, 
                    detailed=detailed_mode, 
                    show_highlights=not no_highlights
                )
        else:
            print("Using legacy string format")
            readings = reader.get_todays_readings()
            
            if compact_mode:
                reader.display_readings_compact(readings)
            else:
                reader.display_readings(readings, show_highlights=False)
        
        # Show cache info
        month, day = reader.get_todays_date()
        if use_structured:
            cache_file = reader.get_structured_cache_filename(month, day)
        else:
            cache_file = reader.get_cache_filename(month, day)
            
        if os.path.exists(cache_file):
            print(f"\n💾 Readings cached in: {cache_file}")
            print("   (Next run will be much faster!)")
        
        # Show usage help if requested
        if '--help' in args:
            print_usage_help()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")


def print_usage_help():
    """Print usage help for command line options"""
    print("\n" + "="*60)
    print("USAGE OPTIONS:")
    print("="*60)
    print("python -m src.mccheyne [OPTIONS]")
    print()
    print("Display Options:")
    print("  --structured, -s    Use structured BiblePassage format")
    print("  --compact, -c       Show compact summary view")
    print("  --detailed, -d      Show detailed view with all verses")
    print("  --metadata, -m      Show only metadata summary")
    print("  --highlights, -h    Show only highlights summary")
    print("  --no-highlights     Hide highlight information")
    print("  --help             Show this help message")
    print()
    print("Environment Variables:")
    print("  MCHEYNE_STRUCTURED=true   Enable structured format by default")
    print()
    print("Examples:")
    print("  python -m src.mccheyne --structured --detailed")
    print("  python -m src.mccheyne --compact")
    print("  python -m src.mccheyne --metadata")

if __name__ == "__main__":
    main()