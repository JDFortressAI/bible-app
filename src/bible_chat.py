import streamlit as st
from streamlit.components.v1 import html
from openai import OpenAI
import os
import re
import json
import glob
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, List, Optional
from bible_models import BiblePassage, BibleVerse
from bible_format import clean_verse_text
from s3_bible_cache import S3BibleCache

# Load environment variables
load_dotenv()

class McCheyneReader:
    """M'Cheyne reading system integration for Streamlit with S3 support"""
    
    def __init__(self):
        # Use S3-enabled cache that falls back to local files
        self.cache = S3BibleCache()
    
    def get_readings_for_day(self, day_offset: int = 0) -> Optional[Dict]:
        """Load M'Cheyne readings for a specific day offset from today"""
        try:
            if day_offset == 0:
                return self.cache.get_todays_readings()
            elif day_offset == 1:
                return self.cache.get_tomorrows_readings()
            elif day_offset == -1:
                return self.cache.get_yesterdays_readings()
            else:
                # For other offsets, calculate the date
                target_date = datetime.now() + timedelta(days=day_offset)
                return self.cache.get_readings_for_date(target_date)
        except Exception as e:
            st.error(f"Error loading M'Cheyne readings: {e}")
            return None
    
    def get_todays_readings(self) -> Optional[Dict]:
        """Load today's M'Cheyne readings from cache (S3 or local)"""
        return self.get_readings_for_day(0)
    
    def get_yesterdays_readings(self) -> Optional[Dict]:
        """Load yesterday's M'Cheyne readings from cache (S3 or local)"""
        return self.get_readings_for_day(-1)
    
    def get_tomorrows_readings(self) -> Optional[Dict]:
        """Load tomorrow's M'Cheyne readings from cache (S3 or local)"""
        return self.get_readings_for_day(1)
    
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

def refresh_speak_html():
    """
    Build Play / Pause / Resume / Stop buttons.
    Text may contain {{pause N}} → real pauses.
    """
    # ------------------------------------------------------------------
    # 1. Escape back-ticks for JS template literals
    # ------------------------------------------------------------------
    raw = st.session_state.full_text.replace("`", "\\`")

    # ------------------------------------------------------------------
    # 2. Split into chunks + pause markers
    # ------------------------------------------------------------------
    import re
    parts = []
    pos = 0
    for m in re.finditer(r"{{pause\s+(\d+)}}", raw):
        if m.start() > pos:
            parts.append((raw[pos:m.start()].strip(), None))
        parts.append(("", int(m.group(1))))
        pos = m.end()
    if pos < len(raw):
        parts.append((raw[pos:].strip(), None))

    # ------------------------------------------------------------------
    # 3. Build JS array of chunks
    # ------------------------------------------------------------------
    js_chunks = []
    for text, pause in parts:
        if pause is not None:
            js_chunks.append(f"{{pauseSec: {pause}}}")
        elif text:
            js_chunks.append(f"{{text: `{text}`}}")
    chunks_array = "[" + ", ".join(js_chunks) + "]"

    # ------------------------------------------------------------------
    # 4. HTML + JS with Play / Pause / Resume / Stop
    # ------------------------------------------------------------------
    speak_html = f"""
<script>
  // ---------- Global state ----------
  let isPaused   = false;
  let isStopped  = false;          // <-- NEW: true after a Stop
  let resumeCb   = null;
  let currentUtt = null;
  let chunkIdx   = 0;
  let chunks     = null;

  // ---------- Start ----------
  function speakNow(allChunks) {{
    if (!('speechSynthesis' in window)) {{
      alert('Speech not supported');
      return;
    }}
    // Reset everything
    window.speechSynthesis.cancel();
    isPaused = false; isStopped = false; resumeCb = null;
    document.getElementById('pauseBtn').textContent = 'Pause';
    chunks = allChunks;
    chunkIdx = 0;
    nextChunk();
  }}

  // ---------- Process next chunk ----------
  function nextChunk() {{
    if (isStopped || chunkIdx >= chunks.length) return;
    if (isPaused) return;               // wait for resume

    const chunk = chunks[chunkIdx++];
    if ('pauseSec' in chunk) {{
      // ---- pause -------------------------------------------------
      const start = Date.now();
      const timer = setInterval(() => {{
        if (Date.now() - start >= chunk.pauseSec * 1000) {{
          clearInterval(timer);
          nextChunk();
        }}
      }}, 50);
      // keep the API alive
      const silent = new SpeechSynthesisUtterance('');
      silent.onend = () => {{}};
      window.speechSynthesis.speak(silent);
    }} else {{
      // ---- speak ------------------------------------------------
      const u = new SpeechSynthesisUtterance(chunk.text);
      u.lang = 'en-UK';
      currentUtt = u;
      u.onend = () => {{ currentUtt = null; nextChunk(); }};
      u.onerror = (e) => {{ console.error(e); nextChunk(); }};
      window.speechSynthesis.speak(u);
    }}
  }}

  // ---------- Pause / Resume ----------
  function togglePause() {{
    const btn = document.getElementById('pauseBtn');
    if (isStopped) return;

    if (isPaused) {{
      // RESUME
      isPaused = false;
      btn.textContent = 'Pause';
      window.speechSynthesis.resume();
      nextChunk();                     // continue from where we left off
    }} else {{
      // PAUSE
      isPaused = true;
      btn.textContent = 'Resume';
      window.speechSynthesis.pause();
    }}
  }}

  // ---------- Stop ----------
  function stopSpeech() {{
    window.speechSynthesis.cancel();
    isStopped = true;
    isPaused = false;
    resumeCb = null;
    const btn = document.getElementById('pauseBtn');
    if (btn) btn.textContent = 'Pause';
  }}
</script>

<button onclick="speakNow({chunks_array})"
    style="padding:12px 20px; font-size:16px; background:#0066cc; color:white;
           border:none; border-radius:8px; cursor:pointer; font-weight:bold; margin-right:8px;">
  Play
</button>

<button id="pauseBtn" onclick="togglePause()"
    style="padding:12px 20px; font-size:16px; background:#ff9800; color:white;
           border:none; border-radius:8px; cursor:pointer; font-weight:bold; margin-right:8px;">
  Pause
</button>

<button onclick="stopSpeech()"
    style="padding:12px 20px; font-size:16px; background:#cc6600; color:white;
           border:none; border-radius:8px; cursor:pointer; font-weight:bold;">
  Stop
</button>
"""
    st.session_state.speak_html = speak_html


def display_bible_passage(passage: BiblePassage, passage_index: int):
    """Display a Bible passage with large, focused typography, handling multi-chapter passages"""
    
    # Add CSS for large, readable text using Streamlit's native color variables
    st.markdown("""
    <style>
    .bible-text {
        font-size: clamp(24px, 4vw, 32px) !important;
        line-height: 1.6 !important;
        font-family: 'Georgia', 'Times New Roman', serif !important;
        margin: 0.5rem 0 !important;
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
    
    audio_text = ""
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
        
        if "psalm" in book_name.lower():
            say_chapter = ""
        else:
            say_chapter = "chapter "
        audio_text += f"{book_name} {say_chapter} {chapter_num}\n"
        audio_text += "{{pause 3}}"

        # Display all verses in this chapter
        for verse in chapter_verses:
            # Use HTML for better typography control
            if verse.text[-1] == ",":
                verse_pause = ""
            else: 
                verse_pause = "{{pause 1}}"
            audio_text_to_add = clean_verse_text(verse.text, verse.verse, chapter_num, book_name, st.session_state.selected_day, True) 
            if audio_text_to_add:
                audio_text += audio_text_to_add + verse_pause
            verse_html = clean_verse_text(verse.text, verse.verse, chapter_num, book_name, st.session_state.selected_day)
            if not (verse_html == "<span></span>"):
                st.html(verse_html)
    
    st.session_state.full_text = audio_text.replace("Lᴏʀᴅ", "Lord")
    refresh_speak_html()

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
    
    # Initialize selected day (0 = today, -1 = yesterday, 1 = tomorrow)
    if 'selected_day' not in st.session_state:
        st.session_state.selected_day = 0
    
    # Load readings for the selected day
    readings = st.session_state.mccheyne_reader.get_readings_for_day(st.session_state.selected_day)
    
    if not readings:
        day_name = ["Yesterday's", "Today's", "Tomorrow's"][st.session_state.selected_day + 1]
        st.error(f"📭 No M'Cheyne readings found for {day_name.lower()} date. Please run the M'Cheyne reader first to generate readings.")
        st.markdown("Run this command to fetch readings:")
        st.code("python -m src.mccheyne --structured")
        return
    
    # Get passage titles and all passages
    titles = st.session_state.mccheyne_reader.get_passage_titles(readings)
    all_passages = st.session_state.mccheyne_reader.get_all_passages(readings)
    
    if not titles or not all_passages:
        st.error("No passages found in the selected day's readings.")
        return
    
    # Sidebar for passage selection and controls
    with st.sidebar:
        # Dynamic sidebar header based on selected day
        day_headers = ["📖 Yesterday’s Passages", "📖 Today’s Passages", "📖 Tomorrow’s Passages"]
        st.header(day_headers[st.session_state.selected_day + 1])
        st.markdown("*Select a passage to read:*")
        
        # Initialize selected passage (morning, evening different!)
        if 'selected_passage_index' not in st.session_state:
            if datetime.now().hour > 15:
                st.session_state.selected_passage_index = 2
            else:
                st.session_state.selected_passage_index = 0
        
        # Ensure selected passage index is valid for current readings
        if st.session_state.selected_passage_index >= len(titles):
            st.session_state.selected_passage_index = 0
        
        # Passage selection buttons
        for i, title in enumerate(titles):
            # Highlight current passage button
            button_type = "primary" if i == st.session_state.selected_passage_index else "secondary"
            if st.button(title, key=f"passage_{i}_{st.session_state.selected_day}", use_container_width=True, type=button_type):
                st.session_state.selected_passage_index = i
                st.rerun()
        
        st.markdown("---")
        st.markdown("**Navigate to:**")
        
        # Day navigation buttons in sidebar
        if st.button("← Yesterday", key="sidebar_yesterday", use_container_width=True, type="primary" if st.session_state.selected_day == -1 else "secondary"):
            st.session_state.selected_day = -1
            # Keep current passage selection when switching days
            st.rerun()
        
        if st.button("Today", key="sidebar_today", use_container_width=True, type="primary" if st.session_state.selected_day == 0 else "secondary"):
            st.session_state.selected_day = 0
            # Keep current passage selection when switching days
            st.rerun()
        
        if st.button("Tomorrow →", key="sidebar_tomorrow", use_container_width=True, type="primary" if st.session_state.selected_day == 1 else "secondary"):
            st.session_state.selected_day = 1
            # Keep current passage selection when switching days
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
    
    # Display the selected passage
    if all_passages and 0 <= st.session_state.selected_passage_index < len(all_passages):
        selected_passage = all_passages[st.session_state.selected_passage_index]
        
        # Create a container for this passage
        with st.container():
            

            
            # Display the passage content
            display_bible_passage(selected_passage, st.session_state.selected_passage_index)
            
            # Add NKJV copyright footnote at the bottom
            st.markdown(
                '<p style="font-size: 12px; color: #888; text-align: center; margin-top: 2rem;">'
                'Scripture taken from the New King James Version®. Copyright © 1982 by Thomas Nelson. All rights reserved.'
                '</p>', 
                unsafe_allow_html=True
            )
    else:
        st.error("Invalid passage selection or no passages available.")
    
    # Bottom navigation buttons (replicate the top navigation)
    st.markdown("---")

    st.markdown("### Select a Passage")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(titles[0], use_container_width=True, type="primary" if st.session_state.selected_passage_index == 0 else "secondary"):
            st.session_state.selected_passage_index = 0
            st.rerun()

    with col2:
        if st.button(titles[1], use_container_width=True, type="primary" if st.session_state.selected_passage_index == 1 else "secondary"):
            st.session_state.selected_passage_index = 1
            st.rerun()

    with col3:
        if st.button(titles[2], use_container_width=True, type="primary" if st.session_state.selected_passage_index == 2 else "secondary"):
            st.session_state.selected_passage_index = 2
            st.rerun()

    with col4:
        if st.button(titles[3], use_container_width=True, type="primary" if st.session_state.selected_passage_index == 3 else "secondary"):
            st.session_state.selected_passage_index = 3
            st.rerun()

    st.markdown("### Navigate to Another Day")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("← Yesterday", key="bottom_yesterday", use_container_width=True, type="primary" if st.session_state.selected_day == -1 else "secondary"):
            st.session_state.selected_day = -1
            # Keep current passage selection when switching days
            st.rerun()
    
    with col2:
        if st.button("Today", key="bottom_today", use_container_width=True, type="primary" if st.session_state.selected_day == 0 else "secondary"):
            st.session_state.selected_day = 0
            # Keep current passage selection when switching days
            st.rerun()
    
    with col3:
        if st.button("Tomorrow →", key="bottom_tomorrow", use_container_width=True, type="primary" if st.session_state.selected_day == 1 else "secondary"):
            st.session_state.selected_day = 1
            # Keep current passage selection when switching days
            st.rerun()

    st.markdown(
                '<p style="font-size: 12px; color: #888; text-align: center; margin-top: 2rem;">'
                'Crafted with love by JDFortress AI Ltd. Copyright © 2025. All rights reserved.'
                '</p>', 
                unsafe_allow_html=True
            )

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
    
    # Dynamic date title based on selected day
    # Initialize selected day if not set (needed for title calculation)
    if 'selected_day' not in st.session_state:
        st.session_state.selected_day = 0
    
    # Calculate the target date based on selected day
    target_date = datetime.now() + timedelta(days=st.session_state.selected_day)
    day_name = target_date.strftime("%A")
    day_num = target_date.day
    month_name = target_date.strftime("%B")
    year = target_date.year
    
    # Dynamic title based on selected day
    if st.session_state.selected_day == -1:
        date_title = f"🗓️ Yesterday was {day_name} {day_num} {month_name} 2025."
    elif st.session_state.selected_day == 0:
        date_title = f"🗓️ Today is {day_name} {day_num} {month_name} 2025."
    else:  # tomorrow
        date_title = f"🗓️ Tomorrow will be {day_name} {day_num} {month_name} 2025."
    
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
        # Initialize selected day if not set
        if 'selected_day' not in st.session_state:
            st.session_state.selected_day = 0
        
        if 'full_text' not in st.session_state:
            st.session_state.full_text = "passage not yet initialised."
        
        st.page_link("pages/about_.py", label="*First time here?*")

        refresh_speak_html()
        html(st.session_state.speak_html, height=100)

        display_reading_mode()
        
        # Detect changes (initial load or switch) and force one rerun after update
        needs_rerun = False
        if 'last_day' not in st.session_state or 'last_index' not in st.session_state:
            needs_rerun = True  # Initial load
        elif (st.session_state.last_day != st.session_state.selected_day or
              st.session_state.last_index != st.session_state.selected_passage_index):
            needs_rerun = True  # Switch detected

        # Update trackers
        st.session_state.last_day = st.session_state.selected_day
        st.session_state.last_index = st.session_state.selected_passage_index

        if needs_rerun:
            st.rerun()

    else:  # Chat mode
        st.markdown("*Ask questions and receive answers grounded in Scripture (NKJV)*")
        display_chat_mode()

if __name__ == "__main__":
    main()