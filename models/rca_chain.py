"""
RCA Chain - LangChain-based RCA Report Generation
Generates Root Cause Analysis reports with mitigation steps using LLM
"""
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import config


class RCAChain:
    """LangChain-based RCA report generation with Jinja2 templates"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.jinja_env = self._initialize_jinja_environment()
        self.rca_template = self._load_rca_template()
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM for RCA generation"""
        return AzureChatOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            deployment_name=config.RCA_GENERATION_MODEL,
            temperature=0.7,  # Slightly creative for recommendations
            max_tokens=400  # Increased for bullet-point format with proper spacing
        )
    
    def _initialize_jinja_environment(self) -> Environment:
        """Initialize Jinja2 environment for template loading"""
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')
        return Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def _load_rca_template(self):
        """Load RCA generator Jinja2 template"""
        return self.jinja_env.get_template('rca_generator.jinja2')
    
    def generate_rca_report(
        self,
        query: str,
        sensor_analysis: str = "",
        operator_analysis: str = "",
        maintenance_analysis: str = "",
        sensor_documents: List[Dict[str, Any]] = None,
        operator_documents: List[Dict[str, Any]] = None,
        maintenance_documents: List[Dict[str, Any]] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate RCA report using Jinja2 template and agent findings
        
        Args:
            query: User's original query
            sensor_analysis: Analysis text from Sensor Agent
            operator_analysis: Analysis text from Operator Agent
            maintenance_analysis: Analysis text from Maintenance Agent
            sensor_documents: Raw documents from Sensor Agent
            operator_documents: Raw documents from Operator Agent
            maintenance_documents: Raw documents from Maintenance Agent
            context: Additional context
            
        Returns:
            Dictionary with RCA report
        """
        try:
            # Render the Jinja2 template with agent findings and documents
            rendered_prompt = self.rca_template.render(
                query=query,
                sensor_analysis=sensor_analysis or "No sensor analysis available.",
                operator_analysis=operator_analysis or "No operator analysis available.",
                maintenance_analysis=maintenance_analysis or "No maintenance analysis available.",
                sensor_documents=sensor_documents or [],
                operator_documents=operator_documents or [],
                maintenance_documents=maintenance_documents or []
            )
            
            # Generate RCA report using the rendered prompt
            response = self.llm.invoke([HumanMessage(content=rendered_prompt)])
            
            return {
                "success": True,
                "rca_report": response.content,
                "query": query,
                "data_sources": {
                    "sensor_analysis": bool(sensor_analysis),
                    "operator_analysis": bool(operator_analysis),
                    "maintenance_analysis": bool(maintenance_analysis),
                    "sensor_documents": sensor_documents is not None and len(sensor_documents) > 0,
                    "operator_documents": operator_documents is not None and len(operator_documents) > 0,
                    "maintenance_documents": maintenance_documents is not None and len(maintenance_documents) > 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def generate_mitigation_steps(
        self,
        root_cause: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """
        Generate specific mitigation steps based on identified root cause
        
        Args:
            root_cause: Identified root cause
            context: Additional context data
            
        Returns:
            List of mitigation steps
        """
        prompt = f"""Based on the following root cause, generate specific, actionable mitigation steps:

Root Cause: {root_cause}

Context: {context}

Provide 5-7 concrete mitigation steps, including:
1. Immediate actions (0-24 hours)
2. Short-term fixes (1-7 days)
3. Long-term preventive measures (1+ months)

Format each step clearly and concisely."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            # Parse the response into list
            steps = [line.strip() for line in response.content.split('\n') if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-'))]
            return steps
        except Exception as e:
            return [f"Error generating mitigation steps: {str(e)}"]
