"""
Base Agent class and utilities for RCA Copilot
Provides common functionality for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import config
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, description: str, search_index: Optional[str] = None, template_name: Optional[str] = None):
        self.name = name
        self.description = description
        self.llm = self._initialize_llm()
        self.search_client = self._initialize_search_client(search_index) if search_index else None
        self.jinja_env = self._initialize_jinja_environment()  # Initialize BEFORE loading template
        self.template = self._load_template(template_name) if template_name else None
    
    def _initialize_jinja_environment(self) -> Environment:
        """Initialize Jinja2 environment for template loading"""
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')
        return Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def _load_template(self, template_name: str):
        """Load Jinja2 template for agent"""
        try:
            template = self.jinja_env.get_template(template_name)
            logger.info(f"✓ Loaded template: {template_name}")
            return template
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return None
    
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
    
    def _initialize_search_client(self, index_name: str) -> Optional[SearchClient]:
        """Initialize Azure Cognitive Search client"""
        if not config.AZURE_SEARCH_ENDPOINT or not config.AZURE_SEARCH_API_KEY:
            logger.warning(f"Azure Search not configured for {self.name}")
            return None
        
        try:
            search_client = SearchClient(
                endpoint=config.AZURE_SEARCH_ENDPOINT,
                index_name=index_name,
                credential=AzureKeyCredential(config.AZURE_SEARCH_API_KEY)
            )
            logger.info(f"✓ Azure Search client initialized for index: {index_name}")
            return search_client
        except Exception as e:
            logger.error(f"Failed to initialize Azure Search client: {e}", exc_info=True)
            return None
    
    def semantic_search(self, query: str, top: int = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search on Azure Cognitive Search
        
        Args:
            query: User query for semantic search
            top: Number of top results to return (defaults to config.TOP_K_DOCUMENTS)
            
        Returns:
            List of matching documents with relevance scores
        """
        if not self.search_client:
            logger.warning(f"Azure Search not available for {self.name}, returning empty results")
            return []
        
        if top is None:
            top = config.TOP_K_DOCUMENTS
        
        try:
            logger.info(f"→ Performing semantic search: '{query}' (top={top})")
            
            # Perform semantic search with Azure Cognitive Search
            results = self.search_client.search(
                search_text=query,
                query_type="semantic",
                semantic_configuration_name="default",
                top=top,
                select=["*"]
            )
            
            documents = []
            for result in results:
                doc = dict(result)
                # Preserve search relevance scores
                if '@search.score' in result:
                    doc['search_score'] = result['@search.score']
                if '@search.reranker_score' in result:
                    doc['reranker_score'] = result['@search.reranker_score']
                documents.append(doc)
            
            logger.info(f"✓ Found {len(documents)} relevant documents via semantic search")
            if documents:
                logger.info(f"✓ Top result score: {documents[0].get('reranker_score', documents[0].get('search_score', 'N/A'))}")
            
            return documents
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}", exc_info=True)
            return []
    
    def generate_analysis(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """
        Generate analysis using Jinja2 template and LLM
        
        Args:
            query: User query
            documents: Retrieved documents from Azure Search
            
        Returns:
            Analysis text from LLM
        """
        if not self.template:
            logger.warning(f"No template loaded for {self.name}, skipping analysis generation")
            return ""
        
        try:
            # Render the template with query and documents
            rendered_prompt = self.template.render(
                query=query,
                documents=documents,
                document_count=len(documents)
            )
            
            logger.info(f"→ Generating analysis using {self.name} template (prompt length: {len(rendered_prompt)} chars)")
            
            # Generate analysis using LLM
            response = self.llm.invoke([HumanMessage(content=rendered_prompt)])
            analysis = response.content
            
            logger.info(f"✓ Analysis generated ({len(analysis)} chars)")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to generate analysis: {e}", exc_info=True)
            return ""
    
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
