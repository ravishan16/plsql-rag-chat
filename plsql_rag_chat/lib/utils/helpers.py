# plsql_rag_chat/lib/utils/helpers.py

from functools import lru_cache
from pathlib import Path
from typing import Tuple, Dict, Any, Optional, List
import json
import logging
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# Local imports
from plsql_rag_chat.lib.embeddings.hash_embeddings import SimpleHashEmbeddings
from plsql_rag_chat.lib.llm_handlers.base import BaseLLMHandler
from plsql_rag_chat.lib.llm_handlers.ollama_handler import OllamaHandler
from plsql_rag_chat.lib.llm_handlers.bedrock_handler import BedrockHandler
from plsql_rag_chat.config.settings import SYSTEM_PROMPTS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_llm_handler(config: Dict[str, Any]) -> Optional[BaseLLMHandler]:
    """Get the appropriate LLM handler based on configuration"""
    provider = config["provider"].lower().strip()
    logger.info(f"Initializing LLM handler for provider: {provider}")
    
    try:
        if provider == "ollama":
            logger.info(f"Creating Ollama handler with base URL: {config['ollama_base_url']}")
            return OllamaHandler(base_url=config["ollama_base_url"])
        elif provider == "bedrock":
            logger.info(f"Creating Bedrock handler for region: {config['aws_region']}")
            return BedrockHandler(region=config["aws_region"])
        else:
            logger.error(f"Unsupported LLM provider: '{provider}'")
            return None
    except Exception as e:
        logger.error(f"Error creating LLM handler: {str(e)}")
        logger.exception("Detailed traceback:")
        return None

@lru_cache(maxsize=1)
def load_vectorstore(
    store_path: Path,
    metadata_path: Path
) -> Tuple[Optional[FAISS], Optional[Dict[str, Any]]]:
    """Load the vector store and metadata with caching"""
    try:
        # Convert to absolute path and resolve any symlinks
        store_path = Path(store_path).resolve()
        metadata_path = Path(metadata_path).resolve()
        
        logger.info(f"Loading vector store from: {store_path}")
        logger.info(f"Vector store files present: {list(store_path.glob('*'))}")
        
        # Create embeddings
        embeddings = SimpleHashEmbeddings(dimension=384)
        
        # Load vector store with explicit path to folder
        vectorstore = FAISS.load_local(
            folder_path=str(store_path),
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        
        logger.info("Successfully loaded vector store")
        
        # Load metadata if it exists
        if metadata_path.exists():
            logger.info(f"Loading metadata from: {metadata_path}")
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            logger.info("Successfully loaded metadata")
        else:
            logger.warning(f"Metadata file not found at: {metadata_path}")
            metadata = {}
            
        return vectorstore, metadata
    except Exception as e:
        logger.error(f"Error loading vector store: {str(e)}", exc_info=True)
        return None, None

def validate_vectorstore(store_path: Path) -> bool:
    """Validate that the vector store exists and contains required files"""
    try:
        store_path = Path(store_path).resolve()
        logger.info(f"Validating vector store at: {store_path}")
        
        index_path = store_path / "index.faiss"
        pickle_path = store_path / "index.pkl"
        
        # Check if files exist and are readable
        if not index_path.exists():
            logger.error(f"Missing vector store index file: {index_path}")
            return False
            
        if not pickle_path.exists():
            logger.error(f"Missing vector store pickle file: {pickle_path}")
            return False
        
        # Check if files are readable
        try:
            with open(index_path, 'rb') as f:
                f.read(1)
            with open(pickle_path, 'rb') as f:
                f.read(1)
        except Exception as e:
            logger.error(f"Error reading vector store files: {str(e)}")
            return False
            
        logger.info("Vector store validation successful")
        return True
    except Exception as e:
        logger.error(f"Error validating vector store: {str(e)}", exc_info=True)
        return False

def initialize_chat_chain(
    llm_handler: BaseLLMHandler,
    vectorstore: FAISS,
    model_params: Dict[str, Any]
) -> Optional[ConversationalRetrievalChain]:
    """Initialize the conversational retrieval chain"""
    try:
        logger.info("Initializing chat chain with parameters: %s", model_params)
        
        # Initialize the language model
        llm = llm_handler.initialize_model(model_params)
        if not llm:
            logger.error("Failed to initialize language model")
            return None
            
        # Configure memory with explicit output key
        memory = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            output_key="answer",  # Specify which key to store in memory
            return_messages=True
        )
        
        # Create the chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(
                search_kwargs={"k": model_params["retrieval_k"]}
            ),
            memory=memory,
            return_source_documents=True,
            verbose=True,
            chain_type="stuff",
            combine_docs_chain_kwargs={
                "prompt": PromptTemplate(
                    template=SYSTEM_PROMPTS["chess_expert"] + """
                    
                    Context: {context}
                    
                    Question: {question}
                    
                    Detailed Answer:""",
                    input_variables=["context", "question"]
                )
            }
        )
        
        logger.info("Successfully initialized chat chain")
        return chain
        
    except Exception as e:
        logger.error(f"Error initializing chat chain: {str(e)}", exc_info=True)
        return None