import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key:
    st.error("Please add your OpenAI API key in the .env file.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Load questions from JSON
with open("sam/json/questions_struc.json", "r", encoding="utf-8") as f:
    data = json.load(f)

categories = list(data["categories"].keys())

# Session State initialization
if "started" not in st.session_state:
    st.session_state.started = False
if "current_category" not in st.session_state:
    st.session_state.current_category = categories[0]
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = data
if "feedback" not in st.session_state:
    st.session_state.feedback = ""
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""
if "reset_input" not in st.session_state:
    st.session_state.reset_input = False

# UI Layout
st.title("💬 Basic Chat Quest Bot")
st.write("Welcome! I will help you step by step.")

# Start button
if not st.session_state.started:
    st.subheader("Do you want to start your application?")
    if st.button("Yes, start"):
        st.session_state.started = True
    elif st.button("No, later"):
        st.stop()

# Question flow
if st.session_state.started:
    current_cat = st.session_state.current_category
    current_idx = st.session_state.current_index
    questions_list = st.session_state.answers["categories"][current_cat]

    if current_idx < len(questions_list):
        current_question = questions_list[current_idx]["question"]

        # Display current question and feedback
        st.subheader(f"Question ({current_cat}):")
        st.write(current_question)

        if st.session_state.feedback:
            st.info(f"💡 AI Feedback: {st.session_state.feedback}")

        # Reset input if flagged
        if st.session_state.reset_input:
            st.session_state.user_input = ""
            st.session_state.reset_input = False

        # Generate feedback when Enter is pressed
        def generate_feedback():
            user_answer = st.session_state.user_input.strip()
            if user_answer and user_answer != st.session_state.last_answer:
                st.session_state.last_answer = user_answer
                with st.spinner("Generating AI feedback..."):
                    try:
                        prompt = f"Question: {current_question}\nAnswer: {user_answer}\nProvide short, constructive feedback."
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a professional career coach."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.7,
                            max_tokens=150
                        )
                        st.session_state.feedback = response.choices[0].message.content
                    except Exception as e:
                        st.error(f"Error generating feedback: {e}")

        # Persistent input field at bottom
        st.text_input("Your answer:", key="user_input", on_change=generate_feedback)

        # Save answer and move to next question
        if st.button("Save Answer"):
            answer = st.session_state.user_input.strip()
            if answer:
                st.session_state.answers["categories"][current_cat][current_idx]["answer"] = answer
                st.session_state.answers["categories"][current_cat][current_idx]["answered"] = True

                # Reset feedback and input
                st.session_state.feedback = ""
                st.session_state.last_answer = ""
                st.session_state.reset_input = True

                # Move to next question
                if current_idx + 1 < len(questions_list):
                    st.session_state.current_index += 1
                else:
                    cat_keys = categories
                    current_cat_idx = cat_keys.index(current_cat)
                    if current_cat_idx + 1 < len(cat_keys):
                        st.session_state.current_category = cat_keys[current_cat_idx + 1]
                        st.session_state.current_index = 0
                    else:
                        st.write("✅ All questions answered!")

                st.rerun()
    else:
        st.write("✅ All questions answered!")

# Export answers
if st.button("📥 Export Answers"):
    st.download_button(
        label="Download as JSON",
        data=json.dumps(st.session_state.answers, indent=4, ensure_ascii=False),
        file_name="application_answers.json",
        mime="application/json"
    )