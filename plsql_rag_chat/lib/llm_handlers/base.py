
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseLLMHandler(ABC):
    """Base class for LLM handlers"""
    
    @abstractmethod
    def initialize_model(self, model_params: Dict[str, Any]) -> Any:
        """Initialize the language model with given parameters"""
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the LLM service is available"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass