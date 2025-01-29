import streamlit as st
import requests
from datetime import datetime
import pandas as pd
import time

# Set page configuration
st.set_page_config(
    page_title="AI Chatbot Dictionary",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if "bookmarks" not in st.session_state:
    st.session_state["bookmarks"] = []
if "search_history" not in st.session_state:
    st.session_state["search_history"] = []
if "word_of_the_day" not in st.session_state:
    st.session_state["word_of_the_day"] = None
if "show_splash" not in st.session_state:
    st.session_state["show_splash"] = True

# Fetch a random word for Word of the Day
def get_word_of_the_day():
    response = requests.get("https://random-word-api.herokuapp.com/word?number=1")
    if response.status_code == 200:
        word = response.json()[0]
        definition_response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        if definition_response.status_code == 200:
            return definition_response.json()[0]
    return None

# Load Word of the Day if not already fetched
if not st.session_state["word_of_the_day"]:
    st.session_state["word_of_the_day"] = get_word_of_the_day()

# Splash Screen Logic
if st.session_state["show_splash"]:
    st.markdown(
        "<h1 style='text-align: center;'>📚 Welcome to AI Chatbot Dictionary</h1>",
        unsafe_allow_html=True
    )
    with st.spinner("Loading... Please wait."):
        time.sleep(3)
    st.session_state["show_splash"] = False  # Disable the splash screen
    st.query_params.clear()  # Clear query parameters to simulate navigation

# Sidebar navigation
if not st.session_state["show_splash"]:
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["🏠 Home", "🌟 Word of the Day", "🔍 Search History", "📌 Bookmarked Words"]
    )

    # Home Page
    if page == "🏠 Home":
        st.markdown("<h1 style='text-align: center;'>📚 AI Chatbot Dictionary</h1>", unsafe_allow_html=True)
        st.write("### How to use this application:")
        st.write("""
        - **Search for a word**: Type a word into the input box to get its definitions and phonetics.
        - **Bookmark words**: Save words you want to revisit later.
        - **View your search history**: See the list of words you have searched for.
        - **Learn a new word every day**: Check out the 'Word of the Day' section for daily inspiration!
        """)
        word = st.text_input("Enter a word to search:", "")

        if word:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            if response.status_code == 200:
                data = response.json()[0]
                st.header(f"Word: {data['word']}")
                if "phonetics" in data and len(data["phonetics"]) > 0:
                    for phonetic in data["phonetics"]:
                        if "text" in phonetic:
                            st.write(f"Phonetics: {phonetic['text']}")
                        if "audio" in phonetic and phonetic["audio"]:
                            st.audio(phonetic["audio"])
                st.subheader("Definitions:")
                for meaning in data["meanings"]:
                    st.write(f"- {meaning['partOfSpeech']}:")
                    for definition in meaning["definitions"]:
                        st.write(f"  - {definition['definition']}")

                # Save to search history
                if not any(entry["word"] == word for entry in st.session_state["search_history"]):
                    st.session_state["search_history"].append({
                        "word": word,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                if st.button("Bookmark this word"):
                    if not any(entry["word"] == word for entry in st.session_state["bookmarks"]):
                        st.session_state["bookmarks"].append({
                            "word": word,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.success(f"'{word}' has been added to bookmarks!")
                    else:
                        st.warning(f"'{word}' is already bookmarked.")
            else:
                st.error("Word not found. Please try another word.")

    # Word of the Day Page
    elif page == "🌟 Word of the Day":
        st.markdown("<h1 style='text-align: center;'>🌟 Word of the Day</h1>", unsafe_allow_html=True)
        word_data = st.session_state["word_of_the_day"]
        if word_data:
            st.header(f"Word: {word_data['word']}")
            if "meanings" in word_data:
                for meaning in word_data["meanings"]:
                    st.write(f"- {meaning['partOfSpeech']}:")
                    for definition in meaning["definitions"]:
                        st.write(f"  - {definition['definition']}")
        else:
            st.error("Unable to fetch Word of the Day. Please try again later.")

    # Search History Page
    elif page == "🔍 Search History":
        st.markdown("<h1 style='text-align: center;'>🔍 Search History</h1>", unsafe_allow_html=True)
        if st.session_state["search_history"]:
            df = pd.DataFrame(st.session_state["search_history"])
            st.table(df)
        else:
            st.info("No search history yet.")

    # Bookmarked Words Page
    elif page == "📌 Bookmarked Words":
        st.markdown("<h1 style='text-align: center;'>📌 Bookmarked Words</h1>", unsafe_allow_html=True)
        if st.session_state["bookmarks"]:
            df = pd.DataFrame(st.session_state["bookmarks"])
            st.table(df)
        else:
            st.info("No bookmarks yet.")
