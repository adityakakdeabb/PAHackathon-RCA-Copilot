"""
RCA Copilot Worker - Background Query Processor
Processes RCA queries from the queue and stores results
"""
import logging
import time
import json
from typing import Dict, Any
from redis import Redis
from agents.master_agent import MasterAgent
import redis_config

# Get logger for this module
logger = logging.getLogger(__name__)


class RCAWorker:
    """Worker that processes RCA queries from Redis queue"""
    
    def __init__(self):
        self.master_agent = None
        self.redis_client = None
        self.running = False
        
    def initialize(self):
        """Initialize the worker components"""
        logger.info("=" * 70)
        logger.info("🔧 Initializing RCA Copilot Worker")
        logger.info("=" * 70)
        
        # Check configuration
        if not self._check_configuration():
            logger.error("Configuration check failed. Exiting.")
            return False
        
        # Initialize Redis connection
        try:
            logger.info("Connecting to Redis using connection string...")
            logger.info(f"Redis Host: {redis_config.REDIS_HOST}:{redis_config.REDIS_PORT}")
            logger.info(f"Redis Database: {redis_config.REDIS_DB}")
            
            # Connect to Redis using connection string (supports passwords, custom hosts, etc.)
            self.redis_client = redis_config.get_redis_client()
            self.redis_client.ping()
            
            # Verify we're in the right project
            project_name = self.redis_client.get(redis_config.PROJECT_KEY)
            logger.info(f"✓ Connected to Redis successfully")
            logger.info(f"✓ Project: {redis_config.PROJECT_NAME}")
            logger.info(f"✓ Queue: {redis_config.QUEUE_NAME}")
            if project_name:
                logger.info(f"✓ Project namespace verified: {project_name}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            logger.error("Make sure Redis is accessible:")
            logger.error(f"  Connection: {redis_config.REDIS_CONNECTION_STRING}")
            logger.error("  Check REDIS_CONNECTION_STRING environment variable if using custom connection")
            return False
        
        # Initialize Master Agent
        try:
            logger.info("Initializing RCA Copilot Master Agent...")
            self.master_agent = MasterAgent()
            
            logger.info("=" * 70)
            logger.info("Available Agents:")
            for agent in self.master_agent.get_available_agents():
                logger.info(f"  • {agent['name']}: {agent['description']}")
            logger.info("=" * 70)
            logger.info("✓ Master Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Master Agent: {e}", exc_info=True)
            return False
        
        logger.info("=" * 70)
        logger.info("✓ Worker initialized and ready to process queries")
        logger.info("=" * 70)
        return True
    
    def _check_configuration(self):
        """Check if required configuration is set"""
        import config
        
        warnings = []
        
        if not config.AZURE_OPENAI_ENDPOINT:
            warnings.append("⚠ AZURE_OPENAI_ENDPOINT not set")
        if not config.AZURE_OPENAI_API_KEY:
            warnings.append("⚠ AZURE_OPENAI_API_KEY not set")
        if not config.AZURE_SEARCH_ENDPOINT:
            warnings.append("⚠ AZURE_SEARCH_ENDPOINT not set (will use local data)")
        if not config.AZURE_SEARCH_API_KEY:
            warnings.append("⚠ AZURE_SEARCH_API_KEY not set (will use local data)")
        
        if warnings:
            logger.warning("Configuration Warnings:")
            for warning in warnings:
                logger.warning(f"  {warning}")
            logger.info("→ Create a .env file with your Azure credentials")
            logger.info("→ Or set environment variables directly")
            
            if not config.AZURE_OPENAI_ENDPOINT or not config.AZURE_OPENAI_API_KEY:
                logger.error("Azure OpenAI credentials are required!")
                logger.error("Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
                return False
        
        return True
    
    def process_query(self, query_id: str, query: str) -> Dict[str, Any]:
        """
        Process a single RCA query
        
        Args:
            query_id: Unique identifier for the query
            query: The RCA question to process
            
        Returns:
            Dictionary with processing results
        """
        from datetime import datetime
        start_time = datetime.now()
        
        logger.info("=" * 70)
        logger.info(f"🔍 Processing Query ID: {query_id}")
        logger.info(f"📝 Query: {query}")
        logger.info(f"⏰ Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        try:
            # Update status to processing
            self._update_query_status(query_id, "processing")
            
            # Process the query using Master Agent
            logger.info(f"Invoking Master Agent for query {query_id}...")
            response = self.master_agent.process_query(query)
            
            # Store results
            if response.get("success"):
                rca_report = response.get("rca_report", "No report generated")
                result = {
                    "query": query,
                    "status": "completed",
                    "rca_report": rca_report,
                    "error": None,
                    "timestamp": response.get("timestamp")
                }
                logger.info(f"✓ Query {query_id} completed successfully")
                logger.info(f"Result : {rca_report}")
            else:
                result = {
                    "query": query,
                    "status": "failed",
                    "rca_report": None,
                    "error": response.get("error", "Unknown error"),
                    "timestamp": response.get("timestamp")
                }
                logger.error(f"✗ Query {query_id} failed: {response.get('error')}")
            
            # Store result in Redis using centralized config
            self.redis_client.setex(
                f"{redis_config.RESULT_PREFIX}{query_id}",
                redis_config.RESULT_TTL,  # TTL from config
                json.dumps(result)
            )
            
            # Calculate processing time
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"✓ Query {query_id} processing complete and result stored in Redis")
            logger.info(f"Processing time: {duration:.2f} seconds")
            logger.info(f"Query ID :{query_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query {query_id}: {str(e)}", exc_info=True)
            
            # Calculate processing time even for errors
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "query": query,
                "status": "failed",
                "rca_report": None,
                "error": str(e),
                "timestamp": None
            }
            
            # Store error result using centralized config
            self.redis_client.setex(
                f"{redis_config.RESULT_PREFIX}{query_id}",
                redis_config.RESULT_TTL,
                json.dumps(result)
            )
            
            logger.info("=" * 70)
            logger.info(f"✗ Query {query_id} failed after {duration:.2f} seconds")
            logger.info("=" * 70)
            
            return result
    
    def _update_query_status(self, query_id: str, status: str):
        """Update query status in Redis"""
        try:
            # Use centralized result prefix
            existing_data = self.redis_client.get(f"{redis_config.RESULT_PREFIX}{query_id}")
            if existing_data:
                data = json.loads(existing_data)
                data["status"] = status
                self.redis_client.setex(
                    f"{redis_config.RESULT_PREFIX}{query_id}",
                    redis_config.RESULT_TTL,
                    json.dumps(data)
                )
        except Exception as e:
            logger.warning(f"Could not update status for {query_id}: {e}")
    
    def start(self):
        """Start the worker loop"""
        logger.info("🚀 Worker started - Listening for queries...")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        
        self.running = True
        
        while self.running:
            try:
                # Block and wait for a query from the queue (with 1 second timeout)
                # Use centralized queue name
                result = self.redis_client.blpop(redis_config.QUEUE_NAME, timeout=1)
                
                if result:
                    queue_name, message = result
                    data = json.loads(message)
                    query_id = data.get('query_id')
                    query = data.get('query')
                    
                    logger.info("")
                    logger.info(f"📥 Received query from queue: {query_id}")
                    
                    # Process the query
                    process_result = self.process_query(query_id, query)
                    
                    # Display summary
                    if process_result.get("status") == "completed":
                        logger.info("✅ SUCCESS - Query completed and result available via API")
                    else:
                        logger.error("❌ FAILED - Query processing encountered an error")

                
            except KeyboardInterrupt:
                logger.info("\n⚠ Received shutdown signal")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}", exc_info=True)
                time.sleep(1)  # Prevent rapid error loops
        
        logger.info("Worker stopped")
    
    def stop(self):
        """Stop the worker"""
        self.running = False


def main():
    """Main entry point for the worker"""
    # Initialize worker
    worker = RCAWorker()
    
    if not worker.initialize():
        logger.error("Failed to initialize worker. Exiting.")
        return
    
    try:
        # Start processing queries
        worker.start()
    except KeyboardInterrupt:
        logger.info("\n⚠ Shutting down worker...")
        worker.stop()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    main()
