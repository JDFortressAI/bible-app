# Source Code Directory

This directory contains the core application modules for the Bible RAG system.

## Core Modules

### Data Models
- **`bible_models.py`** - Pydantic-based data models for Bible content
  - `BibleVerse` - Individual verse with metadata and validation
  - `BiblePassage` - Collection of verses with highlights and metadata
  - `BibleHighlight` - User highlights with position tracking
  - `HighlightPosition` - Precise word-level positioning
  - JSON serialization and caching support

### Data Processing
- **`bible_parser.py`** - Bible text parsing and processing utilities
  - Bible reference parsing (e.g., "John 3:16", "Luke 1:1-38")
  - Book name normalization and validation
  - Verse text cleaning and extraction
  - M'Cheyne format handling

### Integration Services
- **`mccheyne.py`** - M'Cheyne Bible reading plan integration
  - Daily reading plan fetching
  - Bible text retrieval from biblestudytools.com
  - Structured and legacy format support
  - Caching with automatic migration
  - Error handling and fallback mechanisms

### Applications
- **`bible_chat.py`** - Streamlit-based chat interface
  - OpenAI integration for Bible-focused conversations
  - Interactive chat with context awareness
  - Bible passage lookup and display

- **`main.py`** - Command-line interface and utilities
  - CLI tools for Bible data processing
  - Batch operations and utilities

### Demonstrations
- **`demo_serialization.py`** - JSON serialization demonstration
  - Examples of all serialization features
  - Performance benchmarks
  - Cache functionality demos

## Module Dependencies

```
bible_models.py (base models)
    ↑
bible_parser.py (uses models)
    ↑
mccheyne.py (uses models + parser)
    ↑
bible_chat.py (uses all above)
main.py (uses all above)
demo_serialization.py (uses models + mccheyne)
```

## Key Features

### Pydantic Data Models
- **Type Safety** - Full type validation with Pydantic
- **JSON Serialization** - Built-in JSON support with datetime handling
- **Validation** - Comprehensive input validation and error handling
- **Performance** - Optimized for large Bible passages

### Bible Text Processing
- **Reference Parsing** - Handles complex references like "Zechariah 12:1-13:1"
- **Book Normalization** - Supports abbreviations and variations
- **Text Cleaning** - Removes web artifacts and formatting
- **Verse Extraction** - Intelligent verse boundary detection

### M'Cheyne Integration
- **Daily Readings** - Automatic fetching of daily reading plans
- **Multiple Formats** - Both structured (BiblePassage) and legacy (string) formats
- **Caching System** - Persistent caching with automatic migration
- **Error Recovery** - Graceful handling of network and parsing errors

### Highlight System
- **Word-Level Precision** - Exact word positioning within verses
- **Multi-Verse Spans** - Highlights can span multiple verses
- **Popularity Tracking** - Anonymous user highlight aggregation
- **Coverage Analysis** - Calculate percentage of highlighted text

## Usage Examples

### Basic Model Usage
```python
from src.bible_models import BibleVerse, BiblePassage

verse = BibleVerse(
    book="John",
    chapter=3,
    verse=16,
    text="For God so loved the world..."
)

passage = BiblePassage(
    reference="John 3:16",
    version="NKJV",
    verses=[verse]
)

# JSON serialization
json_str = passage.to_json()
restored = BiblePassage.from_json(json_str)
```

### M'Cheyne Integration
```python
from src.mccheyne import McCheyneReader

reader = McCheyneReader()

# Get today's readings as structured objects
readings = reader.get_todays_readings_structured()
for passage in readings["Family"]:
    print(f"{passage.reference}: {passage.total_words} words")
```

### Bible Text Parsing
```python
from src.bible_parser import parse_bible_text

passage = parse_bible_text(
    reference="Luke 1:1-4",
    text="Forasmuch as many have taken in hand...",
    version="NKJV"
)
```

## Testing

All modules are thoroughly tested with 147 test cases covering:
- Unit tests for all models and functions
- Integration tests with real API endpoints
- Performance tests with large datasets
- Error handling and edge cases

Run tests from the project root:
```bash
uv run python -m pytest tests/ -v
```