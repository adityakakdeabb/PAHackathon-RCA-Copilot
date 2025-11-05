"""
Usage Examples for RCA Copilot
Demonstrates various ways to use the Master Agent
"""

from agents.master_agent import MasterAgent


def example_1_simple_query():
    """Example 1: Simple RCA query"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple RCA Query")
    print("="*70 + "\n")
    
    # Initialize Master Agent
    agent = MasterAgent()
    
    # Simple query
    query = "What caused the temperature spike in MCH_003?"
    
    # Get response
    response = agent.process_query(query)
    
    if response['success']:
        print("✓ Success!")
        print("\nRCA Report:")
        print(response['rca_report'])
    else:
        print(f"✗ Error: {response['error']}")


def example_2_specific_machine():
    """Example 2: Query specific machine with filters"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Query with Machine Filter")
    print("="*70 + "\n")
    
    agent = MasterAgent()
    
    query = "Show me all issues and maintenance history for this machine"
    
    # Query with specific machine ID
    response = agent.process_query(
        query,
        machine_id="MCH_003",
        top_k=10
    )
    
    if response['success']:
        print("✓ Query completed")
        print(f"\nRouted to: {response['routing_decision']}")
        print(f"\nRCA Report Preview:")
        print(response['rca_report'][:500] + "...")
    else:
        print(f"✗ Error: {response['error']}")


def example_3_sensor_specific():
    """Example 3: Sensor-specific analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Sensor-Specific Analysis")
    print("="*70 + "\n")
    
    agent = MasterAgent()
    
    query = "Analyze vibration patterns and identify potential bearing failures"
    
    response = agent.process_query(
        query,
        sensor_type="Vibration",
        status="Critical"
    )
    
    if response['success']:
        print("✓ Analysis complete")
        
        # Check which agents were used
        routing = response['routing_decision']
        print(f"\nAgents invoked:")
        for agent_name, invoked in routing.items():
            print(f"  • {agent_name}: {'✓' if invoked else '✗'}")
        
        print(f"\n{response['rca_report'][:500]}...")
    else:
        print(f"✗ Error: {response['error']}")


def example_4_chat_interface():
    """Example 4: Using simple chat interface"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Simple Chat Interface")
    print("="*70 + "\n")
    
    agent = MasterAgent()
    
    queries = [
        "What are the most common failure modes?",
        "Show critical alerts from yesterday",
        "Which machines need preventive maintenance?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 70)
        
        # Use simple chat interface
        report = agent.chat(query)
        print(report[:300] + "...\n")


def example_5_timeline_reconstruction():
    """Example 5: Incident timeline reconstruction"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Incident Timeline Reconstruction")
    print("="*70 + "\n")
    
    agent = MasterAgent()
    
    query = """Reconstruct the complete incident timeline for machine MCH_003:
    - What sensor readings were abnormal?
    - What did operators report?
    - What maintenance was performed?
    - What is the root cause?
    """
    
    response = agent.process_query(
        query,
        machine_id="MCH_003",
        start_date="2025-10-01",
        end_date="2025-10-31"
    )
    
    if response['success']:
        print("✓ Timeline reconstructed")
        print("\n" + response['rca_report'])
    else:
        print(f"✗ Error: {response['error']}")


def example_6_pattern_analysis():
    """Example 6: Pattern analysis across fleet"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Fleet-Wide Pattern Analysis")
    print("="*70 + "\n")
    
    agent = MasterAgent()
    
    query = """Analyze patterns across all machines:
    - Which components fail most frequently?
    - Are there common precursor symptoms?
    - What preventive measures are recommended?
    """
    
    response = agent.process_query(query)
    
    if response['success']:
        print("✓ Pattern analysis complete")
        
        # Show agent responses
        print("\nData sources used:")
        agent_responses = response.get('agent_responses', {})
        
        if 'sensor_data' in agent_responses:
            sensor_meta = agent_responses['sensor_data'].get('metadata', {})
            print(f"  • Sensor data: {sensor_meta.get('records_analyzed', 0)} records")
        
        if 'operator_reports' in agent_responses:
            op_meta = agent_responses['operator_reports'].get('metadata', {})
            print(f"  • Operator reports: {op_meta.get('document_count', 0)} documents")
        
        if 'maintenance_logs' in agent_responses:
            maint_meta = agent_responses['maintenance_logs'].get('metadata', {})
            print(f"  • Maintenance logs: {maint_meta.get('document_count', 0)} documents")
        
        print("\nRCA Report:")
        print(response['rca_report'])
    else:
        print(f"✗ Error: {response['error']}")


def example_7_direct_agent_access():
    """Example 7: Directly accessing specialized agents"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Direct Agent Access")
    print("="*70 + "\n")
    
    # You can also access specialized agents directly
    from agents.sensor_agent import SensorDataAgent
    
    sensor_agent = SensorDataAgent()
    
    # Query sensor data directly
    result = sensor_agent.process_query(
        "Show critical alerts",
        machine_id="MCH_003",
        status="Critical"
    )
    
    if result['success']:
        data = result['data']
        print("✓ Sensor data retrieved")
        print(f"\nStatistics: {data['statistics']}")
        print(f"\nCritical events: {len(data.get('recent_critical_events', []))}")
    else:
        print(f"✗ Error: {result['error']}")


def example_8_get_available_agents():
    """Example 8: Get available agents"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Available Agents")
    print("="*70 + "\n")
    
    agent = MasterAgent()
    
    agents = agent.get_available_agents()
    
    print("Available specialized agents:\n")
    for agent_info in agents:
        print(f"  • {agent_info['name']}")
        print(f"    {agent_info['description']}\n")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("  RCA COPILOT - USAGE EXAMPLES")
    print("="*70)
    
    examples = [
        ("Simple Query", example_1_simple_query),
        ("Machine Filter", example_2_specific_machine),
        ("Sensor Analysis", example_3_sensor_specific),
        ("Chat Interface", example_4_chat_interface),
        ("Timeline Reconstruction", example_5_timeline_reconstruction),
        ("Pattern Analysis", example_6_pattern_analysis),
        ("Direct Agent Access", example_7_direct_agent_access),
        ("Available Agents", example_8_get_available_agents),
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nSelect example to run (1-8, or 'all'): ", end="")
    choice = input().strip()
    
    if choice.lower() == 'all':
        for name, func in examples:
            func()
            input("\nPress Enter to continue to next example...")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        examples[int(choice) - 1][1]()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
