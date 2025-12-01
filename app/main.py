"""
Main Streamlit application for AI Booking Assistant.
"""
import sys
import os

# Add project root to Python path
# Get the directory containing this file (app/)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the project root (parent of app/)
project_root = os.path.dirname(current_dir)
# Add project root to path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from app.config import GEMINI_API_KEY
from app.rag_pipeline import RAGPipeline
from app.chat_logic import ChatLogic
from app.admin_dashboard import render_admin_dashboard
from db.database import Database


# Page configuration
st.set_page_config(
    page_title="Gates Of Argonath - Gaming Convention",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "chat_logic" not in st.session_state:
    st.session_state.chat_logic = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None
if "database" not in st.session_state:
    st.session_state.database = None


def initialize_components():
    """Initialize RAG pipeline, database, and chat logic."""
    try:
        # Check API key
        if not GEMINI_API_KEY:
            st.error("⚠️ Google Gemini API key not found. Please set GEMINI_API_KEY environment variable or in Streamlit secrets.")
            st.stop()
        
        # Initialize database
        if st.session_state.database is None:
            st.session_state.database = Database()
        
        # Initialize RAG pipeline
        if st.session_state.rag_pipeline is None:
            with st.spinner("Initializing RAG pipeline..."):
                st.session_state.rag_pipeline = RAGPipeline()
        
        # Initialize chat logic
        if st.session_state.chat_logic is None:
            st.session_state.chat_logic = ChatLogic(
                st.session_state.rag_pipeline,
                st.session_state.database
            )
        
        return True
    except Exception as e:
        st.error(f"Error initializing components: {str(e)}")
        return False


def main():
    """Main application."""
    # Sidebar
    with st.sidebar:
        st.title("🎮 Gates Of Argonath")
        st.markdown("### Gaming Convention")
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["💬 Chat", "📄 Upload PDFs", "📊 Admin Dashboard"],
            key="nav"
        )
        
        st.markdown("---")
        
        # PDF Upload Section
        if page == "📄 Upload PDFs":
            st.subheader("Upload PDFs")
            st.info("💡 **Beta Testers:** Upload your government ID (PDF) here to complete your beta tester registration for unreleased games.")
            uploaded_files = st.file_uploader(
                "Choose PDF files (Government IDs for beta testers)",
                type="pdf",
                accept_multiple_files=True,
                key="pdf_uploader"
            )
            
            if uploaded_files:
                if st.button("Process PDFs", key="process_pdfs"):
                    initialize_components()
                    if st.session_state.rag_pipeline:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, uploaded_file in enumerate(uploaded_files):
                            try:
                                status_text.text(f"Processing {uploaded_file.name}...")
                                st.session_state.rag_pipeline.process_pdf(
                                    uploaded_file,
                                    uploaded_file.name
                                )
                                progress_bar.progress((idx + 1) / len(uploaded_files))
                                st.success(f"✅ {uploaded_file.name} processed successfully!")
                            except Exception as e:
                                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                        
                        status_text.text("All PDFs processed!")
                        st.balloons()
        
        # Reset conversation
        if st.button("🔄 Reset Conversation", key="reset_conv"):
            if st.session_state.chat_logic:
                st.session_state.chat_logic.reset_conversation()
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("### About Gates Of Argonath")
        st.markdown("""
        A 3-day gaming convention featuring:
        - 🎮 New games and LAN gaming
        - 🔧 Gaming technology insights
        - 🧪 Beta testing opportunities
        - 🎟️ Ticket booking assistance
        """)
    
    # Main content area
    if page == "💬 Chat":
        render_chat_page()
    elif page == "📊 Admin Dashboard":
        render_admin_page()
    elif page == "📄 Upload PDFs":
        st.header("📄 Upload Government ID (PDF)")
        st.markdown("### Beta Tester Registration")
        st.info("""
        **For Beta Testers:** Upload your government ID (PDF) here to complete your registration for beta testing unreleased games at Gates Of Argonath.
        
        Your uploaded documents will be securely processed and used to verify your eligibility for beta testing programs.
        """)
        st.markdown("---")
        st.markdown("Use the sidebar to upload your government ID PDF files.")


def render_chat_page():
    """Render the chat interface."""
    st.header("💬 Chat with Gates Of Argonath Assistant")
    st.markdown("Book your tickets, ask questions about the convention, or learn more about becoming a beta tester!")
    
    # Initialize components
    if not initialize_components():
        return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("tool_used"):
                st.caption(f"🔧 Tool used: {message['tool_used']}")
            if message.get("status") == "success":
                st.success("✅ Booking confirmed!")
            elif message.get("status") == "warning":
                st.warning("⚠️ Booking saved, but email failed")
            elif message.get("status") == "error":
                st.error("❌ Error occurred")
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.chat_logic.process_message(prompt)
                    
                    # Display response
                    st.markdown(result["response"])
                    
                    # Display tool info
                    if result.get("tool_used"):
                        st.caption(f"🔧 Tool used: {result['tool_used']}")
                    
                    # Display status
                    if result.get("status") == "success":
                        st.success("✅ Booking confirmed!")
                    elif result.get("status") == "warning":
                        st.warning("⚠️ Booking saved, but email failed")
                    elif result.get("status") == "error":
                        st.error("❌ Error occurred")
                    
                    # Add assistant message to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "tool_used": result.get("tool_used"),
                        "status": result.get("status"),
                        "booking_id": result.get("booking_id")
                    })
                except Exception as e:
                    error_msg = f"I encountered an error: {str(e)}. Please try again."
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "status": "error"
                    })


def render_admin_page():
    """Render the admin dashboard."""
    # Initialize components
    if not initialize_components():
        return
    
    # Check for admin access (you can add authentication here)
    render_admin_dashboard(st.session_state.database)


if __name__ == "__main__":
    main()

