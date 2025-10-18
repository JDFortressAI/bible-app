#!/usr/bin/env python3
"""
Example script to test the M'Cheyne integration with structured models.
"""

from src.mccheyne import McCheyneReader
from src.bible_models import BiblePassage, BibleVerse
import json

def test_structured_vs_legacy():
    """Test both structured and legacy formats."""
    reader = McCheyneReader()
    
    # Test reference
    reference = "John 3:16"
    
    print("Testing M'Cheyne Integration with Structured Models")
    print("=" * 60)
    
    # Test legacy format (should still work)
    print("\n1. Testing Legacy Format:")
    print("-" * 30)
    try:
        legacy_result = reader.fetch_passage_text(reference, return_structured=False)
        print(f"Legacy result type: {type(legacy_result)}")
        print(f"Legacy result preview: {legacy_result[:100]}...")
    except Exception as e:
        print(f"Legacy format error: {e}")
    
    # Test structured format
    print("\n2. Testing Structured Format:")
    print("-" * 30)
    try:
        structured_result = reader.fetch_passage_text(reference, return_structured=True)
        print(f"Structured result type: {type(structured_result)}")
        
        if isinstance(structured_result, BiblePassage):
            print(f"Reference: {structured_result.reference}")
            print(f"Version: {structured_result.version}")
            print(f"Total verses: {structured_result.total_verses}")
            print(f"Total words: {structured_result.total_words}")
            print(f"Books: {structured_result.books}")
            print(f"Chapter range: {structured_result.chapter_range}")
            
            print("\nVerses:")
            for i, verse in enumerate(structured_result.verses[:3]):  # Show first 3 verses
                print(f"  {i+1}. {verse.reference}: {verse.text[:50]}...")
        else:
            print(f"Unexpected result: {structured_result}")
    except Exception as e:
        print(f"Structured format error: {e}")
    
    # Test JSON serialization
    print("\n3. Testing JSON Serialization:")
    print("-" * 30)
    try:
        structured_result = reader.fetch_passage_text(reference, return_structured=True)
        if isinstance(structured_result, BiblePassage):
            json_data = structured_result.model_dump()
            json_str = json.dumps(json_data, default=str)  # Handle datetime serialization
            print(f"JSON serialization successful: {len(json_str)} characters")
            
            # Test deserialization
            restored_passage = BiblePassage.model_validate(json_data)
            print(f"Deserialization successful: {restored_passage.reference}")
        else:
            print("Cannot serialize non-BiblePassage result")
    except Exception as e:
        print(f"Serialization error: {e}")
    
    # Test error handling
    print("\n4. Testing Error Handling:")
    print("-" * 30)
    invalid_refs = ["", "Invalid Book 999:999", "Not A Reference"]
    
    for invalid_ref in invalid_refs:
        try:
            result = reader.fetch_passage_text(invalid_ref, return_structured=True)
            if isinstance(result, BiblePassage):
                print(f"✓ Invalid ref '{invalid_ref}' handled gracefully: {result.reference}")
            else:
                print(f"✗ Invalid ref '{invalid_ref}' returned: {type(result)}")
        except Exception as e:
            print(f"✗ Invalid ref '{invalid_ref}' caused error: {e}")

def test_cache_functionality():
    """Test caching with structured models."""
    reader = McCheyneReader()
    
    print("\n5. Testing Cache Functionality:")
    print("-" * 30)
    
    # Test structured cache
    month, day = 10, 16
    
    # Create test passage
    test_passage = BiblePassage(
        reference="Test Reference",
        version="NKJV",
        verses=[
            BibleVerse(book="Genesis", chapter=1, verse=1, text="In the beginning God created the heavens and the earth.")
        ]
    )
    
    test_readings = {
        "Family": [test_passage],
        "Secret": []
    }
    
    try:
        # Save to cache
        reader.save_structured_readings_to_cache(month, day, test_readings)
        print("✓ Structured cache save successful")
        
        # Load from cache
        loaded_readings = reader.load_cached_structured_readings(month, day)
        if loaded_readings["Family"] and isinstance(loaded_readings["Family"][0], BiblePassage):
            print("✓ Structured cache load successful")
            print(f"  Loaded passage: {loaded_readings['Family'][0].reference}")
        else:
            print("✗ Structured cache load failed")
            
    except Exception as e:
        print(f"✗ Cache functionality error: {e}")

if __name__ == "__main__":
    test_structured_vs_legacy()
    test_cache_functionality()
    print("\n" + "=" * 60)
    print("Integration test complete!")