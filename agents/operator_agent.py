"""
Operator Agent
Queries Azure Cognitive Search for operator reports and generates RCA insights
"""
import logging
from typing import Dict, Any, List
import config
from agents.base_agent import BaseAgent, AgentResponse

logger = logging.getLogger(__name__)


class OperatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Operator Agent",
            description="Searches operator incident reports to identify patterns, severity levels, and operational issues",
            search_index=config.AZURE_SEARCH_INDEX_OPERATOR
        )
        logger.info(f"Operator Agent initialized with Azure Search index")
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        try:
            logger.info(f"Processing operator query: {query}")
            top_k = kwargs.get('top_k', config.TOP_K_DOCUMENTS)
            documents = self.semantic_search(query, top=top_k)
            
            if not documents:
                return AgentResponse(
                    agent_name=self.name,
                    success=True,
                    data={"summary": "No operator reports found", "documents": [], "count": 0},
                    metadata={"query": query}
                ).to_dict()
            
            analysis = self._analyze_search_results(documents, query)
            return AgentResponse(
                agent_name=self.name,
                success=True,
                data=analysis,
                metadata={"documents_retrieved": len(documents), "query": query}
            ).to_dict()
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return AgentResponse(agent_name=self.name, success=False, error=str(e)).to_dict()
    
    def _analyze_search_results(self, documents: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        reports = []
        for doc in documents:
            reports.append({
                "machine_id": doc.get('machine_id') or doc.get('machineId'),
                "severity": doc.get('severity'),
                "description": doc.get('description') or doc.get('incident_description'),
                "search_score": doc.get('search_score')
            })
        return {
            "summary": f"Found {len(documents)} operator reports",
            "reports": reports[:20],
            "all_documents": documents
        }
