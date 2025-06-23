import streamlit as st
from mk1 import fetch_transcript, generate_timestamps  # Replace with your actual script file name

st.set_page_config(page_title="YouTube Chapter Generator", layout="centered")

st.title("📽️ YouTube Chapter Timestamp Generator")
st.markdown("Generate automatic chapter titles for YouTube videos using AI (FLAN-T5).")

video_url = st.text_input("Enter YouTube Video URL:")

if st.button("Generate Chapters") or video_url:
    if video_url:
        transcript = duration = None  # define defaults to avoid scope issues

        with st.spinner("Fetching transcript..."):
            transcript, duration = fetch_transcript(video_url)

        if not transcript or not duration:
            st.error("Could not extract transcript. Try another video.")
        else:
            with st.spinner("Generating chapter titles..."):
                results = generate_timestamps(transcript, duration)

            st.success("Chapters generated!")
            st.subheader("📌 Chapters:")
            st.code("\n".join(results), language="text")

    else:
        st.warning("Please enter a video URL.")
