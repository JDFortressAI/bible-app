import streamlit as st

st.set_page_config(
    page_title="Why?",
    page_icon="👋",
)

st.write("# 📖 About Our Bible Web-App")

st.markdown("""
    <style>
    .about-text {
        font-size: clamp(20px, 4vw, 28px) !important;
        line-height: 1.6 !important;
        font-family: 'Georgia', 'Times New Roman', serif !important;
        margin: 1.5rem 0 !important;
        max-width: 100% !important;
        word-wrap: break-word !important;
        /* Use Streamlit's native text color variable */
        color: var(--text-color) !important;
    }

    
    /* Mobile responsive */
    @media (max-width: 767px) {
        .about-text {
            font-size: clamp(20px, 6vw, 28px) !important;
            line-height: 1.5 !important;
        }
    }
    
    </style>
    """, unsafe_allow_html=True)


st.markdown(
    """
## Why We Need to Read the Bible

<div class="about-text">Like the Sons of Issachar, who understood the times and knew what to do (1 Chronicles 12:32), we’re called to anchor ourselves in God’s Word to navigate today’s chaos. Instead of doom-scrolling through endless noise, redeem those precious five minutes in the morning or evening to hear God’s voice. Reading the Bible daily sharpens your discernment, renews your mind, and aligns your heart with His truth, equipping you to stand firm in these pivotal days.</div>

## Why the NKJV?

<div class="about-text">The New King James Version (NKJV), rooted in the <em>Textus Receptus</em> manuscript, carries a timeless weight and clarity that resonates deeply. Its fidelity to the original texts ensures you’re engaging with a translation that honors the inspired Word. The NKJV’s poetic cadence and precision make it a powerful choice for hearing God speak clearly, without distraction, straight to your soul.</div>

## Why M’Cheyne?

<div class="about-text">When was the last time you committed to reading the entire Bible but didn’t finish? Or read it cover to cover? The M’Cheyne (or McCheyne) Bible Reading plan is a game-changer: it guides you through the Old Testament once, and the New Testament and Psalms twice, every year. Its four daily passages weave together beautifully, revealing connections across Scripture that you’ll only discover by sticking with it. This plan isn’t just a schedule—it’s a journey to experience God’s Word in its fullness.</div>

## We Welcome Your Feedback

<div class="about-text">Our heart is to serve the Body of Christ, helping believers return to God’s Word in these end of the end times. This app is designed to be simple, beautiful, and distraction-free, so you can focus on what matters: hearing from God. We’re here to listen—your feedback helps us make this tool better for you and the Church. <a href="mailto:contact@jdfortress.com">Share your thoughts freely</a>, and let’s grow together in devotion to His Word.</div>
""", unsafe_allow_html=True
)

if st.button("Take me back!"):
    st.switch_page("bible_chat.py")