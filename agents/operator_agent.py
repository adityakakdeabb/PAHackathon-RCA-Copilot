"""
Operator Agent
Queries Azure Cognitive Search for operator reports and generates RCA insights
"""
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
import config
from agents.base_agent import BaseAgent, AgentResponse

# Get logger for this module
logger = logging.getLogger(__name__)


class OperatorAgent(BaseAgent):
    """Agent for querying operator reports and generating insights"""
    
    def __init__(self):
        super().__init__(
            name="Operator Agent",
            description="Searches operator incident reports to identify patterns, severity levels, and operational issues"
        )
        self.search_client = self._initialize_search_client()
        # Fallback to local data if Azure Search is not configured
        self.use_local_data = not config.AZURE_SEARCH_ENDPOINT
        if self.use_local_data:
            self.operator_data = self._load_local_data()
    
    def _initialize_search_client(self) -> Optional[SearchClient]:
        """Initialize Azure Cognitive Search client"""
        if not config.AZURE_SEARCH_ENDPOINT or not config.AZURE_SEARCH_API_KEY:
            logger.warning("Azure Search not configured, using local data fallback")
            return None
        
        try:
            return SearchClient(
                endpoint=config.AZURE_SEARCH_ENDPOINT,
                index_name=config.AZURE_SEARCH_INDEX_OPERATOR,
                credential=AzureKeyCredential(config.AZURE_SEARCH_API_KEY)
            )
        except Exception as e:
            logger.error(f"Error initializing Azure Search client: {e}", exc_info=True)
            return None
    
    def _load_local_data(self) -> pd.DataFrame:
        """Load operator reports from local CSV as fallback"""
        try:
            return pd.read_csv(config.OPERATOR_REPORTS_PATH)
        except Exception as e:
            logger.error(f"Error loading operator reports: {e}", exc_info=True)
            return pd.DataFrame()
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process operator report query
        
        Args:
            query: User query about operator reports
            **kwargs: Additional parameters (top_k, filters, etc.)
            
        Returns:
            AgentResponse with relevant operator reports
        """
        try:
            top_k = kwargs.get('top_k', config.TOP_K_DOCUMENTS)
            
            if self.use_local_data or self.search_client is None:
                # Use local data search
                documents = self._search_local_data(query, top_k)
            else:
                # Use Azure Cognitive Search
                documents = self._search_azure(query, top_k)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                data={
                    "documents": documents,
                    "query": query,
                    "source": "local" if self.use_local_data else "azure_search"
                },
                metadata={
                    "document_count": len(documents),
                    "top_k": top_k
                }
            ).to_dict()
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                success=False,
                error=str(e)
            ).to_dict()
    
    def _search_azure(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search Azure Cognitive Search for relevant documents"""
        results = []
        
        try:
            search_results = self.search_client.search(
                search_text=query,
                top=top_k,
                select=["report_id", "machine_id", "operator_name", "shift", 
                       "date", "incident_description", "initial_action", 
                       "severity", "status"]
            )
            
            for result in search_results:
                results.append({
                    "report_id": result.get("report_id"),
                    "machine_id": result.get("machine_id"),
                    "operator_name": result.get("operator_name"),
                    "shift": result.get("shift"),
                    "date": result.get("date"),
                    "incident_description": result.get("incident_description"),
                    "initial_action": result.get("initial_action"),
                    "severity": result.get("severity"),
                    "status": result.get("status"),
                    "search_score": result.get("@search.score", 0)
                })
        except Exception as e:
            logger.error(f"Error searching Azure: {e}", exc_info=True)
            # Fallback to local search
            return self._search_local_data(query, top_k)
        
        return results
    
    def _search_local_data(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search local operator reports using keyword matching"""
        if self.operator_data.empty:
            return []
        
        query_lower = query.lower()
        
        # Simple keyword-based scoring
        def calculate_relevance(row):
            score = 0
            text = f"{row['incident_description']} {row['initial_action']} {row['machine_id']}".lower()
            
            # Count keyword matches
            keywords = query_lower.split()
            for keyword in keywords:
                if keyword in text:
                    score += text.count(keyword)
            
            # Boost recent reports
            if row['status'] == 'Open':
                score += 2
            if row['severity'] in ['High', 'Critical']:
                score += 3
            
            return score
        
        # Calculate relevance scores
        self.operator_data['relevance_score'] = self.operator_data.apply(calculate_relevance, axis=1)
        
        # Get top-k results
        top_results = self.operator_data.nlargest(top_k, 'relevance_score')
        
        # Convert to list of dictionaries
        results = []
        for _, row in top_results.iterrows():
            if row['relevance_score'] > 0:  # Only include relevant results
                results.append({
                    "report_id": row['report_id'],
                    "machine_id": row['machine_id'],
                    "operator_name": row['operator_name'],
                    "shift": row['shift'],
                    "date": row['date'],
                    "incident_description": row['incident_description'],
                    "initial_action": row['initial_action'],
                    "severity": row['severity'],
                    "status": row['status'],
                    "relevance_score": float(row['relevance_score'])
                })
        
        return results
    
    def get_reports_by_machine(self, machine_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get all reports for a specific machine"""
        if self.use_local_data:
            machine_reports = self.operator_data[
                self.operator_data['machine_id'] == machine_id
            ].head(limit)
            return machine_reports.to_dict('records')
        else:
            # Use Azure Search with filter
            filter_expr = f"machine_id eq '{machine_id}'"
            results = self.search_client.search(
                search_text="*",
                filter=filter_expr,
                top=limit
            )
            return [dict(r) for r in results]
