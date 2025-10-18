"""
Performance tests for Bible data models to ensure sub-100ms operations.

This module tests the performance of various operations on Bible models
to ensure they meet the requirement of completing within 100ms for typical operations.
"""

import pytest
import time
from typing import List
from src.bible_models import (
    BibleVerse, BiblePassage, BibleHighlight, HighlightPosition,
    PerformanceMonitor, _global_cache
)


class TestPerformanceRequirements:
    """Test performance requirements for Bible data models."""
    
    def setup_method(self):
        """Set up test data for performance tests."""
        # Clear any existing cache
        _global_cache.clear()
        
        # Create test verses for a large passage (Luke 1:1-80)
        self.large_verses = []
        for verse_num in range(1, 81):  # 80 verses
            verse_text = f"This is verse {verse_num} of Luke chapter 1. " * 10  # ~100 words per verse
            self.large_verses.append(BibleVerse(
                book="Luke",
                chapter=1,
                verse=verse_num,
                text=verse_text
            ))
        
        # Create a large passage
        self.large_passage = BiblePassage(
            reference="Luke 1:1-80",
            version="NKJV",
            verses=self.large_verses
        )
        
        # Add many highlights to test highlight operations
        for i in range(0, 50, 2):  # 25 highlights
            start_pos = HighlightPosition(verse_index=i, word_index=0)
            end_pos = HighlightPosition(verse_index=i, word_index=5)
            self.large_passage.add_highlight(start_pos, end_pos)
    
    def time_operation(self, operation, *args, **kwargs):
        """
        Time an operation and return the result and execution time.
        
        Args:
            operation: Function to time
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Tuple of (result, execution_time_ms)
        """
        start_time = time.perf_counter()
        result = operation(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        return result, execution_time
    
    def test_verse_creation_performance(self):
        """Test that verse creation is fast."""
        def create_verse():
            return BibleVerse(
                book="Genesis",
                chapter=1,
                verse=1,
                text="In the beginning God created the heavens and the earth."
            )
        
        _, execution_time = self.time_operation(create_verse)
        assert execution_time < 10, f"Verse creation took {execution_time:.2f}ms, should be < 10ms"
    
    def test_verse_property_access_performance(self):
        """Test that verse property access is fast (cached)."""
        verse = BibleVerse(
            book="John",
            chapter=3,
            verse=16,
            text="For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
        )
        
        # First access (should compute and cache)
        _, first_access_time = self.time_operation(lambda: verse.word_count)
        
        # Second access (should use cache)
        _, second_access_time = self.time_operation(lambda: verse.word_count)
        
        assert first_access_time < 5, f"First word_count access took {first_access_time:.2f}ms"
        assert second_access_time < 1, f"Cached word_count access took {second_access_time:.2f}ms"
        
        # Test other cached properties
        _, char_time = self.time_operation(lambda: verse.char_count)
        _, ref_time = self.time_operation(lambda: verse.reference)
        _, words_time = self.time_operation(lambda: verse.words)
        
        assert char_time < 1, f"char_count access took {char_time:.2f}ms"
        assert ref_time < 1, f"reference access took {ref_time:.2f}ms"
        assert words_time < 5, f"words access took {words_time:.2f}ms"
    
    def test_passage_creation_performance(self):
        """Test that passage creation with multiple verses is reasonably fast."""
        verses = self.large_verses[:10]  # Use 10 verses for this test
        
        def create_passage():
            return BiblePassage(
                reference="Luke 1:1-10",
                version="NKJV",
                verses=verses
            )
        
        _, execution_time = self.time_operation(create_passage)
        assert execution_time < 50, f"Passage creation took {execution_time:.2f}ms, should be < 50ms"
    
    def test_passage_metadata_performance(self):
        """Test that passage metadata calculations are fast."""
        passage = self.large_passage
        
        # Test total_words (lazy property)
        _, words_time = self.time_operation(lambda: passage.total_words)
        assert words_time < 100, f"total_words calculation took {words_time:.2f}ms"
        
        # Second access should be much faster (cached)
        _, cached_words_time = self.time_operation(lambda: passage.total_words)
        assert cached_words_time < 1, f"Cached total_words took {cached_words_time:.2f}ms"
        
        # Test other metadata properties
        _, chars_time = self.time_operation(lambda: passage.total_characters)
        _, books_time = self.time_operation(lambda: passage.books)
        _, range_time = self.time_operation(lambda: passage.chapter_range)
        
        assert chars_time < 100, f"total_characters calculation took {chars_time:.2f}ms"
        assert books_time < 10, f"books calculation took {books_time:.2f}ms"
        assert range_time < 5, f"chapter_range calculation took {range_time:.2f}ms"
    
    def test_highlight_operations_performance(self):
        """Test that highlight operations are fast."""
        passage = self.large_passage
        
        # Test adding a highlight
        start_pos = HighlightPosition(verse_index=10, word_index=5)
        end_pos = HighlightPosition(verse_index=10, word_index=10)
        
        _, add_time = self.time_operation(passage.add_highlight, start_pos, end_pos)
        assert add_time < 10, f"Adding highlight took {add_time:.2f}ms"
        
        # Test getting popular highlights
        _, popular_time = self.time_operation(passage.get_popular_highlights)
        assert popular_time < 20, f"Getting popular highlights took {popular_time:.2f}ms"
        
        # Test highlight coverage calculation (optimized version)
        _, coverage_time = self.time_operation(passage.get_highlight_coverage_optimized)
        assert coverage_time < 100, f"Highlight coverage calculation took {coverage_time:.2f}ms"
        
        # Test highlight search
        _, search_time = self.time_operation(passage.search_highlights, min_count=1)
        assert search_time < 50, f"Highlight search took {search_time:.2f}ms"
    
    def test_json_serialization_performance(self):
        """Test that JSON serialization is fast for large passages."""
        passage = self.large_passage
        
        # Test optimized JSON serialization
        _, serialize_time = self.time_operation(passage.to_json_optimized)
        assert serialize_time < 100, f"JSON serialization took {serialize_time:.2f}ms"
        
        # Test serialization without highlights (should be faster)
        _, serialize_no_highlights_time = self.time_operation(
            passage.to_json_optimized, exclude_highlights=True
        )
        assert serialize_no_highlights_time < 80, f"JSON serialization without highlights took {serialize_no_highlights_time:.2f}ms"
        
        # Test deserialization
        json_data = passage.to_json_optimized()
        _, deserialize_time = self.time_operation(BiblePassage.from_json_optimized, json_data)
        assert deserialize_time < 100, f"JSON deserialization took {deserialize_time:.2f}ms"
    
    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring functionality."""
        passage = self.large_passage
        
        # Test memory usage calculation
        _, memory_time = self.time_operation(passage.get_memory_usage)
        assert memory_time < 10, f"Memory usage calculation took {memory_time:.2f}ms"
        
        # Test system memory monitoring
        _, system_memory_time = self.time_operation(PerformanceMonitor.get_memory_usage)
        assert system_memory_time < 50, f"System memory monitoring took {system_memory_time:.2f}ms"
    
    def test_cache_invalidation_performance(self):
        """Test that cache invalidation is fast."""
        passage = self.large_passage
        
        # Access some properties to populate cache
        _ = passage.total_words
        _ = passage.total_characters
        _ = passage.books
        
        # Test cache invalidation
        _, invalidation_time = self.time_operation(passage.invalidate_cache)
        assert invalidation_time < 5, f"Cache invalidation took {invalidation_time:.2f}ms"
        
        # Test selective cache invalidation
        _ = passage.total_words  # Repopulate cache
        _, selective_time = self.time_operation(passage.invalidate_cache, 'total_words')
        assert selective_time < 2, f"Selective cache invalidation took {selective_time:.2f}ms"
    
    def test_large_passage_operations(self):
        """Test operations on very large passages to ensure scalability."""
        # Create an even larger passage (all of Psalm 119 - 176 verses)
        large_verses = []
        for verse_num in range(1, 177):
            verse_text = f"Psalm 119 verse {verse_num} content. " * 15  # ~150 words per verse
            large_verses.append(BibleVerse(
                book="Psalm",
                chapter=119,
                verse=verse_num,
                text=verse_text
            ))
        
        large_passage = BiblePassage(
            reference="Psalm 119:1-176",
            version="NKJV",
            verses=large_verses
        )
        
        # Add many highlights
        for i in range(0, 100, 5):  # 20 highlights
            if i < len(large_verses):
                start_pos = HighlightPosition(verse_index=i, word_index=0)
                end_pos = HighlightPosition(verse_index=min(i + 2, len(large_verses) - 1), word_index=10)
                large_passage.add_highlight(start_pos, end_pos)
        
        # Test that operations still perform well on large passages
        _, words_time = self.time_operation(lambda: large_passage.total_words)
        assert words_time < 200, f"Large passage total_words took {words_time:.2f}ms"
        
        _, coverage_time = self.time_operation(large_passage.get_highlight_coverage_optimized)
        assert coverage_time < 200, f"Large passage highlight coverage took {coverage_time:.2f}ms"
        
        _, json_time = self.time_operation(large_passage.to_json_optimized)
        assert json_time < 300, f"Large passage JSON serialization took {json_time:.2f}ms"


class TestMemoryUsage:
    """Test memory usage characteristics of Bible models."""
    
    def test_verse_memory_efficiency(self):
        """Test that verses use memory efficiently."""
        verse = BibleVerse(
            book="John",
            chapter=3,
            verse=16,
            text="For God so loved the world that He gave His only begotten Son."
        )
        
        memory_info = PerformanceMonitor.get_memory_usage()
        initial_memory = memory_info['rss_mb']
        
        # Create many verses
        verses = []
        for i in range(1000):
            verses.append(BibleVerse(
                book="Genesis",
                chapter=1,
                verse=i + 1,
                text=f"This is verse {i + 1} with some content to test memory usage."
            ))
        
        final_memory_info = PerformanceMonitor.get_memory_usage()
        final_memory = final_memory_info['rss_mb']
        
        memory_increase = final_memory - initial_memory
        memory_per_verse = memory_increase / 1000 * 1024  # Convert to KB per verse
        
        # Each verse should use less than 5KB on average
        assert memory_per_verse < 5, f"Each verse uses {memory_per_verse:.2f}KB, should be < 5KB"
    
    def test_passage_memory_reporting(self):
        """Test that passage memory reporting is accurate."""
        verses = []
        for i in range(10):
            verses.append(BibleVerse(
                book="Matthew",
                chapter=1,
                verse=i + 1,
                text=f"This is verse {i + 1} of Matthew chapter 1."
            ))
        
        passage = BiblePassage(
            reference="Matthew 1:1-10",
            version="NKJV",
            verses=verses
        )
        
        memory_usage = passage.get_memory_usage()
        
        # Verify memory usage structure
        assert 'total_bytes' in memory_usage
        assert 'total_kb' in memory_usage
        assert 'verse_memory_bytes' in memory_usage
        assert 'highlight_memory_bytes' in memory_usage
        assert 'metadata_memory_bytes' in memory_usage
        assert 'avg_bytes_per_verse' in memory_usage
        
        # Verify reasonable memory usage
        assert memory_usage['total_bytes'] > 0
        assert memory_usage['total_kb'] == memory_usage['total_bytes'] / 1024
        assert memory_usage['avg_bytes_per_verse'] > 0


class TestCacheEffectiveness:
    """Test that caching is working effectively."""
    
    def test_property_caching(self):
        """Test that properties are properly cached."""
        verse = BibleVerse(
            book="Romans",
            chapter=8,
            verse=28,
            text="And we know that all things work together for good to those who love God, to those who are the called according to His purpose."
        )
        
        # First access should compute and cache
        word_count1 = verse.word_count
        
        # Verify cache exists
        assert hasattr(verse, '_cached_word_count')
        assert getattr(verse, '_cached_word_count') == word_count1
        
        # Second access should use cache
        word_count2 = verse.word_count
        assert word_count1 == word_count2
        
        # Test cache invalidation
        verse.invalidate_cache('word_count')
        assert not hasattr(verse, '_cached_word_count')
    
    def test_lazy_property_caching(self):
        """Test that lazy properties work correctly."""
        verses = []
        for i in range(5):
            verses.append(BibleVerse(
                book="Ephesians",
                chapter=2,
                verse=i + 1,
                text=f"Ephesians 2:{i + 1} content with multiple words for testing."
            ))
        
        passage = BiblePassage(
            reference="Ephesians 2:1-5",
            version="NKJV",
            verses=verses
        )
        
        # First access should compute and cache
        total_words1 = passage.total_words
        
        # Verify lazy cache exists
        assert hasattr(passage, '_lazy_total_words')
        assert getattr(passage, '_lazy_total_words') == total_words1
        
        # Second access should use cache
        total_words2 = passage.total_words
        assert total_words1 == total_words2
        
        # Test cache invalidation
        passage.invalidate_cache('total_words')
        assert not hasattr(passage, '_lazy_total_words')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])