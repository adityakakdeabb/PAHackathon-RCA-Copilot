# 🚀 Quick Start Guide - RCA Copilot

## Step-by-Step Setup (5 minutes)

### Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

### Step 2: Configure Azure OpenAI

Create a `.env` file in the project root:

```powershell
copy .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### Step 3: Generate Sample Data (Optional)

If you don't have data in the `datasets` folder:

```powershell
python dataset_generator.py
```

This creates:
- ✅ 10,000 sensor readings
- ✅ 10,000 operator reports  
- ✅ 10,000 maintenance logs

### Step 4: Run the Application

```powershell
python main.py
```

### Step 5: Try Example Queries

Select **Interactive Chat Mode** and try:

```
What caused the temperature spike in MCH_003?
```

```
Show all critical sensor alerts and related maintenance records
```

```
Which components fail most frequently?
```

## 🎯 Your First Query

```
You: Investigate vibration issues in machine MCH_003 with all related data

🤖 RCA Copilot: Processing your query...

Routing Decision: 
  ✓ Sensor Agent
  ✓ Operator Agent
  ✓ Maintenance Agent

→ Invoking Sensor Data Agent...
  ✓ Sensor Agent completed

→ Invoking Operator Agent...
  ✓ Operator Agent completed (12 documents)

→ Invoking Maintenance Agent...
  ✓ Maintenance Agent completed (8 documents)

→ Generating RCA Report using LLM Chain...
  ✓ RCA Report generated

====================================================================
RCA REPORT
====================================================================

## Incident Timeline
- October 15, 08:30 - Vibration levels exceeded normal threshold...
- October 15, 09:15 - Operator reported unusual noise...
- October 15, 10:00 - Emergency maintenance initiated...

## Root Cause Identification
Primary Cause: Bearing Assembly degradation due to...

## Corrective Actions
1. Immediate: Replace bearing assembly
2. Short-term: Increase vibration monitoring frequency
3. Long-term: Implement predictive maintenance...

[Full report continues...]
====================================================================
```

## 📊 Architecture Overview

```
Your Query
    ↓
Master Agent (Orchestrator)
    ↓
├── Sensor Agent → Local CSV Data
├── Operator Agent → Azure Search or Local CSV
└── Maintenance Agent → Azure Search or Local JSON
    ↓
All Data Combined
    ↓
LangChain RCA Chain (GPT-4)
    ↓
Comprehensive RCA Report
```

## 🔧 Common Tasks

### Query a Specific Machine

```python
from agents.master_agent import MasterAgent

agent = MasterAgent()
response = agent.process_query(
    "Show all issues for this machine",
    machine_id="MCH_003"
)
print(response['rca_report'])
```

### Filter by Date Range

```python
response = agent.process_query(
    "Analyze incidents from last week",
    start_date="2025-10-01",
    end_date="2025-10-07"
)
```

### Get Only Critical Issues

```python
response = agent.process_query(
    "Show critical sensor alerts",
    status="Critical"
)
```

## 🌐 Run as API Server

```powershell
python api/main.py
```

Then visit: http://localhost:8000/docs

Test with curl:

```powershell
curl -X POST "http://localhost:8000/query" `
  -H "Content-Type: application/json" `
  -d '{"query": "What caused the temperature spike?"}'
```

## 📚 Run Examples

```powershell
python examples.py
```

Choose from 8 different usage examples!

## ⚡ Pro Tips

1. **Use specific machine IDs** for faster, more focused results
2. **Include time ranges** for timeline reconstruction
3. **Mention sensor types** (temperature, vibration, pressure) for targeted analysis
4. **Ask for patterns** to get fleet-wide insights
5. **Request mitigation steps** explicitly for actionable recommendations

## 🆘 Troubleshooting

### Error: "langchain could not be resolved"
```powershell
pip install langchain langchain-openai langchain-community
```

### Error: "Azure OpenAI credentials not set"
Check your `.env` file and ensure credentials are correct.

### Error: "No module named 'agents'"
Make sure you're running from the project root directory.

### No results returned
- Check that datasets exist in the `datasets/` folder
- Run `python dataset_generator.py` to generate sample data

## 🎓 Next Steps

1. ✅ Explore `examples.py` for advanced usage patterns
2. ✅ Customize prompts in `models/rca_chain.py`
3. ✅ Add custom agents in the `agents/` folder
4. ✅ Set up Azure Cognitive Search for production
5. ✅ Deploy as FastAPI service with `api/main.py`

## 📖 Documentation

- Full README: `README.md`
- Configuration: `config.py`
- Agent Architecture: `agents/base_agent.py`

---

**Ready to investigate root causes with AI! 🚀**
