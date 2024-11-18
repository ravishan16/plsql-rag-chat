from typing import Dict, Any, List, Optional
import requests
from concurrent.futures import ThreadPoolExecutor
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from .base import BaseLLMHandler

class OllamaHandler(BaseLLMHandler):
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.model = None
    
    def initialize_model(self, model_params: Dict[str, Any]) -> Optional[Ollama]:
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        
        self.model = Ollama(
            model=model_params.get("model_name", "llama3.2:latest"),
            temperature=model_params.get("temperature", 0.7),
            callback_manager=callback_manager,
            verbose=True,
            base_url=self.base_url,
            num_ctx=model_params.get("context_length", 2048),
            top_k=model_params.get("top_k", 40),
        )
        return self.model
    
    def health_check(self) -> bool:
        with ThreadPoolExecutor() as executor:
            try:
                future = executor.submit(
                    requests.get,
                    f"{self.base_url}/api/tags",
                    timeout=5
                )
                response = future.result()
                return response.status_code == 200
            except:
                return False
    
    def get_available_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return [model["name"] for model in response.json().get("models", [])]
        except:
            pass
        return []
