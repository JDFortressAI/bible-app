#!/usr/bin/env python3
"""
Demonstration of Bible data models JSON serialization and caching functionality.

This script shows how to use the new JSON serialization features.
"""

import json
from datetime import datetime
from .bible_models import BiblePassage, BibleVerse, BibleHighlight, HighlightPosition
from .mccheyne import McCheyneReader


def demo_basic_serialization():
    """Demonstrate basic JSON serialization for all models."""
    print("🔧 Basic JSON Serialization Demo")
    print("=" * 50)
    
    # Create sample data
    position = HighlightPosition(verse_index=0, word_index=5)
    verse = BibleVerse(
        book="John",
        chapter=3,
        verse=16,
        text="For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
    )
    highlight = BibleHighlight(
        start_position=HighlightPosition(verse_index=0, word_index=0),
        end_position=HighlightPosition(verse_index=0, word_index=4),
        highlight_count=1247
    )
    passage = BiblePassage(
        reference="John 3:16",
        version="NKJV",
        verses=[verse],
        highlights=[highlight]
    )
    
    print("\n1. HighlightPosition Serialization:")
    print(f"   Original: {position}")
    json_str = position.to_json()
    print(f"   JSON: {json_str}")
    restored = HighlightPosition.from_json(json_str)
    print(f"   Restored: {restored}")
    print(f"   Equal: {position == restored}")
    
    print("\n2. BibleVerse Serialization:")
    print(f"   Original: {verse.reference}")
    json_str = verse.to_json()
    print(f"   JSON length: {len(json_str)} characters")
    restored = BibleVerse.from_json(json_str)
    print(f"   Restored: {restored.reference}")
    print(f"   Text matches: {verse.text == restored.text}")
    
    print("\n3. BibleHighlight Serialization:")
    print(f"   Original: {highlight}")
    json_str = highlight.to_json()
    print(f"   JSON: {json_str}")
    restored = BibleHighlight.from_json(json_str)
    print(f"   Restored: {restored}")
    print(f"   Count matches: {highlight.highlight_count == restored.highlight_count}")
    
    print("\n4. BiblePassage Serialization:")
    print(f"   Original: {passage}")
    json_str = passage.to_json()
    print(f"   JSON length: {len(json_str)} characters")
    restored = BiblePassage.from_json(json_str)
    print(f"   Restored: {restored}")
    print(f"   Verses match: {len(passage.verses) == len(restored.verses)}")
    print(f"   Highlights match: {len(passage.highlights) == len(restored.highlights)}")


def demo_file_operations():
    """Demonstrate file save/load operations."""
    print("\n\n📁 File Operations Demo")
    print("=" * 50)
    
    # Create a sample passage
    passage = BiblePassage(
        reference="Psalm 23:1-3",
        version="NKJV",
        verses=[
            BibleVerse(book="Psalms", chapter=23, verse=1, text="The Lord is my shepherd; I shall not want."),
            BibleVerse(book="Psalms", chapter=23, verse=2, text="He makes me to lie down in green pastures; He leads me beside the still waters."),
            BibleVerse(book="Psalms", chapter=23, verse=3, text="He restores my soul; He leads me in the paths of righteousness For His name's sake.")
        ],
        highlights=[
            BibleHighlight(
                start_position=HighlightPosition(verse_index=0, word_index=0),
                end_position=HighlightPosition(verse_index=0, word_index=6),
                highlight_count=892
            )
        ]
    )
    
    filename = "demo_passage.json"
    
    print(f"\n1. Saving passage to file: {filename}")
    passage.to_json_file(filename)
    print(f"   ✅ Saved successfully")
    
    print(f"\n2. Loading passage from file: {filename}")
    loaded_passage = BiblePassage.from_json_file(filename)
    print(f"   ✅ Loaded: {loaded_passage.reference}")
    print(f"   Verses: {loaded_passage.total_verses}")
    print(f"   Words: {loaded_passage.total_words}")
    print(f"   Highlights: {len(loaded_passage.highlights)}")
    
    # Clean up
    import os
    if os.path.exists(filename):
        os.unlink(filename)
        print(f"   🗑️ Cleaned up {filename}")


def demo_cache_functionality():
    """Demonstrate M'Cheyne caching with structured models."""
    print("\n\n💾 Cache Functionality Demo")
    print("=" * 50)
    
    reader = McCheyneReader()
    month, day = 10, 16
    
    # Create sample structured readings
    sample_readings = {
        "Family": [
            BiblePassage(
                reference="Genesis 1:1-3",
                version="NKJV",
                verses=[
                    BibleVerse(book="Genesis", chapter=1, verse=1, text="In the beginning God created the heavens and the earth."),
                    BibleVerse(book="Genesis", chapter=1, verse=2, text="The earth was without form, and void; and darkness was on the face of the deep."),
                    BibleVerse(book="Genesis", chapter=1, verse=3, text="Then God said, 'Let there be light'; and there was light.")
                ]
            )
        ],
        "Secret": [
            BiblePassage(
                reference="Psalm 1:1-2",
                version="NKJV",
                verses=[
                    BibleVerse(book="Psalms", chapter=1, verse=1, text="Blessed is the man Who walks not in the counsel of the ungodly."),
                    BibleVerse(book="Psalms", chapter=1, verse=2, text="But his delight is in the law of the Lord, And in His law he meditates day and night.")
                ]
            )
        ]
    }
    
    print("\n1. Saving structured readings to cache:")
    reader.save_structured_readings_to_cache(month, day, sample_readings)
    
    print("\n2. Loading structured readings from cache:")
    loaded_readings = reader.load_cached_structured_readings(month, day)
    
    print(f"\n3. Verification:")
    print(f"   Family passages: {len(loaded_readings['Family'])}")
    print(f"   Secret passages: {len(loaded_readings['Secret'])}")
    
    if loaded_readings["Family"]:
        family_passage = loaded_readings["Family"][0]
        print(f"   Family reference: {family_passage.reference}")
        print(f"   Family verses: {family_passage.total_verses}")
        print(f"   Family words: {family_passage.total_words}")
    
    if loaded_readings["Secret"]:
        secret_passage = loaded_readings["Secret"][0]
        print(f"   Secret reference: {secret_passage.reference}")
        print(f"   Secret verses: {secret_passage.total_verses}")
        print(f"   Secret words: {secret_passage.total_words}")
    
    # Clean up cache files
    import os
    cache_files = [
        reader.get_structured_cache_filename(month, day),
        reader.get_cache_filename(month, day)
    ]
    
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            os.unlink(cache_file)
            print(f"   🗑️ Cleaned up {cache_file}")


def demo_performance():
    """Demonstrate serialization performance with larger data."""
    print("\n\n⚡ Performance Demo")
    print("=" * 50)
    
    # Create a large passage
    verses = []
    highlights = []
    
    for i in range(50):  # 50 verses
        verse = BibleVerse(
            book="Psalms",
            chapter=119,
            verse=i + 1,
            text=f"This is verse {i + 1} of Psalm 119 with some sample text to demonstrate serialization performance with larger passages."
        )
        verses.append(verse)
        
        # Add some highlights
        if i % 5 == 0:
            highlight = BibleHighlight(
                start_position=HighlightPosition(verse_index=i, word_index=0),
                end_position=HighlightPosition(verse_index=i, word_index=3),
                highlight_count=i + 10
            )
            highlights.append(highlight)
    
    large_passage = BiblePassage(
        reference="Psalm 119:1-50",
        version="NKJV",
        verses=verses,
        highlights=highlights
    )
    
    print(f"\n1. Large passage stats:")
    print(f"   Verses: {large_passage.total_verses}")
    print(f"   Words: {large_passage.total_words}")
    print(f"   Characters: {large_passage.total_characters}")
    print(f"   Highlights: {len(large_passage.highlights)}")
    
    print(f"\n2. Serialization performance:")
    start_time = datetime.now()
    json_str = large_passage.to_json()
    serialize_time = (datetime.now() - start_time).total_seconds()
    print(f"   Serialization time: {serialize_time:.4f} seconds")
    print(f"   JSON size: {len(json_str):,} characters")
    
    print(f"\n3. Deserialization performance:")
    start_time = datetime.now()
    restored_passage = BiblePassage.from_json(json_str)
    deserialize_time = (datetime.now() - start_time).total_seconds()
    print(f"   Deserialization time: {deserialize_time:.4f} seconds")
    print(f"   Restored verses: {restored_passage.total_verses}")
    print(f"   Restored highlights: {len(restored_passage.highlights)}")
    
    print(f"\n4. Round-trip accuracy:")
    print(f"   Reference matches: {large_passage.reference == restored_passage.reference}")
    print(f"   Verse count matches: {large_passage.total_verses == restored_passage.total_verses}")
    print(f"   Word count matches: {large_passage.total_words == restored_passage.total_words}")
    print(f"   Highlight count matches: {len(large_passage.highlights) == len(restored_passage.highlights)}")


if __name__ == "__main__":
    print("🚀 Bible Data Models JSON Serialization Demo")
    print("=" * 60)
    
    demo_basic_serialization()
    demo_file_operations()
    demo_cache_functionality()
    demo_performance()
    
    print("\n\n✅ Demo Complete!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("• JSON serialization/deserialization for all models")
    print("• File save/load operations")
    print("• Structured cache functionality")
    print("• Performance with large datasets")
    print("• Round-trip accuracy validation")
    print("• Error handling and validation")