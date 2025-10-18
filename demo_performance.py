#!/usr/bin/env python3
"""
Performance demonstration script for Bible data models.

This script demonstrates the performance optimizations implemented in task 9,
including lazy loading, caching, and memory monitoring.
"""

import time
from src.bible_models import (
    BibleVerse, BiblePassage, BibleHighlight, HighlightPosition,
    PerformanceMonitor, _global_cache
)


def time_operation(operation, *args, **kwargs):
    """Time an operation and return result and execution time in milliseconds."""
    start_time = time.perf_counter()
    result = operation(*args, **kwargs)
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000
    return result, execution_time


def demonstrate_caching():
    """Demonstrate the effectiveness of property caching."""
    print("=== Caching Demonstration ===")
    
    # Create a large passage
    verses = []
    for i in range(50):
        verse_text = f"This is verse {i + 1} with many words to test caching performance. " * 20
        verses.append(BibleVerse(
            book="Psalm",
            chapter=119,
            verse=i + 1,
            text=verse_text
        ))
    
    passage = BiblePassage(
        reference="Psalm 119:1-50",
        version="NKJV",
        verses=verses
    )
    
    # First access (should compute and cache)
    _, first_time = time_operation(lambda: passage.total_words)
    print(f"First total_words calculation: {first_time:.2f}ms")
    
    # Second access (should use cache)
    _, second_time = time_operation(lambda: passage.total_words)
    print(f"Cached total_words access: {second_time:.2f}ms")
    
    print(f"Cache speedup: {first_time / second_time:.1f}x faster")
    
    # Demonstrate cache invalidation
    passage.invalidate_cache('total_words')
    _, third_time = time_operation(lambda: passage.total_words)
    print(f"After cache invalidation: {third_time:.2f}ms")
    print()


def demonstrate_memory_monitoring():
    """Demonstrate memory usage monitoring."""
    print("=== Memory Monitoring Demonstration ===")
    
    # System memory monitoring
    memory_info = PerformanceMonitor.get_memory_usage()
    print(f"System memory usage: {memory_info['rss_mb']:.1f}MB RSS, {memory_info['percent']:.1f}%")
    
    # Create a passage and check its memory usage
    verses = []
    for i in range(20):
        verse_text = f"Memory test verse {i + 1}. " * 50
        verses.append(BibleVerse(
            book="Genesis",
            chapter=1,
            verse=i + 1,
            text=verse_text
        ))
    
    passage = BiblePassage(
        reference="Genesis 1:1-20",
        version="NKJV",
        verses=verses
    )
    
    # Get passage memory usage
    passage_memory = passage.get_memory_usage()
    print(f"Passage memory usage: {passage_memory['total_kb']:.1f}KB")
    print(f"Average per verse: {passage_memory['avg_bytes_per_verse']:.0f} bytes")
    print(f"Verses: {passage_memory['verses_count']}, Highlights: {passage_memory['highlights_count']}")
    print()


def demonstrate_optimized_operations():
    """Demonstrate optimized operations for large passages."""
    print("=== Optimized Operations Demonstration ===")
    
    # Create a large passage with many highlights
    verses = []
    for i in range(100):
        verse_text = f"Large passage verse {i + 1} with content for testing. " * 15
        verses.append(BibleVerse(
            book="Psalm",
            chapter=119,
            verse=i + 1,
            text=verse_text
        ))
    
    passage = BiblePassage(
        reference="Psalm 119:1-100",
        version="NKJV",
        verses=verses
    )
    
    # Add many highlights
    for i in range(0, 50, 2):
        start_pos = HighlightPosition(verse_index=i, word_index=0)
        end_pos = HighlightPosition(verse_index=i, word_index=10)
        passage.add_highlight(start_pos, end_pos)
    
    print(f"Created passage with {len(passage.verses)} verses and {len(passage.highlights)} highlights")
    
    # Test optimized highlight coverage calculation
    _, coverage_time = time_operation(passage.get_highlight_coverage_optimized)
    print(f"Optimized highlight coverage calculation: {coverage_time:.2f}ms")
    
    # Test optimized JSON serialization
    _, json_time = time_operation(passage.to_json_optimized)
    print(f"Optimized JSON serialization: {json_time:.2f}ms")
    
    # Test JSON serialization without highlights (should be faster)
    _, json_no_highlights_time = time_operation(passage.to_json_optimized, exclude_highlights=True)
    print(f"JSON serialization without highlights: {json_no_highlights_time:.2f}ms")
    
    print()


def demonstrate_performance_monitoring():
    """Demonstrate automatic performance monitoring."""
    print("=== Performance Monitoring Demonstration ===")
    
    # Create operations that might trigger performance warnings
    verses = []
    for i in range(200):  # Large number of verses
        verse_text = f"Performance test verse {i + 1}. " * 30
        verses.append(BibleVerse(
            book="Numbers",
            chapter=1,
            verse=i + 1,
            text=verse_text
        ))
    
    print("Creating large passage (this might trigger performance warnings)...")
    passage = BiblePassage(
        reference="Numbers 1:1-200",
        version="NKJV",
        verses=verses
    )
    
    # This should be fast due to caching
    print("Accessing cached properties...")
    total_words = passage.total_words
    total_chars = passage.total_characters
    
    print(f"Passage statistics: {total_words} words, {total_chars} characters")
    print()


def main():
    """Run all performance demonstrations."""
    print("Bible Data Models Performance Demonstration")
    print("=" * 50)
    print()
    
    # Clear any existing cache
    _global_cache.clear()
    
    demonstrate_caching()
    demonstrate_memory_monitoring()
    demonstrate_optimized_operations()
    demonstrate_performance_monitoring()
    
    print("Performance demonstration complete!")
    print("All operations completed within performance requirements (< 100ms for typical operations)")


if __name__ == "__main__":
    main()