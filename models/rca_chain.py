"""
RCA Chain - LangChain-based RCA Report Generation
Generates Root Cause Analysis reports with mitigation steps using LLM
"""
from typing import Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
import config


class RCAChain:
    """LangChain-based RCA report generation"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.rca_prompt = self._create_rca_prompt()
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM for RCA generation"""
        return AzureChatOpenAI(
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            deployment_name=config.RCA_GENERATION_MODEL,
            temperature=0.7,  # Slightly creative for recommendations
            max_tokens=300  # Reduced for concise responses
        )
    
    def _create_rca_prompt(self) -> ChatPromptTemplate:
        """Create prompt template for RCA generation"""
        system_template = """You are an expert industrial engineer specializing in Root Cause Analysis (RCA) for manufacturing equipment failures. 

Your task is to provide a CONCISE root cause analysis in exactly 3-4 sentences:
1. First sentence: State the primary root cause
2. Second sentence: Mention key contributing factors or evidence
3. Third sentence: Provide the most critical immediate action
4. Fourth sentence (optional): Brief preventive recommendation

Be specific, technical, and direct. No headers, bullet points, or lengthy explanations."""

        human_template = """## User Query
{query}

## Sensor Data Analysis
{sensor_data}

## Operator Reports
{operator_reports}

## Maintenance Logs
{maintenance_logs}

## Additional Context
{context}

Provide a concise 3-4 sentence Root Cause Analysis based on the above information."""

        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        
        return ChatPromptTemplate.from_messages([system_message, human_message])
    
    def generate_rca_report(
        self,
        query: str,
        sensor_data: Dict[str, Any] = None,
        operator_reports: List[Dict[str, Any]] = None,
        maintenance_logs: List[Dict[str, Any]] = None,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate RCA report using LangChain
        
        Args:
            query: User's original query
            sensor_data: Sensor data analysis from Sensor Agent
            operator_reports: Documents from Operator Agent
            maintenance_logs: Documents from Maintenance Agent
            context: Additional context
            
        Returns:
            Dictionary with RCA report
        """
        try:
            # Format the input data
            sensor_summary = self._format_sensor_data(sensor_data)
            operator_summary = self._format_operator_reports(operator_reports)
            maintenance_summary = self._format_maintenance_logs(maintenance_logs)
            
            # Generate the prompt
            prompt_value = self.rca_prompt.format_prompt(
                query=query,
                sensor_data=sensor_summary,
                operator_reports=operator_summary,
                maintenance_logs=maintenance_summary,
                context=context
            )
            
            # Generate RCA report
            response = self.llm.invoke(prompt_value.to_messages())
            
            return {
                "success": True,
                "rca_report": response.content,
                "query": query,
                "data_sources": {
                    "sensor_data": sensor_data is not None,
                    "operator_reports": operator_reports is not None and len(operator_reports) > 0,
                    "maintenance_logs": maintenance_logs is not None and len(maintenance_logs) > 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _format_sensor_data(self, sensor_data: Dict[str, Any]) -> str:
        """Format sensor data for prompt"""
        if not sensor_data:
            return "No sensor data available."
        
        formatted = "### Sensor Data Summary\n\n"
        
        if 'statistics' in sensor_data:
            stats = sensor_data['statistics']
            formatted += f"- Total Records: {stats.get('total_records', 0)}\n"
            formatted += f"- Machines Affected: {stats.get('machines_affected', 0)}\n"
            formatted += f"- Critical Alerts: {stats.get('critical_alerts', 0)}\n"
            formatted += f"- Warning Alerts: {stats.get('warning_alerts', 0)}\n"
            formatted += f"- Status Distribution: {stats.get('status_distribution', {})}\n\n"
        
        if 'anomaly_patterns' in sensor_data and sensor_data['anomaly_patterns']:
            formatted += "**Anomaly Patterns:**\n"
            for pattern in sensor_data['anomaly_patterns'][:5]:
                formatted += f"- {pattern['machine_id']} ({pattern['sensor_type']}): "
                formatted += f"Avg={pattern['avg_value']}, Max={pattern['max_value']}, "
                formatted += f"Alerts={pattern['alert_count']}\n"
            formatted += "\n"
        
        if 'recent_critical_events' in sensor_data and sensor_data['recent_critical_events']:
            formatted += "**Recent Critical Events:**\n"
            for event in sensor_data['recent_critical_events'][:5]:
                formatted += f"- {event['timestamp']}: {event['machine_id']} - "
                formatted += f"{event['sensor_type']}={event['sensor_value']}{event['unit']} "
                formatted += f"({event['status']})\n"
        
        return formatted
    
    def _format_operator_reports(self, operator_reports: List[Dict[str, Any]]) -> str:
        """Format operator reports for prompt"""
        if not operator_reports or len(operator_reports) == 0:
            return "No operator reports available."
        
        formatted = "### Operator Reports\n\n"
        
        for i, report in enumerate(operator_reports[:5], 1):
            formatted += f"**Report #{i}** (ID: {report.get('report_id', 'N/A')})\n"
            formatted += f"- Machine: {report.get('machine_id', 'N/A')}\n"
            formatted += f"- Date: {report.get('date', 'N/A')}\n"
            formatted += f"- Operator: {report.get('operator_name', 'N/A')} ({report.get('shift', 'N/A')} shift)\n"
            formatted += f"- Severity: {report.get('severity', 'N/A')}\n"
            formatted += f"- Status: {report.get('status', 'N/A')}\n"
            formatted += f"- Incident: {report.get('incident_description', 'N/A')}\n"
            formatted += f"- Action Taken: {report.get('initial_action', 'N/A')}\n\n"
        
        return formatted
    
    def _format_maintenance_logs(self, maintenance_logs: List[Dict[str, Any]]) -> str:
        """Format maintenance logs for prompt"""
        if not maintenance_logs or len(maintenance_logs) == 0:
            return "No maintenance logs available."
        
        formatted = "### Maintenance Logs\n\n"
        
        for i, log in enumerate(maintenance_logs[:5], 1):
            formatted += f"**Log #{i}** (ID: {log.get('log_id', 'N/A')})\n"
            formatted += f"- Machine: {log.get('machine_id', 'N/A')}\n"
            formatted += f"- Date: {log.get('date', 'N/A')}\n"
            formatted += f"- Type: {log.get('maintenance_type', 'N/A')}\n"
            formatted += f"- Technician: {log.get('technician', 'N/A')}\n"
            formatted += f"- Downtime: {log.get('downtime_hours', 0)} hours\n"
            formatted += f"- Components: {', '.join(log.get('components_checked', []))}\n"
            formatted += f"- Actions: {log.get('actions_taken', 'N/A')}\n"
            formatted += f"- Remarks: {log.get('remarks', 'N/A')}\n\n"
        
        return formatted
    
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
