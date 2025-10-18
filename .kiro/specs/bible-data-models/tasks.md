# Implementation Plan

- [x] 1. Set up Pydantic models and core data structures
  - Create bible_models.py file with Pydantic BaseModel imports
  - Implement HighlightPosition model with verse_index and word_index fields
  - Add position comparison methods for sorting and validation
  - _Requirements: 1.1, 1.2, 1.4_

- [x] 2. Implement BibleVerse model with metadata
  - Create BibleVerse class with book, chapter, verse, and text fields
  - Add Pydantic field validation for positive integers and non-empty text
  - Implement computed properties for word_count, char_count, and reference
  - Add get_words() method to split verse text into word list
  - Write unit tests for BibleVerse creation and validation
  - _Requirements: 1.3, 2.1, 4.1, 4.3_

- [x] 3. Implement BibleHighlight model with flexible positioning
  - Create BibleHighlight class with start_position, end_position, and highlight_count
  - Add Pydantic validator to ensure end_position is after start_position
  - Implement spans_multiple_verses() method to check verse span
  - Add get_highlighted_text() method to extract text from passage
  - Write unit tests for highlight validation and text extraction
  - _Requirements: 3.1, 3.2, 3.4, 4.1, 4.4_

- [x] 4. Implement BiblePassage model with aggregation features
  - Create BiblePassage class with reference, version, verses, and highlights fields
  - Add computed properties for total_verses, total_words, total_characters
  - Implement books and chapter_range properties for multi-book passages
  - Add methods for highlight management and popularity tracking
  - Write unit tests for passage creation and metadata calculation
  - _Requirements: 1.1, 1.5, 2.2, 2.3, 2.4, 3.3, 3.5_

- [x] 5. Create Bible text parser for M'Cheyne integration
  - Implement parse_bible_text() function to convert raw text to BibleVerse objects
  - Add logic to extract book, chapter, verse numbers from formatted text
  - Handle complex verse ranges like "Luke 1:1-38" and "Zechariah 12:1-13:1"
  - Create verse text cleaning and normalization functions
  - Write unit tests for various M'Cheyne passage formats
  - _Requirements: 5.1, 5.2, 1.5_

- [x] 6. Update M'Cheyne fetcher to use structured models
  - Modify fetch_passage_text() to return BiblePassage objects instead of strings
  - Update passage parsing logic to create proper BibleVerse objects
  - Integrate new models with existing biblestudytools.com scraping
  - Ensure backward compatibility with current display methods
  - Write integration tests for fetcher with new models
  - _Requirements: 5.1, 5.4, 5.5_

- [x] 7. Implement JSON serialization and caching
  - Add Pydantic JSON serialization methods to all models
  - Update cache save/load methods to handle structured models
  - Implement cache migration for existing JSON files
  - Add validation for deserialized cache data
  - Write tests for serialization round-trip accuracy
  - _Requirements: 4.2, 5.3, 5.5_

- [x] 8. Create highlight management system
  - Implement add_highlight() method on BiblePassage
  - Add highlight merging logic for overlapping sections
  - Create highlight popularity aggregation functions
  - Implement highlight search and filtering methods
  - Write unit tests for highlight operations and edge cases
  - _Requirements: 3.3, 3.5, 6.3_

- [x] 9. Add performance optimizations and caching
  - Implement lazy loading for expensive computed properties
  - Add caching decorators for metadata calculations
  - Optimize JSON serialization for large passages
  - Add memory usage monitoring for typical Bible passages
  - Write performance tests to ensure sub-100ms operations
  - _Requirements: 6.1, 6.2, 6.4, 6.5_

- [x] 10. Update display and rendering methods
  - Modify display_readings() to work with BiblePassage objects
  - Add formatted output methods for verses and highlights
  - Implement highlight visualization in text output
  - Update CLI interface to show structured metadata
  - Write tests for display formatting and output
  - _Requirements: 5.4, 2.5_

- [ ] 11. Implement typography and text enhancement system
  - Add proper typographic quote conversion (straight to curly quotes)
  - Implement smart apostrophe handling for contractions
  - Add em dash and ellipsis conversion
  - Implement YHWH divine name typography with small caps
  - Create comprehensive typography test suite
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11.1 Implement basic typography enhancements
  - Convert straight quotes to proper typographic quotes
  - Handle apostrophes in contractions (don't, it's, etc.)
  - Convert double hyphens to em dashes
  - Convert multiple periods to ellipses
  - Write unit tests for basic typography
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 11.2 Implement YHWH divine name typography
  - Create pattern recognition for YHWH references
  - Handle primary cases: "the Lord", "O Lord"
  - Handle compound forms: "Lord God", "Lord of hosts"
  - Handle possessive forms: "Lord's"
  - Support both Unicode small caps and HTML markup
  - Write comprehensive tests for YHWH typography
  - _Requirements: 7.4, 7.5_

- [x] 11.3 Integrate typography into text processing pipeline
  - Update bible_parser.py to apply typography during text cleaning
  - Update mccheyne.py to apply typography during HTML extraction
  - Ensure typography is applied consistently across all text sources
  - Add performance optimizations for typography processing
  - Update existing tests to account for typography changes
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 11. Create comprehensive test suite
  - Write unit tests for all model validation scenarios
  - Add integration tests for M'Cheyne complex passages
  - Create performance benchmarks for large passages
  - Add edge case tests for highlight boundary conditions
  - Implement test fixtures for various passage types
  - _Requirements: 4.1, 4.5, 6.5_

- [x] 12. Implement focused reading interface with large typography
  - Remove distracting statistics and UI controls from Bible display
  - Implement large, responsive font sizing (max 20 words/line desktop, 8 words/line mobile)
  - Fix display options to always show verse numbers, compact view, and all verses
  - Add CSS for large, readable typography with proper line spacing
  - Remove word counts, verse counts, and other metadata from UI
  - Simplify sidebar to focus only on passage selection
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 13. Enhance dark mode support and UI layout
  - Implement proper dark mode text colors for improved legibility (#e8e8e8 main text, #b8b8b8 verse numbers)
  - Add CSS media queries for automatic dark mode detection
  - Move mode selector from top of page to bottom of sidebar for better content focus
  - Ensure high contrast ratios for both light and dark themes
  - Test typography readability across different devices and themes
  - _Requirements: 8.6, 8.7_

- [x] 14. Implement individual passage scroll position memory using native Streamlit tabs
  - Replace complex JavaScript solution with Streamlit's native st.tabs() component
  - Create separate tab for each Bible passage with independent scroll context
  - Ensure each tab automatically maintains its own scroll position
  - Implement clean tab-based navigation for the four daily passages
  - Remove sidebar passage selection buttons in favor of intuitive tab interface
  - Ensure first-time passage visits start at the top, return visits restore position
  - Test scroll memory persistence across tab switches
  - _Requirements: 6.6, 6.7, 6.8_

- [ ] 13. Add error handling and validation
  - Implement BibleValidationError exception class
  - Add comprehensive error messages for validation failures
  - Create error recovery mechanisms for malformed data
  - Add logging for model creation and validation events
  - Write tests for error conditions and recovery
  - _Requirements: 4.5, 4.1_