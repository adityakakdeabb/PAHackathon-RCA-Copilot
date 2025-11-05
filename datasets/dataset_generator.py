import csv
import json
import random
from datetime import datetime, timedelta

# =========================
# CONFIGURATION
# =========================
NUM_ROWS = 10000
MACHINE_IDS = [f"MCH_{str(i).zfill(3)}" for i in range(1, 51)]
TECHNICIANS = ["A. Sharma", "R. Patel", "N. Rao", "V. Singh", "K. Iyer", "L. Mehta"]
OPERATORS = ["S. Kumar", "A. Khan", "R. Verma", "T. Singh", "N. Iyer", "J. Das"]
SENSOR_TYPES = ["Temperature", "Vibration", "Pressure"]
STATUS_LEVELS = ["Normal", "Warning", "Critical"]
MAINTENANCE_TYPES = ["Preventive", "Corrective", "Emergency"]
SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"]
SHIFTS = ["Day", "Evening", "Night"]

# =========================
# 1️⃣ Generate sensor_data.csv
# =========================
sensor_rows = []
start_time = datetime(2025, 10, 1, 8, 0, 0)

for i in range(NUM_ROWS):
    timestamp = start_time + timedelta(minutes=5 * i)
    machine_id = random.choice(MACHINE_IDS)
    sensor_type = random.choice(SENSOR_TYPES)
    
    if sensor_type == "Temperature":
        value = round(random.uniform(55, 90), 2)
        unit = "°C"
    elif sensor_type == "Vibration":
        value = round(random.uniform(2.0, 12.0), 2)
        unit = "mm/s"
    else:
        value = round(random.uniform(1.5, 6.0), 2)
        unit = "bar"

    # Status thresholds (approx)
    if (sensor_type == "Temperature" and value > 80) or \
       (sensor_type == "Vibration" and value > 9) or \
       (sensor_type == "Pressure" and value > 5):
        status = "Critical"
    elif (sensor_type == "Temperature" and value > 70) or \
         (sensor_type == "Vibration" and value > 7) or \
         (sensor_type == "Pressure" and value > 4):
        status = "Warning"
    else:
        status = "Normal"

    sensor_rows.append([timestamp.isoformat() + "Z", machine_id, sensor_type, value, unit, status])

with open("sensor_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "machine_id", "sensor_type", "sensor_value", "unit", "status"])
    writer.writerows(sensor_rows)

print("✅ Generated sensor_data.csv")


# =========================
# 2️⃣ Generate maintenance_logs.json
# =========================
components = [
    "Bearing Assembly", "Cooling Fan", "Oil Pump", "Compressor Valve",
    "Heat Exchanger", "Gearbox", "Motor Shaft", "Hydraulic Pump"
]

logs = []
base_date = datetime(2025, 9, 1)

for i in range(NUM_ROWS):
    log = {
        "log_id": f"LOG_{1000 + i}",
        "machine_id": random.choice(MACHINE_IDS),
        "date": (base_date + timedelta(days=random.randint(0, 45))).strftime("%Y-%m-%d"),
        "maintenance_type": random.choice(MAINTENANCE_TYPES),
        "components_checked": random.sample(components, random.randint(1, 3)),
        "actions_taken": random.choice([
            "Replaced damaged bearing",
            "Lubricated moving parts",
            "Cleaned filters and inspected seals",
            "Calibrated pressure sensor",
            "Replaced cooling fan belt",
            "Repaired valve leakage",
            "Adjusted motor alignment",
            "Performed complete system diagnostics"
        ]),
        "technician": random.choice(TECHNICIANS),
        "downtime_hours": round(random.uniform(1.0, 8.0), 1),
        "remarks": random.choice([
            "System performance restored.",
            "Vibration levels normalized.",
            "Temperature stability improved.",
            "Minor wear detected; monitor closely.",
            "Pressure fluctuation resolved.",
            "Awaiting parts for full replacement."
        ])
    }
    logs.append(log)

with open("maintenance_logs.json", "w") as f:
    json.dump(logs, f, indent=2)

print("✅ Generated maintenance_logs.json")


# =========================
# 3️⃣ Generate operator_reports.csv
# =========================
reports = []
incident_templates = [
    "Unusual vibration noise observed near bearing housing.",
    "Temperature rising faster than normal during startup.",
    "Pressure fluctuations noted under steady load.",
    "Oil leakage detected near coupling joint.",
    "System auto-shutdown triggered by overheat sensor.",
    "Minor smoke detected from motor casing.",
    "Slight delay in start-up sequence observed."
]

actions_templates = [
    "Reduced load and notified maintenance team.",
    "Monitored parameters for 15 minutes.",
    "Reset system and escalated to engineering.",
    "Checked coolant levels and filters.",
    "Temporarily halted machine for inspection.",
    "Adjusted valve and resumed normal operation."
]

for i in range(NUM_ROWS):
    reports.append([
        f"REP_{1000 + i}",
        random.choice(MACHINE_IDS),
        random.choice(OPERATORS),
        random.choice(SHIFTS),
        (base_date + timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d"),
        random.choice(incident_templates),
        random.choice(actions_templates),
        random.choice(SEVERITY_LEVELS),
        random.choice(["Open", "Investigating", "Closed"])
    ])

with open("operator_reports.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "report_id", "machine_id", "operator_name", "shift",
        "date", "incident_description", "initial_action", "severity", "status"
    ])
    writer.writerows(reports)

print("✅ Generated operator_reports.csv")
print("\n🎉 All 3 datasets generated successfully!")
