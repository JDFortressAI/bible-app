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
## Why another Bible app?

<div class="about-text">Hundreds of Bible apps exist—yet how many of us actually read the Bible regularly? We open one, freeze on what to read, then slip back into doom-scrolling. We built this for ourselves first: open it, and today’s readings appear instantly—clean, no logging in, no cookies, no fuss. And it works. Evening 𝕏 is gone; five-minute McCheyne hits now bookend my day in God’s Word, even shaping my dreams. I still read my trusty physical Bible, but this app lets me revisit passages and meditate on God’s Word all day. Our prayer: may it spark a love for God’s Word—to read and hear Him every day.</div>

## Why We Need to Read the Bible

<div class="about-text">Like the sons of Issachar who understood the times and knew what they ought to do (1 Chronicles 12:32), we need God’s Word to cut through today’s chaos. Skip the endless scroll; redeem those precious five minutes throughout the day to hear God’s voice. Daily reading sharpens your discernment, renews your mind, and aligns you with His perfect will, equipping you thoroughly for every good work.</div>

## Why the NKJV?

<div class="about-text">The New King James Version (NKJV), rooted in the <em>Textus Receptus</em> manuscript, ensures you’re engaging with a translation that honours the inspiration and preservation of God’s Word. Its poetic cadence and precision make it a powerful choice for hearing God speak clearly, without distraction.</div>

## Why M’Cheyne?

<div class="about-text">How many times have you started a “whole Bible” plan and bailed halfway? Robert Murray McCheyne’s plan changes that: four passages a day take you through the Old Testament once, and the New Testament and Psalms twice, every year. Those four readings weave together beautifully, revealing connections across Scripture that you’ll only discover by sticking with it. This plan isn’t just a schedule—you’ll experience God’s Word in its fullness.</div>

## We Welcome Your Feedback

<div class="about-text">We built this to serve the Church, helping believers return to God’s Word in these end-of-the-end times. The app is simple, beautiful, and distraction-free, so you can focus on what matters: hearing from God. <a href="mailto:contact@jdfortress.com">Tell us what works, what doesn’t</a>—your input shapes the next version. Let’s keep sharpening this tool so more of us hear clearly from God.</div>
""", unsafe_allow_html=True
)

if st.button("Take me back!"):
    st.switch_page("bible_chat.py")

st.markdown("---")

st.markdown(
                '<p style="font-size: 12px; color: #888; text-align: center; margin-top: 2rem;">'
                'Crafted with love by <a href="https://jdfortress.com">JD Fortress AI Ltd</a>. Copyright © 2025. All rights reserved.'
                '</p>', 
                unsafe_allow_html=True
            )