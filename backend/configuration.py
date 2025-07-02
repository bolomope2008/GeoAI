from pathlib import Path
import os

# Project directories (configurable for Electron)
BASE_DIR = Path(__file__).parent

# Use environment variables if available (for Electron), otherwise use defaults
if os.getenv('KNOWLEDGE_BASE_DIR'):
    KNOWLEDGE_BASE_DIR = Path(os.getenv('KNOWLEDGE_BASE_DIR'))
else:
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"

if os.getenv('CHROMA_DB_DIR'):
    CHROMA_DB_DIR = Path(os.getenv('CHROMA_DB_DIR'))
else:
    CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# ChromaDB settings (static)
COLLECTION_NAME = "knowledge_base"

# Default values for runtime-configurable settings
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
DEFAULT_LLM_MODEL = "phi4:14b-fp16"
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K_CHUNKS = 5

# Runtime-configurable settings
# These can be updated through the /settings endpoint and environment variables
OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "phi4:14b-fp16"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150
TOP_K_CHUNKS = 10
