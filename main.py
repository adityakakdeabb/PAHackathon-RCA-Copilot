"""
Main Application - RCA Copilot API Entry Point
FastAPI-based REST API for RCA queries with Redis queue
"""
import os
import sys
import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from redis import Redis
import redis_config

# Get logger for this module
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RCA Copilot API",
    description="AI-Powered Root Cause Analysis Automation",
    version="1.0.0"
)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Global variables
redis_client: Optional[Redis] = None


# Pydantic models
class AskRequest(BaseModel):
    """Request model for asking RCA questions"""
    query: str


class AskResponse(BaseModel):
    """Response model for ask endpoint"""
    query_id: str
    query: str
    status: str
    message: str


class ResultResponse(BaseModel):
    """Response model for result endpoint"""
    query_id: str
    query: str
    status: str
    rca_report: Optional[str] = None
    error: Optional[str] = None
    timestamp: Optional[str] = None


class RCARequest(BaseModel):
    """Request model for direct RCA generation from alert description"""
    alert_description: str
    alert_id: Optional[str] = None
    machine_id: Optional[str] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None


class RCAResponse(BaseModel):
    """Response model for RCA generation"""
    success: bool
    alert_description: str
    rca_report: Optional[str] = None
    error: Optional[str] = None
    timestamp: str
    routing_decision: Optional[Dict[str, bool]] = None


def check_configuration():
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


@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection on startup"""
    global redis_client
    
    logger.info("=" * 70)
    logger.info("🚀 Starting RCA Copilot API Server")
    logger.info("=" * 70)
    
    try:
        logger.info("Connecting to Redis using connection string...")
        logger.info(f"Redis Host: {redis_config.REDIS_HOST}:{redis_config.REDIS_PORT}")
        logger.info(f"Redis Database: {redis_config.REDIS_DB}")
        
        # Connect to Redis using connection string (supports passwords, custom hosts, etc.)
        redis_client = redis_config.get_redis_client()
        redis_client.ping()
        
        # Set project namespace identifier
        redis_client.set(redis_config.PROJECT_KEY, redis_config.PROJECT_NAME)
        
        logger.info("✓ Connected to Redis successfully")
        logger.info(f"✓ Project: {redis_config.PROJECT_NAME}")
        logger.info(f"✓ Queue: {redis_config.QUEUE_NAME}")
        logger.info("API ready to accept requests")
        logger.info("Make sure the worker is running: python worker.py")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
        logger.error("Make sure Redis is accessible:")
        logger.error(f"  Connection: {redis_config.REDIS_CONNECTION_STRING}")
        logger.error("  Check REDIS_CONNECTION_STRING environment variable if using custom connection")
        redis_client = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RCA Copilot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "ask": "/ask - POST your RCA query (queued processing)",
            "result": "/result/{query_id} - GET the result of your query",
            "get_rca": "/get_rca - POST alert description for immediate RCA generation",
            "results": "/results - GET list of all queries",
            "health": "/health - Check API health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if redis_client is None:
        return {
            "status": "unhealthy",
            "message": "Redis not connected"
        }
    
    try:
        redis_client.ping()
        # Check queue length
        queue_length = redis_client.llen(redis_config.QUEUE_NAME)
        return {
            "status": "healthy",
            "message": "RCA Copilot API is running",
            "redis": "connected",
            "project": redis_config.PROJECT_NAME,
            "pending_queries": queue_length
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Redis error: {str(e)}"
        }


@app.post("/ask", response_model=AskResponse)
async def ask_query(request: AskRequest):
    """
    Submit an RCA query for processing
    
    Args:
        request: AskRequest containing the query
        
    Returns:
        AskResponse with query_id and status
    """
    if redis_client is None:
        raise HTTPException(
            status_code=503,
            detail="Redis not connected. Please check server logs."
        )
    
    try:
        # Generate unique query ID
        query_id = str(uuid.uuid4())
        
        logger.info(f"Received query [ID: {query_id}]: {request.query}")
        
        # Create query message
        query_message = {
            "query_id": query_id,
            "query": request.query,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store initial status in Redis
        initial_result = {
            "query": request.query,
            "status": "queued",
            "rca_report": None,
            "error": None,
            "timestamp": None
        }
        redis_client.setex(
            f"{redis_config.RESULT_PREFIX}{query_id}",
            redis_config.RESULT_TTL,
            json.dumps(initial_result)
        )
        
        # Push query to Redis queue for worker to process
        redis_client.rpush(redis_config.QUEUE_NAME, json.dumps(query_message))
        
        logger.info(f"Query {query_id} added to processing queue")
        
        return AskResponse(
            query_id=query_id,
            query=request.query,
            status="queued",
            message=f"Query queued for processing. Use /result/{query_id} to get results."
        )
        
    except Exception as e:
        logger.error(f"Error queueing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error queueing query: {str(e)}"
        )


@app.get("/result/{query_id}", response_model=ResultResponse)
async def get_result(query_id: str):
    """
    Get the result of a previously submitted query
    
    Args:
        query_id: The unique identifier for the query
        
    Returns:
        ResultResponse with the RCA report or error
    """
    if redis_client is None:
        raise HTTPException(
            status_code=503,
            detail="Redis not connected. Please check server logs."
        )
    
    try:
        # Get result from Redis
        result_data = redis_client.get(f"{redis_config.RESULT_PREFIX}{query_id}")
        
        if not result_data:
            raise HTTPException(
                status_code=404,
                detail=f"Query ID '{query_id}' not found. Please check the query_id or submit a new query using /ask."
            )
        
        result = json.loads(result_data)
        
        return ResultResponse(
            query_id=query_id,
            query=result["query"],
            status=result["status"],
            rca_report=result["rca_report"],
            error=result["error"],
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving result: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving result: {str(e)}"
        )


@app.get("/results")
async def list_results():
    """
    List all query results stored in Redis
    
    Returns:
        Dictionary of all queries and their statuses
    """
    if redis_client is None:
        raise HTTPException(
            status_code=503,
            detail="Redis not connected. Please check server logs."
        )
    
    try:
        # Get all result keys from Redis for this project
        keys = redis_client.keys(f"{redis_config.RESULT_PREFIX}*")
        queries = []
        
        for key in keys:
            query_id = key.replace(redis_config.RESULT_PREFIX, "")
            result_data = redis_client.get(key)
            if result_data:
                result = json.loads(result_data)
                queries.append({
                    "query_id": query_id,
                    "query": result["query"],
                    "status": result["status"],
                    "timestamp": result["timestamp"]
                })
        
        return {
            "total_queries": len(queries),
            "queries": queries
        }
    except Exception as e:
        logger.error(f"Error listing results: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error listing results: {str(e)}"
        )


@app.post("/get_rca", response_model=RCAResponse)
async def get_rca(request: RCARequest):
    """
    Generate RCA report directly from an alert description
    
    This endpoint processes an alert description and generates a comprehensive 
    Root Cause Analysis by consulting relevant agents and documents.
    
    Args:
        request: RCARequest containing alert_description and optional metadata
        
    Returns:
        RCAResponse with the generated RCA report
        
    Example:
        POST /get_rca
        {
            "alert_description": "Sudden temperature spike detected in compressor chamber exceeding 90°C",
            "machine_id": "MCH_012",
            "alert_type": "High Temperature",
            "severity": "Critical"
        }
    """
    try:
        logger.info("=" * 70)
        logger.info(f"Received RCA request for alert description")
        if request.machine_id:
            logger.info(f"Machine ID: {request.machine_id}")
        if request.alert_type:
            logger.info(f"Alert Type: {request.alert_type}")
        logger.info(f"Description: {request.alert_description}")
        logger.info("=" * 70)
        
        # Import MasterAgent here to avoid startup issues
        from agents.master_agent import MasterAgent
        
        # Initialize Master Agent
        master_agent = MasterAgent()
        
        # Build a comprehensive query from the alert information
        query_parts = []
        
        if request.alert_type:
            query_parts.append(f"Alert Type: {request.alert_type}")
        
        if request.machine_id:
            query_parts.append(f"Machine: {request.machine_id}")
        
        if request.severity:
            query_parts.append(f"Severity: {request.severity}")
        
        query_parts.append(f"Issue Description: {request.alert_description}")
        query_parts.append("Please provide a detailed root cause analysis with:")
        query_parts.append("1. Analysis of sensor data and anomalies")
        query_parts.append("2. Review of operator reports and observations")
        query_parts.append("3. Examination of maintenance history")
        query_parts.append("4. Identified root causes")
        query_parts.append("5. Recommended mitigation and preventive actions")
        
        query = "\n".join(query_parts)
        
        logger.info(f"Constructed query for RCA analysis")
        
        # Process the query through the Master Agent
        result = master_agent.process_query(query)
        
        if result.get("success"):
            logger.info("✓ RCA generated successfully")
            
            return RCAResponse(
                success=True,
                alert_description=request.alert_description,
                rca_report=result.get("rca_report"),
                error=None,
                timestamp=result.get("timestamp"),
                routing_decision=result.get("routing_decision")
            )
        else:
            logger.error(f"RCA generation failed: {result.get('error')}")
            
            return RCAResponse(
                success=False,
                alert_description=request.alert_description,
                rca_report=None,
                error=result.get("error", "Unknown error occurred"),
                timestamp=result.get("timestamp"),
                routing_decision=None
            )
        
    except Exception as e:
        logger.error(f"Error in get_rca endpoint: {str(e)}", exc_info=True)
        
        return RCAResponse(
            success=False,
            alert_description=request.alert_description,
            rca_report=None,
            error=str(e),
            timestamp=datetime.now().isoformat(),
            routing_decision=None
        )



if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("🚀 Starting RCA Copilot API Server")
    logger.info("=" * 70)
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Submit Query: POST http://localhost:8000/ask")
    logger.info("Get Result: GET http://localhost:8000/result/{query_id}")
    logger.info("Health Check: http://localhost:8000/health")
    logger.info("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
