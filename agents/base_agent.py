"""
Base Agent class and utilities for RCA Copilot
Provides common functionality for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import config


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM"""
        return AzureChatOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            deployment_name=config.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )
    
    @abstractmethod
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process a query and return results
        
        Args:
            query: User query string
            **kwargs: Additional parameters
            
        Returns:
            Dictionary containing agent results
        """
        pass
    
    def get_capabilities(self) -> Dict[str, str]:
        """Return agent capabilities"""
        return {
            "name": self.name,
            "description": self.description
        }


class AgentResponse:
    """Standardized response format for all agents"""
    
    def __init__(
        self, 
        agent_name: str, 
        success: bool, 
        data: Any = None, 
        error: str = None,
        metadata: Dict[str, Any] = None
    ):
        self.agent_name = agent_name
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "agent_name": self.agent_name,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }
    
    def __repr__(self) -> str:
        return f"AgentResponse(agent={self.agent_name}, success={self.success})"
