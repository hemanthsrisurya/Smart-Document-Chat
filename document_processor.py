"""
Document processing module for handling PDF files
"""
import os
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import config
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles PDF loading and text chunking operations"""
    
    def __init__(self, chunk_size: int = config.CHUNK_SIZE, 
                 chunk_overlap: int = config.CHUNK_OVERLAP):
        """
        Initialize the document processor
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def save_uploaded_file(self, uploaded_file) -> str:
        """
        Save uploaded file to disk
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Path to saved file
        """
        file_path = os.path.join(config.PDF_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info(f"Saved uploaded file to {file_path}")
        return file_path
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Load PDF file and extract text
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of Document objects
        """
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            raise
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split documents into {len(chunks)} chunks")
        return chunks
    
    def process_pdf(self, uploaded_file) -> List[Document]:
        """
        Complete pipeline to process PDF file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            List of chunked Document objects
        """
        # Save file
        file_path = self.save_uploaded_file(uploaded_file)
        
        # Load PDF
        documents = self.load_pdf(file_path)
        
        # Split into chunks
        chunks = self.split_documents(documents)
        
        return chunks
    
    def process_multiple_pdfs(self, uploaded_files: List) -> List[Document]:
        """
        Process multiple PDF files
        
        Args:
            uploaded_files: List of Streamlit UploadedFile objects
            
        Returns:
            Combined list of chunked Document objects
        """
        all_chunks = []
        for uploaded_file in uploaded_files:
            chunks = self.process_pdf(uploaded_file)
            all_chunks.extend(chunks)
        
        logger.info(f"Processed {len(uploaded_files)} PDFs into {len(all_chunks)} total chunks")
        return all_chunks
    
    def get_processed_files(self) -> List[str]:
        """
        Get list of processed PDF files
        
        Returns:
            List of PDF filenames in the PDF directory
        """
        try:
            pdf_files = [f for f in os.listdir(config.PDF_DIR) if f.endswith('.pdf')]
            return pdf_files
        except Exception as e:
            logger.error(f"Error getting processed files: {e}")
            return []
    
    def get_file_info(self) -> dict:
        """
        Get information about processed files
        
        Returns:
            Dictionary with file information
        """
        files = self.get_processed_files()
        file_info = {
            'count': len(files),
            'files': files,
            'total_size_mb': 0
        }
        
        try:
            total_size = 0
            for file in files:
                file_path = os.path.join(config.PDF_DIR, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
            file_info['total_size_mb'] = total_size / (1024 * 1024)
        except Exception as e:
            logger.error(f"Error calculating file sizes: {e}")
        
        return file_info
    
    def clean_pdf_directory(self):
        """
        Clean up the PDF directory by removing any invalid files
        
        Returns:
            Number of files cleaned up
        """
        cleaned_count = 0
        try:
            logger.info("Starting PDF directory cleanup...")
            
            if not os.path.exists(config.PDF_DIR):
                logger.info("PDF directory doesn't exist, creating it...")
                os.makedirs(config.PDF_DIR, exist_ok=True)
                return 0
            
            for filename in os.listdir(config.PDF_DIR):
                file_path = os.path.join(config.PDF_DIR, filename)
                if os.path.isfile(file_path):
                    try:
                        # Check if it's a valid PDF by extension
                        if not filename.lower().endswith('.pdf'):
                            os.remove(file_path)
                            cleaned_count += 1
                            logger.info(f"Removed non-PDF file: {filename}")
                            continue
                        
                        # Check if PDF file is readable
                        test_docs = self.load_pdf(file_path)
                        if not test_docs or len(test_docs) == 0:
                            os.remove(file_path)
                            cleaned_count += 1
                            logger.info(f"Removed empty PDF: {filename}")
                            
                    except Exception as e:
                        # If PDF can't be loaded, it's corrupted
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                            logger.info(f"Removed corrupted PDF: {filename} - Error: {e}")
                        except Exception as remove_error:
                            logger.error(f"Could not remove corrupted file {filename}: {remove_error}")
            
            logger.info(f"PDF directory cleanup completed. Removed {cleaned_count} files.")
            
        except Exception as e:
            logger.error(f"Error cleaning PDF directory: {e}")
        
        return cleaned_count
    
    def delete_pdf(self, filename: str) -> bool:
        """
        Delete a specific PDF file
        
        Args:
            filename: Name of the PDF file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            file_path = os.path.join(config.PDF_DIR, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted PDF file: {filename}")
                return True
            else:
                logger.warning(f"PDF file not found: {filename}")
                return False
        except Exception as e:
            logger.error(f"Error deleting PDF file {filename}: {e}")
            return False
    
    def delete_multiple_pdfs(self, filenames: List[str]) -> int:
        """
        Delete multiple PDF files
        
        Args:
            filenames: List of PDF filenames to delete
            
        Returns:
            Number of files successfully deleted
        """
        deleted_count = 0
        for filename in filenames:
            if self.delete_pdf(filename):
                deleted_count += 1
        return deleted_count
    
    def delete_all_pdfs(self) -> int:
        """
        Delete all PDF files from the directory
        
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        try:
            for filename in os.listdir(config.PDF_DIR):
                if filename.lower().endswith('.pdf'):
                    if self.delete_pdf(filename):
                        deleted_count += 1
        except Exception as e:
            logger.error(f"Error deleting all PDFs: {e}")
        
        return deleted_count