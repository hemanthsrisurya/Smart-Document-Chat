"""
Smart Document Chat App 🚀
Built with Streamlit + RAG - because why read when you can just ask?
Clean, fast, and ridiculously effective document Q&A system
"""
import streamlit as st
import logging
from chatbot import RAGChatbot
import config
import utils

# Setup logging
utils.setup_logging()
logger = logging.getLogger(__name__)


def initialize_session_state():
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = RAGChatbot()
        logger.info("Spinning up a fresh chatbot instance")
        
        if st.session_state.chatbot.has_persistent_data():
            logger.info("Found your saved docs - we're good to go!")
    
    if config.SESSION_MESSAGES not in st.session_state:
        st.session_state[config.SESSION_MESSAGES] = []
    
    if 'chat_available' not in st.session_state:
        st.session_state['chat_available'] = (
            st.session_state.chatbot.is_ready or 
            st.session_state.chatbot.has_persistent_data()
        )


def display_chat_messages():
    for message in st.session_state[config.SESSION_MESSAGES]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main():
    # Page setup 
    st.set_page_config(
        page_title=config.PAGE_TITLE,
        page_icon=config.PAGE_ICON,
        layout=config.PAGE_LAYOUT
    )
    
    initialize_session_state()
    
    st.title(config.PAGE_TITLE)
    
    # Smart welcome based on what's already loaded
    if st.session_state.chatbot.has_persistent_data():
        st.markdown("📄🚀 " + config.PERSISTENT_DATA_MESSAGE)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            doc_count = st.session_state.chatbot.get_document_count()
            file_info = st.session_state.chatbot.document_processor.get_file_info()
            
            st.info(f"💾 **Ready to rock!** {doc_count} chunks from {file_info['count']} PDFs loaded up.")
    else:
        st.markdown(config.WELCOME_MESSAGE)
    
    with st.sidebar:
        st.header("📄 Your Documents")
        
        if st.session_state.chatbot.has_persistent_data():
            doc_count = st.session_state.chatbot.get_document_count()
            file_info = st.session_state.chatbot.document_processor.get_file_info()
            
            st.success(f"🎯 {file_info['count']} PDFs loaded ({doc_count} chunks)")
            
            with st.expander("📋 Files Loaded :"):
                for file in file_info['files']:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"• {file}")
                    with col2:
                        if st.button("🗑️", key=f"delete_{file}", help=f"Remove {file}"):
                            with st.spinner(f"Deleting {file}..."):
                                try:
                                    success = st.session_state.chatbot.delete_pdf(file)
                                    if success:
                                        st.success(f"✅ Deleted {file}")
                                        # Clear any cached data
                                        if 'chat_available' in st.session_state:
                                            st.session_state['chat_available'] = st.session_state.chatbot.has_persistent_data()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Failed to delete {file}")
                                except Exception as e:
                                    st.error(f"❌ Error deleting {file}: {str(e)}")
                                    logger.error(f"Delete error: {e}")
            
            st.info("")
        
        uploaded_files = st.file_uploader(
            "Drop your PDFs here",
            type=['pdf'],
            accept_multiple_files=True,
            help="Expand your knowledge base" if st.session_state.chatbot.has_persistent_data() else "Get started with some PDFs"
        )
        
        # Check for files from main uploader too
        main_files = st.session_state.get('main_files', [])
        if main_files and not uploaded_files:
            uploaded_files = main_files
            st.info("📄 Files from main page ready to process!")
        
        if uploaded_files:
            valid_files = []
            for file in uploaded_files:
                if utils.validate_pdf_file(file):
                    valid_files.append(file)
                    st.success(f"🎯 {file.name} ({utils.get_file_size_mb(file):.2f} MB)")
                else:
                    st.error(f"❌ {file.name} isn't a proper PDF")
            
            if valid_files and st.button("🚀 Process These PDFs", type="primary"):
                with st.spinner(config.PROCESSING_MESSAGE):
                    try:
                        success = st.session_state.chatbot.process_pdfs(valid_files)
                        if success:
                            st.success(config.SUCCESS_MESSAGE)
                            st.balloons()
                            st.session_state['chat_available'] = True
                            # Clear main files after processing
                            if 'main_files' in st.session_state:
                                del st.session_state['main_files']
                            st.rerun()
                        else:
                            st.error("Something went wrong processing those PDFs.")
                    except Exception as e:
                        st.error(config.ERROR_MESSAGE.format(str(e)))
                        logger.error(f"PDF processing error: {e}")
        
        st.divider()
        st.header("🔧 Control Panel")
        
        # Temperature slider
        st.subheader("🌡️ AI Temperature")
        temperature = st.slider(
            "Creativity Level",
            min_value=0.0,
            max_value=1.0,
            value=config.LLM_TEMPERATURE,
            step=0.1,
            help="Lower = more focused, Higher = more creative"
        )
        if temperature != config.LLM_TEMPERATURE:
            # Update the chatbot's temperature
            if hasattr(st.session_state.chatbot, 'llm_handler'):
                st.session_state.chatbot.llm_handler.temperature = temperature
            st.info(f"Temperature updated to {temperature}")
        
        st.divider()
        
        if st.button("🧽 Clean PDF Folder", help="Remove any corrupted files"):
            with st.spinner("Cleaning PDF folder..."):
                try:
                    cleaned_count = st.session_state.chatbot.document_processor.clean_pdf_directory()
                    if cleaned_count > 0:
                        st.success(f"✅ Cleaned up {cleaned_count} corrupted files!")
                        # Rebuild vector store after cleaning
                        st.session_state.chatbot._rebuild_vector_store_from_remaining_pdfs()
                        st.rerun()
                    else:
                        st.info("✨ All files are clean already!")
                except Exception as e:
                    st.error(f"❌ Error cleaning folder: {str(e)}")
                    logger.error(f"Clean folder error: {e}")
        
        if st.button("🔥 Total Reset", help="Nuclear option - start completely fresh", type="secondary"):
            # Use a confirmation in session state to avoid nested button issue
            if 'confirm_reset' not in st.session_state:
                st.session_state['confirm_reset'] = False
            
            if not st.session_state['confirm_reset']:
                st.session_state['confirm_reset'] = True
                st.warning("⚠️ Click 'Total Reset' again to confirm - this will delete EVERYTHING!")
                st.rerun()
            else:
                with st.spinner("Resetting everything..."):
                    try:
                        # Reset the existing chatbot completely
                        st.session_state.chatbot.reset()
                        
                        # Clear all session state except chatbot (we'll keep the reset one)
                        keys_to_delete = [key for key in st.session_state.keys() if key != 'chatbot']
                        for key in keys_to_delete:
                            del st.session_state[key]
                        
                        # Reinitialize session state variables
                        st.session_state[config.SESSION_MESSAGES] = []
                        st.session_state['chat_available'] = False
                        
                        st.success("🔥 Everything reset - fresh start!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Reset failed: {str(e)}")
                        logger.error(f"Reset error: {e}")
                        # If reset fails, try to create a fresh chatbot
                        try:
                            st.session_state.chatbot = RAGChatbot()
                            st.session_state[config.SESSION_MESSAGES] = []
                            st.session_state['chat_available'] = False
                            st.warning("Reset partially completed - created fresh chatbot")
                            st.rerun()
                        except Exception as e2:
                            st.error(f"❌ Failed to create fresh chatbot: {str(e2)}")
                            logger.error(f"Fresh chatbot creation error: {e2}")
        
        st.divider()
        
        if st.session_state.chatbot.has_persistent_data():
            st.success("🟢 System Online!")
        elif st.session_state.chatbot.is_ready:
            st.success("🟢 Ready to go!")
        else:
            st.info("🔴 " + config.UPLOAD_PROMPT)
    
    # Main chat interface - ready when docs are loaded
    if st.session_state.chatbot.is_ready or st.session_state.chatbot.has_persistent_data():
        if (st.session_state.chatbot.has_persistent_data() and 
            len(st.session_state[config.SESSION_MESSAGES]) == 0):
            with st.chat_message("assistant"):
                st.markdown("🎯 Hey! I've got your docs loaded and ready. What do you want to know?")
        
        display_chat_messages()
        
        # Input handling
        if prompt := st.chat_input("Ask me anything about your documents..."):
            st.session_state[config.SESSION_MESSAGES].append({
                "role": "user",
                "content": prompt
            })
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.chatbot.chat(prompt)
                        answer = response.get('result', 'Sorry, I could not generate a response.')
                        
                        utils.display_message_with_typing(answer)
                        
                        if response.get('source_documents'):
                            with st.expander("📚 Sources"):
                                sources = utils.format_sources(response['source_documents'])
                                st.markdown(sources)
                        
                        st.session_state[config.SESSION_MESSAGES].append({
                            "role": "assistant",
                            "content": answer
                        })
                        
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        logger.error(f"Chat error: {e}")
    
    else:
        # Enhanced welcome screen with drag and drop focus
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            # Main drag and drop area
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 15px; margin: 1rem 0; color: white;">
                <h2>📄 Drag & Drop Your PDFs Here</h2>
                <p style="font-size: 1.2em; margin: 1rem 0;">Simply drop your documents or use the sidebar uploader</p>
                <p style="font-size: 1em; opacity: 0.9;">Transform any PDF into an interactive Q&A experience!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick upload area for main page
            main_uploaded_files = st.file_uploader(
                "📂 Choose PDF files to get started",
                type=['pdf'],
                accept_multiple_files=True,
                help="Select multiple PDFs for a comprehensive knowledge base",
                key="main_uploader"
            )
            
            if main_uploaded_files:
                st.info("👈 Great! Now head to the sidebar and click 'Process These PDFs' to get started!")
                # Add the files to the chatbot for processing
                if hasattr(st.session_state, 'main_files'):
                    st.session_state.main_files = main_uploaded_files
                else:
                    st.session_state['main_files'] = main_uploaded_files
            
            st.markdown("---")
            
            # Features showcase
            st.markdown("""
            ## 🚀 Features
            
            **🤖 Smart AI Assistant**  
            Ask natural questions and get intelligent answers from your documents
            
            **📚 Multiple Document Support**  
            Upload and query across multiple PDFs simultaneously
            
            **💾 Persistent Memory**  
            Your documents stay loaded between sessions - no re-uploading needed!
            
            **🔒 Privacy First**  
            Everything runs locally - your documents never leave your system
            """)
            
            # Quick start guide
            with st.expander("🎯 Quick Start Guide", expanded=True):
                st.markdown("""
                ### Getting Started in 3 Steps:
                
                **1. 📄 Upload Documents**
                - Drag & drop PDFs above or use the sidebar uploader
                - Multiple files supported - the more the better!
                
                **2. ⚡ Process & Wait**
                - Click "Process These PDFs" in the sidebar
                - Grab a coffee while AI analyzes your documents
                
                **3. 💬 Start Chatting**
                - Ask anything about your documents
                - Get instant, accurate answers with sources
                """)
            
            # Example questions
            with st.expander("� Example Questions to Try"):
                st.markdown("""
                **📊 Analysis Questions:**
                - "What are the main themes in these documents?"
                - "Summarize the key findings from chapter 3"
                - "What recommendations are mentioned?"
                
                **🔍 Search Questions:**
                - "Find all mentions of [specific topic]"
                - "What does the document say about [subject]?"
                - "Compare different approaches discussed"
                
                **📝 Summary Questions:**
                - "Give me a brief overview of this document"
                - "What are the most important points?"
                - "List the main conclusions"
                """)
    
    # Footer status
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.session_state.chatbot.has_persistent_data():
            st.markdown("**💾 Data Status:** Your documents are loaded and ready for questions!")
        else:
            st.markdown("**💾 Data Status:** Upload PDFs to get started with document Q&A")


if __name__ == "__main__":
    main()