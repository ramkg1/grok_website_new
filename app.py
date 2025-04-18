import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
import requests
import os

# Set page config as the first Streamlit command
st.set_page_config(page_title="Grok-Powered Website", layout="wide", initial_sidebar_state="expanded")

# Load CSV data file
try:
    df = pd.read_csv("data.csv")
except (FileNotFoundError, pd.errors.EmptyDataError):
    df = pd.DataFrame()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tone" not in st.session_state:
    st.session_state.tone = "Witty"

# xAI API configuration
XAI_API_URL = "https://api.x.ai/v1/chat/completions"  # Example endpoint
XAI_API_KEY = os.getenv("XAI_API_KEY", "xai-Q1RdkNwxb1CjpuAzXon6gNG4Zgl3Y1XPk8Ez4otznTCq94xMHZlPFr7Y3dTrFF7j9pmz8q9vpq9SNvw0")  # Use environment variable or fallback

# Search CSV for answers
def find_answer_from_data(query):
    if df.empty or not query:
        return None
    
    query = query.lower()
    best_score = 0
    best_answer = None

    # Search relevant columns
    for _, row in df.iterrows():
        # Check personname, firstname, lastname for a match
        names = [str(row.get(col, '')).lower() for col in ['personname', 'firstname', 'lastname'] if str(row.get(col, ''))]
        name_score = max(fuzz.token_sort_ratio(query, name) for name in names) if names else 0
        
        # If query matches a name or contains keywords
        if name_score > 60 or any(name in query for name in names):
            # Construct answer based on question context
            if "degree" in query or "education" in query:
                answer = f"{row.get('personname', 'Unknown')} earned a {row.get('degreetypename', 'unknown degree')} from {row.get('degreeinstitution', 'unknown institution')} in {row.get('degreeyear', 'unknown year')}."
            elif "emeritus" in query:
                status = "emeritus" if row.get('isemeritus', 0) == 1 else "not emeritus"
                answer = f"{row.get('personname', 'Unknown')} is {status}."
            elif "administration" in query:
                status = "in administration" if row.get('isadministration', 0) == 1 else "not in administration"
                answer = f"{row.get('personname', 'Unknown')} is {status}."
            else:
                answer = f"{row.get('personname', 'Unknown')} earned a {row.get('degreetypename', 'unknown degree')} from {row.get('degreeinstitution', 'unknown institution')} in {row.get('degreeyear', 'unknown year')}."
            
            # Update best answer if this score is higher
            if name_score > best_score:
                best_score = name_score
                best_answer = answer

    return best_answer

# xAI API call
def query_xai(query, tone):
    headers = {"Authorization": f"Bearer {XAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "grok-3",
        "messages": [{"role": "user", "content": f"Answer in a {tone.lower()} tone: {query}"}],
        "temperature": 0.5
    }
    try:
        response = requests.post(XAI_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error calling xAI API: {str(e)}. Try a question about the CSV data."

# Styling
st.markdown("""
    <style>
    .stTextInput > div > input { border: 2px solid #4CAF50; border-radius: 5px; padding: 10px; }
    .stButton > button { background-color: #4CAF50; color: white; border-radius: 5px; }
    .stSelectbox > div { background-color: #f0f2f6; border-radius: 5px; }
    .chat-container { background-color: #f9f9f9; padding: 15px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# Display data file error if applicable
if df.empty:
    st.error("CSV data file not found or invalid. Using API only.")

# Multi-page navigation
page = st.sidebar.selectbox("Navigate", ["Home", "Chat with Grok", "About"])

# Home page
if page == "Home":
    st.title("Welcome to the Grok-Powered Website")
    st.markdown("""
        Dive into a universe of knowledge with our AI-powered site! 
        - **Chat with Grok**: Ask questions about academic records or anything else, powered by a CSV data file and Grok’s cosmic insights.
        - **About**: Learn about our mission to explore the stars.
        Built with xAI’s Grok and a curated dataset for out-of-this-world answers.
    """)
    st.image("https://via.placeholder.com/800x400.png?text=Cosmic+Universe", caption="Explore the Cosmos")

# Chat page
elif page == "Chat with Grok":
    st.title("Chat with Grok")
    st.markdown("Ask about academic records or anything else, and Grok will answer using a CSV data file or its cosmic knowledge!")

    # Tone selection
    tone = st.selectbox("Select Grok's Tone", ["Witty", "Formal", "Casual"], index=["Witty", "Formal", "Casual"].index(st.session_state.tone))
    st.session_state.tone = tone

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # Chat container
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**You**: {msg['content']}")
            else:
                st.markdown(f"**Grok**: {msg['content']}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Input form
    with st.form(key="input_form", clear_on_submit=True):
        user_input = st.text_input("Ask Grok a question:", key="user_input")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        data_response = find_answer_from_data(user_input)
        response = data_response if data_response else query_xai(user_input, tone)
        st.session_state.messages.append({"role": "bot", "content": response})
        st.rerun()

# About page
else:
    st.title("About Us")
    st.markdown("""
        We’re a team of cosmic enthusiasts, inspired by xAI’s mission to accelerate human discovery.
        Our Grok-like chat feature uses a CSV data file of academic records for curated answers and xAI’s API for dynamic responses.
        Reach out at cosmic@website.com or follow us on X!
    """)