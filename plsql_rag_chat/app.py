# plsql_rag_chat/app.py

import streamlit as st
from pathlib import Path
import sys
import logging
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import configurations and utilities
from plsql_rag_chat.config.settings import (
    UI_CONFIG,
    MODEL_PARAMS,
    LLM_CONFIG,
    VECTOR_STORE_PATH,
    METADATA_PATH
)
from plsql_rag_chat.lib.ui.styles import CUSTOM_CSS
from plsql_rag_chat.lib.ui.components import (
    render_sidebar_config,
    render_chess_package_explorer
)
from plsql_rag_chat.lib.utils.helpers import (
    load_vectorstore,
    initialize_chat_chain,
    get_llm_handler
)

# Add these constants at the top of the file
EXAMPLE_PROMPTS = [
    {
        "category": "Architecture",
        "prompts": [
            "Explain the overall architecture of the chess engine",
            "How does the move generation system work?",
            "What are the main components and their interactions?"
        ]
    },
    {
        "category": "Algorithms",
        "prompts": [
            "How does the position evaluation work?",
            "Explain the minimax algorithm implementation",
            "How are valid moves calculated?"
        ]
    },
    {
        "category": "Data Structures",
        "prompts": [
            "How is the chess board represented in memory?",
            "Explain the piece movement data structures",
            "How are game states stored and managed?"
        ]
    }
]

# Configure page
st.set_page_config(**UI_CONFIG)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_chain" not in st.session_state:
        st.session_state.chat_chain = None

def display_chat_messages():
    """Display chat message history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def handle_chat_input(chat_container):
    """Handle chat input and generate responses"""
    if prompt := st.chat_input("Ask about chess engine implementation..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
            
            if st.session_state.chat_chain is None:
                with st.chat_message("assistant"):
                    st.error("Please initialize the assistant first! 🔧")
            else:
                try:
                    with st.chat_message("assistant"):
                        with st.spinner("Analyzing..."):
                            # Get chat history
                            chat_history = []
                            if len(st.session_state.messages) > 1:
                                for i in range(0, len(st.session_state.messages)-1, 2):
                                    if i+1 < len(st.session_state.messages):
                                        chat_history.append(
                                            (st.session_state.messages[i]["content"],
                                             st.session_state.messages[i+1]["content"])
                                        )
                            
                            # Generate response
                            response = st.session_state.chat_chain({
                                "question": prompt,
                                "chat_history": chat_history
                            })
                            
                            # Display response
                            st.write(response["answer"])
                            
                            # Show source code if available
                            if response.get("source_documents"):
                                with st.expander("📚 Reference Code"):
                                    for i, doc in enumerate(response["source_documents"], 1):
                                        st.subheader(f"📦 Source {i}: {doc.metadata['package_name']}")
                                        st.code(doc.metadata['formatted_content'], 
                                               language="sql")
                            
                            # Update message history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": response["answer"]
                            })
                
                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")
                    logger.exception("Detailed error:")

def load_knowledge_base():
    """Load and parse the knowledge base markdown file"""
    kb_path = Path("docs/knowledge_base.md")
    if not kb_path.exists():
        return {"error": "Knowledge base file not found"}
    
    try:
        content = kb_path.read_text()
        # Split content into sections based on headers
        sections = []
        current_section = {"title": "Introduction", "content": ""}
        
        for line in content.split('\n'):
            if line.startswith('# '):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {
                    "title": line[2:].strip(),
                    "content": ""
                }
            else:
                current_section["content"] += line + "\n"
        
        if current_section["content"]:
            sections.append(current_section)
        
        return {"sections": sections}
    except Exception as e:
        logger.exception("Error loading knowledge base:")
        return {"error": f"Error loading knowledge base: {str(e)}"}

def render_knowledge_base():
    """Render the knowledge base in a wiki-style format"""
    kb_data = load_knowledge_base()
    
    if "error" in kb_data:
        st.error(kb_data["error"])
        return
    
    # Create sidebar navigation
    st.sidebar.subheader("📚 Navigation")
    selected_section = st.sidebar.radio(
        "Jump to section:",
        options=[section["title"] for section in kb_data["sections"]]
    )
    
    # Render selected section
    for section in kb_data["sections"]:
        if section["title"] == selected_section:
            st.header(section["title"])
            st.markdown(section["content"])
            break

def render_example_prompts():
    """Render example prompts with categories"""
    st.subheader("🔍 Example Prompts")
    
    for category in EXAMPLE_PROMPTS:
        with st.expander(f"📑 {category['category']}"):
            for prompt in category['prompts']:
                if st.button(prompt, key=f"prompt_{hash(prompt)}"):
                    # Add prompt to chat
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    # Force a rerun to show the new message
                    st.rerun()

def main():
    """Main application function"""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Add tabs to the interface
        tab1, tab2, tab3 = st.tabs(["💬 Chat", "📖 Knowledge Base", "❓ Examples"])
        
        with tab1:
            st.title("♟️ Chess Engine Code Assistant")
            
            # Sidebar configuration
            with st.sidebar:
                # Model parameters
                model_params = render_sidebar_config(MODEL_PARAMS)
                
                # Initialize button
                if st.button("🚀 Initialize Assistant", use_container_width=True):
                    with st.spinner("Loading knowledge base..."):
                        initialize_assistant(model_params)
            
            # Main chat container
            chat_container = st.container()
            
            # Display chat history
            with chat_container:
                display_chat_messages()
            
            # Handle chat input
            handle_chat_input(chat_container)
        
        with tab2:
            render_knowledge_base()
        
        with tab3:
            render_example_prompts()
    
    except Exception as e:
        logger.exception("Application error:")
        st.error(f"Application error: {str(e)}")

# Extracted initialization logic for clarity
def initialize_assistant(model_params):
    # Get LLM handler
    llm_handler = get_llm_handler(LLM_CONFIG)
    
    if not llm_handler:
        st.error(f"Failed to initialize {LLM_CONFIG['provider']} handler")
        return
    
    # Check LLM health
    if not llm_handler.health_check():
        st.error(f"Cannot connect to {LLM_CONFIG['provider']}. Please check if the service is running.")
        return
    
    # Load vector store
    vectorstore, metadata = load_vectorstore(
        VECTOR_STORE_PATH,
        METADATA_PATH
    )
    
    if not vectorstore or not metadata:
        st.error("Failed to load vector store or metadata")
        return
    
    # Initialize chat chain
    st.session_state.chat_chain = initialize_chat_chain(
        llm_handler,
        vectorstore,
        model_params
    )
    
    if st.session_state.chat_chain:
        render_chess_package_explorer(metadata)
        st.success("Ready to assist! 🎉")
    else:
        st.error("Failed to initialize chat chain")

if __name__ == "__main__":
    main()
