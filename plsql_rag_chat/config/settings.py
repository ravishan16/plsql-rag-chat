from pathlib import Path
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "vectorstore").mkdir(exist_ok=True)
(DATA_DIR / "chat_histories").mkdir(exist_ok=True)
(DATA_DIR / "metadata").mkdir(exist_ok=True)

# Debug: Print raw environment variable
logger.info(f"Raw LLM_PROVIDER value: '{os.getenv('LLM_PROVIDER')}'")

# Data paths with validation
VECTOR_STORE_PATH = Path(os.getenv("VECTOR_STORE_PATH", str(DATA_DIR / "vectorstore")))
METADATA_PATH = Path(os.getenv("METADATA_PATH", str(DATA_DIR / "metadata" / "chess_metadata.json")))
CHAT_HISTORIES_PATH = Path(os.getenv("CHAT_HISTORIES_PATH", str(DATA_DIR / "chat_histories")))

# LLM settings with extra validation
raw_provider = os.getenv("LLM_PROVIDER", "ollama")
provider = raw_provider.lower().strip()
logger.info(f"Cleaned provider value: '{provider}'")


def clean_env_value(value: str, default: str) -> str:
    """Clean environment variable value and apply default if necessary"""
    if not value:
        return default
    # Remove any comments and whitespace
    cleaned = value.split('#')[0].strip()
    return cleaned if cleaned else default

# Load and validate LLM provider
raw_provider = os.getenv('LLM_PROVIDER', '')
provider = clean_env_value(raw_provider, 'ollama')
logger.info(f"Raw LLM_PROVIDER value: '{raw_provider}'")
logger.info(f"Cleaned provider value: '{provider}'")

if provider not in ['ollama', 'bedrock']:
    logger.error(f"Invalid provider '{provider}'. Defaulting to 'ollama'")
    provider = 'ollama'

# LLM Configuration
LLM_CONFIG = {
    "provider": provider,
    "ollama_base_url": clean_env_value(
        os.getenv("OLLAMA_BASE_URL", ''),
        "http://localhost:11434"
    ),
    "bedrock_model_id": clean_env_value(
        os.getenv("BEDROCK_MODEL_ID", ''),
        "anthropic.claude-v2"
    ),
    "aws_region": clean_env_value(
        os.getenv("AWS_REGION", ''),
        "us-east-1"
    ),
    "model_name": clean_env_value(
        os.getenv("MODEL_NAME", ''),
        "llama3.2:latest"
    )
}

# Log validated configuration
logger.info(f"Validated LLM CONFIG: {LLM_CONFIG}")

# Model parameters with validation
MODEL_PARAMS = {
    "temperature": float(clean_env_value(
        os.getenv("DEFAULT_TEMPERATURE", ''),
        "0.7"
    )),
    "context_length": int(clean_env_value(
        os.getenv("DEFAULT_CONTEXT_LENGTH", ''),
        "2048"
    )),
    "top_k": int(clean_env_value(
        os.getenv("DEFAULT_TOP_K", ''),
        "40"
    )),
    "retrieval_k": int(clean_env_value(
        os.getenv("DEFAULT_RETRIEVAL_K", ''),
        "3"
    )),
    "model_name": LLM_CONFIG["model_name"]
}


# System prompts
SYSTEM_PROMPTS = {
    "chess_expert": '''You are a highly knowledgeable chess engine expert, specifically focusing on PL/SQL-based chess implementations. 
    Your responses should:
    1. Explain chess-specific algorithms and logic clearly
    2. Reference relevant procedures and functions with examples
    3. Highlight important implementation details and design choices
    4. Suggest potential optimizations when appropriate
    
    Always maintain context from the chat history and refer back to previous discussions when relevant.'''
}

# UI Configuration
UI_CONFIG = {
    "page_title": "Chess Engine Code Assistant",
    "page_icon": "♟️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Categories for package explorer
PACKAGE_CATEGORIES = {
    "move_generation": "🎯 Move Generation",
    "evaluation": "⚖️ Position Evaluation",
    "notation": "📝 Chess Notation",
    "general": "🔧 General Utilities"
}

# Export all variables that should be accessible
__all__ = [
    'VECTOR_STORE_PATH',
    'METADATA_PATH',
    'CHAT_HISTORIES_PATH',
    'LLM_CONFIG',
    'MODEL_PARAMS',
    'SYSTEM_PROMPTS',
    'UI_CONFIG',
    'PACKAGE_CATEGORIES'
]
