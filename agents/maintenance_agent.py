"""
Maintenance Agent
Queries Azure Cognitive Search for maintenance logs and generates RCA insights
"""
import logging
import json
from typing import Dict, Any, List, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import config
from agents.base_agent import BaseAgent, AgentResponse

# Get logger for this module
logger = logging.getLogger(__name__)


class MaintenanceAgent(BaseAgent):
    """Agent for querying maintenance logs and generating insights"""
    
    def __init__(self):
        super().__init__(
            name="Maintenance Agent",
            description="Searches maintenance logs to identify repair history, component failures, and preventive maintenance patterns"
        )
        self.search_client = self._initialize_search_client()
        # Fallback to local data if Azure Search is not configured
        self.use_local_data = not config.AZURE_SEARCH_ENDPOINT
        if self.use_local_data:
            self.maintenance_data = self._load_local_data()
    
    def _initialize_search_client(self) -> Optional[SearchClient]:
        """Initialize Azure Cognitive Search client"""
        if not config.AZURE_SEARCH_ENDPOINT or not config.AZURE_SEARCH_API_KEY:
            logger.warning("Azure Search not configured, using local data fallback")
            return None
        
        try:
            return SearchClient(
                endpoint=config.AZURE_SEARCH_ENDPOINT,
                index_name=config.AZURE_SEARCH_INDEX_MAINTENANCE,
                credential=AzureKeyCredential(config.AZURE_SEARCH_API_KEY)
            )
        except Exception as e:
            logger.error(f"Error initializing Azure Search client: {e}", exc_info=True)
            return None
    
    def _load_local_data(self) -> List[Dict[str, Any]]:
        """Load maintenance logs from local JSON as fallback"""
        try:
            with open(config.MAINTENANCE_LOGS_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading maintenance logs: {e}", exc_info=True)
            return []
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process maintenance log query
        
        Args:
            query: User query about maintenance logs
            **kwargs: Additional parameters (top_k, filters, etc.)
            
        Returns:
            AgentResponse with relevant maintenance logs
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
                select=["log_id", "machine_id", "date", "maintenance_type",
                       "components_checked", "actions_taken", "technician",
                       "downtime_hours", "remarks"]
            )
            
            for result in search_results:
                results.append({
                    "log_id": result.get("log_id"),
                    "machine_id": result.get("machine_id"),
                    "date": result.get("date"),
                    "maintenance_type": result.get("maintenance_type"),
                    "components_checked": result.get("components_checked"),
                    "actions_taken": result.get("actions_taken"),
                    "technician": result.get("technician"),
                    "downtime_hours": result.get("downtime_hours"),
                    "remarks": result.get("remarks"),
                    "search_score": result.get("@search.score", 0)
                })
        except Exception as e:
            logger.error(f"Error searching Azure: {e}", exc_info=True)
            # Fallback to local search
            return self._search_local_data(query, top_k)
        
        return results
    
    def _search_local_data(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search local maintenance logs using keyword matching"""
        if not self.maintenance_data:
            return []
        
        query_lower = query.lower()
        
        # Simple keyword-based scoring
        scored_logs = []
        for log in self.maintenance_data:
            score = 0
            
            # Convert log to searchable text
            text = f"{log.get('machine_id', '')} {log.get('maintenance_type', '')} "
            text += f"{' '.join(log.get('components_checked', []))} "
            text += f"{log.get('actions_taken', '')} {log.get('remarks', '')}"
            text = text.lower()
            
            # Count keyword matches
            keywords = query_lower.split()
            for keyword in keywords:
                if keyword in text:
                    score += text.count(keyword)
            
            # Boost emergency and corrective maintenance
            if log.get('maintenance_type') in ['Emergency', 'Corrective']:
                score += 2
            
            # Boost high downtime
            if log.get('downtime_hours', 0) > 5:
                score += 1
            
            if score > 0:
                log_copy = log.copy()
                log_copy['relevance_score'] = score
                scored_logs.append(log_copy)
        
        # Sort by score and return top-k
        scored_logs.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_logs[:top_k]
    
    def get_maintenance_history(self, machine_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get maintenance history for a specific machine"""
        if self.use_local_data:
            machine_logs = [
                log for log in self.maintenance_data 
                if log.get('machine_id') == machine_id
            ]
            return machine_logs[:limit]
        else:
            # Use Azure Search with filter
            filter_expr = f"machine_id eq '{machine_id}'"
            results = self.search_client.search(
                search_text="*",
                filter=filter_expr,
                top=limit
            )
            return [dict(r) for r in results]
    
    def get_component_failure_patterns(self) -> Dict[str, int]:
        """Analyze component failure patterns across all maintenance logs"""
        if not self.use_local_data or not self.maintenance_data:
            return {}
        
        component_counts = {}
        for log in self.maintenance_data:
            if log.get('maintenance_type') in ['Corrective', 'Emergency']:
                for component in log.get('components_checked', []):
                    component_counts[component] = component_counts.get(component, 0) + 1
        
        return dict(sorted(component_counts.items(), key=lambda x: x[1], reverse=True))
