#!/usr/bin/env python3
"""
Bible Parser Integration Example

Demonstrates how to integrate the new Bible text parser with the existing M'Cheyne system.
This example shows how to convert raw Bible text into structured BiblePassage objects.
"""

from src.bible_parser import parse_bible_text, parse_mcheyne_passage_list
from src.bible_models import BiblePassage, BibleVerse
from typing import Dict, List


def example_parse_single_passage():
    """Example of parsing a single Bible passage."""
    print("=== Single Passage Parsing Example ===")
    
    # Simulate raw text from biblestudytools.com or similar source
    raw_text = """16 For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life. 17 For God did not send His Son into the world to condemn the world, but that the world through Him might be saved."""
    
    reference = "John 3:16-17"
    
    # Parse the text into a structured passage
    passage = parse_bible_text(raw_text, reference)
    
    print(f"Reference: {passage.reference}")
    print(f"Version: {passage.version}")
    print(f"Total verses: {passage.total_verses}")
    print(f"Total words: {passage.total_words}")
    print(f"Books: {passage.books}")
    print(f"Chapter range: {passage.chapter_range}")
    print()
    
    # Display individual verses
    for i, verse in enumerate(passage.verses):
        print(f"Verse {i+1}: {verse.reference}")
        print(f"  Text: {verse.text}")
        print(f"  Words: {verse.word_count}, Characters: {verse.char_count}")
        print()


def example_parse_complex_mcheyne_formats():
    """Example of parsing complex M'Cheyne formats."""
    print("=== Complex M'Cheyne Formats Example ===")
    
    # Simulate various M'Cheyne passage formats
    mcheyne_passages = {
        "Luke 1:1-38": """1 Inasmuch as many have taken in hand to set in order a narrative of those things which have been fulfilled among us, 2 just as those who from the beginning were eyewitnesses and ministers of the word delivered them to us, 3 it seemed good to me also, having had perfect understanding of all things from the very first, to write to you an orderly account, most excellent Theophilus, 4 that you may know the certainty of those things in which you were instructed.""",
        
        "Zechariah 12:1-13:1": """1 The burden of the word of the Lord against Israel. Thus says the Lord, who stretches out the heavens, lays the foundation of the earth, and forms the spirit of man within him: 2 Behold, I will make Jerusalem a cup of drunkenness to all the surrounding peoples, when they lay siege against Judah and Jerusalem. In that day a fountain shall be opened for the house of David and for the inhabitants of Jerusalem, for sin and for uncleanness.""",
        
        "Psalm 119:1-24": """1 Blessed are the undefiled in the way, Who walk in the law of the Lord! 2 Blessed are those who keep His testimonies, Who seek Him with the whole heart! 3 They also do no iniquity; They walk in His ways. 4 You have commanded us To keep Your precepts diligently.""",
        
        "Genesis 1": """1 In the beginning God created the heavens and the earth. 2 The earth was without form, and void; and darkness was on the face of the deep. And the Spirit of God was hovering over the face of the waters. 3 Then God said, "Let there be light"; and there was light."""
    }
    
    # Parse all passages
    parsed_passages = parse_mcheyne_passage_list(mcheyne_passages)
    
    for reference, passage in parsed_passages.items():
        print(f"📖 {reference}")
        print(f"   Books: {', '.join(passage.books)}")
        print(f"   Verses: {passage.total_verses}, Words: {passage.total_words}")
        print(f"   Chapter range: {passage.chapter_range}")
        
        # Show first verse as example
        if passage.verses:
            first_verse = passage.verses[0]
            preview = first_verse.text[:100] + "..." if len(first_verse.text) > 100 else first_verse.text
            print(f"   Preview: {preview}")
        print()


def example_integration_with_mcheyne_fetcher():
    """Example of how this would integrate with the existing M'Cheyne fetcher."""
    print("=== M'Cheyne Fetcher Integration Example ===")
    
    # Simulate what the M'Cheyne fetcher would return (raw text)
    def simulate_mcheyne_fetch() -> Dict[str, List[str]]:
        """Simulate the existing M'Cheyne fetcher returning raw text."""
        return {
            "Family": ["Genesis 1", "Matthew 1"],
            "Secret": ["Psalm 1", "Romans 1"]
        }
    
    # Simulate raw text that would be fetched for each passage
    def simulate_fetch_passage_text(reference: str) -> str:
        """Simulate fetching raw text for a passage."""
        sample_texts = {
            "Genesis 1": "1 In the beginning God created the heavens and the earth. 2 The earth was without form, and void.",
            "Matthew 1": "1 The book of the genealogy of Jesus Christ, the Son of David, the Son of Abraham:",
            "Psalm 1": "1 Blessed is the man Who walks not in the counsel of the ungodly, Nor stands in the path of sinners.",
            "Romans 1": "1 Paul, a bondservant of Jesus Christ, called to be an apostle, separated to the gospel of God"
        }
        return sample_texts.get(reference, f"Sample text for {reference}")
    
    # Get today's readings
    readings = simulate_mcheyne_fetch()
    
    # Convert to structured passages
    structured_readings = {}
    
    for category, references in readings.items():
        structured_readings[category] = []
        
        for reference in references:
            # Fetch raw text (this would use the existing fetcher)
            raw_text = simulate_fetch_passage_text(reference)
            
            # Parse into structured passage
            try:
                passage = parse_bible_text(raw_text, reference)
                structured_readings[category].append(passage)
                print(f"✅ Parsed {reference} -> {passage.total_verses} verses, {passage.total_words} words")
            except Exception as e:
                print(f"❌ Failed to parse {reference}: {e}")
    
    print()
    print("Structured readings summary:")
    for category, passages in structured_readings.items():
        print(f"{category}: {len(passages)} passages")
        for passage in passages:
            print(f"  - {passage.reference} ({passage.total_verses} verses)")


def example_highlight_integration():
    """Example of how highlights would work with parsed passages."""
    print("=== Highlight Integration Example ===")
    
    # Create a sample passage
    raw_text = "16 For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
    passage = parse_bible_text(raw_text, "John 3:16")
    
    print(f"Original passage: {passage.reference}")
    print(f"Text: {passage.verses[0].text}")
    print()
    
    # Add some highlights (this would come from user interaction)
    from bible_models import HighlightPosition
    
    # Highlight "For God so loved the world"
    start_pos = HighlightPosition(verse_index=0, word_index=0)
    end_pos = HighlightPosition(verse_index=0, word_index=5)
    highlight1 = passage.add_highlight(start_pos, end_pos)
    
    # Highlight "whoever believes in Him"
    start_pos2 = HighlightPosition(verse_index=0, word_index=15)
    end_pos2 = HighlightPosition(verse_index=0, word_index=18)
    highlight2 = passage.add_highlight(start_pos2, end_pos2)
    
    print(f"Added {len(passage.highlights)} highlights:")
    for i, highlight in enumerate(passage.highlights):
        highlighted_text = highlight.get_highlighted_text(passage)
        print(f"  {i+1}. \"{highlighted_text}\" (count: {highlight.highlight_count})")
    
    print(f"Highlight coverage: {passage.get_highlight_coverage():.1f}%")


if __name__ == "__main__":
    print("Bible Parser Integration Examples")
    print("=" * 50)
    print()
    
    example_parse_single_passage()
    example_parse_complex_mcheyne_formats()
    example_integration_with_mcheyne_fetcher()
    example_highlight_integration()
    
    print("Integration examples completed! 🎉")