# Redis Connection String Guide

## Overview
The RCA Copilot now supports flexible Redis connection using connection strings. This allows you to connect to various Redis deployments including local Docker, remote servers, Azure Cache for Redis, and more.

## Connection String Format

```
redis://[[username]:[password]]@host:port/database
rediss://[[username]:[password]]@host:port/database  # SSL/TLS
```

### Components:
- **Scheme**: `redis://` (plain) or `rediss://` (SSL/TLS)
- **Username**: (optional) Redis 6.0+ ACL username
- **Password**: (optional) Redis authentication password
- **Host**: Redis server hostname or IP
- **Port**: Redis server port (default: 6379)
- **Database**: Database number (0-15, we use 1 for PA_Hackathon)

## Configuration Methods

### Method 1: Environment Variable (Recommended)

Create or edit `.env` file in project root:

```bash
REDIS_CONNECTION_STRING=redis://localhost:6379/1
```

### Method 2: System Environment Variable (Windows PowerShell)

```powershell
# Set for current session
$env:REDIS_CONNECTION_STRING = "redis://localhost:6379/1"

# Set permanently (requires admin)
[System.Environment]::SetEnvironmentVariable('REDIS_CONNECTION_STRING', 'redis://localhost:6379/1', 'User')
```

### Method 3: Default Configuration

If not specified, defaults to: `redis://localhost:6379/1`

## Connection Examples

### 1. Local Docker Redis (Default)
```bash
REDIS_CONNECTION_STRING=redis://localhost:6379/1
```

**Use Case:** Development with local Docker container

**Docker Command:**
```powershell
docker run -d --name redis-pa-hackathon -p 6379:6379 redis:latest
```

---

### 2. Redis with Password
```bash
REDIS_CONNECTION_STRING=redis://:mypassword123@localhost:6379/1
```

**Use Case:** Secured local or remote Redis

**Note:** The colon (`:`) before password is required even without username

**Docker Command with Password:**
```powershell
docker run -d --name redis-pa-hackathon -p 6379:6379 redis:latest redis-server --requirepass mypassword123
```

---

### 3. Redis with Username and Password (Redis 6.0+)
```bash
REDIS_CONNECTION_STRING=redis://admin:mypassword123@localhost:6379/1
```

**Use Case:** Redis 6.0+ with ACL users

---

### 4. Remote Redis Server
```bash
REDIS_CONNECTION_STRING=redis://redis-server.example.com:6379/1
```

**Use Case:** Shared Redis server on network

---

### 5. Azure Cache for Redis (Basic/Standard)
```bash
REDIS_CONNECTION_STRING=redis://:your-access-key@your-cache.redis.cache.windows.net:6380/1
```

**Use Case:** Azure managed Redis (non-SSL port)

**Getting Access Key:**
1. Azure Portal → Your Redis Cache
2. Settings → Access keys
3. Copy Primary or Secondary key

---

### 6. Azure Cache for Redis with SSL (Premium)
```bash
REDIS_CONNECTION_STRING=rediss://:your-access-key@your-cache.redis.cache.windows.net:6380/1
```

**Use Case:** Azure managed Redis with SSL (recommended)

**Note:** Use `rediss://` (double 's') for SSL connections

---

### 7. AWS ElastiCache for Redis
```bash
REDIS_CONNECTION_STRING=redis://your-cluster.abc123.0001.use1.cache.amazonaws.com:6379/1
```

**Use Case:** AWS managed Redis

---

### 8. Redis Cloud (Redis Enterprise Cloud)
```bash
REDIS_CONNECTION_STRING=redis://:your-password@redis-12345.c123.us-east-1-1.ec2.cloud.redislabs.com:12345/1
```

**Use Case:** Redis Cloud managed service

---

## Verification

### Check Current Configuration

```python
# In Python
import redis_config

print(f"Connection String: {redis_config.REDIS_CONNECTION_STRING}")
print(f"Host: {redis_config.REDIS_HOST}")
print(f"Port: {redis_config.REDIS_PORT}")
print(f"Database: {redis_config.REDIS_DB}")
```

### Test Connection

**Option 1: Python Test Script**

Create `test_redis_connection.py`:

```python
import redis_config

def test_connection():
    try:
        client = redis_config.get_redis_client()
        client.ping()
        print("✓ Redis connection successful!")
        print(f"  Host: {redis_config.REDIS_HOST}")
        print(f"  Port: {redis_config.REDIS_PORT}")
        print(f"  Database: {redis_config.REDIS_DB}")
        
        # Test project key
        client.set(redis_config.PROJECT_KEY, redis_config.PROJECT_NAME)
        project = client.get(redis_config.PROJECT_KEY)
        print(f"  Project: {project}")
        
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")

if __name__ == "__main__":
    test_connection()
```

Run:
```powershell
python test_redis_connection.py
```

**Option 2: API Health Check**

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "redis": "connected",
  "project": "PA_Hackathon",
  "pending_queries": 0
}
```

---

## Troubleshooting

### Problem: "Connection refused"

**Possible Causes:**
1. Redis server not running
2. Wrong host/port
3. Firewall blocking connection

**Solutions:**
```powershell
# Check if Redis is running (Docker)
docker ps | Select-String redis

# Start Redis container
docker start <container-id>

# Check Redis logs
docker logs <container-id>

# Test connection with redis-cli
docker exec -it <container-id> redis-cli ping
```

---

### Problem: "Authentication failed"

**Possible Causes:**
1. Wrong password
2. Password contains special characters not properly encoded
3. Username/password format incorrect

**Solutions:**
```bash
# Correct format with password
redis://:password@host:port/db

# If password has special characters, URL encode them
# Example: password with @ symbol
redis://:p%40ssword@localhost:6379/1
```

**URL Encoding Reference:**
- `@` → `%40`
- `:` → `%3A`
- `/` → `%2F`
- `#` → `%23`

---

### Problem: "SSL/TLS connection error"

**Possible Causes:**
1. Using `redis://` instead of `rediss://`
2. SSL certificate issues

**Solutions:**
```bash
# Use rediss:// for SSL connections
REDIS_CONNECTION_STRING=rediss://:password@host:6380/1
```

---

### Problem: "Database index out of range"

**Possible Causes:**
1. Redis cluster doesn't support multiple databases
2. Database number > 15

**Solutions:**
```bash
# Use database 0 for Redis Cluster
REDIS_CONNECTION_STRING=redis://host:port/0

# For standalone Redis, use 0-15
REDIS_CONNECTION_STRING=redis://host:port/1
```

---

## Migration from Old Configuration

### Old Method (Individual Parameters)
```python
# Old in redis_config.py
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 1

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
```

### New Method (Connection String)
```bash
# New in .env
REDIS_CONNECTION_STRING=redis://localhost:6379/1
```

```python
# New in code
redis_client = redis_config.get_redis_client()
```

**Benefits:**
✅ Single configuration point
✅ Supports passwords and SSL
✅ Compatible with cloud services
✅ Standard Redis URL format
✅ Easy to copy from cloud providers

---

## Best Practices

### 1. Use Environment Variables
Don't hardcode connection strings in code:
```bash
# ✓ Good - .env file
REDIS_CONNECTION_STRING=redis://localhost:6379/1
```

```python
# ✗ Bad - hardcoded
redis_client = Redis.from_url("redis://localhost:6379/1")
```

### 2. Use SSL for Production
```bash
# Development
REDIS_CONNECTION_STRING=redis://localhost:6379/1

# Production
REDIS_CONNECTION_STRING=rediss://:password@prod-redis.example.com:6380/1
```

### 3. Store Passwords Securely
- Use Azure Key Vault, AWS Secrets Manager, or similar
- Never commit `.env` files to Git
- Use different credentials for dev/staging/prod

### 4. Use Dedicated Databases
- Database 0: Default/other applications
- Database 1: PA_Hackathon (current project)
- Database 2-15: Other projects

### 5. Monitor Connection Health
```python
# Regularly check connection
redis_client.ping()

# Set connection timeout
client = Redis.from_url(url, socket_timeout=5, socket_connect_timeout=5)
```

---

## Cloud Provider Examples

### Azure Cache for Redis

**Connection String from Azure Portal:**
1. Navigate to your Redis Cache
2. Go to "Settings" → "Access keys"
3. Copy "Primary connection string (StackExchange.Redis)"
4. Convert to Python format:

```
# Azure gives:
mycache.redis.cache.windows.net:6380,password=abc123,ssl=True,abortConnect=False

# Convert to:
REDIS_CONNECTION_STRING=rediss://:abc123@mycache.redis.cache.windows.net:6380/1
```

### AWS ElastiCache

**Finding Connection Endpoint:**
1. AWS Console → ElastiCache → Redis
2. Select your cluster
3. Copy "Primary Endpoint"

```bash
REDIS_CONNECTION_STRING=redis://master.my-cluster.abc123.use1.cache.amazonaws.com:6379/1
```

### Google Cloud Memorystore

**Finding Connection:**
1. GCP Console → Memorystore → Redis
2. Copy "Host" and "Port"

```bash
REDIS_CONNECTION_STRING=redis://10.0.0.3:6379/1
```

---

## Security Considerations

### 1. Network Security
- Use private networks (VPC, VNet) for production
- Enable firewall rules to restrict access
- Use SSL/TLS for connections over internet

### 2. Authentication
- Always use passwords in production
- Rotate passwords regularly
- Use Redis ACL for fine-grained access control (Redis 6.0+)

### 3. Encryption
- Use `rediss://` for encrypted connections
- Enable encryption at rest in cloud services
- Use VPN for connections to remote Redis

### 4. Connection Strings
- Never log connection strings with passwords
- Use masked logging for sensitive data
- Audit access to configuration files

---

## FAQ

**Q: Can I use multiple Redis connections?**
A: Yes, create multiple connection strings:
```python
primary_client = Redis.from_url("redis://primary:6379/1")
cache_client = Redis.from_url("redis://cache:6379/2")
```

**Q: Does this work with Redis Sentinel?**
A: For Sentinel, use redis-py's SentinelConnectionPool:
```python
from redis.sentinel import Sentinel
sentinel = Sentinel([('sentinel-host', 26379)])
client = sentinel.master_for('mymaster', db=1)
```

**Q: How do I use Redis Cluster?**
A: Redis Cluster requires different client:
```python
from redis.cluster import RedisCluster
client = RedisCluster.from_url("redis://cluster-host:6379")
```

**Q: Can I test connection without starting the app?**
A: Yes, use the test script above or redis-cli:
```powershell
# Test with redis-cli
docker exec -it <container-id> redis-cli -u redis://localhost:6379/1 ping
```

---

## Summary

✅ **Connection String Format**: `redis://[user:pass@]host:port/db`
✅ **Configuration**: Set `REDIS_CONNECTION_STRING` in `.env`
✅ **Default**: `redis://localhost:6379/1`
✅ **Method**: Use `redis_config.get_redis_client()`
✅ **SSL**: Use `rediss://` for encrypted connections
✅ **Testing**: Run health check or test script
✅ **Security**: Use passwords and SSL for production

For more details, see `redis_config.py` source code.
