#!/usr/bin/env python3
"""
AWS Lambda function for daily M'Cheyne Bible readings update.

This function runs daily at 4AM GMT to fetch fresh Bible passages
and store them in S3 for the Streamlit application to use.
"""

import json
import boto3
import os
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional
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
        
        # Web scraping setup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; BibleChatBot/1.0)'
        })
    
    def get_todays_date(self) -> tuple:
        """Get today's month and day in GMT"""
        now = datetime.now(timezone.utc)
        return now.month, now.day, now.year
    
    def fetch_reading_plan(self, month: int, day: int) -> Dict[str, List[str]]:
        """Fetch today's reading passages from M'Cheyne plan"""
        try:
            url = "https://bibleplan.org/plans/mcheyne/"
            logger.info(f"Fetching reading plan from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            readings = {"Family": [], "Secret": []}
            
            # Create date patterns to search for
            if day in [1, 21, 31]:
                ordinal = f"{day}st"
            elif day in [2, 22]:
                ordinal = f"{day}nd"
            elif day in [3, 23]:
                ordinal = f"{day}rd"
            else:
                ordinal = f"{day}th"
            
            # Get month name
            month_names = ["", "January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
            month_name = month_names[month]
            
            date_patterns = [
                f"{month_name} {ordinal}:",
                f"{month_name[:3]} {ordinal}:",
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
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        
                        # Look for Family and Secret readings
                        for cell_text in cell_texts:
                            if 'Family:' in cell_text:
                                family_refs = self.extract_bible_references(cell_text)
                                if family_refs:
                                    readings["Family"] = family_refs
                                    logger.info(f"Found Family readings: {family_refs}")
                            elif 'Secret:' in cell_text:
                                secret_refs = self.extract_bible_references(cell_text)
                                if secret_refs:
                                    readings["Secret"] = secret_refs
                                    logger.info(f"Found Secret readings: {secret_refs}")
                        
                        if readings["Family"] and readings["Secret"]:
                            return readings
            
            logger.warning("Could not find readings in table format, trying alternative parsing")
            return readings
            
        except Exception as e:
            logger.error(f"Error fetching reading plan: {e}")
            return {"Family": [], "Secret": []}
    
    def extract_bible_references(self, text: str) -> List[str]:
        """Extract Bible references from formatted text"""
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
        if not text or len(text) > 50:
            return False
        
        text = text.strip()
        
        # Skip common non-Bible text
        skip_words = ['old testament', 'new testament', 'bible in', 'years', 'days', 'plan', 'reading']
        if any(skip.lower() in text.lower() for skip in skip_words):
            return False
        
        # Pattern for Bible references
        patterns = [
            r'^\d*\s*[A-Za-z]+\s+\d+(?:\s*-\s*\d+)?(?::\d+(?:\s*-\s*\d+)?)?$',
            r'^[A-Za-z]+\s+\d+(?:\s*-\s*\d+)?(?::\d+(?:\s*-\s*\d+)?)?$',
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        return False
    
    def fetch_bible_passage(self, reference: str) -> Optional[Dict]:
        """Fetch Bible passage text from biblestudytools.com"""
        try:
            # Parse reference
            book, chapter, verses = self.parse_bible_reference(reference)
            if not book or not chapter:
                logger.error(f"Could not parse reference: {reference}")
                return None
            
            # Format URL
            book_url = self.format_book_name(book)
            url = f"https://www.biblestudytools.com/nkjv/{book_url}/{chapter}.html"
            
            logger.info(f"Fetching passage from: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find verses with data-verse-id attributes
            verse_elements = soup.find_all(attrs={"data-verse-id": True})
            
            if not verse_elements:
                logger.warning(f"No verses found for {reference}")
                return None
            
            verses_data = []
            for verse_elem in verse_elements:
                verse_id = verse_elem.get('data-verse-id', '')
                verse_text = verse_elem.get_text(strip=True)
                
                # Extract verse number from data-verse-id
                verse_match = re.search(r':(\d+)$', verse_id)
                if verse_match:
                    verse_num = int(verse_match.group(1))
                    verses_data.append({
                        "book": book,
                        "chapter": int(chapter),
                        "verse": verse_num,
                        "text": verse_text
                    })
            
            if verses_data:
                return {
                    "reference": reference,
                    "version": "NKJV",
                    "verses": verses_data,
                    "highlights": [],
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching passage {reference}: {e}")
            return None
    
    def parse_bible_reference(self, reference: str) -> tuple:
        """Parse a Bible reference into book, chapter, and verses"""
        reference = reference.strip()
        
        # Handle ranges like "Psalm 99-101"
        if '-' in reference and ':' not in reference:
            parts = reference.split('-')
            if len(parts) == 2:
                first_part = parts[0].strip()
                pattern = r'(\d?\s*[A-Za-z]+)\s+(\d+)'
                match = re.match(pattern, first_part)
                if match:
                    book = match.group(1).strip()
                    chapter = match.group(2)
                    return book, chapter, f"chapters {reference.split()[-1]}"
        
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
        """Format book name for URL"""
        book = book.lower().strip()
        
        # Handle numbered books
        if book.startswith('1 '):
            book = '1-' + book[2:]
        elif book.startswith('2 '):
            book = '2-' + book[2:]
        elif book.startswith('3 '):
            book = '3-' + book[2:]
        
        # Replace spaces with hyphens
        book = book.replace(' ', '-')
        
        # Handle special cases
        book_mappings = {
            'song-of-solomon': 'song-of-songs',
            'song-of-songs': 'song-of-songs',
        }
        
        return book_mappings.get(book, book)
    
    def save_to_s3(self, data: Dict, key: str) -> bool:
        """Save data to S3 bucket"""
        try:
            json_data = json.dumps(data, indent=2, ensure_ascii=False, default=str)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json',
                ServerSideEncryption='AES256'
            )
            
            logger.info(f"Successfully saved data to S3: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to S3: {e}")
            return False
    
    def trigger_ecs_update(self) -> bool:
        """Trigger ECS service update to pick up new cache"""
        try:
            if not self.ecs_service_arn or not self.ecs_cluster_arn:
                logger.info("ECS service ARN not provided, skipping service update")
                return True
            
            # Force new deployment to pick up updated cache
            response = self.ecs_client.update_service(
                cluster=self.ecs_cluster_arn,
                service=self.ecs_service_arn,
                forceNewDeployment=True
            )
            
            logger.info("Successfully triggered ECS service update")
            return True
            
        except Exception as e:
            logger.error(f"Error triggering ECS update: {e}")
            return False
    
    def update_readings(self) -> Dict:
        """Main function to update today's readings"""
        month, day, year = self.get_todays_date()
        logger.info(f"Updating M'Cheyne readings for {month:02d}/{day:02d}/{year}")
        
        # Fetch reading plan
        readings = self.fetch_reading_plan(month, day)
        
        if not readings["Family"] and not readings["Secret"]:
            return {
                "success": False,
                "message": "Could not fetch reading plan",
                "date": f"{month:02d}/{day:02d}/{year}"
            }
        
        # Fetch Bible passages
        structured_readings = {"Family": [], "Secret": []}
        
        for category in ["Family", "Secret"]:
            for reference in readings[category]:
                passage_data = self.fetch_bible_passage(reference)
                if passage_data:
                    structured_readings[category].append(passage_data)
                    logger.info(f"Successfully fetched {category}: {reference}")
                else:
                    logger.warning(f"Failed to fetch {category}: {reference}")
        
        # Prepare cache data
        cache_data = {
            "format_version": "1.0",
            "date": f"{month:02d}/{day:02d}/{year}",
            "cached_at": datetime.now(timezone.utc).isoformat(),
            "Family": structured_readings["Family"],
            "Secret": structured_readings["Secret"]
        }
        
        # Save to S3
        cache_key = f"mcheyne_structured_{year}_{month:02d}_{day:02d}.json"
        success = self.save_to_s3(cache_data, cache_key)
        
        if success:
            # Trigger ECS service update
            self.trigger_ecs_update()
            
            return {
                "success": True,
                "message": f"Successfully updated readings for {month:02d}/{day:02d}/{year}",
                "date": f"{month:02d}/{day:02d}/{year}",
                "family_count": len(structured_readings["Family"]),
                "secret_count": len(structured_readings["Secret"]),
                "s3_key": cache_key
            }
        else:
            return {
                "success": False,
                "message": "Failed to save readings to S3",
                "date": f"{month:02d}/{day:02d}/{year}"
            }


def lambda_handler(event, context):
    """AWS Lambda handler function"""
    logger.info("Starting M'Cheyne readings update")
    
    try:
        updater = McCheyneUpdater()
        result = updater.update_readings()
        
        logger.info(f"Update result: {result}")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {e}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Lambda execution failed: {str(e)}'
            })
        }