"""
Sensor Data Agent
Handles queries related to time-series sensor data (temperature, vibration, pressure)
Uses Azure Cognitive Search with semantic search capabilities
"""
import logging
from typing import Dict, Any, List
import config
from agents.base_agent import BaseAgent, AgentResponse

# Get logger for this module
logger = logging.getLogger(__name__)


class SensorDataAgent(BaseAgent):
    """Agent for querying and analyzing sensor data using Azure Cognitive Search"""
    
    def __init__(self):
        super().__init__(
            name="Sensor Data Agent",
            description="Analyzes time-series sensor data including temperature, vibration, and pressure readings to identify anomalies and trends",
            search_index=config.AZURE_SEARCH_INDEX_SENSOR
        )
        logger.info(f"✓ SensorDataAgent initialized with Azure Search index: {config.AZURE_SEARCH_INDEX_SENSOR}")
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process sensor data query using Azure Cognitive Search semantic search
        
        Args:
            query: User query about sensor data
            **kwargs: Additional parameters (top_k, filters, etc.)
            
        Returns:
            AgentResponse with sensor data analysis from Azure Search
        """
        try:
            logger.info(f"→ Processing sensor query: {query}")
            
            # Perform semantic search on Azure Cognitive Search
            top_k = kwargs.get('top_k', config.TOP_K_DOCUMENTS)
            documents = self.semantic_search(query, top=top_k)
            
            if not documents:
                logger.warning("⚠ No sensor data found via semantic search")
                return AgentResponse(
                    agent_name=self.name,
                    success=True,
                    data={
                        "summary": "No sensor data found matching the query",
                        "documents": [],
                        "count": 0
                    },
                    metadata={"query": query, "source": "azure_search"}
                ).to_dict()
            
            # Analyze the retrieved documents
            analysis = self._analyze_search_results(documents, query)
            
            logger.info(f"✓ Sensor analysis complete: {len(documents)} documents processed")
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                data=analysis,
                metadata={
                    "documents_retrieved": len(documents),
                    "query": query,
                    "source": "azure_search"
                }
            ).to_dict()
            
        except Exception as e:
            logger.error(f"Error in SensorDataAgent: {str(e)}", exc_info=True)
            return AgentResponse(
                agent_name=self.name,
                success=False,
                error=str(e)
            ).to_dict()
    
    def _analyze_search_results(self, documents: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Analyze sensor data retrieved from Azure Search"""
        
        # Extract sensor information from documents
        sensors = []
        machines = set()
        sensor_types = set()
        statuses = {}
        critical_count = 0
        warning_count = 0
        
        for doc in documents:
            # Extract fields (adjust based on your index schema)
            machine_id = doc.get('machine_id') or doc.get('machineId') or doc.get('MachineID')
            sensor_type = doc.get('sensor_type') or doc.get('sensorType') or doc.get('SensorType')
            status = doc.get('status') or doc.get('Status')
            sensor_value = doc.get('sensor_value') or doc.get('sensorValue') or doc.get('Value')
            
            if machine_id:
                machines.add(machine_id)
            if sensor_type:
                sensor_types.add(sensor_type)
            if status:
                statuses[status] = statuses.get(status, 0) + 1
                if status and 'critical' in str(status).lower():
                    critical_count += 1
                elif status and 'warning' in str(status).lower():
                    warning_count += 1
            
            # Add to sensors list with relevant fields
            sensor_info = {
                "machine_id": machine_id,
                "sensor_type": sensor_type,
                "status": status,
                "value": sensor_value,
                "search_score": doc.get('search_score'),
                "reranker_score": doc.get('reranker_score'),
                "timestamp": doc.get('timestamp') or doc.get('Timestamp')
            }
            sensors.append(sensor_info)
        
        # Generate statistics
        stats = {
            "total_documents": len(documents),
            "unique_machines": len(machines),
            "sensor_types": list(sensor_types),
            "status_distribution": statuses,
            "critical_alerts": critical_count,
            "warning_alerts": warning_count
        }
        
        # Summary
        summary = f"Found {len(documents)} relevant sensor readings"
        if machines:
            summary += f" across {len(machines)} machine(s)"
        if critical_count > 0:
            summary += f" with {critical_count} critical alert(s)"
        
        return {
            "summary": summary,
            "statistics": stats,
            "sensors": sensors[:20],  # Return top 20 most relevant
            "all_documents": documents  # Full documents for LLM context
        }
