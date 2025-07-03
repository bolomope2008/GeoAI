"""
Document Processing and Vector Database Update Script

This module processes documents from a knowledge base directory and updates a ChromaDB vector database
for use with the RAG chatbot. It supports multiple document formats (PDF, DOCX, XLSX, CSV, TXT) and
handles document chunking and embedding generation.

The process works as follows:
1. Read documents from the knowledge base directory
2. Extract text and metadata from each supported file type
3. Split documents into manageable chunks
4. Generate embeddings for each chunk
5. Store chunks and embeddings in ChromaDB

Key Components:
- ChromaDB: Vector database for storing document embeddings
- Ollama: Local embeddings model
- LangChain: Text splitting and embedding generation
- Various document parsers (pdfplumber, python-docx, pandas)
"""

import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from typing import List, Dict, Any, Tuple
import pandas as pd
import pdfplumber
from docx import Document
from langchain_ollama import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from configuration import *
from settings_manager import SettingsManager

def create_chroma_client_for_update(chroma_db_dir):
    """
    Create a ChromaDB client with standardized settings for update operations.
    
    Args:
        chroma_db_dir: Path to the ChromaDB directory
        
    Returns:
        chromadb.PersistentClient: Configured ChromaDB client
    """
    import chromadb.config
    return chromadb.PersistentClient(
        path=str(chroma_db_dir),
        settings=chromadb.config.Settings(
            allow_reset=True,
            anonymized_telemetry=False,
            is_persistent=True
        )
    )

def read_pdf(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Extract text and page numbers from PDF files using pdfplumber.
    
    This function:
    1. Opens the PDF file
    2. Extracts text from each page
    3. Maintains page numbers in metadata
    4. Handles multi-page documents
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple containing:
        - Concatenated text from all pages
        - List of metadata dicts with page numbers
    """
    text_parts = []
    metadata_parts = []
    
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
                metadata_parts.append({
                    "page": i,
                    "total_pages": len(pdf.pages)
                })
    
    return "\n\n".join(text_parts), metadata_parts

def read_docx(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Extract text from DOCX files.
    
    Processes Microsoft Word documents by:
    1. Opening the document
    2. Extracting text from all paragraphs
    3. Preserving paragraph structure
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Tuple containing:
        - Concatenated text from all paragraphs
        - Empty metadata list (no page numbers for DOCX)
    """
    doc = Document(file_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text, [{}]  # Empty metadata as no page numbers

def read_excel(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Extract text from Excel files.
    
    Converts Excel spreadsheets to text by:
    1. Reading the file with pandas
    2. Converting dataframe to string representation
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        Tuple containing:
        - String representation of the spreadsheet
        - Empty metadata list
    """
    df = pd.read_excel(file_path)
    return df.to_string(), [{}]

def read_csv(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Extract text from CSV files.
    
    Processes CSV files by:
    1. Reading with pandas
    2. Converting to string format
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Tuple containing:
        - String representation of the CSV data
        - Empty metadata list
    """
    df = pd.read_csv(file_path)
    return df.to_string(), [{}]

def read_txt(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Read text from TXT files.
    
    Simple text file processing:
    1. Opens file with UTF-8 encoding
    2. Reads entire content
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Tuple containing:
        - File contents as string
        - Empty metadata list
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read(), [{}]

def process_document(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Process a document and return its text content and metadata.
    
    This function:
    1. Determines file type from extension
    2. Calls appropriate reader function
    3. Generates consistent metadata format
    4. Handles errors gracefully
    
    Args:
        file_path: Path to the document to process
        
    Returns:
        Tuple containing:
        - Extracted text content
        - Metadata dictionary with source, type, path, and page info
        
    Raises:
        ValueError: If file type is not supported
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)
    doc_path = os.path.abspath(file_path)
    
    try:
        if file_extension == '.pdf':
            text, page_metadata = read_pdf(file_path)
            doc_type = 'pdf'
        elif file_extension == '.docx':
            text, page_metadata = read_docx(file_path)
            doc_type = 'docx'
        elif file_extension == '.xlsx':
            text, page_metadata = read_excel(file_path)
            doc_type = 'excel'
        elif file_extension == '.csv':
            text, page_metadata = read_csv(file_path)
            doc_type = 'csv'
        elif file_extension == '.txt':
            text, page_metadata = read_txt(file_path)
            doc_type = 'txt'
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Combine document metadata with page metadata
        metadata = {
            "source": file_name,
            "doc_type": doc_type,
            "path": doc_path
        }
        
        # If we have page metadata, update the metadata
        if page_metadata and page_metadata[0]:
            metadata.update(page_metadata[0])
        
        return text, metadata
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        return "", {}

def chunk_text(text: str, metadata: Dict[str, Any], chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[tuple[str, Dict[str, Any]]]:
    """Split text into chunks with metadata.
    
    Uses LangChain's RecursiveCharacterTextSplitter to:
    1. Split text into manageable chunks
    2. Maintain context with overlap
    3. Preserve metadata for each chunk
    
    Args:
        text: Text content to split
        metadata: Document metadata to attach to chunks
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of tuples containing:
        - Text chunk
        - Chunk metadata
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunks = text_splitter.split_text(text)
    chunk_metadata = []
    
    for chunk in chunks:
        chunk_meta = metadata.copy()
        chunk_metadata.append((chunk, chunk_meta))
    
    return chunk_metadata

def should_process_file(file_name: str) -> bool:
    """Check if the file should be processed.
    
    Filters files based on:
    1. Hidden files (starting with .)
    2. Supported file extensions
    
    Args:
        file_name: Name of the file to check
        
    Returns:
        Boolean indicating if file should be processed
    """
    # Skip hidden files (starting with .)
    if file_name.startswith('.'):
        return False
    
    # Get the file extension
    file_extension = os.path.splitext(file_name)[1].lower()
    
    # List of supported extensions
    supported_extensions = ['.pdf', '.docx', '.xlsx', '.csv', '.txt']
    
    return file_extension in supported_extensions

def main():
    """Main function to update the vector database."""
    logger.info("\n=== Starting Database Update Process ===")
    
    # Load settings from settings manager
    settings_manager = SettingsManager()
    settings = settings_manager.get_all_settings()
    
    # Use settings for configuration values
    chroma_db_dir = CHROMA_DB_DIR  # This comes from environment variable
    ollama_base_url = settings.get('ollama_base_url', OLLAMA_BASE_URL)
    embedding_model = settings.get('embedding_model', EMBEDDING_MODEL)
    chunk_size = settings.get('chunk_size', CHUNK_SIZE)
    chunk_overlap = settings.get('chunk_overlap', CHUNK_OVERLAP)
    
    # Initialize ChromaDB with standardized settings
    logger.info("Initializing ChromaDB...")
    chroma_client = create_chroma_client_for_update(chroma_db_dir)
    
    # Initialize Ollama embeddings
    logger.info(f"Initializing Ollama embeddings with model: {embedding_model}")
    embeddings = OllamaEmbeddings(
        base_url=ollama_base_url,
        model=embedding_model
    )
    
    # Get or create collection
    try:
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        logger.info(f"Found existing collection: {COLLECTION_NAME}")
        
        # ALWAYS clear existing documents first for a proper refresh
        try:
            existing_data = collection.get()
            if existing_data['ids']:
                logger.info(f"Clearing {len(existing_data['ids'])} existing documents...")
                collection.delete(ids=existing_data['ids'])
                logger.info("Successfully cleared existing documents")
            else:
                logger.info("No existing documents to clear")
        except Exception as e:
            logger.warning(f"Warning when clearing existing documents: {str(e)}")
            # If clearing fails, try to delete and recreate the collection
            try:
                logger.info("Attempting to delete and recreate collection...")
                chroma_client.delete_collection(name=COLLECTION_NAME)
                collection = chroma_client.create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("Successfully recreated collection")
            except Exception as recreate_error:
                logger.error(f"Failed to recreate collection: {str(recreate_error)}")
                raise
                
    except (ValueError, chromadb.errors.InvalidCollectionException):
        collection = chroma_client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Created new collection: {COLLECTION_NAME}")
    
    # Process all documents in the knowledge base directory
    documents = []
    metadatas = []
    ids = []
    doc_id = 0
    
    logger.info("\nScanning knowledge base directory...")
    files_to_process = [f for f in os.listdir(KNOWLEDGE_BASE_DIR) if should_process_file(f)]
    logger.info(f"Found {len(files_to_process)} files to process")
    
    for file_name in files_to_process:
        file_path = os.path.join(KNOWLEDGE_BASE_DIR, file_name)
        if os.path.isfile(file_path):
            logger.info(f"\nProcessing {file_name}...")
            text, metadata = process_document(file_path)
            
            if text and metadata:
                logger.info(f"Chunking text from {file_name}...")
                chunks = chunk_text(text, metadata, chunk_size, chunk_overlap)
                for chunk, chunk_metadata in chunks:
                    documents.append(chunk)
                    metadatas.append(chunk_metadata)
                    ids.append(f"doc_{doc_id}")
                    doc_id += 1
                logger.info(f"Created {len(chunks)} chunks from {file_name}")
            else:
                logger.warning(f"No content extracted from {file_name}")
    
    if documents:
        logger.info(f"\nGenerating embeddings for {len(documents)} chunks...")
        embeddings_list = embeddings.embed_documents(documents)
        
        logger.info("Adding new documents to the database...")
        collection.add(
            embeddings=embeddings_list,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"\n=== Successfully processed {len(documents)} chunks from {len(files_to_process)} files ===")
    else:
        logger.info("\n=== No documents found in the knowledge base directory ===")
        logger.info("Database is now empty and ready for new documents")
    
    # Properly close the ChromaDB client
    try:
        if hasattr(chroma_client, 'close'):
            chroma_client.close()
        logger.info("ChromaDB client closed successfully")
    except Exception as e:
        logger.warning(f"Warning while closing ChromaDB client: {e}")
    
    logger.info("=== Database Update Process Completed ===\n")

if __name__ == "__main__":
    main() 