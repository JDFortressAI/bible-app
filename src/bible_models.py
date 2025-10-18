"""
Bible Data Models using Pydantic BaseModel for validation and serialization.

This module provides structured data models for Bible passages, verses, and user highlights
with comprehensive validation and metadata support.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Any, Dict, TYPE_CHECKING, Optional
from datetime import datetime
import json
import functools
import time
import psutil
import os
from threading import Lock

if TYPE_CHECKING:
    pass  # BiblePassage will be defined later in this file


# Performance monitoring utilities
class PerformanceMonitor:
    """Utility class for monitoring performance and memory usage."""
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage statistics."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            'percent': process.memory_percent()
        }
    
    @staticmethod
    def time_function(func):
        """Decorator to time function execution."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Log if execution takes longer than 100ms
            if execution_time > 100:
                print(f"Performance warning: {func.__name__} took {execution_time:.2f}ms")
            
            return result
        return wrapper


# Caching decorators and utilities
class CacheManager:
    """Thread-safe cache manager for expensive computations."""
    
    def __init__(self):
        self._cache = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Any:
        """Get value from cache."""
        with self._lock:
            return self._cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        with self._lock:
            self._cache[key] = value
    
    def clear(self) -> None:
        """Clear all cached values."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get number of cached items."""
        with self._lock:
            return len(self._cache)


# Global cache instance
_global_cache = CacheManager()


def cached_property(func):
    """
    Decorator for caching expensive property computations.
    
    This decorator caches the result of a property computation on the instance
    to avoid recalculating expensive operations like word counts and statistics.
    """
    cache_attr = f'_cached_{func.__name__}'
    
    @functools.wraps(func)
    def wrapper(self):
        # Check if we have a cached value
        if hasattr(self, cache_attr):
            return getattr(self, cache_attr)
        
        # Compute and cache the value
        result = func(self)
        setattr(self, cache_attr, result)
        return result
    
    return property(wrapper)


def lazy_property(func):
    """
    Decorator for lazy loading of expensive properties.
    
    Similar to cached_property but with additional performance monitoring.
    """
    cache_attr = f'_lazy_{func.__name__}'
    
    @functools.wraps(func)
    def wrapper(self):
        # Check if we have a cached value
        if hasattr(self, cache_attr):
            return getattr(self, cache_attr)
        
        # Monitor performance for expensive operations
        start_time = time.perf_counter()
        result = func(self)
        end_time = time.perf_counter()
        
        execution_time = (end_time - start_time) * 1000
        if execution_time > 50:  # Log if takes more than 50ms
            print(f"Lazy property {func.__name__} computed in {execution_time:.2f}ms")
        
        # Cache the result
        setattr(self, cache_attr, result)
        return result
    
    return property(wrapper)


def invalidate_cache(self, *property_names):
    """
    Invalidate cached properties on an instance.
    
    Args:
        property_names: Names of properties to invalidate. If none provided, 
                       invalidates all cached properties.
    """
    if not property_names:
        # Invalidate all cached properties
        attrs_to_remove = [attr for attr in dir(self) 
                          if attr.startswith('_cached_') or attr.startswith('_lazy_')]
    else:
        # Invalidate specific properties
        attrs_to_remove = []
        for prop_name in property_names:
            attrs_to_remove.extend([
                f'_cached_{prop_name}',
                f'_lazy_{prop_name}'
            ])
    
    for attr in attrs_to_remove:
        if hasattr(self, attr):
            delattr(self, attr)


class HighlightPosition(BaseModel):
    """
    Represents a position within a Bible passage for highlighting purposes.
    
    Uses verse_index to reference a specific verse within a passage's verse list,
    and word_index to reference a specific word within that verse.
    """
    verse_index: int = Field(..., ge=0, description="Index of verse in passage.verses list")
    word_index: int = Field(..., ge=0, description="Index of word within the verse")
    
    def __lt__(self, other: 'HighlightPosition') -> bool:
        """
        Enable position comparison for sorting highlights.
        
        Args:
            other: Another HighlightPosition to compare against
            
        Returns:
            True if this position comes before the other position
        """
        if self.verse_index != other.verse_index:
            return self.verse_index < other.verse_index
        return self.word_index < other.word_index
    
    def __le__(self, other: 'HighlightPosition') -> bool:
        """Less than or equal comparison."""
        return self < other or self == other
    
    def __gt__(self, other: 'HighlightPosition') -> bool:
        """Greater than comparison."""
        return not self <= other
    
    def __ge__(self, other: 'HighlightPosition') -> bool:
        """Greater than or equal comparison."""
        return not self < other
    
    def __eq__(self, other: object) -> bool:
        """
        Equality comparison for positions.
        
        Args:
            other: Another object to compare against
            
        Returns:
            True if both positions reference the same verse and word
        """
        if not isinstance(other, HighlightPosition):
            return False
        return (self.verse_index == other.verse_index and 
                self.word_index == other.word_index)
    
    def __hash__(self) -> int:
        """Enable use as dictionary key or in sets."""
        return hash((self.verse_index, self.word_index))
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"HighlightPosition(verse={self.verse_index}, word={self.word_index})"
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"HighlightPosition(verse_index={self.verse_index}, word_index={self.word_index})"
    
    def to_json(self) -> str:
        """
        Serialize to JSON string.
        
        Returns:
            JSON string representation of the position
        """
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'HighlightPosition':
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            HighlightPosition object
            
        Raises:
            ValueError: If JSON is invalid or data doesn't match schema
        """
        return cls.model_validate_json(json_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation suitable for JSON
        """
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HighlightPosition':
        """
        Create from dictionary data.
        
        Args:
            data: Dictionary with position data
            
        Returns:
            HighlightPosition object
            
        Raises:
            ValueError: If data doesn't match schema
        """
        return cls.model_validate(data)


class BibleVerse(BaseModel):
    """
    Represents a single Bible verse with metadata and validation.
    
    Contains the actual verse text along with its location (book, chapter, verse)
    and provides computed properties for statistics and text manipulation.
    """
    book: str = Field(..., min_length=1, description="Bible book name (e.g., 'Genesis', '1 Kings')")
    chapter: int = Field(..., gt=0, description="Chapter number (must be positive)")
    verse: int = Field(..., gt=0, description="Verse number (must be positive)")
    text: str = Field(..., min_length=1, description="The actual verse text (cannot be empty)")
    
    @field_validator('book')
    @classmethod
    def validate_book_name(cls, v):
        """Ensure book name is not just whitespace."""
        if not v.strip():
            raise ValueError('Book name cannot be empty or just whitespace')
        return v.strip()
    
    @field_validator('text')
    @classmethod
    def validate_text_content(cls, v):
        """Ensure verse text is not just whitespace."""
        if not v.strip():
            raise ValueError('Verse text cannot be empty or just whitespace')
        return v.strip()
    
    @cached_property
    def word_count(self) -> int:
        """
        Number of words in the verse.
        
        Returns:
            Count of words separated by whitespace
        """
        return len(self.text.split())
    
    @cached_property
    def char_count(self) -> int:
        """
        Number of characters in the verse text.
        
        Returns:
            Total character count including spaces and punctuation
        """
        return len(self.text)
    
    @cached_property
    def reference(self) -> str:
        """
        Full verse reference in standard format.
        
        Returns:
            Formatted reference string (e.g., 'John 3:16')
        """
        return f"{self.book} {self.chapter}:{self.verse}"
    
    @cached_property
    def words(self) -> List[str]:
        """
        Split verse text into individual words (cached).
        
        Returns:
            List of words from the verse text, split by whitespace
        """
        return self.text.split()
    
    def get_words(self) -> List[str]:
        """
        Split verse text into individual words.
        
        Returns:
            List of words from the verse text, split by whitespace
        """
        return self.words  # Use cached property
    
    def invalidate_cache(self, *property_names):
        """
        Invalidate cached properties when verse data changes.
        
        Args:
            property_names: Specific properties to invalidate, or all if none specified
        """
        invalidate_cache(self, *property_names)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.reference}: {self.text}"
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"BibleVerse(book='{self.book}', chapter={self.chapter}, verse={self.verse}, text='{self.text[:50]}...')"
    
    def to_json(self) -> str:
        """
        Serialize to JSON string.
        
        Returns:
            JSON string representation of the verse
        """
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BibleVerse':
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            BibleVerse object
            
        Raises:
            ValueError: If JSON is invalid or data doesn't match schema
        """
        return cls.model_validate_json(json_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation suitable for JSON
        """
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BibleVerse':
        """
        Create from dictionary data.
        
        Args:
            data: Dictionary with verse data
            
        Returns:
            BibleVerse object
            
        Raises:
            ValueError: If data doesn't match schema
        """
        return cls.model_validate(data)
    
    def format_display(self, show_reference: bool = True, max_width: int = 80) -> str:
        """
        Format verse for display with optional reference and word wrapping.
        
        Args:
            show_reference: Whether to include the verse reference
            max_width: Maximum line width for text wrapping
            
        Returns:
            Formatted verse string ready for display
        """
        if show_reference:
            reference_text = f"{self.reference}: "
            available_width = max_width - len(reference_text)
        else:
            reference_text = ""
            available_width = max_width
        
        # Simple word wrapping
        words = self.text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + (1 if current_line else 0)  # +1 for space
            
            if current_length + word_length <= available_width or not current_line:
                current_line.append(word)
                current_length += word_length
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Add reference to first line and indent subsequent lines
        if show_reference and lines:
            lines[0] = reference_text + lines[0]
            indent = ' ' * len(reference_text)
            lines[1:] = [indent + line for line in lines[1:]]
        
        return '\n'.join(lines)
    
    def format_compact(self) -> str:
        """
        Format verse in compact form for lists and summaries.
        
        Returns:
            Compact verse representation
        """
        return f"{self.reference}: {self.text[:50]}{'...' if len(self.text) > 50 else ''}"


class BibleHighlight(BaseModel):
    """
    Represents a user highlight within a Bible passage with flexible positioning.
    
    Supports highlighting from single words to multi-verse spans and tracks
    popularity through highlight_count for anonymous user aggregation.
    """
    start_position: HighlightPosition = Field(..., description="Start position of highlight")
    end_position: HighlightPosition = Field(..., description="End position of highlight")
    highlight_count: int = Field(default=1, ge=1, description="Number of users who highlighted this section")
    
    @model_validator(mode='after')
    def validate_position_order(self):
        """Ensure end position is after or equal to start position."""
        if self.end_position < self.start_position:
            raise ValueError('End position must be after or equal to start position')
        return self
    
    def spans_multiple_verses(self) -> bool:
        """
        Check if highlight spans multiple verses.
        
        Returns:
            True if the highlight crosses verse boundaries, False otherwise
        """
        return self.start_position.verse_index != self.end_position.verse_index
    
    def get_highlighted_text(self, passage: 'BiblePassage') -> str:
        """
        Extract the highlighted text from the given passage.
        
        Args:
            passage: The BiblePassage containing the verses to extract from
            
        Returns:
            The highlighted text as a string
            
        Raises:
            IndexError: If highlight positions are invalid for the passage
            ValueError: If passage doesn't contain enough verses
        """
        # Validate that the passage has enough verses
        if len(passage.verses) <= max(self.start_position.verse_index, self.end_position.verse_index):
            raise ValueError(f"Passage only has {len(passage.verses)} verses, but highlight references verse {max(self.start_position.verse_index, self.end_position.verse_index)}")
        
        # Single verse highlight
        if not self.spans_multiple_verses():
            verse = passage.verses[self.start_position.verse_index]
            words = verse.get_words()
            
            # Validate word indices
            if self.start_position.word_index >= len(words):
                raise IndexError(f"Start word index {self.start_position.word_index} is beyond verse length {len(words)}")
            if self.end_position.word_index >= len(words):
                raise IndexError(f"End word index {self.end_position.word_index} is beyond verse length {len(words)}")
            
            # Extract highlighted words (inclusive range)
            highlighted_words = words[self.start_position.word_index:self.end_position.word_index + 1]
            return ' '.join(highlighted_words)
        
        # Multi-verse highlight
        highlighted_parts = []
        
        # Process each verse in the highlight range
        for verse_idx in range(self.start_position.verse_index, self.end_position.verse_index + 1):
            verse = passage.verses[verse_idx]
            words = verse.get_words()
            
            if verse_idx == self.start_position.verse_index:
                # First verse: from start_position to end of verse
                if self.start_position.word_index >= len(words):
                    raise IndexError(f"Start word index {self.start_position.word_index} is beyond verse length {len(words)}")
                highlighted_words = words[self.start_position.word_index:]
            elif verse_idx == self.end_position.verse_index:
                # Last verse: from beginning to end_position
                if self.end_position.word_index >= len(words):
                    raise IndexError(f"End word index {self.end_position.word_index} is beyond verse length {len(words)}")
                highlighted_words = words[:self.end_position.word_index + 1]
            else:
                # Middle verses: entire verse
                highlighted_words = words
            
            if highlighted_words:
                highlighted_parts.append(' '.join(highlighted_words))
        
        return ' '.join(highlighted_parts)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"BibleHighlight({self.start_position} to {self.end_position}, count={self.highlight_count})"
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"BibleHighlight(start_position={self.start_position!r}, end_position={self.end_position!r}, highlight_count={self.highlight_count})"
    
    def to_json(self) -> str:
        """
        Serialize to JSON string.
        
        Returns:
            JSON string representation of the highlight
        """
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BibleHighlight':
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            BibleHighlight object
            
        Raises:
            ValueError: If JSON is invalid or data doesn't match schema
        """
        return cls.model_validate_json(json_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation suitable for JSON
        """
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BibleHighlight':
        """
        Create from dictionary data.
        
        Args:
            data: Dictionary with highlight data
            
        Returns:
            BibleHighlight object
            
        Raises:
            ValueError: If data doesn't match schema
        """
        return cls.model_validate(data)
    
    def format_display(self, passage: 'BiblePassage', show_context: bool = True, 
                      context_words: int = 3) -> str:
        """
        Format highlight for display with optional context.
        
        Args:
            passage: The BiblePassage containing this highlight
            show_context: Whether to show surrounding context words
            context_words: Number of context words to show before/after highlight
            
        Returns:
            Formatted highlight string with visual indicators
        """
        try:
            highlighted_text = self.get_highlighted_text(passage)
            
            if not show_context or not highlighted_text:
                return f"✨ \"{highlighted_text}\" (highlighted by {self.highlight_count} users)"
            
            # Get context for single verse highlights
            if not self.spans_multiple_verses():
                verse = passage.verses[self.start_position.verse_index]
                words = verse.get_words()
                
                # Calculate context range
                start_context = max(0, self.start_position.word_index - context_words)
                end_context = min(len(words), self.end_position.word_index + 1 + context_words)
                
                # Build context with highlight markers
                context_parts = []
                
                # Before highlight
                if start_context < self.start_position.word_index:
                    before_words = words[start_context:self.start_position.word_index]
                    context_parts.append(' '.join(before_words))
                
                # Highlighted text with markers
                context_parts.append(f"**{highlighted_text}**")
                
                # After highlight
                if self.end_position.word_index + 1 < end_context:
                    after_words = words[self.end_position.word_index + 1:end_context]
                    context_parts.append(' '.join(after_words))
                
                context_text = ' '.join(context_parts)
                verse_ref = verse.reference
                
                return f"✨ {verse_ref}: ...{context_text}... (highlighted by {self.highlight_count} users)"
            else:
                # Multi-verse highlight - show simplified format
                start_verse = passage.verses[self.start_position.verse_index]
                end_verse = passage.verses[self.end_position.verse_index]
                
                return (f"✨ {start_verse.reference}-{end_verse.reference}: "
                       f"\"{highlighted_text[:100]}{'...' if len(highlighted_text) > 100 else ''}\" "
                       f"(highlighted by {self.highlight_count} users)")
                
        except (IndexError, ValueError) as e:
            return f"✨ Invalid highlight: {e} (highlighted by {self.highlight_count} users)"
    
    def format_compact(self) -> str:
        """
        Format highlight in compact form for lists.
        
        Returns:
            Compact highlight representation
        """
        if self.spans_multiple_verses():
            return (f"✨ Verses {self.start_position.verse_index}-{self.end_position.verse_index} "
                   f"({self.highlight_count} users)")
        else:
            return (f"✨ Verse {self.start_position.verse_index}, "
                   f"words {self.start_position.word_index}-{self.end_position.word_index} "
                   f"({self.highlight_count} users)")
    
    def get_position_description(self, passage: 'BiblePassage') -> str:
        """
        Get human-readable description of highlight position.
        
        Args:
            passage: The BiblePassage containing this highlight
            
        Returns:
            Description of where the highlight is located
        """
        try:
            if self.spans_multiple_verses():
                start_verse = passage.verses[self.start_position.verse_index]
                end_verse = passage.verses[self.end_position.verse_index]
                return f"From {start_verse.reference} to {end_verse.reference}"
            else:
                verse = passage.verses[self.start_position.verse_index]
                if self.start_position.word_index == self.end_position.word_index:
                    return f"{verse.reference}, word {self.start_position.word_index + 1}"
                else:
                    return (f"{verse.reference}, words {self.start_position.word_index + 1}-"
                           f"{self.end_position.word_index + 1}")
        except IndexError:
            return "Invalid position"


class BiblePassage(BaseModel):
    """
    Represents a Bible passage containing multiple verses with metadata and highlights.
    
    Provides aggregation features for metadata calculation, highlight management,
    and support for complex multi-chapter and multi-book passages.
    """
    reference: str = Field(..., min_length=1, description="Human-readable reference (e.g., 'Luke 1:1-38')")
    version: str = Field(default="NKJV", description="Bible version")
    verses: List[BibleVerse] = Field(..., min_length=1, description="List of verses in the passage")
    highlights: List[BibleHighlight] = Field(default_factory=list, description="User highlights")
    fetched_at: datetime = Field(default_factory=datetime.now, description="When passage was fetched")
    
    @field_validator('reference')
    @classmethod
    def validate_reference(cls, v):
        """Ensure reference is not just whitespace."""
        if not v.strip():
            raise ValueError('Reference cannot be empty or just whitespace')
        return v.strip()
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v):
        """Ensure version is not just whitespace."""
        if not v.strip():
            raise ValueError('Version cannot be empty or just whitespace')
        return v.strip()
    
    @cached_property
    def total_verses(self) -> int:
        """
        Total number of verses in the passage.
        
        Returns:
            Count of verses in the passage
        """
        return len(self.verses)
    
    @lazy_property
    def total_words(self) -> int:
        """
        Total word count across all verses in the passage.
        
        Returns:
            Sum of word counts from all verses
        """
        return sum(verse.word_count for verse in self.verses)
    
    @lazy_property
    def total_characters(self) -> int:
        """
        Total character count across all verses in the passage.
        
        Returns:
            Sum of character counts from all verses
        """
        return sum(verse.char_count for verse in self.verses)
    
    @cached_property
    def books(self) -> List[str]:
        """
        List of unique books in this passage, preserving order.
        
        Returns:
            Ordered list of unique book names in the passage
        """
        seen = set()
        result = []
        for verse in self.verses:
            if verse.book not in seen:
                seen.add(verse.book)
                result.append(verse.book)
        return result
    
    @cached_property
    def chapter_range(self) -> str:
        """
        Human-readable chapter range for the passage.
        
        Returns:
            Formatted chapter range string (e.g., '1:1-38', '12:1-13:1')
        """
        if not self.verses:
            return ""
        
        # Single verse case
        if len(self.verses) == 1:
            verse = self.verses[0]
            return f"{verse.chapter}:{verse.verse}"
        
        # Multiple verses
        first_verse = self.verses[0]
        last_verse = self.verses[-1]
        
        # Same chapter
        if first_verse.chapter == last_verse.chapter:
            return f"{first_verse.chapter}:{first_verse.verse}-{last_verse.verse}"
        
        # Different chapters
        return f"{first_verse.chapter}:{first_verse.verse}-{last_verse.chapter}:{last_verse.verse}"
    
    def add_highlight(self, start_position: HighlightPosition, end_position: HighlightPosition) -> BibleHighlight:
        """
        Add a new highlight to the passage or increment existing highlight count.
        
        Args:
            start_position: Starting position of the highlight
            end_position: Ending position of the highlight
            
        Returns:
            The BibleHighlight object (new or existing)
            
        Raises:
            ValueError: If positions are invalid for this passage
        """
        # Validate positions are within bounds
        max_verse_index = len(self.verses) - 1
        if start_position.verse_index > max_verse_index or end_position.verse_index > max_verse_index:
            raise ValueError(f"Highlight positions reference verses beyond passage length ({len(self.verses)} verses)")
        
        # Validate word indices
        start_verse = self.verses[start_position.verse_index]
        end_verse = self.verses[end_position.verse_index]
        
        if start_position.word_index >= len(start_verse.get_words()):
            raise ValueError(f"Start word index {start_position.word_index} is beyond verse length {len(start_verse.get_words())}")
        
        if end_position.word_index >= len(end_verse.get_words()):
            raise ValueError(f"End word index {end_position.word_index} is beyond verse length {len(end_verse.get_words())}")
        
        # Check if highlight already exists
        for highlight in self.highlights:
            if (highlight.start_position == start_position and 
                highlight.end_position == end_position):
                highlight.highlight_count += 1
                return highlight
        
        # Create new highlight
        new_highlight = BibleHighlight(
            start_position=start_position,
            end_position=end_position,
            highlight_count=1
        )
        self.highlights.append(new_highlight)
        return new_highlight
    
    def get_popular_highlights(self, min_count: int = 1) -> List[BibleHighlight]:
        """
        Get highlights sorted by popularity (highlight count).
        
        Args:
            min_count: Minimum highlight count to include
            
        Returns:
            List of highlights sorted by count (descending)
        """
        filtered_highlights = [h for h in self.highlights if h.highlight_count >= min_count]
        return sorted(filtered_highlights, key=lambda h: h.highlight_count, reverse=True)
    
    def merge_overlapping_highlights(self) -> None:
        """
        Merge overlapping or adjacent highlights by combining their counts.
        
        This method modifies the highlights list in place, combining highlights
        that overlap or are adjacent to each other.
        """
        if len(self.highlights) <= 1:
            return
        
        # Sort highlights by start position
        sorted_highlights = sorted(self.highlights, key=lambda h: h.start_position)
        merged = []
        current = sorted_highlights[0]
        
        for next_highlight in sorted_highlights[1:]:
            # Check if highlights overlap or are adjacent
            if self._highlights_overlap_or_adjacent(current, next_highlight):
                # Merge highlights
                current = self._merge_two_highlights(current, next_highlight)
            else:
                merged.append(current)
                current = next_highlight
        
        merged.append(current)
        self.highlights = merged
    
    def _highlights_overlap_or_adjacent(self, h1: BibleHighlight, h2: BibleHighlight) -> bool:
        """
        Check if two highlights overlap or are adjacent.
        
        Args:
            h1: First highlight
            h2: Second highlight
            
        Returns:
            True if highlights overlap or are adjacent
        """
        # h2 starts before or at h1 ends (allowing for adjacent highlights)
        return h2.start_position <= h1.end_position or (
            h1.end_position.verse_index == h2.start_position.verse_index and
            h1.end_position.word_index + 1 == h2.start_position.word_index
        )
    
    def _merge_two_highlights(self, h1: BibleHighlight, h2: BibleHighlight) -> BibleHighlight:
        """
        Merge two highlights into one.
        
        Args:
            h1: First highlight
            h2: Second highlight
            
        Returns:
            New merged highlight
        """
        start_pos = h1.start_position if h1.start_position <= h2.start_position else h2.start_position
        end_pos = h1.end_position if h1.end_position >= h2.end_position else h2.end_position
        
        return BibleHighlight(
            start_position=start_pos,
            end_position=end_pos,
            highlight_count=h1.highlight_count + h2.highlight_count
        )
    
    def get_highlight_coverage(self) -> float:
        """
        Calculate what percentage of the passage is highlighted.
        
        Returns:
            Percentage of words that are highlighted (0.0 to 100.0)
        """
        if not self.highlights or self.total_words == 0:
            return 0.0
        
        highlighted_words = set()
        
        for highlight in self.highlights:
            # Add all word positions covered by this highlight
            for verse_idx in range(highlight.start_position.verse_index, highlight.end_position.verse_index + 1):
                verse = self.verses[verse_idx]
                words = verse.get_words()
                
                if verse_idx == highlight.start_position.verse_index and verse_idx == highlight.end_position.verse_index:
                    # Single verse highlight
                    for word_idx in range(highlight.start_position.word_index, highlight.end_position.word_index + 1):
                        if word_idx < len(words):
                            highlighted_words.add((verse_idx, word_idx))
                elif verse_idx == highlight.start_position.verse_index:
                    # First verse of multi-verse highlight
                    for word_idx in range(highlight.start_position.word_index, len(words)):
                        highlighted_words.add((verse_idx, word_idx))
                elif verse_idx == highlight.end_position.verse_index:
                    # Last verse of multi-verse highlight
                    for word_idx in range(0, highlight.end_position.word_index + 1):
                        if word_idx < len(words):
                            highlighted_words.add((verse_idx, word_idx))
                else:
                    # Middle verse of multi-verse highlight
                    for word_idx in range(len(words)):
                        highlighted_words.add((verse_idx, word_idx))
        
        return (len(highlighted_words) / self.total_words) * 100.0
    
    def search_highlights(self, text_query: str = None, min_count: int = None, 
                         verse_range: tuple = None, spans_multiple: bool = None) -> List[BibleHighlight]:
        """
        Search and filter highlights based on various criteria.
        
        Args:
            text_query: Search for highlights containing this text (case-insensitive)
            min_count: Minimum highlight count to include
            verse_range: Tuple of (start_verse_index, end_verse_index) to limit search
            spans_multiple: If True, only multi-verse highlights; if False, only single-verse
            
        Returns:
            List of highlights matching the criteria
        """
        results = self.highlights.copy()
        
        # Filter by minimum count
        if min_count is not None:
            results = [h for h in results if h.highlight_count >= min_count]
        
        # Filter by verse range
        if verse_range is not None:
            start_idx, end_idx = verse_range
            results = [h for h in results 
                      if (h.start_position.verse_index >= start_idx and 
                          h.end_position.verse_index <= end_idx)]
        
        # Filter by span type
        if spans_multiple is not None:
            if spans_multiple:
                results = [h for h in results if h.spans_multiple_verses()]
            else:
                results = [h for h in results if not h.spans_multiple_verses()]
        
        # Filter by text content
        if text_query is not None:
            text_query_lower = text_query.lower()
            filtered_results = []
            for highlight in results:
                try:
                    highlighted_text = highlight.get_highlighted_text(self)
                    if text_query_lower in highlighted_text.lower():
                        filtered_results.append(highlight)
                except (IndexError, ValueError):
                    # Skip highlights with invalid positions
                    continue
            results = filtered_results
        
        return results
    
    def get_highlight_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about highlights in this passage.
        
        Returns:
            Dictionary containing various highlight statistics
        """
        if not self.highlights:
            return {
                'total_highlights': 0,
                'total_highlight_count': 0,
                'average_popularity': 0.0,
                'most_popular_count': 0,
                'coverage_percentage': 0.0,
                'single_verse_highlights': 0,
                'multi_verse_highlights': 0,
                'verses_with_highlights': 0
            }
        
        total_highlights = len(self.highlights)
        total_highlight_count = sum(h.highlight_count for h in self.highlights)
        average_popularity = total_highlight_count / total_highlights if total_highlights > 0 else 0.0
        most_popular_count = max(h.highlight_count for h in self.highlights)
        
        single_verse = sum(1 for h in self.highlights if not h.spans_multiple_verses())
        multi_verse = total_highlights - single_verse
        
        # Count verses that have at least one highlight
        verses_with_highlights = set()
        for highlight in self.highlights:
            for verse_idx in range(highlight.start_position.verse_index, highlight.end_position.verse_index + 1):
                verses_with_highlights.add(verse_idx)
        
        return {
            'total_highlights': total_highlights,
            'total_highlight_count': total_highlight_count,
            'average_popularity': round(average_popularity, 2),
            'most_popular_count': most_popular_count,
            'coverage_percentage': round(self.get_highlight_coverage(), 2),
            'single_verse_highlights': single_verse,
            'multi_verse_highlights': multi_verse,
            'verses_with_highlights': len(verses_with_highlights)
        }
    
    def remove_highlight(self, start_position: HighlightPosition, end_position: HighlightPosition) -> bool:
        """
        Remove a specific highlight from the passage.
        
        Args:
            start_position: Starting position of the highlight to remove
            end_position: Ending position of the highlight to remove
            
        Returns:
            True if highlight was found and removed, False otherwise
        """
        for i, highlight in enumerate(self.highlights):
            if (highlight.start_position == start_position and 
                highlight.end_position == end_position):
                del self.highlights[i]
                return True
        return False
    
    def clear_highlights(self) -> int:
        """
        Remove all highlights from the passage.
        
        Returns:
            Number of highlights that were removed
        """
        count = len(self.highlights)
        self.highlights.clear()
        return count
    
    def get_highlights_by_verse(self, verse_index: int) -> List[BibleHighlight]:
        """
        Get all highlights that include a specific verse.
        
        Args:
            verse_index: Index of the verse to search for
            
        Returns:
            List of highlights that include the specified verse
        """
        if verse_index < 0 or verse_index >= len(self.verses):
            return []
        
        return [h for h in self.highlights 
                if (h.start_position.verse_index <= verse_index <= h.end_position.verse_index)]
    
    def invalidate_cache(self, *property_names):
        """
        Invalidate cached properties when passage data changes.
        
        Args:
            property_names: Specific properties to invalidate, or all if none specified
        """
        invalidate_cache(self, *property_names)
    
    @PerformanceMonitor.time_function
    def to_json_optimized(self, exclude_highlights: bool = False) -> str:
        """
        Optimized JSON serialization for large passages.
        
        Args:
            exclude_highlights: If True, excludes highlights to reduce size
            
        Returns:
            Compact JSON string representation
        """
        # Use Pydantic's built-in JSON serialization which handles datetime properly
        if exclude_highlights:
            # Create a copy without highlights
            data = self.model_dump(exclude={'highlights'})
            return json.dumps(data, separators=(',', ':'), ensure_ascii=False, default=str)
        else:
            # Use Pydantic's optimized JSON serialization
            return self.model_dump_json()
    
    @classmethod
    @PerformanceMonitor.time_function
    def from_json_optimized(cls, json_str: str) -> 'BiblePassage':
        """
        Optimized JSON deserialization with validation.
        
        Args:
            json_str: JSON string to deserialize
            
        Returns:
            BiblePassage object
        """
        return cls.model_validate_json(json_str)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get memory usage statistics for this passage.
        
        Returns:
            Dictionary with memory usage information
        """
        import sys
        
        # Calculate approximate memory usage
        verse_memory = sum(sys.getsizeof(verse.text) + sys.getsizeof(verse.book) + 64 
                          for verse in self.verses)
        highlight_memory = len(self.highlights) * 128  # Approximate size per highlight
        metadata_memory = (sys.getsizeof(self.reference) + 
                          sys.getsizeof(self.version) + 64)
        
        total_memory = verse_memory + highlight_memory + metadata_memory
        
        return {
            'total_bytes': total_memory,
            'total_kb': total_memory / 1024,
            'verse_memory_bytes': verse_memory,
            'highlight_memory_bytes': highlight_memory,
            'metadata_memory_bytes': metadata_memory,
            'verses_count': len(self.verses),
            'highlights_count': len(self.highlights),
            'avg_bytes_per_verse': verse_memory / len(self.verses) if self.verses else 0
        }
    
    @PerformanceMonitor.time_function
    def get_highlight_coverage_optimized(self) -> float:
        """
        Optimized calculation of highlight coverage percentage.
        
        Returns:
            Percentage of words that are highlighted (0.0 to 100.0)
        """
        if not self.highlights or self.total_words == 0:
            return 0.0
        
        # Use a more efficient algorithm for large passages
        highlighted_words = 0
        
        # Create a bitmap for each verse to track highlighted words
        verse_bitmaps = {}
        
        for highlight in self.highlights:
            for verse_idx in range(highlight.start_position.verse_index, 
                                 highlight.end_position.verse_index + 1):
                if verse_idx not in verse_bitmaps:
                    verse_word_count = len(self.verses[verse_idx].get_words())
                    verse_bitmaps[verse_idx] = [False] * verse_word_count
                
                verse = self.verses[verse_idx]
                words = verse.get_words()
                
                if verse_idx == highlight.start_position.verse_index and verse_idx == highlight.end_position.verse_index:
                    # Single verse highlight
                    start_word = min(highlight.start_position.word_index, len(words) - 1)
                    end_word = min(highlight.end_position.word_index, len(words) - 1)
                    for word_idx in range(start_word, end_word + 1):
                        verse_bitmaps[verse_idx][word_idx] = True
                elif verse_idx == highlight.start_position.verse_index:
                    # First verse of multi-verse highlight
                    start_word = min(highlight.start_position.word_index, len(words) - 1)
                    for word_idx in range(start_word, len(words)):
                        verse_bitmaps[verse_idx][word_idx] = True
                elif verse_idx == highlight.end_position.verse_index:
                    # Last verse of multi-verse highlight
                    end_word = min(highlight.end_position.word_index, len(words) - 1)
                    for word_idx in range(0, end_word + 1):
                        verse_bitmaps[verse_idx][word_idx] = True
                else:
                    # Middle verse of multi-verse highlight
                    for word_idx in range(len(words)):
                        verse_bitmaps[verse_idx][word_idx] = True
        
        # Count highlighted words
        for bitmap in verse_bitmaps.values():
            highlighted_words += sum(bitmap)
        
        return (highlighted_words / self.total_words) * 100.0
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"BiblePassage({self.reference}, {self.total_verses} verses, {len(self.highlights)} highlights)"
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return f"BiblePassage(reference='{self.reference}', version='{self.version}', verses={len(self.verses)}, highlights={len(self.highlights)})"
    
    def to_json(self) -> str:
        """
        Serialize to JSON string with datetime handling.
        
        Returns:
            JSON string representation of the passage
        """
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BiblePassage':
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON string representation
            
        Returns:
            BiblePassage object
            
        Raises:
            ValueError: If JSON is invalid or data doesn't match schema
        """
        return cls.model_validate_json(json_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization with datetime handling.
        
        Returns:
            Dictionary representation suitable for JSON
        """
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BiblePassage':
        """
        Create from dictionary data.
        
        Args:
            data: Dictionary with passage data
            
        Returns:
            BiblePassage object
            
        Raises:
            ValueError: If data doesn't match schema
        """
        return cls.model_validate(data)
    
    def format_display(self, show_metadata: bool = True, show_highlights: bool = True, 
                      max_verses: int = 10, max_width: int = 80) -> str:
        """
        Format passage for comprehensive display with metadata and highlights.
        
        Args:
            show_metadata: Whether to include passage metadata
            show_highlights: Whether to show highlight information
            max_verses: Maximum number of verses to display (0 for all)
            max_width: Maximum line width for formatting
            
        Returns:
            Formatted passage string ready for display
        """
        lines = []
        
        # Header with reference and version
        header = f"📖 {self.reference} ({self.version})"
        lines.append(header)
        lines.append("─" * len(header))
        
        # Metadata section
        if show_metadata:
            metadata_lines = []
            metadata_lines.append(f"📊 {self.total_verses} verses, {self.total_words} words, {self.total_characters} characters")
            
            if len(self.books) > 1:
                metadata_lines.append(f"📚 Books: {', '.join(self.books)}")
            
            metadata_lines.append(f"📖 Chapter range: {self.chapter_range}")
            
            if show_highlights and self.highlights:
                coverage = self.get_highlight_coverage()
                metadata_lines.append(f"✨ {len(self.highlights)} highlights ({coverage:.1f}% coverage)")
            
            lines.extend(metadata_lines)
            lines.append("")
        
        # Verses section
        verses_to_show = self.verses[:max_verses] if max_verses > 0 else self.verses
        
        for verse in verses_to_show:
            verse_text = verse.format_display(show_reference=True, max_width=max_width)
            
            # Add highlight visualization if enabled
            if show_highlights and self.highlights:
                verse_text = self._add_highlight_visualization(verse_text, verse, max_width)
            
            lines.append(verse_text)
        
        # Show truncation message if needed
        if max_verses > 0 and len(self.verses) > max_verses:
            remaining = len(self.verses) - max_verses
            lines.append(f"\n... and {remaining} more verses")
        
        # Highlights section
        if show_highlights and self.highlights:
            lines.append("\n" + "─" * 40)
            lines.append("HIGHLIGHTS:")
            
            popular_highlights = self.get_popular_highlights()[:5]  # Show top 5
            for i, highlight in enumerate(popular_highlights, 1):
                highlight_text = highlight.format_display(self, show_context=True)
                lines.append(f"{i}. {highlight_text}")
            
            if len(self.highlights) > 5:
                lines.append(f"... and {len(self.highlights) - 5} more highlights")
        
        return '\n'.join(lines)
    
    def format_compact(self) -> str:
        """
        Format passage in compact form for lists and summaries.
        
        Returns:
            Compact passage representation
        """
        highlight_info = f", {len(self.highlights)} highlights" if self.highlights else ""
        return f"📖 {self.reference} ({self.total_verses} verses{highlight_info})"
    
    def format_metadata_summary(self) -> str:
        """
        Format just the metadata as a summary.
        
        Returns:
            Formatted metadata summary
        """
        lines = [
            f"Reference: {self.reference}",
            f"Version: {self.version}",
            f"Verses: {self.total_verses}",
            f"Words: {self.total_words}",
            f"Characters: {self.total_characters}",
        ]
        
        if len(self.books) > 1:
            lines.append(f"Books: {', '.join(self.books)}")
        
        lines.append(f"Chapter range: {self.chapter_range}")
        
        if self.highlights:
            coverage = self.get_highlight_coverage()
            lines.append(f"Highlights: {len(self.highlights)} ({coverage:.1f}% coverage)")
        
        return '\n'.join(lines)
    
    def format_verses_with_highlights(self, max_width: int = 80) -> str:
        """
        Format verses with highlight visualization.
        
        Args:
            max_width: Maximum line width for formatting
            
        Returns:
            Formatted verses with highlight markers
        """
        lines = []
        
        for verse in self.verses:
            verse_text = verse.format_display(show_reference=True, max_width=max_width)
            verse_text = self._add_highlight_visualization(verse_text, verse, max_width)
            lines.append(verse_text)
        
        return '\n'.join(lines)
    
    def _add_highlight_visualization(self, verse_text: str, verse: BibleVerse, max_width: int) -> str:
        """
        Add highlight visualization to verse text.
        
        Args:
            verse_text: Original formatted verse text
            verse: The BibleVerse object
            max_width: Maximum line width
            
        Returns:
            Verse text with highlight markers
        """
        if not self.highlights:
            return verse_text
        
        # Find verse index in passage
        verse_index = -1
        for i, v in enumerate(self.verses):
            if (v.book == verse.book and v.chapter == verse.chapter and v.verse == verse.verse):
                verse_index = i
                break
        
        if verse_index == -1:
            return verse_text
        
        # Find highlights that affect this verse
        verse_highlights = []
        for highlight in self.highlights:
            if (highlight.start_position.verse_index <= verse_index <= highlight.end_position.verse_index):
                verse_highlights.append(highlight)
        
        if not verse_highlights:
            return verse_text
        
        # Add highlight indicators
        highlight_indicators = []
        for highlight in verse_highlights:
            if highlight.spans_multiple_verses():
                if verse_index == highlight.start_position.verse_index:
                    highlight_indicators.append(f"  ✨ Highlight starts here (by {highlight.highlight_count} users)")
                elif verse_index == highlight.end_position.verse_index:
                    highlight_indicators.append(f"  ✨ Highlight ends here (by {highlight.highlight_count} users)")
                else:
                    highlight_indicators.append(f"  ✨ Part of multi-verse highlight (by {highlight.highlight_count} users)")
            else:
                words = verse.get_words()
                start_word = highlight.start_position.word_index
                end_word = highlight.end_position.word_index
                if start_word < len(words) and end_word < len(words):
                    highlighted_words = words[start_word:end_word + 1]
                    highlight_indicators.append(f"  ✨ \"{' '.join(highlighted_words)}\" (by {highlight.highlight_count} users)")
        
        if highlight_indicators:
            return verse_text + '\n' + '\n'.join(highlight_indicators)
        
        return verse_text
    
    def format_highlights_summary(self) -> str:
        """
        Format a summary of all highlights in the passage.
        
        Returns:
            Formatted highlights summary
        """
        if not self.highlights:
            return "No highlights in this passage."
        
        lines = [f"✨ HIGHLIGHTS SUMMARY ({len(self.highlights)} total):"]
        lines.append("─" * 40)
        
        popular_highlights = self.get_popular_highlights()
        
        for i, highlight in enumerate(popular_highlights, 1):
            position_desc = highlight.get_position_description(self)
            try:
                text_preview = highlight.get_highlighted_text(self)[:50]
                if len(highlight.get_highlighted_text(self)) > 50:
                    text_preview += "..."
            except (IndexError, ValueError):
                text_preview = "[Invalid highlight]"
            
            lines.append(f"{i}. {position_desc}")
            lines.append(f"   \"{text_preview}\"")
            lines.append(f"   Highlighted by {highlight.highlight_count} users")
            lines.append("")
        
        # Add coverage statistics
        coverage = self.get_highlight_coverage()
        lines.append(f"Total coverage: {coverage:.1f}% of passage")
        
        return '\n'.join(lines)
    
    def to_json_file(self, filepath: str) -> None:
        """
        Save passage to JSON file.
        
        Args:
            filepath: Path to save the JSON file
            
        Raises:
            IOError: If file cannot be written
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_json_file(cls, filepath: str) -> 'BiblePassage':
        """
        Load passage from JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            BiblePassage object
            
        Raises:
            IOError: If file cannot be read
            ValueError: If JSON is invalid or data doesn't match schema
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())