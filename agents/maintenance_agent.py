"""
Maintenance Agent
Queries Azure Cognitive Search for maintenance logs and generates RCA insights
"""
import logging
from typing import Dict, Any, List
import config
from agents.base_agent import BaseAgent, AgentResponse

# Get logger for this module
logger = logging.getLogger(__name__)


class MaintenanceAgent(BaseAgent):
    """Agent for querying maintenance logs using Azure Cognitive Search"""
    
    def __init__(self):
        super().__init__(
            name="Maintenance Agent",
            description="Searches maintenance logs to identify repair history, component failures, and preventive maintenance patterns",
            search_index=config.AZURE_SEARCH_INDEX_MAINTENANCE,
            template_name="maintenance_agent.jinja2"
        )
        logger.info(f"✓ MaintenanceAgent initialized with Azure Search index: {config.AZURE_SEARCH_INDEX_MAINTENANCE}")
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process maintenance log query using Azure Cognitive Search semantic search
        
        Args:
            query: User query about maintenance logs
            **kwargs: Additional parameters (top_k, filters, etc.)
            
        Returns:
            AgentResponse with relevant maintenance logs from Azure Search
        """
        try:
            logger.info(f"→ Processing maintenance query: {query}")
            
            # Perform semantic search on Azure Cognitive Search
            top_k = kwargs.get('top_k', config.TOP_K_DOCUMENTS)
            documents = self.semantic_search(query, top=top_k)
            
            if not documents:
                logger.warning("⚠ No maintenance logs found via semantic search")
                return AgentResponse(
                    agent_name=self.name,
                    success=True,
                    data={
                        "analysis": "No maintenance logs found matching the query",
                        "summary": "No maintenance logs found matching the query",
                        "documents": [],
                        "all_documents": [],
                        "count": 0
                    },
                    metadata={"query": query, "source": "azure_search", "document_count": 0}
                ).to_dict()
            
            # Generate analysis using Jinja2 template and LLM
            analysis_text = self.generate_analysis(query, documents)
            
            # Analyze the retrieved documents for statistics
            stats_analysis = self._analyze_search_results(documents, query)
            stats_analysis["analysis"] = analysis_text
            
            logger.info(f"✓ Maintenance log analysis complete: {len(documents)} documents processed")
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                data=stats_analysis,
                metadata={
                    "documents_retrieved": len(documents),
                    "document_count": len(documents),
                    "query": query,
                    "source": "azure_search"
                }
            ).to_dict()
            
        except Exception as e:
            logger.error(f"Error in MaintenanceAgent: {str(e)}", exc_info=True)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                error=str(e)
            ).to_dict()
    
    def _analyze_search_results(self, documents: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Analyze maintenance logs retrieved from Azure Search"""
        
        # Extract maintenance log information from documents
        logs = []
        maintenance_types = {}
        machines = set()
        components = set()
        
        for doc in documents:
            # Extract fields (adjust based on your index schema)
            log_id = doc.get('log_id') or doc.get('logId') or doc.get('LogID')
            machine_id = doc.get('machine_id') or doc.get('machineId') or doc.get('MachineID')
            maintenance_type = doc.get('maintenance_type') or doc.get('maintenanceType') or doc.get('MaintenanceType')
            actions_taken = doc.get('actions_taken') or doc.get('actionsTaken') or doc.get('ActionsTaken')
            components_checked = doc.get('components_checked') or doc.get('componentsChecked') or doc.get('Components')
            
            if machine_id:
                machines.add(machine_id)
            if maintenance_type:
                maintenance_types[maintenance_type] = maintenance_types.get(maintenance_type, 0) + 1
            if components_checked:
                if isinstance(components_checked, list):
                    components.update(components_checked)
                else:
                    components.add(str(components_checked))
            
            # Add to logs list with relevant fields
            log_info = {
                "log_id": log_id,
                "machine_id": machine_id,
                "maintenance_type": maintenance_type,
                "actions_taken": actions_taken,
                "components_checked": components_checked,
                "search_score": doc.get('search_score'),
                "reranker_score": doc.get('reranker_score'),
                "timestamp": doc.get('timestamp') or doc.get('Timestamp') or doc.get('date')
            }
            logs.append(log_info)
        
        # Generate statistics
        stats = {
            "total_logs": len(documents),
            "unique_machines": len(machines),
            "maintenance_types": list(maintenance_types.keys()),
            "type_distribution": maintenance_types,
            "components_affected": list(components)
        }
        
        # Summary
        summary = f"Found {len(documents)} relevant maintenance log(s)"
        if machines:
            summary += f" across {len(machines)} machine(s)"
        if maintenance_types:
            emergency = maintenance_types.get('Emergency', 0) + maintenance_types.get('Corrective', 0)
            if emergency > 0:
                summary += f" with {emergency} emergency/corrective maintenance(s)"
        
        return {
            "summary": summary,
            "statistics": stats,
            "logs": logs[:20],  # Return top 20 most relevant
            "documents": documents,  # For master agent compatibility
            "all_documents": documents  # Full documents for LLM context
        }
