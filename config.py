import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Logging Configuration
def setup_logging():
    """Configure logging for the application"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Initialize logging
setup_logging()

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")

# Azure Cognitive Search Configuration
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "")
AZURE_SEARCH_INDEX_SENSOR = os.getenv("AZURE_SEARCH_INDEX_SENSOR", "sensor-data-index")
AZURE_SEARCH_INDEX_OPERATOR = os.getenv("AZURE_SEARCH_INDEX_OPERATOR", "operator-reports-index")
AZURE_SEARCH_INDEX_MAINTENANCE = os.getenv("AZURE_SEARCH_INDEX_MAINTENANCE", "maintenance-logs-index")

# Sensor Data API Configuration (FastAPI endpoint)
SENSOR_DATA_API_URL = os.getenv("SENSOR_DATA_API_URL", "http://localhost:8000")

# Model Parameters
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TOP_K_DOCUMENTS = int(os.getenv("TOP_K_DOCUMENTS", "5"))

# Agent Configuration
MASTER_AGENT_MODEL = os.getenv("MASTER_AGENT_MODEL", "gpt-4")
RCA_GENERATION_MODEL = os.getenv("RCA_GENERATION_MODEL", "gpt-4")

# Paths
DATASETS_PATH = os.path.join(os.path.dirname(__file__), "datasets")
SENSOR_DATA_PATH = os.path.join(DATASETS_PATH, "sensor_data.csv")
MAINTENANCE_LOGS_PATH = os.path.join(DATASETS_PATH, "maintenance_logs.json")
OPERATOR_REPORTS_PATH = os.path.join(DATASETS_PATH, "operator_reports.csv")
