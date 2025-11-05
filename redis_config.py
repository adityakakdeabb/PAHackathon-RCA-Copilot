"""
Redis Configuration for RCA Copilot
Centralized Redis settings for API and Worker
Supports both connection string and individual parameters
"""
import os
from redis import Redis
from urllib.parse import urlparse

# Redis Connection String (preferred method)
# Format: redis://[[username]:[password]]@host:port/database
# Can be set via environment variable REDIS_CONNECTION_STRING
# Examples:
#   redis://localhost:6379/1
#   redis://:password@localhost:6379/1
#   redis://username:password@redis-server:6379/1
REDIS_CONNECTION_STRING = os.getenv(
    'REDIS_CONNECTION_STRING',
    'redis://localhost:6379/1'  # Default: localhost, port 6379, database 1
)

# Parse connection string to extract individual components
_parsed_url = urlparse(REDIS_CONNECTION_STRING)
REDIS_HOST = _parsed_url.hostname or 'localhost'
REDIS_PORT = _parsed_url.port or 6379
REDIS_DB = int(_parsed_url.path.lstrip('/')) if _parsed_url.path and _parsed_url.path != '/' else 1
REDIS_PASSWORD = _parsed_url.password

# Redis Keys/Namespaces
PROJECT_NAME = 'PA_Hackathon'
QUEUE_NAME = 'pa_hackathon:rca_queue'
RESULT_PREFIX = 'pa_hackathon:result:'
PROJECT_KEY = 'pa_hackathon:project:name'

# Redis TTL Settings
RESULT_TTL = 3600  # Results expire after 1 hour (in seconds)


def get_redis_client():
    """
    Get Redis client instance using connection string (RECOMMENDED)
    
    Returns:
        Redis: Configured Redis client instance
        
    Example:
        redis_client = get_redis_client()
        redis_client.ping()
    """
    return Redis.from_url(
        REDIS_CONNECTION_STRING,
        decode_responses=True
    )


def get_redis_config():
    """
    Get Redis configuration dictionary (legacy support)
    
    Returns:
        dict: Redis connection parameters
        
    Note: Use get_redis_client() for connection string support
    """
    config = {
        'host': REDIS_HOST,
        'port': REDIS_PORT,
        'db': REDIS_DB,
        'decode_responses': True
    }
    
    if REDIS_PASSWORD:
        config['password'] = REDIS_PASSWORD
    
    return config
