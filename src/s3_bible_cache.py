#!/usr/bin/env python3
"""
S3-enabled Bible cache for AWS deployment.

This module handles reading M'Cheyne Bible passages from S3 cache
when running in AWS ECS environment.
"""

import boto3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from .bible_models import BiblePassage
import logging

logger = logging.getLogger(__name__)

class S3BibleCache:
    """S3-enabled Bible cache for reading M'Cheyne passages"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = os.environ.get('S3_BUCKET')
        self.use_s3 = bool(self.bucket_name)
        
        if self.use_s3:
            try:
                self.s3_client = boto3.client('s3')
                logger.info(f"S3 cache enabled with bucket: {self.bucket_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize S3 client: {e}")
                self.use_s3 = False
        else:
            logger.info("S3_BUCKET not set, using local cache only")
    
    def get_cache_key(self, month: int, day: int, year: int = None) -> str:
        """Generate S3 cache key for readings"""
        if year is None:
            year = datetime.now().year
        return f"mcheyne_structured_{year}_{month:02d}_{day:02d}.json"
    
    def load_from_s3(self, cache_key: str) -> Optional[Dict]:
        """Load readings from S3 cache"""
        if not self.use_s3 or not self.s3_client:
            return None
        
        try:
            logger.info(f"Loading from S3: {cache_key}")
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=cache_key
            )
            
            data = json.loads(response['Body'].read().decode('utf-8'))
            logger.info(f"Successfully loaded {cache_key} from S3")
            return data
            
        except self.s3_client.exceptions.NoSuchKey:
            logger.info(f"Cache key {cache_key} not found in S3")
            return None
        except Exception as e:
            logger.error(f"Error loading from S3: {e}")
            return None
    
    def load_from_local(self, cache_key: str) -> Optional[Dict]:
        """Load readings from local cache file"""
        try:
            # Convert S3 key to local filename
            local_filename = cache_key
            
            if os.path.exists(local_filename):
                logger.info(f"Loading from local cache: {local_filename}")
                with open(local_filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Successfully loaded {local_filename} from local cache")
                return data
            else:
                logger.info(f"Local cache file {local_filename} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error loading from local cache: {e}")
            return None
    
    def get_todays_readings(self) -> Optional[Dict]:
        """Load today's M'Cheyne readings from cache (S3 or local)"""
        today = datetime.now()
        cache_key = self.get_cache_key(today.month, today.day, today.year)
        
        # Try S3 first if available
        if self.use_s3:
            data = self.load_from_s3(cache_key)
            if data:
                return self.parse_cache_data(data)
        
        # Fallback to local cache
        data = self.load_from_local(cache_key)
        if data:
            return self.parse_cache_data(data)
        
        # Try previous day's cache as fallback
        yesterday = datetime.now().replace(day=today.day - 1) if today.day > 1 else datetime.now().replace(month=today.month - 1, day=31)
        fallback_key = self.get_cache_key(yesterday.month, yesterday.day, yesterday.year)
        
        logger.warning(f"Today's cache not found, trying fallback: {fallback_key}")
        
        if self.use_s3:
            data = self.load_from_s3(fallback_key)
            if data:
                return self.parse_cache_data(data)
        
        data = self.load_from_local(fallback_key)
        if data:
            return self.parse_cache_data(data)
        
        logger.error("No cache data found for today or yesterday")
        return None
    
    def parse_cache_data(self, data: Dict) -> Optional[Dict]:
        """Parse cache data into BiblePassage objects"""
        try:
            # Validate cache data structure
            if not isinstance(data, dict) or 'Family' not in data or 'Secret' not in data:
                logger.error("Invalid cache data structure")
                return None
            
            # Convert to BiblePassage objects
            structured_readings = {"Family": [], "Secret": []}
            
            for category in ["Family", "Secret"]:
                for passage_data in data.get(category, []):
                    try:
                        passage = BiblePassage.from_dict(passage_data)
                        structured_readings[category].append(passage)
                    except Exception as e:
                        logger.error(f"Error parsing {category} passage: {e}")
                        continue
            
            return {
                "date": data.get("date", "Unknown"),
                "readings": structured_readings
            }
            
        except Exception as e:
            logger.error(f"Error parsing cache data: {e}")
            return None
    
    def get_passage_titles(self, readings: Dict) -> List[str]:
        """Generate intelligent titles for the four passages"""
        titles = []
        
        if readings and "readings" in readings:
            # Family readings
            for i, passage in enumerate(readings["readings"]["Family"], 1):
                titles.append(f"Family {i}: {passage.reference}")
            
            # Secret readings  
            for i, passage in enumerate(readings["readings"]["Secret"], 1):
                titles.append(f"Secret {i}: {passage.reference}")
        
        return titles
    
    def get_all_passages(self, readings: Dict) -> List[BiblePassage]:
        """Get all four passages in order"""
        passages = []
        if readings and "readings" in readings:
            passages.extend(readings["readings"]["Family"])
            passages.extend(readings["readings"]["Secret"])
        return passages