import streamlit as st
from openai import OpenAI
import os
import json
import glob
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Optional
from bible_models import BiblePassage, BibleVerse
from s3_bible_cache import S3BibleCache

# Load environment variables
load_dotenv()

class McCheyneReader:
    """M'Cheyne reading system integration for Streamlit with S3 support"""
    
    def __init__(self):
        # Use S3-enabled cache that falls back to local files
        self.cache = S3BibleCache()
    
    def get_todays_readings(self) -> Optional[Dict]:
        """Load today's M'Cheyne readings from cache (S3 or local)"""
        try:
            return self.cache.get_todays_readings()
        except Exception as e:
            st.error(f"Error loading M'Cheyne readings: {e}")
            return None
    
    def get_passage_titles(self, readings: Dict) -> List[str]:
        """Generate intelligent titles for the four passages"""
        return self.cache.get_passage_titles(readings)
    
    def get_all_passages(self, readings: Dict) -> List[BiblePassage]:
        """Get all four passages in order"""
        return self.cache.get_all_passages(readings)

class BibleChat:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = """You are a Bible-focused assistant specializing in the New King James Version (NKJV). 

Your role:
1. Answer questions using NKJV Bible text and references
2. Always include explicit Bible references (book, chapter, verse) in your responses
3. Provide spiritual insight and practical application
4. Quote relevant verses directly from the NKJV when appropriate
5. Keep responses biblical, accurate, and helpful

Guidelines:
- Use only NKJV text when quoting Scripture
- Convert all neutral quotes ("") into Proper Quotes ("") always.
- Convert all neutral apostrophe (') into Proper apostrophe ('). 
- Include multiple relevant verses when helpful
- Provide context and explanation for the verses
- Offer practical application of biblical principles
- If unsure about a reference, acknowledge it rather than guess"""
    
    def generate_response(self, user_query):
        """Generate AI response with Bible references"""
        if not self.client.api_key:
            yield "Please set your OPENAI_API_KEY in the .env file to use this chat."
            return
        
        try:
            stream = self.client.responses.create(
                model="gpt-5-nano",
                input=[
                    {"role": "developer", "content": self.system_prompt},
                    {"role": "user", "content": user_query}
                ],
                text={"verbosity": "low"}, # Set the response verbosity (low, medium, or high)
                reasoning={"effort": "low"}, # Set the reasoning effort (minimal, low, medium, or high)
                stream=True,
            )
            for event in stream:
                # Yield only the text delta events; ignore others like created/done
                if event.type == "response.output_text.delta":
                    yield event.delta
        except Exception as e:
            yield f"Error generating response: {str(e)}"

def group_verses_by_chapter(verses: List[BibleVerse]) -> Dict[int, List[BibleVerse]]:
    """Group verses by chapter number"""
    chapters = {}
    for verse in verses:
        if verse.chapter not in chapters:
            chapters[verse.chapter] = []
        chapters[verse.chapter].append(verse)
    return chapters

def display_bible_passage(passage: BiblePassage, passage_index: int):
    """Display a Bible passage with large, focused typography, handling multi-chapter passages"""
    
    # Add CSS for large, readable text using Streamlit's native color variables
    st.markdown("""
    <style>
    .bible-text {
        font-size: clamp(24px, 4vw, 32px) !important;
        line-height: 1.6 !important;
        font-family: 'Georgia', 'Times New Roman', serif !important;
        margin: 1.5rem 0 !important;
        max-width: 100% !important;
        word-wrap: break-word !important;
        /* Use Streamlit's native text color variable */
        color: var(--text-color) !important;
    }
    
    .verse-number {
        font-size: 0.75em !important;
        opacity: 0.7 !important;
        margin-right: 0.5em !important;
        font-weight: bold !important;
        /* Use Streamlit's secondary text color */
        color: var(--text-color-light-1) !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 767px) {
        .bible-text {
            font-size: clamp(20px, 6vw, 28px) !important;
            line-height: 1.5 !important;
        }
    }
    
    .small-caps {
        font-variant: small-caps;
        font-weight: bold;
    }
    
    /* Hide Streamlit's default markdown styling for bible text */
    .bible-text p {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .chapter-separator {
        margin: 2rem 0 1rem 0 !important;
        border-top: 2px solid var(--text-color-light-3) !important;
        padding-top: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Group verses by chapter
    chapters = group_verses_by_chapter(passage.verses)
    chapter_numbers = sorted(chapters.keys())
    
    # Display each chapter separately
    for i, chapter_num in enumerate(chapter_numbers):
        chapter_verses = chapters[chapter_num]
        
        # Get the book name from the first verse
        book_name = chapter_verses[0].book if chapter_verses else "Unknown"
        
        # Display chapter header
        if i == 0:
            # First chapter - use main header
            st.markdown(f"## {book_name} {chapter_num}")
        else:
            # Subsequent chapters - use separator and subheader
            st.markdown('<div class="chapter-separator"></div>', unsafe_allow_html=True)
            st.markdown(f"## {book_name} {chapter_num}")
        
        # Display all verses in this chapter
        for verse in chapter_verses:
            # Use HTML for better typography control
            verse_html = f"""
            <div class="bible-text">
                <span class="verse-number">{verse.verse}.</span>{verse.text}
            </div>
            """
            st.markdown(verse_html, unsafe_allow_html=True)
    
    # Highlights section (if any exist) - minimal display
    if passage.highlights:
        st.markdown("---")
        st.markdown("### ✨ Popular Highlights")
        
        popular_highlights = passage.get_popular_highlights()[:3]  # Show top 3 only
        for i, highlight in enumerate(popular_highlights, 1):
            try:
                highlighted_text = highlight.get_highlighted_text(passage)
                
                with st.expander(f"Highlight {i} ({highlight.highlight_count} users)"):
                    st.markdown(f'<div class="bible-text">"{highlighted_text}"</div>', unsafe_allow_html=True)
                            
            except Exception as e:
                st.error(f"Error displaying highlight {i}: {e}")

def display_reading_mode():
    """Display the M'Cheyne reading interface with focused, distraction-free design"""
    # Initialize M'Cheyne reader
    if 'mccheyne_reader' not in st.session_state:
        st.session_state.mccheyne_reader = McCheyneReader()
    
    # Load today's readings
    if 'todays_readings' not in st.session_state:
        st.session_state.todays_readings = st.session_state.mccheyne_reader.get_todays_readings()
    
    readings = st.session_state.todays_readings
    
    if not readings:
        st.error("📭 No M'Cheyne readings found. Please run the M'Cheyne reader first to generate today's readings.")
        st.markdown("Run this command to fetch today's readings:")
        st.code("python -m src.mccheyne --structured")
        return
    
    
    # Get passage titles and all passages
    titles = st.session_state.mccheyne_reader.get_passage_titles(readings)
    all_passages = st.session_state.mccheyne_reader.get_all_passages(readings)
    
    if not titles or not all_passages:
        st.error("No passages found in today's readings.")
        return
    
    # Sidebar for passage selection and controls
    with st.sidebar:
        st.header("📖 Today’s Passages")
        st.markdown("*Select a passage to read:*")
        
        # Initialize selected passage
        if 'selected_passage_index' not in st.session_state:
            st.session_state.selected_passage_index = 0
        
        # Passage selection buttons
        for i, title in enumerate(titles):
            # Highlight current passage button
            button_type = "primary" if i == st.session_state.selected_passage_index else "secondary"
            if st.button(title, key=f"passage_{i}", use_container_width=True, type=button_type):
                st.session_state.selected_passage_index = i
                st.rerun()
        
        st.markdown("---")
        
        if st.button("🔄 Refresh Readings", use_container_width=True):
            st.session_state.todays_readings = None
            st.rerun()
        
        # Mode selector at bottom of sidebar
        st.markdown("---")
        st.markdown("**Choose Mode:**")
        mode = st.radio(
            "",
            ["📖 Reading", "💬 Chat"],
            index=0,  # Default to Reading mode
            key="mode_selector_reading"
        )
        
        # Switch to chat mode if selected
        if mode == "💬 Chat":
            st.rerun()
    
    # Display the selected passage with scroll position memory
    if all_passages and 0 <= st.session_state.selected_passage_index < len(all_passages):
        selected_passage = all_passages[st.session_state.selected_passage_index]
        
        # Use a unique container key for each passage to maintain scroll positions
        container_key = f"passage_container_{st.session_state.selected_passage_index}_{selected_passage.reference}"
        
        # Create a container with a unique key for this passage
        with st.container():
            # Add a unique identifier for scroll position tracking
            st.markdown(f'<div id="passage-{st.session_state.selected_passage_index}"></div>', unsafe_allow_html=True)
            
            # Add JavaScript to always scroll to top when switching passages
            st.markdown(f"""
            <script>
            (function() {{
                const passageIndex = {st.session_state.selected_passage_index};
                
                // Always scroll to top when switching passages
                // Use multiple methods to ensure it works reliably
                setTimeout(() => {{
                    window.scrollTo({{ top: 0, behavior: 'auto' }});
                    document.documentElement.scrollTop = 0;
                    document.body.scrollTop = 0;
                }}, 50);
                
                // Additional scroll to top after content loads
                setTimeout(() => {{
                    window.scrollTo({{ top: 0, behavior: 'smooth' }});
                }}, 200);
                
                // Store current passage index for future reference
                window.currentPassageIndex = passageIndex;
            }})();
            </script>
            """, unsafe_allow_html=True)
            
            # Display the passage content
            display_bible_passage(selected_passage, st.session_state.selected_passage_index)
            
            # Add NKJV copyright footnote at the bottom
            st.markdown("---")
            st.markdown(
                '<p style="font-size: 12px; color: #888; text-align: center; margin-top: 2rem;">'
                'Scripture taken from the New King James Version®. Copyright © 1982 by Thomas Nelson. All rights reserved.'
                '</p>', 
                unsafe_allow_html=True
            )
    else:
        st.error("Invalid passage selection or no passages available.")

def display_chat_mode():
    """Display the Bible chat interface"""
    # Initialize the chat system
    if 'bible_chat' not in st.session_state:
        st.session_state.bible_chat = BibleChat()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Initialize selected question state
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = None
    
    # Sidebar with suggestions
    with st.sidebar:
        st.header("💡 Question Suggestions")
        st.markdown("*Click any question to use it:*")
        
        # Define question categories and questions
        questions = {
            "Spiritual Growth": [
                "How can I grow closer to God?",
                "What does the Bible say about prayer?",
                "How should I handle difficult times?",
                "What is God's will for my life?"
            ],
            "Life Guidance": [
                "How should I treat others?",
                "What does the Bible say about love?",
                "How can I find peace in anxiety?",
                "What does Scripture say about work?"
            ],
            "Faith Questions": [
                "How can I be saved?",
                "What is the Gospel?",
                "How do I know God loves me?",
                "What happens after death?"
            ],
            "Character Development": [
                "How can I be more patient?",
                "What does the Bible say about forgiveness?",
                "How should I handle anger?",
                "What does Scripture teach about humility?"
            ],
            "Biblical Topics": [
                "What does the Bible say about money?",
                "How should Christians view suffering?",
                "What is biblical wisdom?",
                "How can I overcome temptation?"
            ]
        }
        
        # Display clickable questions by category
        for category, question_list in questions.items():
            st.markdown(f"**{category}:**")
            for question in question_list:
                if st.button(question, key=f"btn_{question}", use_container_width=True):
                    st.session_state.selected_question = question
                    st.rerun()
            st.markdown("")
        
        st.markdown("---")
        st.markdown("**Note:** All responses include explicit NKJV Scripture references.")
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Mode selector at bottom of sidebar
        st.markdown("---")
        st.markdown("**Choose Mode:**")
        mode = st.radio(
            "",
            ["📖 Reading", "💬 Chat"],
            index=1,  # Default to Chat mode when in chat
            key="mode_selector_chat"
        )
        
        # Switch to reading mode if selected
        if mode == "📖 Reading":
            st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle selected question from sidebar
    if st.session_state.selected_question:
        prompt = st.session_state.selected_question
        st.session_state.selected_question = None  # Clear the selection
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response  
        with st.chat_message("assistant"):
            response = st.write_stream(st.session_state.bible_chat.generate_response(prompt))
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Chat input
    if prompt := st.chat_input("Ask a Bible-related question..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching Scripture..."):
                full_response = st.write_stream(st.session_state.bible_chat.generate_response(prompt))
            # Append full response to history for persistence
            st.session_state.messages.append({"role": "assistant", "content": full_response})

def main():
    st.set_page_config(
        page_title="Bible Reading & Chat",
        page_icon="assets/favicon.jpeg",
        layout="wide"
    )
    
    # Dynamic date title
    today = datetime.now()
    day_name = today.strftime("%A")
    day_num = today.day
    month_name = today.strftime("%B")
    
    # Add ordinal suffix to day
    if 10 <= day_num % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")
    
    date_title = f"🗓️ Today is {day_name}, {day_num}<sup>{suffix}</sup> of {month_name}."
    st.markdown(f"# {date_title}", unsafe_allow_html=True)
    
    # Initialize mode in session state
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "📖 Reading"
    
    # Check for mode changes from sidebar
    if 'mode_selector_reading' in st.session_state:
        st.session_state.current_mode = st.session_state.mode_selector_reading
    elif 'mode_selector_chat' in st.session_state:
        st.session_state.current_mode = st.session_state.mode_selector_chat
    
    # Display appropriate interface based on mode
    if st.session_state.current_mode == "📖 Reading":
        url = "https://bibleplan.org/plans/mcheyne/"
        st.markdown("*Today’s [M’Cheyne Bible Reading Plan](%s)*" % url)
        display_reading_mode()
    else:  # Chat mode
        st.markdown("*Ask questions and receive answers grounded in Scripture (NKJV)*")
        display_chat_mode()

if __name__ == "__main__":
    main()