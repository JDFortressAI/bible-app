# Bible Chat

A simple Bible-focused chat application using OpenAI's LLM with built-in NKJV knowledge.

## Features

- **Bible-grounded responses**: All answers include explicit NKJV Bible references
- **Direct LLM approach**: Leverages OpenAI's built-in Bible knowledge
- **Question suggestions**: UI includes helpful prompts for different types of biblical inquiries
- **Chat history**: Maintains conversation context
- **NKJV focus**: Uses New King James Version text exclusively
- **Simple interface**: Built with Streamlit for ease of use

## Setup

1. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

2. **Set up OpenAI API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the application:**
   ```bash
   uv run streamlit run bible_chat.py
   ```

## Usage

1. Open the app in your browser (typically http://localhost:8501)
2. Check the sidebar for question suggestions across different categories
3. Type your Bible-related question in the chat input
4. Receive Scripture-grounded responses with explicit NKJV references
5. Continue the conversation - chat history is maintained

## Question Categories

The app handles various types of biblical inquiries:
- **Spiritual Growth**: Prayer, closeness to God, handling difficulties
- **Life Guidance**: Relationships, love, work, decision-making
- **Faith Questions**: Salvation, Gospel, God's love, afterlife
- **Character Development**: Patience, forgiveness, anger, humility
- **Biblical Topics**: Money, suffering, wisdom, temptation

## Technical Notes

- Uses OpenAI GPT-3.5-turbo with specialized Bible-focused system prompt
- No external Bible database required - leverages LLM's built-in knowledge
- Streamlit chat interface with persistent conversation history
- NKJV-specific prompting for accurate verse quotations

## Next Steps

To expand this application:
- Add conversation export/import
- Include verse lookup functionality
- Add multiple Bible versions support
- Implement topic-based conversation starters
- Add verse bookmarking and favorites