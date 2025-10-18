# Bible Data Models - Design Document

## Overview

This design document outlines the implementation of a structured Bible data modeling system using Pydantic BaseModel classes. The system provides a flexible two-level hierarchy (BiblePassage → BibleVerse) that can handle complex M'Cheyne reading patterns while supporting anonymous user highlighting with popularity tracking.

## Architecture

### Core Design Principles

1. **Simplicity**: Two-level hierarchy keeps the model simple while remaining flexible
2. **Focus**: Eliminate distracting statistics and UI controls to center attention on Scripture
3. **Readability**: Large, responsive typography optimized for comfortable reading
4. **Validation**: Pydantic ensures data integrity and type safety
5. **Privacy**: Anonymous highlighting without user identification
6. **Extensibility**: Design allows for future enhancements

### System Components

```
BiblePassage
├── metadata (reference, version, stats)
├── verses: List[BibleVerse]
└── highlights: List[BibleHighlight]

BibleVerse
├── book: str
├── chapter: int
├── verse: int
├── text: str
└── metadata (word_count, char_count)

BibleHighlight
├── start_position: HighlightPosition
├── end_position: HighlightPosition
└── highlight_count: int

HighlightPosition
├── verse_index: int (index in passage.verses)
└── word_index: int (word position in verse)
```

## Components and Interfaces

### BibleVerse Model

```python
class BibleVerse(BaseModel):
    book: str = Field(..., description="Bible book name (e.g., 'Genesis', '1 Kings')")
    chapter: int = Field(..., gt=0, description="Chapter number")
    verse: int = Field(..., gt=0, description="Verse number")
    text: str = Field(..., min_length=1, description="The actual verse text")
    
    # Essential properties only (no statistics)
    @property
    def reference(self) -> str:
        """Full verse reference (e.g., 'John 3:16')"""
        return f"{self.book} {self.chapter}:{self.verse}"
    
    def get_words(self) -> List[str]:
        """Split verse text into individual words (for highlighting only)"""
        return self.text.split()
```

### HighlightPosition Model

```python
class HighlightPosition(BaseModel):
    verse_index: int = Field(..., ge=0, description="Index of verse in passage.verses list")
    word_index: int = Field(..., ge=0, description="Index of word within the verse")
    
    def __lt__(self, other: 'HighlightPosition') -> bool:
        """Enable position comparison for sorting"""
        if self.verse_index != other.verse_index:
            return self.verse_index < other.verse_index
        return self.word_index < other.word_index
```

### BibleHighlight Model

```python
class BibleHighlight(BaseModel):
    start_position: HighlightPosition = Field(..., description="Start position of highlight")
    end_position: HighlightPosition = Field(..., description="End position of highlight")
    highlight_count: int = Field(default=1, ge=1, description="Number of users who highlighted this section")
    
    @validator('end_position')
    def end_after_start(cls, v, values):
        """Ensure end position is after start position"""
        if 'start_position' in values and v < values['start_position']:
            raise ValueError('End position must be after start position')
        return v
    
    def spans_multiple_verses(self) -> bool:
        """Check if highlight spans multiple verses"""
        return self.start_position.verse_index != self.end_position.verse_index
    
    def get_highlighted_text(self, passage: 'BiblePassage') -> str:
        """Extract the highlighted text from the passage"""
        # Implementation details in the code section
```

### BiblePassage Model

```python
class BiblePassage(BaseModel):
    reference: str = Field(..., description="Human-readable reference (e.g., 'Luke 1:1-38')")
    version: str = Field(default="NKJV", description="Bible version")
    verses: List[BibleVerse] = Field(..., min_items=1, description="List of verses in the passage")
    highlights: List[BibleHighlight] = Field(default_factory=list, description="User highlights")
    fetched_at: datetime = Field(default_factory=datetime.now, description="When passage was fetched")
    
    # Essential properties only (no statistics exposed to UI)
    @property
    def books(self) -> List[str]:
        """List of unique books in this passage"""
        return list(dict.fromkeys(verse.book for verse in self.verses))
    
    @property
    def chapter_range(self) -> str:
        """Human-readable chapter range"""
        # Implementation details in the code section
```

## Data Models

### JSON Schema Examples

**Single Chapter Passage:**
```json
{
  "reference": "John 3:16-17",
  "version": "NKJV",
  "verses": [
    {
      "book": "John",
      "chapter": 3,
      "verse": 16,
      "text": "For God so loved the world that He gave His only begotten Son, that whoever believes in Him should not perish but have everlasting life."
    },
    {
      "book": "John", 
      "chapter": 3,
      "verse": 17,
      "text": "For God did not send His Son into the world to condemn the world, but that the world through Him might be saved."
    }
  ],
  "highlights": [
    {
      "start_position": {"verse_index": 0, "word_index": 0},
      "end_position": {"verse_index": 0, "word_index": 4},
      "highlight_count": 1247
    }
  ],
  "fetched_at": "2025-10-16T10:30:00Z"
}
```

**Multi-Chapter Passage:**
```json
{
  "reference": "Zechariah 12:1-13:1",
  "version": "NKJV",
  "verses": [
    {
      "book": "Zechariah",
      "chapter": 12,
      "verse": 1,
      "text": "The burden of the word of the Lord against Israel. Thus says the Lord, who stretches out the heavens, lays the foundation of the earth, and forms the spirit of man within him:"
    },
    {
      "book": "Zechariah",
      "chapter": 13,
      "verse": 1,
      "text": "In that day a fountain shall be opened for the house of David and for the inhabitants of Jerusalem, for sin and for uncleanness."
    }
  ],
  "highlights": [],
  "fetched_at": "2025-10-16T10:30:00Z"
}
```

## Error Handling

### Validation Errors

1. **Invalid verse references**: Negative or zero chapter/verse numbers
2. **Empty text**: Verses must contain actual content
3. **Invalid highlight positions**: Word indices beyond verse boundaries
4. **Malformed highlights**: End position before start position

### Error Response Format

```python
class BibleValidationError(Exception):
    def __init__(self, message: str, field: str = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(message)
```

## Testing Strategy

### Unit Tests

1. **Model Validation Tests**
   - Valid data creation
   - Invalid data rejection
   - Edge cases (single word verses, maximum lengths)

2. **Metadata Calculation Tests**
   - Word count accuracy
   - Character count accuracy
   - Reference string generation

3. **Highlight System Tests**
   - Position validation
   - Multi-verse highlighting
   - Highlight text extraction

### Integration Tests

1. **M'Cheyne Integration Tests**
   - Complex passage parsing
   - Cache serialization/deserialization
   - Backward compatibility

2. **Performance Tests**
   - Large passage handling
   - Highlight lookup performance
   - JSON serialization speed

### Test Data

```python
# Test fixtures for various passage types
SINGLE_VERSE = BibleVerse(book="John", chapter=3, verse=16, text="For God so loved...")
MULTI_CHAPTER_PASSAGE = BiblePassage(
    reference="Luke 1:1-38",
    verses=[...],  # 38 verses spanning Luke 1
    highlights=[]
)
COMPLEX_HIGHLIGHT = BibleHighlight(
    start_position=HighlightPosition(verse_index=0, word_index=5),
    end_position=HighlightPosition(verse_index=2, word_index=10),
    highlight_count=42
)
```

## Focused Reading Interface Design

### Large Text Display System

The interface prioritizes Scripture readability through large, responsive typography and minimal visual distractions.

#### Responsive Font Sizing

**Desktop Display (≥768px width):**
- Base font size: 28-32px
- Line height: 1.6-1.8
- Maximum 20 words per line
- Generous margins and padding

**Mobile Display (<768px width):**
- Base font size: 24-28px  
- Line height: 1.5-1.7
- Maximum 8 words per line
- Optimized touch targets

#### Fixed Display Options

The interface removes user configuration options to maintain focus:
- **Verse numbers**: Always displayed (no toggle)
- **View mode**: Always compact format (no detailed/metadata modes)
- **Verse display**: Always show all verses (no pagination)
- **Statistics**: Never displayed (no word counts, verse counts, etc.)

#### CSS Implementation

```css
.bible-text {
  font-size: clamp(24px, 4vw, 32px);
  line-height: 1.6;
  max-width: 100%;
  word-wrap: break-word;
  font-family: 'Georgia', 'Times New Roman', serif;
}

/* Light mode colors */
[data-theme="light"] .bible-text {
  color: #2c3e50;
}

/* Dark mode colors - optimized for readability */
[data-theme="dark"] .bible-text {
  color: #e8e8e8;
}

/* Auto-detect dark mode */
@media (prefers-color-scheme: dark) {
  .bible-text {
    color: #e8e8e8;
  }
  .verse-number {
    color: #b8b8b8;
  }
}

@media (max-width: 767px) {
  .bible-text {
    font-size: clamp(20px, 6vw, 28px);
    line-height: 1.5;
  }
}

.verse-number {
  font-size: 0.75em;
  opacity: 0.8;
  margin-right: 0.5em;
  font-weight: bold;
}
```

#### Interface Layout

- **Mode Selector**: Moved to bottom of sidebar for better focus on content
- **Sidebar Organization**: 
  - Reading Mode: Passage selection → Refresh button → Mode selector
  - Chat Mode: Question suggestions → Clear history → Mode selector

#### Scroll Position Memory System

**Native Streamlit Tabs Implementation:**
- Each Bible passage displayed in separate `st.tabs()` component
- Streamlit automatically maintains independent scroll contexts per tab
- No complex JavaScript or localStorage management required
- Clean, intuitive user interface with tab navigation

**Tab-Based Architecture:**
```python
# Create tabs for each passage
tab_labels = [f"{passage.reference}" for passage in all_passages]
tabs = st.tabs(tab_labels)

# Each passage gets its own tab with independent scroll context
for i, (tab, passage) in enumerate(zip(tabs, all_passages)):
    with tab:
        display_bible_passage(passage, i)
```

**User Experience:**
- Click tabs to switch between passages instantly
- Each tab remembers exact scroll position automatically
- First visit to any passage starts at the top
- Return visits restore previous reading position
- Visual indication of current passage via active tab
- Seamless reading experience across all four daily passages

## Typography and Text Processing

### Typography Enhancement System

The system includes comprehensive typography processing to ensure professional, readable Bible text that follows established conventions.

#### Quote and Punctuation Processing

1. **Smart Quotes**: Convert straight quotes to proper typographic quotes
   - `"text"` → `"text"` (Unicode 8220, 8221)
   - `'text'` → `'text'` (Unicode 8216, 8217)
   - Context-aware apostrophe handling for contractions

2. **Enhanced Punctuation**:
   - Em dashes: `--` → `—`
   - Ellipses: `...` → `…`
   - Proper apostrophes in contractions: `don't` → `don't`

#### Divine Name (YHWH) Typography

Special handling for the tetragrammaton YHWH, following biblical typography conventions and theological accuracy:

**Theological Context:**
- **Old Testament**: "Lord" often represents YHWH (tetragrammaton) → small caps
- **New Testament**: "Lord" typically refers to Jesus Christ → normal case

**Book Detection:**
```python
def is_old_testament_book(book: str) -> bool:
    old_testament_books = {
        'genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy',
        'joshua', 'judges', 'ruth', '1 samuel', '2 samuel', '1 kings', '2 kings',
        # ... all OT books
    }
    return book.lower() in old_testament_books
```

**Pattern Recognition (Old Testament Only):**
```python
yhwh_patterns = [
    # Primary cases (99.9%)
    r'\bthe Lord\b' → 'the Lᴏʀᴅ',
    r'\bO Lord\b' → 'O Lᴏʀᴅ',
    
    # Compound forms
    r'\bthe Lord God\b' → 'the Lᴏʀᴅ God',
    r'\bLord of hosts\b' → 'Lᴏʀᴅ of hosts',
    
    # Possessive forms
    r'\bthe Lord\'s\b' → 'the Lᴏʀᴅ's',
]
```

**Output Examples:**
- **Old Testament**: "The Lᴏʀᴅ said to Moses" (Exodus)
- **New Testament**: "The Lord Jesus Christ" (1 Thessalonians)
- **Plain Text**: Unicode small caps (ᴏʀᴅ)
- **HTML**: `<span class="small-caps">ORD</span>`

#### Text Processing Pipeline

```python
def apply_proper_typography(text: str) -> str:
    """Apply comprehensive typography enhancements"""
    # 1. Handle escaped quotes
    text = text.replace('\\"', '"').replace("\\'", "'")
    
    # 2. Convert straight quotes to typographic quotes
    text = convert_quotes(text)
    
    # 3. Handle apostrophes in contractions
    text = fix_apostrophes(text)
    
    # 4. Convert punctuation (em dashes, ellipses)
    text = enhance_punctuation(text)
    
    # 5. Apply YHWH typography
    text = apply_yhwh_typography(text)
    
    return text
```

## Implementation Notes

### Performance Considerations

1. **Lazy Loading**: Compute expensive properties only when accessed
2. **Caching**: Cache computed metadata to avoid recalculation
3. **Efficient Serialization**: Use Pydantic's optimized JSON handling
4. **Memory Management**: Avoid storing redundant data
5. **Typography Processing**: Apply enhancements during text extraction, not on every display

### Migration Strategy

1. **Phase 1**: Implement models alongside existing system
2. **Phase 2**: Update M'Cheyne fetcher to use new models
3. **Phase 3**: Migrate cache format with backward compatibility
4. **Phase 4**: Remove legacy string-based storage

### Future Extensibility

1. **Cross-References**: Add optional cross_references field to BibleVerse
2. **Commentary**: Add commentary field to BiblePassage
3. **Audio**: Add audio_url field for verse audio
4. **Translations**: Support multiple versions in single passage
5. **Analytics**: Add highlight analytics and trending features