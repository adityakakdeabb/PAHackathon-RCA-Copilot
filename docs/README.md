# 🤖 RCA Copilot - AI-Powered Root Cause Analysis Automation

An intelligent AI copilot that accelerates fault investigation by combining time-series sensor data, maintenance logs, and operator reports into a unified diagnostic experience. Engineers and quality teams can interact with the copilot via natural language to reconstruct incident timelines, identify causal patterns, and generate RCA reports with recommended corrective actions.

## 🎯 Problem Statement

AI Copilot for RCA Automation reduces downtime, prevents repeat failures, and boosts operational reliability by:
- **Combining Multiple Data Sources**: Sensor data, maintenance logs, and operator reports
- **Natural Language Interface**: Engineers query in plain English
- **Automated Timeline Reconstruction**: Build incident timelines automatically
- **Pattern Identification**: Surface insights from historical events
- **Standardized RCA Workflows**: Generate comprehensive RCA reports with mitigation steps

## 🏗️ Architecture

```
┌─────────────┐
│   User      │──── Natural Language Query
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Master Agent    │──── Orchestrator (LangChain)
│  (Orchestrator)  │
└────┬─────────────┘
     │
     ├──────────────┬──────────────┬─────────────────┐
     ▼              ▼              ▼                 ▼
┌─────────┐   ┌──────────┐   ┌──────────┐   ┌──────────────┐
│ Sensor  │   │ Operator │   │Maintenance│   │  RCA Chain   │
│  Agent  │   │  Agent   │   │  Agent    │   │    (LLM)     │
└────┬────┘   └────┬─────┘   └────┬─────┘   └──────────────┘
     │             │              │
     │             ▼              ▼
     │      ┌──────────────────────┐
     │      │ Azure Cognitive      │
     │      │ Search (Vector DB)   │
     │      └──────────────────────┘
     ▼
┌──────────┐
│ Local    │
│ Sensor   │
│ Data     │
└──────────┘
```

## 📁 Project Structure

```
RCA_Copilot_Kraken/
├── agents/
│   ├── base_agent.py          # Base agent class & utilities
│   ├── master_agent.py        # Master orchestrator agent
│   ├── sensor_agent.py        # Sensor data analysis agent
│   ├── operator_agent.py      # Operator reports agent
│   └── maintenance_agent.py   # Maintenance logs agent
├── models/
│   └── rca_chain.py           # LangChain RCA generation
├── datasets/
│   ├── sensor_data.csv        # Time-series sensor data
│   ├── operator_reports.csv   # Operator incident reports
│   └── maintenance_logs.json  # Maintenance history
├── config.py                  # Configuration & environment
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
└── .env                       # Environment variables (create this)
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9 or higher
- Azure OpenAI API access
- (Optional) Azure Cognitive Search for production use

### 2. Installation

```powershell
# Clone or navigate to the project directory
cd RCA_Copilot_Kraken

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the project root:

```env
# Azure OpenAI Configuration (REQUIRED)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# Azure Cognitive Search (OPTIONAL - will use local data if not set)
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_OPERATOR=operator-reports-index
AZURE_SEARCH_INDEX_MAINTENANCE=maintenance-logs-index

# Model Parameters
TEMPERATURE=0.7
MAX_TOKENS=2000
TOP_K_DOCUMENTS=5
```

### 4. Generate Sample Data (if needed)

```powershell
python dataset_generator.py
```

This creates:
- `datasets/sensor_data.csv` - 10,000 sensor readings
- `datasets/operator_reports.csv` - 10,000 operator reports
- `datasets/maintenance_logs.json` - 10,000 maintenance logs

### 5. Run the Application

```powershell
python main.py
```

## 💡 Usage Examples

### Interactive Mode

```
Select Mode:
  1. Interactive Chat Mode
  2. Run Example Queries
  3. Single Query Mode

Enter choice (1-3): 1

You: What caused the temperature spike in MCH_003 last week?

🤖 RCA Copilot: Processing your query...

====================================================================
RCA REPORT
====================================================================
[Comprehensive RCA report with timeline, root cause, and mitigation steps]
====================================================================
```

### Example Queries

Here are some powerful queries you can try:

#### 1. Timeline Reconstruction
```
"Show me the complete incident timeline for MCH_003 on October 15th"
```

#### 2. Pattern Analysis
```
"What are the common patterns in machines with vibration alerts?"
```

#### 3. Specific Investigation
```
"Investigate the temperature spike in MCH_045 - include sensor data, operator reports, and maintenance history"
```

#### 4. Component Analysis
```
"Which components fail most frequently and what maintenance was performed?"
```

#### 5. Critical Alerts
```
"Show all critical sensor alerts from the last 48 hours with associated maintenance records"
```

#### 6. Preventive Insights
```
"Based on historical data, which machines are likely to fail next?"
```

## 🔧 Key Components

### Master Agent
The orchestrator that:
- Analyzes user queries using LLM
- Routes to appropriate specialized agents
- Aggregates responses
- Generates comprehensive RCA reports

### Sensor Data Agent
Handles:
- Time-series sensor analysis (temperature, vibration, pressure)
- Anomaly detection
- Status tracking (Normal, Warning, Critical)
- Machine timeline reconstruction

### Operator Agent
Handles:
- Operator incident reports
- Initial actions documentation
- Severity classification
- Real-time observations

### Maintenance Agent
Handles:
- Maintenance history
- Component failure patterns
- Technician actions
- Downtime analysis

### RCA Chain (LangChain)
- Uses Azure OpenAI GPT-4
- Combines all data sources
- Generates structured RCA reports with:
  - Incident Timeline
  - Root Cause Identification
  - Causal Pattern Analysis
  - Impact Assessment
  - Corrective Actions
  - Long-term Recommendations

## 🔍 How It Works

### 1. Query Processing
```python
User Query → Master Agent → LLM Routing Decision
```

### 2. Agent Invocation
```python
Master Agent → [Sensor Agent, Operator Agent, Maintenance Agent]
                     ↓              ↓                 ↓
              Local Data    Azure Search      Azure Search
```

### 3. Data Aggregation
```python
Agent Responses → Master Agent → Context Building
```

### 4. RCA Generation
```python
Context + User Query → RCA Chain (LangChain + GPT-4) → RCA Report
```

## 📊 Data Sources

### Sensor Data (`sensor_data.csv`)
- **Fields**: timestamp, machine_id, sensor_type, sensor_value, unit, status
- **Sensor Types**: Temperature (°C), Vibration (mm/s), Pressure (bar)
- **Status Levels**: Normal, Warning, Critical

### Operator Reports (`operator_reports.csv`)
- **Fields**: report_id, machine_id, operator_name, shift, date, incident_description, initial_action, severity, status
- **Severity Levels**: Low, Medium, High, Critical
- **Status**: Open, Investigating, Closed

### Maintenance Logs (`maintenance_logs.json`)
- **Fields**: log_id, machine_id, date, maintenance_type, components_checked, actions_taken, technician, downtime_hours, remarks
- **Maintenance Types**: Preventive, Corrective, Emergency

## 🎨 Customization

### Adding Custom Agents

```python
from agents.base_agent import BaseAgent, AgentResponse

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Custom Agent",
            description="Your custom agent description"
        )
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        # Your implementation
        return AgentResponse(
            agent_name=self.name,
            success=True,
            data=your_data
        ).to_dict()
```

### Modifying RCA Prompts

Edit `models/rca_chain.py` to customize the prompt templates:

```python
def _create_rca_prompt(self):
    system_template = """Your custom system prompt..."""
    # Modify templates as needed
```

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use Azure Key Vault** for production credentials
3. **Rotate API keys** regularly
4. **Implement rate limiting** for production use
5. **Validate user inputs** before processing

## 🚀 Production Deployment

### Azure Cognitive Search Setup

1. Create Azure Cognitive Search service
2. Create indexes for operator reports and maintenance logs
3. Upload data using Azure SDK or portal
4. Enable semantic search for better relevance

### Scaling Considerations

- Use **Azure Functions** for serverless deployment
- Implement **caching** for frequent queries
- Use **Azure Redis** for session management
- Deploy as **Azure Container Apps** for high availability

## 📈 Performance Optimization

1. **Parallel Agent Execution**: Agents run in parallel where possible
2. **Local Data Fallback**: Works without Azure Search using local data
3. **Prompt Optimization**: Efficient token usage in LLM calls
4. **Lazy Loading**: Data loaded only when needed

## 🧪 Testing

```python
# Test individual agents
from agents.sensor_agent import SensorDataAgent

agent = SensorDataAgent()
result = agent.process_query("Show critical alerts", machine_id="MCH_003")
print(result)
```

## 🤝 Contributing

This is a reference implementation. Customize it for your specific:
- Data schemas
- Business logic
- Reporting requirements
- Integration points

## 📝 License

Internal ABB project - modify as needed for your use case.

## 🆘 Troubleshooting

### Issue: "Import langchain could not be resolved"
**Solution**: Install dependencies: `pip install -r requirements.txt`

### Issue: "Azure OpenAI credentials not set"
**Solution**: Create `.env` file with your Azure OpenAI credentials

### Issue: "No data found"
**Solution**: Run `python dataset_generator.py` to generate sample data

### Issue: "Azure Search errors"
**Solution**: System will automatically fall back to local data search

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review configuration in `config.py`
3. Verify `.env` file settings
4. Check Azure service status

---

**Built with ❤️ using LangChain, Azure OpenAI, and Python**
