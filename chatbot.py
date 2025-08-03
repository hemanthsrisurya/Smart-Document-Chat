"""
Smart RAG Chatbot Brain 🧠
The main orchestrator that brings all the pieces together
Handles document processing, vector storage, and intelligent conversations
"""
import os
from typing import Optional, Dict, Any, List
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager
from llm_handler import LLMHandler
import config
import logging

logger = logging.getLogger(__name__)


class RAGChatbot:
    """Your personal document assistant - connects docs, vectors, and LLM magic ✨"""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.vector_store_manager = VectorStoreManager()
        self.llm_handler = LLMHandler()
        self._is_initialized = False
        
        self._auto_initialize()
        
        logger.info("RAG Chatbot initialized and ready to roll")
    
    def _auto_initialize(self):
        """Try to auto-initialize from existing persistent data"""
        try:
            if self.vector_store_manager.has_documents():
                # Initialize QA chain with existing vector store
                retriever = self.vector_store_manager.get_retriever()
                self.llm_handler.create_qa_chain(retriever)
                self._is_initialized = True
                doc_count = self.vector_store_manager.get_document_count()
                logger.info(f"Auto-initialized chatbot from persistent storage with {doc_count} documents")
            else:
                logger.info("No persistent data found - chatbot ready for new uploads")
        except Exception as e:
            logger.warning(f"Could not auto-initialize from persistent storage: {e}")
            # Don't fail completely, just mark as not initialized
            self._is_initialized = False
    
    def process_pdfs(self, uploaded_files: List) -> bool:
        """
        Process uploaded PDF files and create or update vector store
        
        Args:
            uploaded_files: List of uploaded PDF files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Process PDFs into chunks
            if isinstance(uploaded_files, list):
                chunks = self.document_processor.process_multiple_pdfs(uploaded_files)
            else:
                chunks = self.document_processor.process_pdf(uploaded_files)
            
            # Check if we should add to existing or create new
            if self.vector_store_manager.has_documents():
                # Add to existing vector store
                self.vector_store_manager.add_documents(chunks)
                logger.info("Added new documents to existing vector store")
            else:
                # Create new vector store
                self.vector_store_manager.create_vector_store(chunks)
                logger.info("Created new vector store with documents")
            
            # Initialize or reinitialize QA chain
            retriever = self.vector_store_manager.get_retriever()
            self.llm_handler.create_qa_chain(retriever)
            
            self._is_initialized = True
            logger.info("Successfully processed PDFs and initialized chatbot")
            return True
            
        except Exception as e:
            logger.error(f"Error processing PDFs: {e}")
            return False
    
    def add_pdfs(self, uploaded_files: List) -> bool:
        """
        Add additional PDFs to existing vector store
        
        Args:
            uploaded_files: List of uploaded PDF files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Process new PDFs
            if isinstance(uploaded_files, list):
                chunks = self.document_processor.process_multiple_pdfs(uploaded_files)
            else:
                chunks = self.document_processor.process_pdf(uploaded_files)
            
            # Add to vector store
            self.vector_store_manager.add_documents(chunks)
            
            # Reinitialize QA chain with updated retriever
            retriever = self.vector_store_manager.get_retriever()
            self.llm_handler.create_qa_chain(retriever)
            
            logger.info("Successfully added new PDFs to chatbot")
            return True
            
        except Exception as e:
            logger.error(f"Error adding PDFs: {e}")
            return False
    
    def chat(self, question: str) -> Dict[str, Any]:
        """
        Chat with the bot about the uploaded documents
        
        Args:
            question: User question
            
        Returns:
            Dictionary with response and source documents
        """
        if not self._is_initialized:
            return {
                "result": "Please upload a PDF file first to start chatting.",
                "source_documents": []
            }
        
        try:
            response = self.llm_handler.query(question)
            return response
        except Exception as e:
            logger.error(f"Error during chat: {e}")
            return {
                "result": f"Sorry, I encountered an error: {str(e)}",
                "source_documents": []
            }
    
    def search_documents(self, query: str, k: int = 4) -> List:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of relevant documents
        """
        return self.vector_store_manager.search(query, k)
    
    def clear_chat_history(self):
        """Clear the conversation history"""
        self.llm_handler.clear_memory()
        logger.info("Cleared chat history")
    
    def get_chat_history(self) -> list:
        """
        Get conversation history
        
        Returns:
            List of conversation messages
        """
        return self.llm_handler.get_conversation_history()
    
    def reset(self):
        """Reset the entire chatbot state"""
        try:
            logger.info("Starting chatbot reset...")
            
            # Clear vector store
            self.vector_store_manager.clear_vector_store()
            logger.info("Cleared vector store")
            
            # Clear memory
            self.llm_handler.clear_memory()
            logger.info("Cleared LLM memory")
            
            # Delete all PDF files
            deleted_count = self.document_processor.delete_all_pdfs()
            logger.info(f"Deleted {deleted_count} PDF files")
            
            # Reset initialization flag
            self._is_initialized = False
            logger.info("Reset chatbot state completed successfully")
            
        except Exception as e:
            logger.error(f"Error during reset: {e}")
            # Force reset even if some operations failed
            self._is_initialized = False
            raise
    
    def delete_pdf(self, filename: str) -> bool:
        """
        Delete a specific PDF file and update vector store
        
        Args:
            filename: Name of the PDF file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            logger.info(f"Attempting to delete PDF: {filename}")
            
            # Delete the PDF file first
            success = self.document_processor.delete_pdf(filename)
            if not success:
                logger.error(f"Failed to delete PDF file: {filename}")
                return False
            
            # Rebuild vector store from remaining PDFs
            logger.info("Rebuilding vector store after PDF deletion...")
            self._rebuild_vector_store_from_remaining_pdfs()
            
            logger.info(f"Successfully deleted PDF and updated vector store: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting PDF {filename}: {e}")
            return False
    
    def delete_multiple_pdfs(self, filenames: List[str]) -> int:
        """
        Delete multiple PDF files and update vector store
        
        Args:
            filenames: List of PDF filenames to delete
            
        Returns:
            Number of files successfully deleted
        """
        try:
            deleted_count = self.document_processor.delete_multiple_pdfs(filenames)
            if deleted_count > 0:
                self._rebuild_vector_store_from_remaining_pdfs()
                logger.info(f"Successfully deleted {deleted_count} PDFs and updated vector store")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting multiple PDFs: {e}")
            return 0
    
    def _rebuild_vector_store_from_remaining_pdfs(self):
        """
        Rebuild the vector store from remaining PDF files
        This is called after deleting PDFs to update the vector store
        """
        try:
            logger.info("Starting vector store rebuild...")
            remaining_files = self.document_processor.get_processed_files()
            
            if not remaining_files:
                # No files left, clear the vector store
                logger.info("No PDFs remaining, clearing vector store...")
                self.vector_store_manager.clear_vector_store()
                self._is_initialized = False
                logger.info("Vector store cleared - no documents remaining")
                return
            
            # Process remaining PDFs
            all_chunks = []
            successful_files = []
            
            for filename in remaining_files:
                file_path = os.path.join(config.PDF_DIR, filename)
                try:
                    if os.path.exists(file_path):
                        documents = self.document_processor.load_pdf(file_path)
                        if documents:
                            chunks = self.document_processor.split_documents(documents)
                            if chunks:
                                all_chunks.extend(chunks)
                                successful_files.append(filename)
                                logger.info(f"Successfully processed {filename}: {len(chunks)} chunks")
                        else:
                            logger.warning(f"No documents extracted from {filename}")
                    else:
                        logger.warning(f"File not found: {filename}")
                except Exception as e:
                    logger.warning(f"Could not process {filename} during rebuild: {e}")
            
            if all_chunks:
                # Recreate vector store with remaining documents
                logger.info(f"Recreating vector store with {len(all_chunks)} chunks from {len(successful_files)} files")
                self.vector_store_manager.create_vector_store(all_chunks)
                
                # Reinitialize QA chain
                retriever = self.vector_store_manager.get_retriever()
                self.llm_handler.create_qa_chain(retriever)
                self._is_initialized = True
                logger.info(f"Successfully rebuilt vector store with {len(all_chunks)} chunks")
            else:
                logger.info("No valid chunks remaining, clearing vector store")
                self.vector_store_manager.clear_vector_store()
                self._is_initialized = False
                
        except Exception as e:
            logger.error(f"Error rebuilding vector store: {e}")
            # Fallback: clear everything and mark as uninitialized
            try:
                self.vector_store_manager.clear_vector_store()
            except:
                pass
            self._is_initialized = False
    
    @property
    def is_ready(self) -> bool:
        """Check if chatbot is ready for queries"""
        return self._is_initialized
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store"""
        return self.vector_store_manager.get_document_count()
    
    def has_persistent_data(self) -> bool:
        """Check if there's persistent data available"""
        return self.vector_store_manager.has_documents()