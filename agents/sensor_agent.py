"""
Sensor Data Agent
Handles queries related to time-series sensor data (temperature, vibration, pressure)
Uses FastAPI to query local sensor data
"""
import logging
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timedelta
import config
from agents.base_agent import BaseAgent, AgentResponse

# Get logger for this module
logger = logging.getLogger(__name__)


class SensorDataAgent(BaseAgent):
    """Agent for querying and analyzing sensor data"""
    
    def __init__(self):
        super().__init__(
            name="Sensor Data Agent",
            description="Analyzes time-series sensor data including temperature, vibration, and pressure readings to identify anomalies and trends"
        )
        self.sensor_data = self._load_sensor_data()
    
    def _load_sensor_data(self) -> pd.DataFrame:
        """Load sensor data from CSV"""
        try:
            df = pd.read_csv(config.SENSOR_DATA_PATH)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            logger.error(f"Error loading sensor data: {e}", exc_info=True)
            return pd.DataFrame()
    
    def process_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Process sensor data query
        
        Args:
            query: User query about sensor data
            **kwargs: Additional parameters (machine_id, sensor_type, time_range, etc.)
            
        Returns:
            AgentResponse with sensor data analysis
        """
        try:
            # Extract parameters
            machine_id = kwargs.get('machine_id')
            sensor_type = kwargs.get('sensor_type')
            start_date = kwargs.get('start_date')
            end_date = kwargs.get('end_date')
            status_filter = kwargs.get('status')
            
            # Filter data
            filtered_data = self.sensor_data.copy()
            
            if machine_id:
                filtered_data = filtered_data[filtered_data['machine_id'] == machine_id]
            
            if sensor_type:
                filtered_data = filtered_data[filtered_data['sensor_type'] == sensor_type]
            
            if start_date:
                filtered_data = filtered_data[filtered_data['timestamp'] >= pd.to_datetime(start_date)]
            
            if end_date:
                filtered_data = filtered_data[filtered_data['timestamp'] <= pd.to_datetime(end_date)]
            
            if status_filter:
                filtered_data = filtered_data[filtered_data['status'] == status_filter]
            
            # Analyze data
            analysis = self._analyze_sensor_data(filtered_data, query)
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                data=analysis,
                metadata={
                    "records_analyzed": len(filtered_data),
                    "query": query
                }
            ).to_dict()
            
        except Exception as e:
            return AgentResponse(
                agent_name=self.name,
                success=False,
                error=str(e)
            ).to_dict()
    
    def _analyze_sensor_data(self, data: pd.DataFrame, query: str) -> Dict[str, Any]:
        """Analyze sensor data and generate insights"""
        if data.empty:
            return {
                "summary": "No sensor data found for the specified criteria",
                "records": []
            }
        
        # Generate statistics
        stats = {
            "total_records": len(data),
            "machines_affected": data['machine_id'].nunique(),
            "sensor_types": data['sensor_type'].unique().tolist(),
            "status_distribution": data['status'].value_counts().to_dict(),
            "critical_alerts": len(data[data['status'] == 'Critical']),
            "warning_alerts": len(data[data['status'] == 'Warning'])
        }
        
        # Get critical readings
        critical_data = data[data['status'].isin(['Critical', 'Warning'])].sort_values('timestamp', ascending=False)
        
        # Group by machine and sensor type for anomaly patterns
        anomaly_summary = []
        if not critical_data.empty:
            grouped = critical_data.groupby(['machine_id', 'sensor_type']).agg({
                'sensor_value': ['mean', 'max', 'min'],
                'status': 'count'
            }).reset_index()
            
            for _, row in grouped.head(10).iterrows():
                anomaly_summary.append({
                    "machine_id": row['machine_id'],
                    "sensor_type": row['sensor_type'],
                    "avg_value": round(row['sensor_value']['mean'], 2),
                    "max_value": round(row['sensor_value']['max'], 2),
                    "min_value": round(row['sensor_value']['min'], 2),
                    "alert_count": int(row['status']['count'])
                })
        
        # Recent critical events
        recent_critical = critical_data.head(20).to_dict('records')
        for record in recent_critical:
            record['timestamp'] = record['timestamp'].isoformat()
        
        return {
            "summary": f"Analyzed {len(data)} sensor readings across {data['machine_id'].nunique()} machines",
            "statistics": stats,
            "anomaly_patterns": anomaly_summary,
            "recent_critical_events": recent_critical,
            "time_range": {
                "start": data['timestamp'].min().isoformat() if not data.empty else None,
                "end": data['timestamp'].max().isoformat() if not data.empty else None
            }
        }
    
    def get_machine_timeline(self, machine_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get timeline of sensor readings for a specific machine"""
        end_time = self.sensor_data['timestamp'].max()
        start_time = end_time - timedelta(hours=hours)
        
        machine_data = self.sensor_data[
            (self.sensor_data['machine_id'] == machine_id) &
            (self.sensor_data['timestamp'] >= start_time)
        ].sort_values('timestamp')
        
        timeline = machine_data.to_dict('records')
        for record in timeline:
            record['timestamp'] = record['timestamp'].isoformat()
        
        return timeline
