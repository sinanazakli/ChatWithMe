import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# .env laden
load_dotenv()

# Streamlit-Seite konfigurieren
st.set_page_config(page_title="💬 Basic Chatbot", layout="centered")

# Titel und Beschreibung
st.title("💬 Basic Chatbot")
st.write("Hallo! Dies ist ein einfacher Chatbot mit Streamlit und OpenAI.")

# API-Key aus .env oder Eingabe
default_api_key = os.getenv("OPENAI_API_KEY", "")
if not default_api_key:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("Bitte füge deinen OpenAI API-Key hinzu, um fortzufahren.", icon="🗝️")
        st.stop()
    else:
        default_api_key = openai_api_key

# OpenAI-Client erstellen
client = OpenAI(api_key=default_api_key)

# Session State für Nachrichten
if "messages" not in st.session_state:
    st.session_state.messages = []

# Modell- und Parameter-Auswahl
st.sidebar.header("⚙️ Einstellungen")
model = st.sidebar.selectbox("Modell wählen", ["gpt-3.5-turbo", "gpt-4"])
temperature = st.sidebar.slider("Kreativität (temperature)", 0.0, 1.0, 0.7)
max_tokens = st.sidebar.slider("Max Tokens", 256, 2048, 512)

# Bisherige Nachrichten anzeigen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Eingabefeld für neue Nachricht
if prompt := st.chat_input("Was möchtest du fragen?"):
    # Nutzer-Nachricht speichern und anzeigen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Antwort generieren
    try:
        with st.spinner("Antwort wird generiert..."):
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            # Antwort streamen und speichern
            with st.chat_message("assistant"):
                response = st.write_stream(stream)

            st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"Fehler bei der API-Anfrage: {e}")