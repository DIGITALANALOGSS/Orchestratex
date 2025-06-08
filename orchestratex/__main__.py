import asyncio
import logging
from orchestratex.orchestrator import Orchestrator
from orchestratex.agents.meta_orchestrator import MetaOrchestrator
from orchestratex.agents.rag_maestro import RAGMaestro
from orchestratex.agents.code_architect import CodeArchitect
from orchestratex.agents.voice_agent import VoiceAgent
from orchestratex.agents.security_agent import SecurityAgent
from orchestratex.agents.analytics_agent import AnalyticsAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main entry point for Orchestratex AEM."""
    try:
        # Initialize orchestrator
        orchestrator = Orchestrator()
        
        # Example workflow
        workflow = {
            "name": "Code Generation and Analysis",
            "tasks": [
                {
                    "id": "1",
                    "type": "code_generation",
                    "specification": {
                        "language": "python",
                        "requirements": ["fastapi", "pydantic"],
                        "description": "Create a REST API for user management"
                    },
                    "required_capabilities": ["multi-lang", "test_gen"]
                },
                {
                    "id": "2",
                    "type": "security_scan",
                    "code": "{{task_1_result.code}}",
                    "required_capabilities": ["threat_detection", "compliance_check"]
                },
                {
                    "id": "3",
                    "type": "performance_analysis",
                    "metrics": ["response_time", "throughput"],
                    "required_capabilities": ["real_time_alerting", "drift_detection"]
                }
            ]
        }
        
        # Execute workflow
        result = await orchestrator.orchestrate(workflow)
        print("Workflow result:", result)
        
        # Print metrics
        metrics = orchestrator.get_metrics()
        print("\nMetrics:", metrics)
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
