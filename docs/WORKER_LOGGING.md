# Worker Logging Enhancement Summary

## Overview
The worker now displays comprehensive logging including the full RCA report, processing times, and result retrieval information.

## Enhanced Worker Log Output

### 1. Query Receipt
```
📥 Received query from queue: a1b2c3d4-5678-90ab-cdef-1234567890ab
```

### 2. Processing Start
```
======================================================================
🔍 Processing Query ID: a1b2c3d4-5678-90ab-cdef-1234567890ab
📝 Query: What is causing the temperature sensor to read high values?
⏰ Started: 2025-11-05 14:30:45
======================================================================
```

### 3. Agent Processing (existing detailed logs)
```
Invoking Master Agent for query a1b2c3d4...
[Master Agent processing logs...]
[Sensor Agent logs...]
[Operator Agent logs...]
[Maintenance Agent logs...]
```

### 4. RCA Report Display (NEW!)
```
✓ Query a1b2c3d4... completed successfully

📊 RCA REPORT:
----------------------------------------------------------------------
Root cause: Sensor calibration drift detected on temperature sensor
T-101. Evidence: Consistent +5°C offset across all readings in the
past 24 hours. Immediate action: Recalibrate sensor immediately and
compare with backup sensor. Prevention: Implement quarterly calibration
schedule and install redundant temperature monitoring.
----------------------------------------------------------------------
```

### 5. Completion Summary (ENHANCED!)
```
======================================================================
✓ Query a1b2c3d4... processing complete and result stored in Redis
⏱️  Processing time: 12.45 seconds
🔗 Retrieve result using: GET /result/a1b2c3d4-5678-90ab-cdef-1234567890ab
======================================================================

✅ SUCCESS - Query completed and result available via API

Ready for next query...
```

## Benefits

### For Development
✅ **Immediate Visibility**: See RCA results without calling the API
✅ **Performance Monitoring**: Track processing time for each query
✅ **Debugging**: Full context visible in one terminal
✅ **Status Clarity**: Clear success/failure indicators

### For Operations
✅ **Audit Trail**: Complete processing history in logs
✅ **Performance Metrics**: Processing duration tracking
✅ **Quick Verification**: Verify results before API retrieval
✅ **Error Visibility**: Detailed error information for troubleshooting

## Log Levels

The worker uses appropriate log levels:

```python
logger.info()    # Normal processing flow, status updates, RCA reports
logger.warning() # Non-critical issues, configuration warnings
logger.error()   # Processing failures, connection errors
```

## Example Complete Log Flow

```
======================================================================
🔧 Initializing RCA Copilot Worker
======================================================================
Connecting to Redis using connection string...
Redis Host: localhost:6379
Redis Database: 1
✓ Connected to Redis successfully
✓ Project: PA_Hackathon
✓ Queue: pa_hackathon:rca_queue
✓ Project namespace verified: PA_Hackathon
Initializing RCA Copilot Master Agent...
======================================================================
Available Agents:
  • sensor_agent: Analyzes sensor data and time-series measurements
  • operator_agent: Reviews operator reports and human observations
  • maintenance_agent: Examines maintenance logs and service records
======================================================================
✓ Master Agent initialized successfully
======================================================================
✓ Worker initialized and ready to process queries
======================================================================
🚀 Worker started - Listening for queries...
Press Ctrl+C to stop


📥 Received query from queue: abc-123
======================================================================
🔍 Processing Query ID: abc-123
📝 Query: Why is pump P-205 vibrating?
⏰ Started: 2025-11-05 14:35:22
======================================================================
Invoking Master Agent for query abc-123...
Master Agent analyzing query...
Selected agents: ['sensor_agent', 'maintenance_agent']
Invoking sensor_agent...
  ✓ Sensor data retrieved
  ✓ Analysis complete
Invoking maintenance_agent...
  ✓ Maintenance logs retrieved
  ✓ Analysis complete
Generating RCA report...
✓ Query abc-123 completed successfully

📊 RCA REPORT:
----------------------------------------------------------------------
Root cause: Bearing wear in pump P-205 due to exceeded service interval.
Evidence: Vibration increased from 2mm/s to 8mm/s over 3 weeks, last
bearing replacement was 18 months ago (recommended: 12 months). Immediate
action: Schedule pump shutdown for bearing replacement. Prevention:
Implement predictive maintenance alerts at 11 months.
----------------------------------------------------------------------
======================================================================
✓ Query abc-123 processing complete and result stored in Redis
⏱️  Processing time: 8.32 seconds
🔗 Retrieve result using: GET /result/abc-123
======================================================================

✅ SUCCESS - Query completed and result available via API

Ready for next query...
```

## Configuration

The enhanced logging works with the existing configuration in `config.py`:

```python
# Logging format (existing)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

## Viewing Logs

### Option 1: Terminal Output (Real-time)
```powershell
python worker.py
```
See all logs in real-time as queries are processed.

### Option 2: File Logging (Optional)
To save logs to a file, modify `config.py`:

```python
# Add file handler
file_handler = logging.FileHandler('worker.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
```

### Option 3: Docker Logs (If running in container)
```powershell
docker logs -f worker-container
```

## Performance Metrics

The worker now tracks:
- **Query Start Time**: When processing begins
- **Query End Time**: When processing completes
- **Processing Duration**: Total time in seconds
- **Success/Failure Status**: Clear indicators

Example metrics from logs:
```
⏱️  Processing time: 8.32 seconds    # Fast query
⏱️  Processing time: 15.67 seconds   # Average query
⏱️  Processing time: 45.21 seconds   # Complex query
```

## Troubleshooting

### Issue: RCA report not showing in logs

**Check:**
1. Worker is running: `python worker.py`
2. Query completed successfully (look for ✓ symbol)
3. No errors during processing

### Issue: Processing time seems too long

**Possible causes:**
- Large dataset analysis
- Multiple agents invoked
- Azure OpenAI API latency
- Network delays

**Solutions:**
- Check Azure OpenAI response times
- Optimize agent data retrieval
- Use caching for frequent queries

### Issue: Logs too verbose

**Solution:**
Adjust log level in `config.py`:
```python
logger.setLevel(logging.WARNING)  # Only warnings and errors
```

## Summary of Changes

### Files Modified:
1. **worker.py** - Enhanced logging with:
   - RCA report display
   - Processing time tracking
   - Start/end timestamps
   - API endpoint information
   - Success/failure summaries

### New Features:
- 📊 RCA report displayed in worker logs
- ⏱️ Processing time measurement
- ⏰ Start time timestamp
- 🔗 API endpoint reference
- ✅/❌ Success/failure indicators

### Log Sections:
1. **Initialization**: Worker and agent setup
2. **Query Receipt**: Incoming query notification
3. **Processing**: Detailed agent workflow
4. **RCA Report**: Final analysis result (NEW!)
5. **Completion**: Summary with metrics (ENHANCED!)

## Next Steps

1. ✅ Start worker: `python worker.py`
2. ✅ Submit query via API: `POST /ask`
3. ✅ Watch worker logs for full RCA report
4. ✅ Retrieve via API: `GET /result/{query_id}` (optional)

The worker logs now provide complete visibility into the RCA process! 🎉
