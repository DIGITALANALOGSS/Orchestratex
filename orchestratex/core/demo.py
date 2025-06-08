import asyncio
import json
from orchestratex.core.agents import SecurityAgent, QuantumAgent, Orchestrator

async def main():
    """Demo Orchestratex AEM core agents."""
    try:
        # Initialize agents
        security = SecurityAgent()
        quantum = QuantumAgent()
        
        # Create orchestrator
        orchestrator = Orchestrator([security, quantum])
        
        # Example workflow
        tasks = [
            {
                "id": "1",
                "priority": 1,
                "description": "High priority task"
            },
            {
                "id": "2",
                "priority": 2,
                "description": "Medium priority task"
            },
            {
                "id": "3",
                "priority": 3,
                "description": "Low priority task"
            }
        ]
        
        # Execute workflow
        result = await orchestrator.execute_workflow(
            user_role="admin",
            query="Explain quantum error correction",
            tasks=tasks
        )
        
        # Print results
        print("\nWorkflow Result:")
        print(json.dumps(result, indent=2))
        
        # Print metrics
        print("\nAgent Metrics:")
        for agent in orchestrator.agents.values():
            print(f"\n{agent.name} Metrics:")
            print(json.dumps(agent.get_metrics(), indent=2))
        
        # Print audit log
        print("\nWorkflow Audit Log:")
        for entry in orchestrator.workflow_log.entries:
            print(f"\n{entry['timestamp']}: {entry['action']}")
            print(json.dumps(entry['details'], indent=2))
            
    except Exception as e:
        print(f"Error in demo: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
