"""
FastAPI Backend for RAG Chatbot

This module provides REST API endpoints for the RAG chatbot functionality.
It handles chat interactions, file uploads, and database management.

Key Features:
- Chat Interface: Processes user messages using RAG (Retrieval Augmented Generation)
- Document Management: Handles file uploads and processing for the knowledge base
- Vector Database: Manages ChromaDB for efficient document retrieval
- Settings Management: Provides dynamic configuration of LLM and embedding models
- Memory Management: Maintains conversation context
- Streaming Support: Enables real-time chat responses

Dependencies:
- FastAPI: Web framework for building APIs
- ChromaDB: Vector database for document storage
- Langchain: Framework for LLM applications
- Ollama: Local LLM integration
- Pydantic: Data validation using Python type annotations

Environment Setup:
- Requires Ollama running locally or at specified OLLAMA_BASE_URL
- Requires ChromaDB for vector storage
- Requires appropriate file processing libraries based on document types
"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

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

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os
import shutil
from typing import List, Dict, Any
import chromadb
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.memory import ConversationBufferMemory
import configuration
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
import requests
import signal
import asyncio
from ollama import AsyncClient  # Add this import at the top
from datetime import datetime

# Import local modules
from configuration import *
from update_database import process_document, chunk_text
from settings_manager import SettingsManager

# Initialize settings manager
settings_manager = SettingsManager()

# Initialize FastAPI app
app = FastAPI(title="RAG Chatbot API")

def format_context(chunks: list, metadatas: list) -> str:
    """Format retrieved chunks with their source citations.
    
    This function takes the raw document chunks and their metadata and formats them
    into a string that can be used in the LLM prompt. Each chunk is prefixed with
    its source citation.
    
    Args:
        chunks: List of text chunks retrieved from the vector store
        metadatas: List of metadata for each chunk (source, page numbers, etc.)
    
    Returns:
        Formatted string with chunks and their citations for the LLM prompt
    
    Example:
        >>> chunks = ["Some text", "More text"]
        >>> metadatas = [{"source": "doc1.pdf"}, {"source": "doc2.pdf"}]
        >>> print(format_context(chunks, metadatas))
        [Source: doc1.pdf]:
        Some text

        [Source: doc2.pdf]:
        More text
    """
    formatted_chunks = []
    
    for chunk, meta in zip(chunks, metadatas):
        citation = f"[Source: {meta['source']}]"
        formatted_chunks.append(f"{citation}:\n{chunk}")
    
    return "\n\n".join(formatted_chunks)

def generate_prompt(query: str, context: str = "", memory: ConversationBufferMemory = None) -> str:
    """Generate the prompt for the LLM with context and conversation history.
    
    This function constructs the prompt that will be sent to the LLM. It includes:
    - System instructions for the AI's role and response format
    - Retrieved context with citations (if available)
    - Conversation history for context (if available)
    - The user's current question
    """
    # Handle case when no relevant context is found
    if not context:
        return f"""You are a helpful AI assistant. The user asked: "{query}"

Since no documents are currently available in the knowledge base, I cannot provide specific information from uploaded documents. 

Please respond with: "I don't have access to any documents in the knowledge base at the moment. To get started, please upload some documents using the 'Upload File' button in the sidebar, then click 'Refresh Database' to process them. Once documents are available, I'll be able to answer questions based on their content."

Keep the response exactly as specified, without any additional text or citations."""
    
    # Include conversation history if available
    chat_history = ""
    if memory:
        history = memory.load_memory_variables({})
        if "history" in history and history["history"]:
            # Format the chat history to be more explicit
            messages = history["history"]
            formatted_history = []
            for i in range(0, len(messages), 2):
                if i + 1 < len(messages):
                    user_msg = messages[i].content
                    assistant_msg = messages[i + 1].content
                    formatted_history.append(f"User: {user_msg}\nAssistant: {assistant_msg}")
            chat_history = "\nPrevious conversation:\n" + "\n\n".join(formatted_history)
    
     # Main prompt template with context and citation instructions
        return f"""You are a helpful geologist researcher. You have access to the following:

        1. Previous Conversation History:
        {chat_history}

        2. Relevant Document Excerpts:
        {context}

        Current Question: {query}

        Instructions:
        1. Use the provided document excerpts to answer the question.
        2. If the question is about previous conversation, refer to the conversation history.
        3. Always cite your sources when applicable using [Source: filename] format.
        4. If you don't know or can't find the answer in the provided document excerpts, say so.
        5. Keep track of the conversation context when answering follow-up questions.
        6. Do not give answer in markdown format.
        7. If the question cannot be answered using the provided document excerpts, state that you cannot find the answer in the documents and do not provide an answer from your general knowledge.
        8. Your answer must be solely based on the 'Relevant Document Excerpts'. Do not use any external or prior knowledge.


        Answer Format:
        1. Detailed technical answer with inline citations when applicable

        Answer: """

def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    # Clean up any resources
    if chroma_client:
        try:
            chroma_client.close()
        except:
            pass
    print("Shutdown complete")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

def create_chroma_client():
    """
    Create a ChromaDB client with standardized settings.
    
    Returns:
        chromadb.PersistentClient: Configured ChromaDB client
    """
    import chromadb.config
    return chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR),
        settings=chromadb.config.Settings(
            allow_reset=True,
            anonymized_telemetry=False,
            is_persistent=True
        )
    )

# Initialize ChromaDB with standardized settings
chroma_client = create_chroma_client()

# Global variables for clients
embeddings = None
llm = None
text_splitter = None

# Runtime configuration variables (loaded from settings manager)
runtime_config = settings_manager.get_all_settings()

class ChatMessage(BaseModel):
    """
    Pydantic model for incoming chat messages.
    
    Attributes:
        message (str): The user's chat message
    """
    message: str

class ChatResponse(BaseModel):
    """
    Pydantic model for chat response including sources.
    
    Attributes:
        answer (str): The AI-generated response
        sources (List[Dict[str, Any]]): List of source documents used for the response
    """
    answer: str
    sources: List[Dict[str, Any]]

class FileInfo(BaseModel):
    """
    Pydantic model for file metadata.
    
    Attributes:
        name (str): Name of the file
        size (int): Size of the file in bytes
        type (str): File extension/type (e.g., PDF, TXT)
    """
    name: str
    size: int
    type: str

class Settings(BaseModel):
    """
    Pydantic model for configurable settings.
    
    Attributes:
        ollama_base_url (str | None): Base URL for Ollama API
        llm_model (str | None): Name of the LLM model to use
        embedding_model (str | None): Name of the embedding model
        chunk_size (int | None): Size of text chunks for processing
        chunk_overlap (int | None): Overlap between text chunks
        top_k_chunks (int | None): Number of chunks to retrieve
    """
    ollama_base_url: str | None = None
    llm_model: str | None = None
    embedding_model: str | None = None
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    top_k_chunks: int | None = None

class SessionMemoryManager:
    def __init__(self):
        self.memory = ConversationBufferMemory(return_messages=True)
        logger.info("Initialized session-only memory manager (no persistence)")
    
    def save_context(self, input_text: str, output_text: str):
        """Save context in memory only"""
        self.memory.save_context({"input": input_text}, {"output": output_text})
    
    def load_memory_variables(self, inputs: dict) -> dict:
        """Load memory variables"""
        return self.memory.load_memory_variables(inputs)
    
    def clear(self):
        """Clear memory for new session"""
        self.memory.clear()
        logger.info("Conversation memory cleared")

# Initialize memory manager
memory_manager = SessionMemoryManager()

def initialize_clients():
    """
    Initialize or reinitialize Ollama clients with current settings.
    
    This function sets up:
    - Embedding model for document vectorization
    - LLM model for generating responses
    - Text splitter for document chunking
    
    Returns:
        bool: True if initialization successful, False otherwise
    
    Raises:
        Exception: If unable to connect to Ollama or initialize components
    """
    global embeddings, llm, text_splitter, runtime_config
    logger.info("Initializing clients...")
    try:
        # Reload runtime config from settings manager
        runtime_config = settings_manager.get_all_settings()
        
        logger.info(f"Setting up embedding model: {runtime_config['embedding_model']}")
        embeddings = OllamaEmbeddings(
            base_url=runtime_config['ollama_base_url'],
            model=runtime_config['embedding_model']
        )
        
        logger.info(f"Setting up LLM model: {runtime_config['llm_model']}")
        llm = OllamaLLM(
            base_url=runtime_config['ollama_base_url'],
            model=runtime_config['llm_model']
        )
        
        logger.info(f"Setting up text splitter (chunk_size: {runtime_config['chunk_size']}, overlap: {runtime_config['chunk_overlap']})")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=runtime_config['chunk_size'],
            chunk_overlap=runtime_config['chunk_overlap']
        )
        
        # Test basic connectivity
        logger.info("Testing Ollama connectivity...")
        response = requests.get(f"{runtime_config['ollama_base_url']}/api/version")
        if response.status_code != 200:
            raise Exception("Failed to connect to Ollama")
        
        logger.info("All clients initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing clients: {str(e)}")
        return False

# Initialize clients at startup
logger.info("Starting application initialization...")
if not initialize_clients():
    logger.error("Failed to initialize clients at startup!")
    sys.exit(1)
logger.info("Application initialization completed successfully")

@app.get("/settings")
async def get_settings():
    """Get current settings"""
    global runtime_config
    runtime_config = settings_manager.get_all_settings()
    
    logger.info("\n=== Current Settings ===")
    logger.info(f"Ollama Base URL: {runtime_config['ollama_base_url']}")
    logger.info(f"LLM Model: {runtime_config['llm_model']}")
    logger.info(f"Embedding Model: {runtime_config['embedding_model']}")
    logger.info(f"Chunk Size: {runtime_config['chunk_size']}")
    logger.info(f"Chunk Overlap: {runtime_config['chunk_overlap']}")
    logger.info(f"Top K Chunks: {runtime_config['top_k_chunks']}")
    return runtime_config

@app.post("/settings")
async def update_settings(settings: Settings):
    """Update settings dynamically and persist to JSON file"""
    try:
        logger.info("\n=== Updating Settings ===")
        
        # Build settings dictionary from provided values
        new_settings = {}
        if settings.ollama_base_url is not None:
            new_settings['ollama_base_url'] = settings.ollama_base_url
            logger.info(f"Ollama Base URL -> {settings.ollama_base_url}")
        if settings.llm_model is not None:
            new_settings['llm_model'] = settings.llm_model
            logger.info(f"LLM Model -> {settings.llm_model}")
        if settings.embedding_model is not None:
            new_settings['embedding_model'] = settings.embedding_model
            logger.info(f"Embedding Model -> {settings.embedding_model}")
        if settings.chunk_size is not None:
            new_settings['chunk_size'] = settings.chunk_size
            logger.info(f"Chunk Size -> {settings.chunk_size}")
        if settings.chunk_overlap is not None:
            new_settings['chunk_overlap'] = settings.chunk_overlap
            logger.info(f"Chunk Overlap -> {settings.chunk_overlap}")
        if settings.top_k_chunks is not None:
            new_settings['top_k_chunks'] = settings.top_k_chunks
            logger.info(f"Top K Chunks -> {settings.top_k_chunks}")

        # Validate models exist before saving (if models were changed)
        if 'llm_model' in new_settings or 'embedding_model' in new_settings:
            try:
                # Test connection to Ollama
                test_url = new_settings.get('ollama_base_url', runtime_config['ollama_base_url'])
                models_url = f"{test_url}/api/tags"
                
                import requests
                response = requests.get(models_url, timeout=5)
                if response.status_code == 200:
                    available_models = [model['name'] for model in response.json().get('models', [])]
                    
                    # Check if specified models exist
                    if 'llm_model' in new_settings and new_settings['llm_model'] not in available_models:
                        raise HTTPException(
                            status_code=404, 
                            detail=f"LLM model '{new_settings['llm_model']}' not found. Available models: {', '.join(available_models)}"
                        )
                    
                    if 'embedding_model' in new_settings and new_settings['embedding_model'] not in available_models:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Embedding model '{new_settings['embedding_model']}' not found. Available models: {', '.join(available_models)}"
                        )
                else:
                    logger.warning("Could not validate models - Ollama may not be running")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Could not connect to Ollama to validate models: {e}")

        # Save settings using settings manager
        if not settings_manager.save_settings(new_settings):
            raise HTTPException(status_code=500, detail="Failed to save settings")

        logger.info("Settings saved to JSON file")

        # Reinitialize clients with new settings
        if not initialize_clients():
            raise HTTPException(status_code=500, detail="Failed to initialize clients with new settings")

        return await get_settings()
        
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")

@app.get("/files/search")
async def search_files(query: str = ""):
    """
    Search for files in the knowledge base.
    """
    try:
        files = []
        for file in os.listdir(KNOWLEDGE_BASE_DIR):
            if query.lower() in file.lower():
                file_path = os.path.join(KNOWLEDGE_BASE_DIR, file)
                file_info = FileInfo(
                    name=file,
                    size=os.path.getsize(file_path),
                    type=os.path.splitext(file)[1][1:].upper()
                )
                files.append(file_info)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message and return the AI response with sources.
    
    The function performs the following steps:
    1. Ensures models are initialized
    2. Retrieves relevant documents from ChromaDB
    3. Generates embeddings for the query
    4. Uses LLM to generate a response based on context
    
    Args:
        message (ChatMessage): The user's input message
        
    Returns:
        ChatResponse: AI response with relevant source documents
        
    Raises:
        HTTPException: If model initialization fails or processing error occurs
    """
    try:
        # Ensure models are initialized
        if embeddings is None or llm is None:
            print("Models not initialized, attempting to initialize...")
            if not initialize_clients():
                raise HTTPException(status_code=500, detail="Failed to initialize models")
        
        # Check if collection exists and has documents
        try:
            collection = chroma_client.get_collection(name=COLLECTION_NAME)
            # Check if collection has any documents
            collection_data = collection.get()
            has_documents = len(collection_data['ids']) > 0 if collection_data['ids'] else False
        except (ValueError, chromadb.errors.InvalidCollectionException):
            # Collection doesn't exist - database is empty
            has_documents = False
            collection = None
        
        # Generate response based on retrieved context
        if not has_documents or not collection:
            # No documents in database
            prompt = generate_prompt(message.message, "", memory_manager.memory)
            response = llm.invoke(prompt)
            sources = []
        else:
            # Generate embedding for user query
            query_embedding = embeddings.embed_query(message.message)
            
            # Search for relevant document chunks
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=runtime_config['top_k_chunks']
            )
            
            if not results['documents'][0]:
                # No relevant documents found
                prompt = generate_prompt(message.message, "", memory_manager.memory)
                response = llm.invoke(prompt)
                sources = []
            else:
                # Found relevant documents
                context = format_context(results['documents'][0], results['metadatas'][0])
                prompt = generate_prompt(message.message, context, memory_manager.memory)
                response = llm.invoke(prompt)
                sources = [
                    {"content": doc, "metadata": meta}
                    for doc, meta in zip(results['documents'][0], results['metadatas'][0])
                ]
        
        # Use memory manager to save context
        memory_manager.save_context(message.message, response)
        
        return ChatResponse(answer=response, sources=sources)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(message: ChatMessage):
    """
    Process a chat message and stream the AI response with sources.
    
    This endpoint provides real-time streaming of:
    1. Source documents being used for the response
    2. Token-by-token generation of the AI response
    3. Completion status
    
    Args:
        message (ChatMessage): The user's input message
        
    Returns:
        StreamingResponse: Server-sent events stream containing:
            - sources: List of relevant documents
            - tokens: Individual response tokens
            - done: Completion signal
            
    Raises:
        HTTPException: If model initialization fails or processing error occurs
    """
    try:
        # Ensure models are initialized
        if embeddings is None or llm is None:
            print("Models not initialized, attempting to initialize...")
            if not initialize_clients():
                raise HTTPException(status_code=500, detail="Failed to initialize models")
        
        # Check if collection exists and has documents
        try:
            collection = chroma_client.get_collection(name=COLLECTION_NAME)
            # Check if collection has any documents
            collection_data = collection.get()
            has_documents = len(collection_data['ids']) > 0 if collection_data['ids'] else False
        except (ValueError, chromadb.errors.InvalidCollectionException):
            # Collection doesn't exist - database is empty
            has_documents = False
            collection = None
        
        async def generate_stream():
            try:
                full_response = ""
                first_token_sent = False
                
                if has_documents and collection:
                    # Database has documents - proceed with normal RAG flow
                    print(f"Generating embeddings using {runtime_config['embedding_model']}")
                    query_embedding = embeddings.embed_query(message.message)
                    
                    # Search for relevant documents
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=runtime_config['top_k_chunks']
                    )
                    
                    if results['documents'][0]:
                        # Format context and generate response
                        context = format_context(results['documents'][0], results['metadatas'][0])
                        prompt = generate_prompt(message.message, context, memory_manager.memory)
                        print("Making request to Ollama...")
                        
                        # Process and send sources first
                        print("Debug - Metadata:", results['metadatas'][0])  # Debug log
                        unique_files = {}  # Changed from set to dict to store both name and path
                        for source in results['metadatas'][0]:
                            print("Debug - Source object:", source)  # Debug log
                            if 'source' in source and 'path' in source:
                                unique_files[source['source']] = source['path']
                        
                        # Send sources as array of Source objects with both name and path
                        sources_list = [{"source": file, "path": path} for file, path in sorted(unique_files.items())]
                        print("Debug - Sources list:", sources_list)  # Debug log
                        yield f"data: {json.dumps({'type': 'sources', 'sources': sources_list})}\n\n"
                    else:
                        # No relevant documents found
                        prompt = generate_prompt(message.message, "", memory_manager.memory)
                        yield f"data: {json.dumps({'type': 'sources', 'sources': []})}\n\n"
                else:
                    # No documents in database
                    prompt = generate_prompt(message.message, "", memory_manager.memory)
                    yield f"data: {json.dumps({'type': 'sources', 'sources': []})}\n\n"
                
                # Generate response using Ollama
                client = AsyncClient(host=runtime_config['ollama_base_url'].replace('http://', ''))
                async for chunk in await client.generate(
                    model=runtime_config['llm_model'],
                    prompt=prompt,
                    stream=True
                ):
                    if chunk.response:
                        full_response += chunk.response
                        if not first_token_sent:
                            first_token_sent = True
                            yield f"data: {json.dumps({'type': 'token', 'content': chunk.response})}\n\n"
                        else:
                            yield f"data: {json.dumps({'type': 'token', 'content': chunk.response})}\n\n"
                        await asyncio.sleep(0)
                
                # Save to memory manager after complete response
                memory_manager.save_context(message.message, full_response)
                
                # Send done signal
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    
            except Exception as e:
                print(f"Error in stream generation: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        print(f"Error in chat stream endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a new document for the knowledge base.
    
    Processing steps:
    1. Saves uploaded file to knowledge base directory
    2. Extracts and processes text content
    3. Chunks the text and generates embeddings
    4. Stores document chunks in ChromaDB
    
    Args:
        file (UploadFile): The file to be uploaded and processed
        
    Returns:
        dict: Success message with processing details
        
    Raises:
        HTTPException: If file processing fails or database operation fails
    """
    global chroma_client
    try:
        logger.info(f"Starting upload process for file: {file.filename}")
        
        # Ensure models are initialized
        if embeddings is None or llm is None:
            logger.info("Models not initialized, attempting to initialize...")
            if not initialize_clients():
                raise HTTPException(status_code=500, detail="Failed to initialize models")
        
        # Always create a fresh ChromaDB client for upload operations to avoid readonly database issues
        logger.info("Creating fresh ChromaDB client for upload...")
        upload_client = create_chroma_client()
        
        # Create knowledge base directory if it doesn't exist
        os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(KNOWLEDGE_BASE_DIR, file.filename)
        logger.info(f"Saving file to: {file_path}")
        logger.info(f"Knowledge base directory: {KNOWLEDGE_BASE_DIR}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved to: {file_path}")
        logger.info(f"File exists after save: {os.path.exists(file_path)}")
        logger.info(f"File size: {os.path.getsize(file_path) if os.path.exists(file_path) else 'N/A'}")
        
        # Process the document
        logger.info(f"Processing document: {file.filename}")
        text, metadata = process_document(file_path)
        if not text:
            raise HTTPException(status_code=400, detail=f"Could not extract text from {file.filename}")
        
        logger.info(f"Extracted {len(text)} characters from {file.filename}")
        
        # Get or create collection with retry logic using fresh client
        collection = None
        max_retries = 3
        for attempt in range(max_retries):
            try:
                collection = upload_client.get_collection(name=COLLECTION_NAME)
                logger.info(f"Using existing collection: {COLLECTION_NAME}")
                break
            except (ValueError, chromadb.errors.InvalidCollectionException):
                try:
                    collection = upload_client.create_collection(
                        name=COLLECTION_NAME,
                        metadata={"hnsw:space": "cosine"}
                    )
                    logger.info(f"Created new collection: {COLLECTION_NAME}")
                    break
                except Exception as create_error:
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} to create collection failed: {create_error}")
                    if attempt == max_retries - 1:
                        # Try to reinitialize the client as a last resort
                        logger.info("Reinitializing ChromaDB client as final attempt...")
                        upload_client = create_chroma_client()
                        collection = upload_client.create_collection(
                            name=COLLECTION_NAME,
                            metadata={"hnsw:space": "cosine"}
                        )
                        logger.info(f"Successfully created collection after client reinit: {COLLECTION_NAME}")
                        break
                    import time
                    time.sleep(0.5)  # Brief pause before retry
        
        # Process chunks and generate embeddings
        logger.info(f"Chunking text from {file.filename}")
        chunks = chunk_text(text, metadata)
        documents = []
        metadatas = []
        ids = []
        
        for i, (chunk, chunk_metadata) in enumerate(chunks):
            documents.append(chunk)
            metadatas.append(chunk_metadata)
            ids.append(f"doc_{file.filename}_{i}")
        
        logger.info(f"Created {len(chunks)} chunks from {file.filename}")
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(documents)} chunks")
        embeddings_list = embeddings.embed_documents(documents)
        
        # Add to collection
        logger.info(f"Adding {len(documents)} chunks to database")
        collection.add(
            embeddings=embeddings_list,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully processed {file.filename}")
        
        # Clean up the upload client
        try:
            if hasattr(upload_client, 'close'):
                upload_client.close()
            logger.info("Upload client closed successfully")
        except Exception as cleanup_error:
            logger.warning(f"Warning while closing upload client: {cleanup_error}")
        
        # Update the global client to maintain consistency
        chroma_client = create_chroma_client()
        
        return {
            "message": f"File '{file.filename}' processed successfully",
            "details": {
                "filename": file.filename,
                "file_size": os.path.getsize(file_path),
                "text_length": len(text),
                "chunks_created": len(chunks),
                "embeddings_generated": len(embeddings_list)
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {str(e)}")
        # Clean up the upload client on error too
        try:
            if 'upload_client' in locals() and hasattr(upload_client, 'close'):
                upload_client.close()
        except Exception as cleanup_error:
            logger.warning(f"Warning while cleaning up upload client after error: {cleanup_error}")
        raise HTTPException(status_code=500, detail=f"Failed to process {file.filename}: {str(e)}")

@app.post("/refresh")
async def refresh_database():
    """
    Refresh the vector database with all documents in the knowledge base.
    
    This operation:
    1. Closes existing ChromaDB connection
    2. Reprocesses all documents in the knowledge base
    3. Reinitializes clients with current settings
    
    Returns:
        dict: Success message if refresh completed
        
    Raises:
        HTTPException: If database refresh fails or client reinitialization fails
    """
    try:
        global chroma_client
        logger.info("\n=== Starting Database Refresh ===")
        logger.info("Current Settings:")
        logger.info(f"- Embedding Model: {runtime_config['embedding_model']}")
        logger.info(f"- Chunk Size: {runtime_config['chunk_size']}")
        logger.info(f"- Chunk Overlap: {runtime_config['chunk_overlap']}")
        
        # Close existing client with proper cleanup
        if chroma_client:
            try:
                logger.info("Closing existing ChromaDB client...")
                # Properly close the client if it has a close method
                if hasattr(chroma_client, 'close'):
                    chroma_client.close()
                # Reset the client with allow_reset=True
                if hasattr(chroma_client, 'reset'):
                    chroma_client.reset()
            except Exception as e:
                logger.warning(f"Warning while closing ChromaDB client: {e}")
            finally:
                # Delete the client reference completely
                chroma_client = None
        
        # Import garbage collection to ensure cleanup
        import gc
        import time
        gc.collect()  # Force garbage collection
        time.sleep(1.0)  # Allow more time for cleanup
        
        # Import and run the update_database main function directly
        logger.info("Starting database update process...")
        from update_database import main
        main()
        
        logger.info("Database update completed, reinitializing clients...")
        # Reinitialize ChromaDB client with standardized settings
        chroma_client = create_chroma_client()
        
        # Reinitialize other clients to ensure they're using the latest settings
        logger.info("Reinitializing Ollama clients...")
        if not initialize_clients():
            logger.error("Failed to initialize clients after refresh!")
            raise HTTPException(status_code=500, detail="Failed to initialize clients after refresh")
        
        logger.info("=== Database Refresh Completed Successfully ===\n")
        return {"message": "Database refreshed successfully"}
    except Exception as e:
        logger.error(f"Error refreshing database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{filename}")
async def get_file(filename: str):
    """
    Serve a file from the knowledge base.
    
    Features:
    - Content type detection based on file extension
    - Browser-compatible content disposition
    - Support for various document types (PDF, TXT, CSV, etc.)
    
    Args:
        filename (str): Name of the file to retrieve
        
    Returns:
        FileResponse: File content with appropriate content type
        
    Raises:
        HTTPException: If file not found or access error occurs
    """
    try:
        # URL decode the filename in case it's encoded
        from urllib.parse import unquote
        decoded_filename = unquote(filename)
        logger.info(f"Original filename: {filename}")
        logger.info(f"Decoded filename: {decoded_filename}")
        
        file_path = os.path.join(KNOWLEDGE_BASE_DIR, decoded_filename)
        logger.info(f"Looking for file: {file_path}")
        logger.info(f"Knowledge base directory: {KNOWLEDGE_BASE_DIR}")
        logger.info(f"Directory exists: {os.path.exists(KNOWLEDGE_BASE_DIR)}")
        
        if os.path.exists(KNOWLEDGE_BASE_DIR):
            files_in_dir = os.listdir(KNOWLEDGE_BASE_DIR)
            logger.info(f"Files in knowledge base: {files_in_dir}")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {decoded_filename}. Looking in: {KNOWLEDGE_BASE_DIR}")
        
        # Get the file extension
        file_extension = os.path.splitext(decoded_filename)[1].lower()
        
        # Set content type based on file extension
        content_type = None
        if file_extension == '.pdf':
            content_type = 'application/pdf'
        elif file_extension == '.txt':
            content_type = 'text/plain'
        elif file_extension == '.csv':
            content_type = 'text/csv'
        elif file_extension in ['.doc', '.docx']:
            content_type = 'application/msword'
        elif file_extension in ['.xls', '.xlsx']:
            content_type = 'application/vnd.ms-excel'
        else:
            content_type = 'application/octet-stream'
            
        # Use FileResponse with content_disposition_type="inline" to open in browser
        return FileResponse(
            file_path,
            filename=decoded_filename,
            media_type=content_type,
            content_disposition_type="inline"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-memory")
async def clear_memory():
    """
    Clear the conversation memory to start a new chat session.
    """
    try:
        memory_manager.clear()
        return {"message": "Conversation memory cleared and new session started"}
    except Exception as e:
        logger.error(f"Error clearing memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-database")
async def clear_database():
    """
    Clear the entire vector database and remove all source documents.
    This will remove all document embeddings, metadata, and source files.
    """
    try:
        global chroma_client
        logger.info("=== Starting Complete Database Clear Process ===")
        
        # Close existing client with proper cleanup
        if chroma_client:
            try:
                logger.info("Closing existing ChromaDB client...")
                # Properly close the client if it has a close method
                if hasattr(chroma_client, 'close'):
                    chroma_client.close()
                # Reset the client with allow_reset=True
                if hasattr(chroma_client, 'reset'):
                    chroma_client.reset()
            except Exception as e:
                logger.warning(f"Warning while closing ChromaDB client: {e}")
            finally:
                # Delete the client reference completely
                chroma_client = None
        
        # Import garbage collection to ensure cleanup
        import gc
        import time
        gc.collect()  # Force garbage collection
        time.sleep(2.0)  # Allow more time for cleanup - increased from 1.0 to 2.0
        
        # Delete all collections
        try:
            temp_client = create_chroma_client()
            
            # Get all collections and delete them
            collections = temp_client.list_collections()
            logger.info(f"Found {len(collections)} collections to delete")
            
            for collection in collections:
                try:
                    collection_name = collection.name if hasattr(collection, 'name') else str(collection)
                    temp_client.delete_collection(name=collection_name)
                    logger.info(f"Successfully deleted collection: {collection_name}")
                except Exception as e:
                    logger.warning(f"Error deleting collection {collection}: {str(e)}")
            
            # Properly close the temporary client
            if hasattr(temp_client, 'close'):
                temp_client.close()
        except Exception as e:
            logger.warning(f"Error during collection cleanup: {str(e)}")
        
        # Clear all files from knowledge base directory
        try:
            logger.info("Clearing all files from knowledge base directory...")
            for filename in os.listdir(KNOWLEDGE_BASE_DIR):
                file_path = os.path.join(KNOWLEDGE_BASE_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file: {filename}")
            logger.info("Successfully cleared all source documents")
        except Exception as e:
            logger.warning(f"Warning when clearing source documents: {str(e)}")
        
        # Clean up ChromaDB data directories (but NOT the SQLite file)
        try:
            logger.info("Cleaning up ChromaDB data directories...")
            import shutil
            
            # Remove UUID directories only - let ChromaDB manage its own SQLite file
            for item in os.listdir(CHROMA_DB_DIR):
                item_path = os.path.join(CHROMA_DB_DIR, item)
                if os.path.isdir(item_path) and len(item) == 36:  # UUID directories
                    shutil.rmtree(item_path)
                    logger.info(f"Removed UUID directory: {item}")
            
            # DO NOT delete the SQLite file - this causes readonly database errors
            # ChromaDB will handle its own database file management
            logger.info("Skipping SQLite file deletion to prevent readonly database errors")
                
        except Exception as e:
            logger.warning(f"Warning when cleaning ChromaDB directories: {str(e)}")
        
        # Additional cleanup before reinitialization
        gc.collect()  # Another garbage collection
        time.sleep(1.0)  # Additional delay
        
        # Reinitialize ChromaDB client with standardized settings
        logger.info("Creating fresh ChromaDB client...")
        chroma_client = create_chroma_client()
        logger.info("ChromaDB client reinitialized successfully")
        
        # Reinitialize other clients
        logger.info("Reinitializing Ollama clients...")
        if not initialize_clients():
            logger.error("Failed to initialize clients after clear!")
            raise HTTPException(status_code=500, detail="Failed to initialize clients after clear")
        
        logger.info("=== Complete Database Clear Completed Successfully ===")
        return {"message": "Database and source documents cleared successfully. All documents, embeddings, and source files have been removed."}
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Docker and monitoring.
    
    Returns:
        dict: Status indicating service health
    """
    return {"status": "healthy"}

# Initialize on startup
print("\nStarting server...")
if not initialize_clients():
    print("Warning: Failed to initialize clients on startup")
else:
    print("Server ready to handle requests")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 