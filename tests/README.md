# Tests Directory

This directory contains comprehensive tests for the Bible data models and M'Cheyne integration system.

## Test Files

### Core Model Tests
- **`test_bible_verse.py`** - Comprehensive tests for all Bible data models (78 tests)
  - BibleVerse creation, validation, and methods
  - BibleHighlight functionality and text extraction
  - BiblePassage metadata, highlight management, and coverage analysis
  - HighlightPosition comparison and validation

- **`test_bible_verse_simple.py`** - Simple functionality test for basic model operations

### Serialization and Caching Tests
- **`test_bible_serialization.py`** - JSON serialization and caching functionality (13 tests)
  - Round-trip serialization accuracy for all models
  - File save/load operations
  - Cache validation and error handling
  - Legacy cache migration
  - Performance testing with large datasets

### Integration Tests
- **`test_mcheyne_integration.py`** - M'Cheyne fetcher integration tests (13 tests)
  - Structured vs legacy format compatibility
  - Cache functionality and migration
  - Error handling and fallback mechanisms
  - Network error simulation

- **`test_integration_example.py`** - Integration example demonstrating real usage
  - Live API testing (when network available)
  - Cache functionality demonstration
  - Error handling examples

### Parser Tests
- **`test_bible_parser.py`** - Bible text parsing functionality (37 tests)
  - Bible reference parsing and validation
  - Book name normalization
  - Verse text cleaning and extraction
  - Complex M'Cheyne format handling

### Example Scripts
- **`bible_parser_integration_example.py`** - Demonstrates parser integration with real data

## Running Tests

### Run All Tests
```bash
uv run python -m pytest tests/ -v
```

### Run Specific Test File
```bash
uv run python -m pytest tests/test_bible_serialization.py -v
```

### Run Specific Test Class
```bash
uv run python -m pytest tests/test_bible_serialization.py::TestBibleModelsSerialization -v
```

### Run Integration Examples
```bash
uv run python tests/test_integration_example.py
uv run python tests/bible_parser_integration_example.py
```

## Test Coverage

- **147 total tests** across all test files
- **100% pass rate** with comprehensive validation
- **Performance benchmarks** included for serialization operations
- **Error handling** tested for all major failure scenarios
- **Integration testing** with real API endpoints (when available)

## Test Categories

### Unit Tests
- Model validation and business logic
- Serialization round-trip accuracy
- Parser functionality
- Cache operations

### Integration Tests
- API integration with biblestudytools.com
- Cache migration scenarios
- End-to-end workflow testing

### Performance Tests
- Large dataset serialization (50+ verses)
- Cache save/load performance
- Memory usage validation

### Error Handling Tests
- Invalid input validation
- Network failure simulation
- Malformed cache handling
- Graceful degradation testing

## Dependencies

Tests use the following frameworks:
- **pytest** - Main testing framework
- **unittest** - Python standard library testing
- **unittest.mock** - Mocking for network calls and file operations

All tests are designed to run independently and clean up after themselves (cache files, temporary files, etc.).