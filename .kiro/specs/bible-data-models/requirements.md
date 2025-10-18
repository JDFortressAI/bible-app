# Bible Data Models - Requirements Document

## Introduction

This specification defines a structured data modeling system for Bible passages using Pydantic BaseModel classes. The system will provide a flexible two-level organization of Bible content (BiblePassage → BibleVerse) with rich metadata and support for user highlighting/annotation features. This design accommodates complex M'Cheyne reading patterns like verse ranges across chapters (Luke 1:1-38, Zechariah 12:1-13:1, etc.).

## Requirements

### Requirement 1: Core Bible Data Structure

**User Story:** As a developer, I want a flexible two-level data structure for Bible content, so that I can handle complex passage ranges while maintaining simplicity and validation.

#### Acceptance Criteria

1. WHEN creating Bible data models THEN the system SHALL implement a two-tier hierarchy: BiblePassage → BibleVerse
2. WHEN defining models THEN each model SHALL use Pydantic BaseModel for validation and serialization
3. WHEN structuring data THEN BibleVerse SHALL contain the actual Bible text content and metadata (book, chapter, verse number)
4. WHEN organizing content THEN BiblePassage SHALL contain a list of BibleVerse objects
5. WHEN handling complex ranges THEN the system SHALL support verses from multiple chapters within a single passage

### Requirement 2: Minimal Metadata Management

**User Story:** As a developer, I want essential metadata without distracting statistics, so that the focus remains on the Bible text itself.

#### Acceptance Criteria

1. WHEN creating BibleVerse THEN it SHALL contain only essential metadata: book name, chapter number, verse number, and text content
2. WHEN creating BiblePassage THEN it SHALL contain only reference string, Bible version, and date fetched (no statistics)
3. WHEN handling multi-chapter passages THEN BiblePassage SHALL automatically determine the book and chapter range from its verses
4. WHEN displaying passages THEN statistics like word count, verse count, and character count SHALL NOT be shown to users
5. WHEN accessing metadata THEN only essential reference information SHALL be available

### Requirement 3: User Highlighting System

**User Story:** As a user, I want to highlight specific portions of Bible text with flexible granularity, so that I can mark important sections from single words to multi-verse spans and track popular highlights across all users.

#### Acceptance Criteria

1. WHEN creating highlights THEN the system SHALL support flexible positioning from single words to multi-verse spans
2. WHEN defining highlights THEN BibleHighlight SHALL specify start and end positions that can reference any verse and word within the passage
3. WHEN tracking highlights THEN each highlight SHALL include a counter of how many users highlighted that exact section
4. WHEN storing highlights THEN BiblePassage SHALL contain a list of BibleHighlight objects without user identification data
5. WHEN calculating popularity THEN the system SHALL aggregate highlight counts for overlapping or identical sections

### Requirement 4: Data Validation and Serialization

**User Story:** As a developer, I want robust data validation and serialization, so that Bible data is always consistent and can be easily stored/retrieved.

#### Acceptance Criteria

1. WHEN creating models THEN Pydantic SHALL validate all field types and constraints
2. WHEN serializing data THEN models SHALL convert to/from JSON format seamlessly
3. WHEN validating content THEN verse numbers SHALL be positive integers
4. WHEN validating highlights THEN word indices SHALL be within valid ranges for the verse
5. WHEN handling errors THEN validation failures SHALL provide clear error messages

### Requirement 5: Integration with Existing System

**User Story:** As a developer, I want the new data models to integrate with the existing M'Cheyne reading system, so that complex passage ranges are properly structured and cached.

#### Acceptance Criteria

1. WHEN fetching Bible passages THEN the system SHALL parse raw text into structured BibleVerse objects with proper book/chapter/verse metadata
2. WHEN handling complex ranges THEN the system SHALL support passages like "Luke 1:1-38", "Zechariah 12:1-13:1", and "Psalm 119:1-24"
3. WHEN caching readings THEN the system SHALL serialize structured models to JSON
4. WHEN loading cached data THEN the system SHALL deserialize JSON back to model objects
5. WHEN migrating existing code THEN the change SHALL be backward compatible with current functionality

### Requirement 6: Focused Reading Experience

**User Story:** As a user, I want a distraction-free Bible reading interface with large, readable text and intelligent scroll memory, so that I can focus entirely on the Scripture and maintain my reading position across passages.

#### Acceptance Criteria

1. WHEN displaying Bible passages THEN the text SHALL use large font sizes optimized for reading (maximum 20 words per line on desktop, 8 words per line on mobile)
2. WHEN showing Bible text THEN verse numbers SHALL always be displayed without user configuration options
3. WHEN rendering passages THEN compact view SHALL always be used without user toggle options
4. WHEN displaying content THEN all verses SHALL always be shown without pagination or "show more" controls
5. WHEN presenting the interface THEN statistics, word counts, and metadata SHALL be hidden to eliminate distractions
6. WHEN switching between passages THEN each passage SHALL maintain its own independent scroll position
7. WHEN returning to a previously viewed passage THEN the system SHALL restore the exact scroll position where the user left off
8. WHEN viewing a passage for the first time THEN the system SHALL start at the top of the passage

### Requirement 7: Typography and Text Enhancement

**User Story:** As a user, I want Bible text to display with proper typography and formatting conventions, so that the text is readable, professional, and follows established biblical typography standards.

#### Acceptance Criteria

1. WHEN processing Bible text THEN the system SHALL convert straight quotes to proper typographic quotes (", ", ', ')
2. WHEN processing contractions THEN the system SHALL use proper apostrophes (') instead of straight quotes
3. WHEN processing punctuation THEN the system SHALL convert double hyphens to em dashes (—) and multiple periods to ellipses (…)
4. WHEN encountering the divine name YHWH in Old Testament passages THEN the system SHALL render "Lord" in small caps to distinguish from Adonai
5. WHEN processing New Testament passages THEN "Lord" SHALL remain in normal case as it typically refers to Jesus Christ
6. WHEN displaying YHWH references THEN the system SHALL handle compound forms like "Lord God", "Lord of hosts", and possessives correctly in Old Testament only

### Requirement 8: Large Text Display and Responsive Typography

**User Story:** As a user, I want Bible text displayed in very large, readable fonts that adapt to my device and theme, so that I can read comfortably without straining my eyes in any lighting condition.

#### Acceptance Criteria

1. WHEN displaying on desktop THEN the font size SHALL be large enough to limit lines to maximum 20 words per line
2. WHEN displaying on mobile devices THEN the font size SHALL be large enough to limit lines to maximum 8 words per line
3. WHEN rendering text THEN the system SHALL use responsive CSS that automatically adjusts font size based on screen width
4. WHEN showing verses THEN line height and spacing SHALL be optimized for comfortable reading of large text
5. WHEN displaying passages THEN the text SHALL be the primary visual element with minimal interface chrome
6. WHEN using dark mode THEN text colors SHALL be light enough for comfortable reading (#e8e8e8 for main text, #b8b8b8 for verse numbers)
7. WHEN switching between light and dark modes THEN text SHALL remain highly legible with appropriate contrast ratios

### Requirement 9: Extensibility for Future Features

**User Story:** As a developer, I want the data models to be extensible, so that future features like cross-references, commentary, and advanced analytics can be easily added.

#### Acceptance Criteria

1. WHEN designing models THEN the structure SHALL allow for additional metadata fields
2. WHEN extending functionality THEN new highlight types SHALL be easily supported
3. WHEN adding features THEN the core model structure SHALL remain stable
4. WHEN implementing analytics THEN the models SHALL support aggregation queries
5. WHEN integrating external data THEN the models SHALL accommodate cross-references and commentary links