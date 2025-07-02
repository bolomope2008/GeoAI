## GeoAI Backend Documentation

### Overview

The GeoAI backend is a robust FastAPI application designed to power a Retrieval Augmented Generation (RAG) chatbot. It leverages local Large Language Models (LLMs) and embedding models via Ollama, and utilizes ChromaDB for efficient document retrieval. This backend facilitates intelligent conversations by grounding LLM responses in a user-managed knowledge base of documents.

### Technologies Used

*   **FastAPI**: High-performance web framework for building APIs.
*   **Ollama**: Runs open-source LLMs and embedding models locally.
*   **ChromaDB**: An open-source embedding database (vector store) for storing and querying document embeddings.
*   **LangChain**: Framework for developing applications powered by language models, used here for memory management and text splitting.
*   **Pydantic**: Data validation and settings management using Python type hints.
*   **`pdfplumber`**: For extracting text from PDF documents.
*   **`python-docx`**: For extracting text from DOCX documents.
*   **`pandas`**: For extracting text from XLSX and CSV documents.

### Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd GeoAI_V2/backend
    ```
2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install Ollama:**
    Download and install Ollama from [ollama.com](https://ollama.com/).
4.  **Download Ollama Models:**
    Before running the backend, ensure you have the required LLM and embedding models downloaded via Ollama. The default models are `phi4:14b-fp16` for LLM and `nomic-embed-text` for embeddings. You can download them using the Ollama CLI:
    ```bash
    ollama pull phi4:14b-fp16
    ollama pull nomic-embed-text
    ```
    You can change these models in `backend/configuration.py` or dynamically via the `/settings` API endpoint.
5.  **Run the FastAPI application:**
    ```bash
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
    ```
    The API will be accessible at `http://localhost:8000`.

### Configuration

The `backend/configuration.py` file defines key settings for the application. These settings can be overridden by environment variables (useful for deployment, e.g., in Electron apps) or dynamically updated via the `/settings` API endpoint.

**Key Configuration Variables:**

*   `BASE_DIR`: Base directory of the backend.
*   `KNOWLEDGE_BASE_DIR`: Directory where source documents are stored (default: `backend/knowledge_base`). Can be set via `KNOWLEDGE_BASE_DIR` environment variable.
*   `CHROMA_DB_DIR`: Directory for ChromaDB's persistent data (default: `backend/chroma_db`). Can be set via `CHROMA_DB_DIR` environment variable.
*   `COLLECTION_NAME`: The name of the ChromaDB collection used for storing document embeddings (default: `"knowledge_base"`).
*   `OLLAMA_BASE_URL`: The URL of your running Ollama instance (default: `"http://localhost:11434"`).
*   `EMBEDDING_MODEL`: The Ollama model used for generating document embeddings (default: `"nomic-embed-text"`).
*   `LLM_MODEL`: The Ollama model used for generating chat responses (default: `"phi4:14b-fp16"`).
*   `CHUNK_SIZE`: The maximum size of text chunks when processing documents (default: `1500`).
*   `CHUNK_OVERLAP`: The overlap between text chunks to maintain context (default: `150`).
*   `TOP_K_CHUNKS`: The number of most relevant document chunks to retrieve for RAG (default: `10`).

### API Endpoints

All API endpoints are served from `http://localhost:8000` (or your configured host/port).

#### 1. Chat Endpoints

*   **`POST /chat`**
    *   **Description**: Processes a user chat message and returns an AI-generated response with sources.
    *   **Request Body**:
        ```json
        {
          "message": "string"
        }
        ```
    *   **Response Body**:
        ```json
        {
          "answer": "string",
          "sources": [
            {
              "content": "string",
              "metadata": {}
            }
          ]
        }
        ```
    *   **Error Handling**: Returns `500 Internal Server Error` if models are not initialized or an error occurs during processing.

*   **`POST /chat/stream`**
    *   **Description**: Processes a user chat message and streams the AI response token-by-token, along with sources. This endpoint uses Server-Sent Events (SSE).
    *   **Request Body**:
        ```json
        {
          "message": "string"
        }
        ```
    *   **Response Stream (SSE)**:
        *   `data: {"type": "sources", "sources": [{"source": "filename.pdf", "path": "/absolute/path/to/filename.pdf"}, ...]}`: Sent first, contains a list of source documents used.
        *   `data: {"type": "token", "content": "..."}`: Sent for each generated token of the AI response.
        *   `data: {"type": "done"}`: Sent when the AI response is complete.
        *   `data: {"type": "error", "error": "..."}`: Sent if an error occurs during streaming.
    *   **Error Handling**: Returns `500 Internal Server Error` if models are not initialized or an error occurs during processing.

#### 2. Document Management Endpoints

*   **`POST /upload`**
    *   **Description**: Uploads a document to the knowledge base, processes it (extracts text, chunks, embeds), and adds it to ChromaDB.
    *   **Request Body**: `multipart/form-data` with a `file` field.
    *   **Supported File Types**: PDF, DOCX, XLSX, CSV, TXT.
    *   **Response Body**:
        ```json
        {
          "message": "File 'filename.pdf' processed successfully",
          "details": {
            "filename": "filename.pdf",
            "file_size": 12345,
            "text_length": 54321,
            "chunks_created": 10,
            "embeddings_generated": 10
          }
        }
        ```
    *   **Error Handling**:
        *   `400 Bad Request`: If text extraction fails.
        *   `500 Internal Server Error`: If file processing or database operation fails.

*   **`POST /refresh`**
    *   **Description**: Clears the existing ChromaDB collection and reprocesses all documents found in the `knowledge_base` directory. This ensures the vector database is up-to-date with the latest documents and configuration settings.
    *   **Request Body**: None.
    *   **Response Body**:
        ```json
        {
          "message": "Database refreshed successfully"
        }
        ```
    *   **Error Handling**: Returns `500 Internal Server Error` if the refresh process or client reinitialization fails.

*   **`POST /clear-database`**
    *   **Description**: **CAUTION: This endpoint permanently deletes all document embeddings from ChromaDB and removes all source files from the `knowledge_base` directory.** Use with care.
    *   **Request Body**: None.
    *   **Response Body**:
        ```json
        {
          "message": "Database and source documents cleared successfully. All documents, embeddings, and source files have been removed."
        }
        ```
    *   **Error Handling**: Returns `500 Internal Server Error` if the clearing process encounters an issue.

*   **`GET /files/search`**
    *   **Description**: Searches for files within the `knowledge_base` directory based on a query string.
    *   **Query Parameters**:
        *   `query` (string, optional): The search string to filter filenames.
    *   **Response Body**:
        ```json
        {
          "files": [
            {
              "name": "example.pdf",
              "size": 12345,
              "type": "PDF"
            },
            {
              "name": "report.docx",
              "size": 67890,
              "type": "DOCX"
            }
          ]
        }
        ```
    *   **Error Handling**: Returns `500 Internal Server Error` if an error occurs during file listing.

*   **`GET /files/{filename}`**
    *   **Description**: Serves a specific file from the `knowledge_base` directory. The file is returned with an appropriate `Content-Type` header, allowing browsers to display it inline if supported.
    *   **Path Parameters**:
        *   `filename` (string, required): The name of the file to retrieve.
    *   **Response**: The content of the requested file.
    *   **Error Handling**:
        *   `404 Not Found`: If the specified file does not exist.
        *   `500 Internal Server Error`: If an error occurs during file retrieval.

#### 3. Settings Endpoints

*   **`GET /settings`**
    *   **Description**: Retrieves the current runtime configuration settings of the backend.
    *   **Request Body**: None.
    *   **Response Body**:
        ```json
        {
          "ollama_base_url": "http://localhost:11434",
          "llm_model": "phi4:14b-fp16",
          "embedding_model": "nomic-embed-text",
          "chunk_size": 1500,
          "chunk_overlap": 150,
          "top_k_chunks": 10
        }
        ```

*   **`POST /settings`**
    *   **Description**: Updates the backend's configuration settings dynamically and persists these changes to the `backend/configuration.py` file. After updating, it reinitializes the Ollama clients (LLM and embeddings) with the new settings.
    *   **Request Body**:
        ```json
        {
          "ollama_base_url": "string",
          "llm_model": "string",
          "embedding_model": "string",
          "chunk_size": integer,
          "chunk_overlap": integer,
          "top_k_chunks": integer
        }
        ```
        (All fields are optional; only provided fields will be updated.)
    *   **Response Body**: Returns the updated settings (same as `GET /settings`).
    *   **Error Handling**: Returns `500 Internal Server Error` if the settings update or client reinitialization fails.

#### 4. Utility Endpoints

*   **`POST /clear-memory`**
    *   **Description**: Clears the current conversation memory, effectively starting a new chat session without affecting the knowledge base.
    *   **Request Body**: None.
    *   **Response Body**:
        ```json
        {
          "message": "Conversation memory cleared and new session started"
        }
        ```
    *   **Error Handling**: Returns `500 Internal Server Error` if an error occurs.

*   **`GET /health`**
    *   **Description**: A simple health check endpoint to verify the backend service is running.
    *   **Request Body**: None.
    *   **Response Body**:
        ```json
        {
          "status": "healthy"
        }
        ```

### Logging

The backend uses Python's standard `logging` module. Logs are configured to output to `sys.stdout` with `INFO` level and a timestamped format. This is useful for monitoring the application's behavior and debugging.

### Error Handling

The API endpoints are designed to return appropriate HTTP status codes and detailed error messages in case of failures (e.g., `400 Bad Request`, `404 Not Found`, `500 Internal Server Error`). Detailed error logs are also generated on the server side.

### Development Notes

*   **CORS**: The application is configured with `CORSMiddleware` to allow all origins (`allow_origins=["*"]`) for development purposes. For production, this should be restricted to specific frontend origins.
*   **Hot Reloading**: When running with `uvicorn api:app --reload`, changes to the backend code will automatically trigger a server restart.
*   **Environment Variables**: For production deployments or specific environments (like Electron), it's recommended to use environment variables (`KNOWLEDGE_BASE_DIR`, `CHROMA_DB_DIR`) to configure paths rather than modifying `configuration.py` directly.
