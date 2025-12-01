"""
RAG Pipeline for PDF processing and retrieval.
"""
import os
import pickle
from typing import List, Optional
from pathlib import Path
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import app.config as config


class RAGPipeline:
    """RAG pipeline for PDF processing and retrieval."""
    
    def __init__(self):
        """Initialize RAG pipeline."""
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            google_api_key=config.GEMINI_API_KEY
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        self.vector_store: Optional[FAISS] = None
        self.vector_store_path = config.VECTOR_STORE_PATH
        self._load_or_create_vector_store()
    
    def _load_or_create_vector_store(self):
        """Load existing vector store or create a new one."""
        if os.path.exists(self.vector_store_path) and os.path.isdir(self.vector_store_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                print(f"Error loading vector store: {e}. Creating new one.")
                self.vector_store = None
        
        if self.vector_store is None:
            # Create empty vector store
            self.vector_store = FAISS.from_texts(
                ["Initial document"],
                self.embeddings
            )
            # Remove the initial document
            self._save_vector_store()
    
    def _save_vector_store(self):
        """Save vector store to disk."""
        os.makedirs(self.vector_store_path, exist_ok=True)
        self.vector_store.save_local(self.vector_store_path)
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def process_pdf(self, pdf_file, filename: str) -> bool:
        """Process and add PDF to vector store."""
        try:
            # Extract text
            text = self.extract_text_from_pdf(pdf_file)
            if not text.strip():
                raise Exception("No text extracted from PDF")
            
            # Split into chunks
            chunks = self.text_splitter.split_text(text)
            documents = [Document(page_content=chunk, metadata={"source": filename}) 
                         for chunk in chunks]
            
            # Create temporary vector store for new documents
            temp_store = FAISS.from_documents(documents, self.embeddings)
            
            # Merge with existing vector store
            if self.vector_store is None:
                self.vector_store = temp_store
            else:
                self.vector_store.merge_from(temp_store)
            
            # Save to disk
            self._save_vector_store()
            return True
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def search(self, query: str, k: int = 3) -> List[str]:
        """Search for relevant chunks."""
        if self.vector_store is None:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
    
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """Get relevant context as a single string."""
        chunks = self.search(query, k=k)
        return "\n\n".join(chunks) if chunks else ""

