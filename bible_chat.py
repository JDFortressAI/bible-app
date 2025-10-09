import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
- Convert all neutral quotes ("") into Proper Quotes (“”) always.
- Convert all neutral apostrophe (') into Proper apostrophe (’). 
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

def main():
    st.set_page_config(
        page_title="Bible Chat",
        page_icon="📖",
        layout="wide"
    )
    
    st.title("📖 Bible Chat")
    st.markdown("*Ask questions and receive answers grounded in Scripture (NKJV)*")
    
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

if __name__ == "__main__":
    main()