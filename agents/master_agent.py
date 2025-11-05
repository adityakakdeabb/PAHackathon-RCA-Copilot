"""
Master Agent - Orchestrator for RCA Copilot
Routes queries to appropriate specialized agents using LangChain
"""
import logging
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import config
from agents.sensor_agent import SensorDataAgent
from agents.operator_agent import OperatorAgent
from agents.maintenance_agent import MaintenanceAgent
from models.rca_chain import RCAChain

# Get logger for this module
logger = logging.getLogger(__name__)


class MasterAgent:
    """
    Master Agent that orchestrates queries across specialized agents
    Acts as the main entry point for RCA Copilot
    """
    
    def __init__(self):
        self.name = "Master Agent"
        self.llm = self._initialize_llm()
        
        # Initialize specialized agents
        logger.info("Initializing specialized agents...")
        self.sensor_agent = SensorDataAgent()
        self.operator_agent = OperatorAgent()
        self.maintenance_agent = MaintenanceAgent()
        
        # Initialize RCA chain
        self.rca_chain = RCAChain()
        
        logger.info("✓ Master Agent initialized successfully")
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM for routing decisions"""
        return AzureChatOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            deployment_name=config.MASTER_AGENT_MODEL,
            temperature=0.3,  # Low temperature for consistent routing
            max_tokens=500
        )
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Main entry point - processes user query and orchestrates agents
        
        Args:
            query: User's natural language query
            **kwargs: Additional parameters
            
        Returns:
            Complete RCA response with mitigation steps
        """
        logger.info(f"{'='*60}")
        logger.info(f"Master Agent Processing Query: {query}")
        logger.info(f"{'='*60}")
        
        try:
            # Step 1: Determine which agents to invoke
            routing_decision = self._route_query(query)
            logger.info(f"Routing Decision: {routing_decision}")
            
            # Step 2: Invoke the selected agents
            agent_responses = self._invoke_agents(query, routing_decision, **kwargs)
            
            # Step 3: Generate RCA report using LLM chain
            rca_report = self._generate_rca_report(query, agent_responses)
            
            # Step 4: Compile final response
            final_response = {
                "success": True,
                "query": query,
                "routing_decision": routing_decision,
                "agent_responses": agent_responses,
                "rca_report": rca_report.get("rca_report", ""),
                "timestamp": self._get_timestamp()
            }
            
            logger.info("Query processed successfully")
            return final_response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "timestamp": self._get_timestamp()
            }
    
    def _route_query(self, query: str) -> Dict[str, bool]:
        """
        Use LLM to determine which agents should handle the query
        
        Args:
            query: User query
            
        Returns:
            Dictionary indicating which agents to invoke
        """
        routing_prompt = f"""You are a routing agent for an RCA (Root Cause Analysis) system. 
Analyze the user's query and determine which specialized agents should be invoked.

Available Agents:
1. **Sensor Data Agent**: Handles queries about time-series sensor data (temperature, vibration, pressure), anomalies, and real-time measurements
2. **Operator Agent**: Handles queries about operator incident reports, observations, and initial actions taken
3. **Maintenance Agent**: Handles queries about maintenance history, repairs, component failures, and technician actions

User Query: "{query}"

Based on the query, determine which agents are relevant. Respond in this exact format:
SENSOR_AGENT: YES/NO
OPERATOR_AGENT: YES/NO
MAINTENANCE_AGENT: YES/NO

Rules:
- If the query mentions sensors, readings, temperature, vibration, pressure, or real-time data → SENSOR_AGENT: YES
- If the query mentions operators, reports, incidents, observations → OPERATOR_AGENT: YES
- If the query mentions maintenance, repairs, components, failures, technicians → MAINTENANCE_AGENT: YES
- For general RCA or comprehensive analysis, invoke ALL agents
- At least one agent must be selected

Your response:"""

        try:
            response = self.llm.invoke([HumanMessage(content=routing_prompt)])
            routing_text = response.content.strip()
            
            # Parse the response
            routing = {
                "sensor_agent": "SENSOR_AGENT: YES" in routing_text.upper(),
                "operator_agent": "OPERATOR_AGENT: YES" in routing_text.upper(),
                "maintenance_agent": "MAINTENANCE_AGENT: YES" in routing_text.upper()
            }
            
            # Ensure at least one agent is selected
            if not any(routing.values()):
                # Default to all agents for safety
                logger.warning("No agents selected by routing logic, defaulting to all agents")
                routing = {
                    "sensor_agent": True,
                    "operator_agent": True,
                    "maintenance_agent": True
                }
            
            return routing
            
        except Exception as e:
            logger.error(f"Error in routing: {e}", exc_info=True)
            # Default to all agents on error
            return {
                "sensor_agent": True,
                "operator_agent": True,
                "maintenance_agent": True
            }
    
    def _invoke_agents(
        self, 
        query: str, 
        routing: Dict[str, bool],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Invoke the selected specialized agents
        
        Args:
            query: User query
            routing: Dictionary indicating which agents to invoke
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with responses from each agent
        """
        responses = {}
        
        # Invoke Sensor Agent
        if routing.get("sensor_agent", False):
            logger.info("→ Invoking Sensor Data Agent...")
            try:
                sensor_response = self.sensor_agent.process_query(query, **kwargs)
                responses["sensor_data"] = sensor_response
                logger.info("✓ Sensor Agent completed")
            except Exception as e:
                logger.error(f"✗ Sensor Agent error: {e}", exc_info=True)
                responses["sensor_data"] = {"success": False, "error": str(e)}
        
        # Invoke Operator Agent
        if routing.get("operator_agent", False):
            logger.info("→ Invoking Operator Agent...")
            try:
                operator_response = self.operator_agent.process_query(query, **kwargs)
                responses["operator_reports"] = operator_response
                doc_count = operator_response.get('metadata', {}).get('document_count', 0)
                logger.info(f"✓ Operator Agent completed ({doc_count} documents)")
            except Exception as e:
                logger.error(f"✗ Operator Agent error: {e}", exc_info=True)
                responses["operator_reports"] = {"success": False, "error": str(e)}
        
        # Invoke Maintenance Agent
        if routing.get("maintenance_agent", False):
            logger.info("→ Invoking Maintenance Agent...")
            try:
                maintenance_response = self.maintenance_agent.process_query(query, **kwargs)
                responses["maintenance_logs"] = maintenance_response
                doc_count = maintenance_response.get('metadata', {}).get('document_count', 0)
                logger.info(f"✓ Maintenance Agent completed ({doc_count} documents)")
            except Exception as e:
                logger.error(f"✗ Maintenance Agent error: {e}", exc_info=True)
                responses["maintenance_logs"] = {"success": False, "error": str(e)}
        
        return responses
    
    def _generate_rca_report(
        self, 
        query: str, 
        agent_responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive RCA report using LangChain with agent findings
        
        Args:
            query: Original user query
            agent_responses: Responses from specialized agents
            
        Returns:
            RCA report with mitigation steps
        """
        logger.info("→ Generating RCA Report using LLM Chain with agent findings...")
        
        # Extract analysis text and documents from agent responses
        sensor_analysis = ""
        sensor_documents = []
        operator_analysis = ""
        operator_documents = []
        maintenance_analysis = ""
        maintenance_documents = []
        
        # Extract Sensor Agent data
        if "sensor_data" in agent_responses and agent_responses["sensor_data"].get("success"):
            sensor_data = agent_responses["sensor_data"].get("data", {})
            sensor_analysis = sensor_data.get("analysis", "")
            sensor_documents = sensor_data.get("all_documents", [])
            logger.info(f"  Sensor: {len(sensor_documents)} documents, analysis length: {len(sensor_analysis)} chars")
        
        # Extract Operator Agent data
        if "operator_reports" in agent_responses and agent_responses["operator_reports"].get("success"):
            operator_data = agent_responses["operator_reports"].get("data", {})
            operator_analysis = operator_data.get("analysis", "")
            operator_documents = operator_data.get("documents", [])
            logger.info(f"  Operator: {len(operator_documents)} documents, analysis length: {len(operator_analysis)} chars")
        
        # Extract Maintenance Agent data
        if "maintenance_logs" in agent_responses and agent_responses["maintenance_logs"].get("success"):
            maintenance_data = agent_responses["maintenance_logs"].get("data", {})
            maintenance_analysis = maintenance_data.get("analysis", "")
            maintenance_documents = maintenance_data.get("documents", [])
            logger.info(f"  Maintenance: {len(maintenance_documents)} documents, analysis length: {len(maintenance_analysis)} chars")
        
        # Generate RCA report with agent analyses and documents
        rca_report = self.rca_chain.generate_rca_report(
            query=query,
            sensor_analysis=sensor_analysis,
            operator_analysis=operator_analysis,
            maintenance_analysis=maintenance_analysis,
            sensor_documents=sensor_documents,
            operator_documents=operator_documents,
            maintenance_documents=maintenance_documents,
            context=""
        )
        
        logger.info("✓ RCA Report generated with agent findings")
        
        return rca_report
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def chat(self, query: str) -> str:
        """
        Simplified chat interface
        
        Args:
            query: User query
            
        Returns:
            RCA report as string
        """
        result = self.process_query(query)
        
        if result.get("success"):
            return result.get("rca_report", "No report generated")
        else:
            return f"Error: {result.get('error', 'Unknown error')}"
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """Get list of available agents"""
        return [
            self.sensor_agent.get_capabilities(),
            self.operator_agent.get_capabilities(),
            self.maintenance_agent.get_capabilities()
        ]
