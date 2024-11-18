from typing import Dict, Any, List, Optional
import boto3
from langchain_community.llms import Bedrock  # Updated import
from .base import BaseLLMHandler

class BedrockHandler(BaseLLMHandler):
    def __init__(self, region: str):
        self.region = region
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model = None
    
    def initialize_model(self, model_params: Dict[str, Any]) -> Optional[Bedrock]:
        self.model = Bedrock(
            model_id=model_params.get("model_id", "anthropic.claude-v2"),
            client=self.client,
            model_kwargs={
                "temperature": model_params.get("temperature", 0.7),
                "max_tokens": model_params.get("context_length", 2048),
                "top_k": model_params.get("top_k", 40),
            }
        )
        return self.model
    
    def health_check(self) -> bool:
        try:
            self.client.list_foundation_models()
            return True
        except:
            return False
    
    def get_available_models(self) -> List[str]:
        try:
            response = self.client.list_foundation_models()
            return [model["modelId"] for model in response["modelSummaries"]]
        except:
            return []
