import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from document_loader import load_documents_into_database

from llm import getStreamingChain


EMBEDDING_MODEL = "models/embedding-001"
PATH = "research"

st.title("Google Gemini RAG ")

if "list_of_models" not in st.session_state:
    st.session_state["list_of_models"] = []

if not os.getenv("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY environment variable not set.")

gemini_models = ["gemini-2.5-flash"]
selected_model = st.sidebar.selectbox("Select a model:", gemini_models)

if st.session_state.get("gemini_model") != selected_model:
    st.session_state["gemini_model"] = selected_model
    st.session_state["llm"] = ChatGoogleGenerativeAI(model=selected_model)


# Folder selection
folder_path = st.sidebar.text_input("Enter the folder path:", PATH)

# Initialize states
if "db" not in st.session_state:
    st.session_state.db = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if folder_path:
    if not os.path.isdir(folder_path):
        st.error(
            "The provided path is not a valid directory. Please enter a valid folder path."
        )
    else:
        if st.sidebar.button("Index Documents"):
            with st.spinner(
                "Creating embeddings and loading documents into Chroma..."
            ):
                st.session_state.db = load_documents_into_database(EMBEDDING_MODEL, folder_path)
            st.info("All set to answer questions!")
else:
    st.warning("Please enter a folder path to load documents into the database.")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat interface
if st.session_state.db is None:
    st.warning("Please index your documents first by clicking 'Index Documents'")
    st.chat_input("Question (indexing required)", disabled=True)
else:
    if prompt := st.chat_input("Question"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = getStreamingChain(
                prompt,
                st.session_state.messages,
                st.session_state.llm,
                st.session_state.db,
            )
            response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})