# 📁 Project Structure - RCA Copilot

## Complete File Tree

```
RCA_Copilot_Kraken/
│
├── 📄 config.py                    # Configuration & environment variables
├── 📄 main.py                      # Main application entry point
├── 📄 examples.py                  # Usage examples and demonstrations
├── 📄 dataset_generator.py         # Generate sample datasets
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Example environment configuration
├── 📄 .gitignore                   # Git ignore rules
├── 📄 README.md                    # Comprehensive documentation
├── 📄 QUICKSTART.md               # Quick start guide
│
├── 📁 agents/                      # Agent implementations
│   ├── 📄 __init__.py             # Package initialization
│   ├── 📄 base_agent.py           # Base agent class & utilities
│   ├── 📄 master_agent.py         # Master orchestrator agent ⭐
│   ├── 📄 sensor_agent.py         # Sensor data analysis agent
│   ├── 📄 operator_agent.py       # Operator reports agent
│   └── 📄 maintenance_agent.py    # Maintenance logs agent
│
├── 📁 models/                      # LangChain models & chains
│   ├── 📄 __init__.py             # Package initialization
│   └── 📄 rca_chain.py            # RCA generation chain ⭐
│
├── 📁 api/                         # FastAPI REST API
│   └── 📄 main.py                 # API server implementation
│
└── 📁 datasets/                    # Data sources
    ├── 📄 sensor_data.csv         # Time-series sensor readings
    ├── 📄 operator_reports.csv    # Operator incident reports
    └── 📄 maintenance_logs.json   # Maintenance history
```

## 🗂️ File Descriptions

### Core Files

#### `config.py`
- Environment variable loading
- Azure OpenAI configuration
- Azure Cognitive Search settings
- Model parameters and paths

#### `main.py` ⭐ Main Entry Point
- Interactive chat interface
- Example query runner
- Single query mode
- Configuration validation

#### `examples.py`
- 8 comprehensive usage examples
- Direct agent access patterns
- Different query types

#### `requirements.txt`
- All Python dependencies
- LangChain packages
- Azure SDKs
- FastAPI for API mode

### Agent Implementations

#### `agents/base_agent.py`
- Abstract base class for all agents
- AgentResponse standardized format
- Common LLM initialization
- Shared utilities

#### `agents/master_agent.py` ⭐ Orchestrator
- **Main orchestrator** that routes queries
- Uses LLM to determine which agents to invoke
- Aggregates responses from specialized agents
- Generates final RCA report via RCA Chain
- Key methods:
  - `process_query()` - Main entry point
  - `_route_query()` - LLM-based routing
  - `_invoke_agents()` - Parallel agent execution
  - `_generate_rca_report()` - Final report generation

#### `agents/sensor_agent.py`
- Analyzes time-series sensor data
- Detects anomalies and patterns
- Machine timeline reconstruction
- Statistics and critical event tracking
- Works with local CSV data

#### `agents/operator_agent.py`
- Queries operator incident reports
- Azure Cognitive Search integration
- Local data fallback
- Keyword-based relevance scoring
- Document retrieval and ranking

#### `agents/maintenance_agent.py`
- Queries maintenance history
- Component failure pattern analysis
- Azure Cognitive Search integration
- Local data fallback
- Maintenance timeline for machines

### LangChain Models

#### `models/rca_chain.py` ⭐ RCA Generation
- LangChain-based RCA report generation
- Comprehensive prompt templates
- Data formatting for LLM context
- Key methods:
  - `generate_rca_report()` - Main RCA generation
  - `generate_mitigation_steps()` - Specific mitigation advice
  - `_format_*()` - Data formatters for each source

### API Implementation

#### `api/main.py`
- FastAPI REST API server
- `/query` endpoint - Full RCA query
- `/chat` endpoint - Simplified chat
- `/health` endpoint - Health check
- `/agents` endpoint - Available agents
- Automatic OpenAPI documentation

### Data Files

#### `datasets/sensor_data.csv`
- **10,000 sensor readings**
- Columns: timestamp, machine_id, sensor_type, sensor_value, unit, status
- Sensor types: Temperature, Vibration, Pressure
- Status levels: Normal, Warning, Critical

#### `datasets/operator_reports.csv`
- **10,000 operator reports**
- Columns: report_id, machine_id, operator_name, shift, date, incident_description, initial_action, severity, status
- Severity: Low, Medium, High, Critical
- Status: Open, Investigating, Closed

#### `datasets/maintenance_logs.json`
- **10,000 maintenance logs**
- Fields: log_id, machine_id, date, maintenance_type, components_checked, actions_taken, technician, downtime_hours, remarks
- Types: Preventive, Corrective, Emergency

## 🔄 Data Flow

### Query Processing Flow

```
1. User Query
   ↓
2. main.py → MasterAgent.process_query()
   ↓
3. MasterAgent._route_query() [Uses LLM]
   ↓
4. Routing Decision:
   • Sensor Agent? YES/NO
   • Operator Agent? YES/NO
   • Maintenance Agent? YES/NO
   ↓
5. MasterAgent._invoke_agents()
   ├─→ SensorAgent.process_query() → Local CSV
   ├─→ OperatorAgent.process_query() → Azure Search/Local CSV
   └─→ MaintenanceAgent.process_query() → Azure Search/Local JSON
   ↓
6. Aggregate Agent Responses
   ↓
7. MasterAgent._generate_rca_report()
   ↓
8. RCAChain.generate_rca_report() [LangChain + GPT-4]
   ↓
9. Final RCA Report
   ↓
10. Return to User
```

## 🎯 Key Components

### Master Agent (Orchestrator)
- **Location**: `agents/master_agent.py`
- **Purpose**: Main orchestrator that routes queries to specialized agents
- **Technology**: LangChain, Azure OpenAI
- **Key Feature**: Intelligent routing based on query content

### Specialized Agents
1. **Sensor Agent**: Time-series data analysis
2. **Operator Agent**: Incident report retrieval
3. **Maintenance Agent**: Maintenance history retrieval

### RCA Chain
- **Location**: `models/rca_chain.py`
- **Purpose**: Generate comprehensive RCA reports
- **Technology**: LangChain with custom prompts
- **Output**: Structured RCA with timeline, root cause, mitigation steps

## 🚀 Getting Started

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: Copy `.env.example` to `.env` and add credentials
3. **Generate Data**: `python dataset_generator.py` (if needed)
4. **Run**: `python main.py`

## 📊 Data Sources

### Local Data (Default)
- Works out of the box
- No Azure services required
- Uses CSV/JSON files in `datasets/`

### Azure Cognitive Search (Production)
- Configure in `.env`
- Better search relevance
- Scalable for large datasets
- Automatic fallback to local data if unavailable

## 🔧 Customization Points

1. **Add Custom Agents**: Extend `BaseAgent` in `agents/`
2. **Modify Prompts**: Edit templates in `models/rca_chain.py`
3. **Change Routing Logic**: Update `MasterAgent._route_query()`
4. **Add Data Sources**: Extend agent `process_query()` methods
5. **Customize Output**: Modify `RCAChain._format_*()` methods

## 📝 Environment Variables

Required in `.env`:
```
AZURE_OPENAI_ENDPOINT          # Required
AZURE_OPENAI_API_KEY           # Required
AZURE_OPENAI_DEPLOYMENT_NAME   # Required
```

Optional in `.env`:
```
AZURE_SEARCH_ENDPOINT          # Optional (uses local data if not set)
AZURE_SEARCH_API_KEY           # Optional
TEMPERATURE                    # Default: 0.7
MAX_TOKENS                     # Default: 2000
TOP_K_DOCUMENTS               # Default: 5
```

## 🎓 Learning Path

1. Start with `QUICKSTART.md`
2. Run `python examples.py` for usage patterns
3. Explore `agents/master_agent.py` to understand orchestration
4. Study `models/rca_chain.py` to see LangChain integration
5. Customize agents for your specific use case

---

**Complete RCA Copilot Implementation! 🎉**
