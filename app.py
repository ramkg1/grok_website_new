import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz

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

# Search CSV for answers
def find_answer_from_data(query):
    if df.empty or not query:
        return "No data available to answer the question."
    
    query = query.lower()
    best_score = 0
    best_answer = None

    # Search relevant columns
    for _, row in df.iterrows():
        # Check personname, firstname, lastname for a match
        names = [str(row.get(col, '')).lower() for col in ['personname', 'firstname', 'lastname'] if str(row.get(col, ''))]
        name_scores = [(name, fuzz.token_sort_ratio(query, name)) for name in names] if names else []
        
        # Log scores for debugging
        print(f"Query: {query}, Name scores: {name_scores}")
        
        # Get the highest score
        if name_scores:
            name_score = max(score for _, score in name_scores)
            matched_name = max(name_scores, key=lambda x: x[1])[0]
        else:
            name_score = 0
        
        # If query matches a name or contains keywords
        if name_score > 60 or any(name in query for name in names):
            # Construct answer based on question context
            if "degree" in query or "education" in query:
                degree = row.get('degreetypename', 'unknown degree')
                institution = row.get('degreeinstitution', 'unknown institution')
                year = row.get('degreeyear', 'unknown year')
                answer = f"{row.get('personname', 'Unknown')} earned a {degree} from {institution} in {year}."
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

    return best_answer if best_answer else f"No record found for '{query}'. Try a different name or question."

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
    st.error("CSV data file not found or invalid. Cannot answer questions.")

# Multi-page navigation
page = st.sidebar.selectbox("Navigate", ["Home", "Chat with Grok", "About"])

# Home page
if page == "Home":
    st.title("Welcome to the Grok-Powered Website")
    st.markdown("""
        Dive into a universe of knowledge with our AI-powered site! 
        - **Chat with Grok**: Ask questions about academic records from our CSV data file.
        - **About**: Learn about our mission to explore the stars.
        Built with a curated dataset for out-of-this-world answers.
    """)
    st.image("https://via.placeholder.com/800x400.png?text=Cosmic+Universe", caption="Explore the Cosmos")

# Chat page
elif page == "Chat with Grok":
    st.title("Chat with Grok")
    st.markdown("Ask about academic records, and Grok will answer using the CSV data file!")

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
        response = find_answer_from_data(user_input)
        st.session_state.messages.append({"role": "bot", "content": response})
        st.rerun()

# About page
else:
    st.title("About Us")
    st.markdown("""
        We’re a team of cosmic enthusiasts, inspired by xAI’s mission to accelerate human discovery.
        Our Grok-like chat feature uses a CSV data file of academic records to answer your questions.
        Reach out at cosmic@website.com or follow us on X!
    """)