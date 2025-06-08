from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from .agents.base_agent import BaseAgent
from .config.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config_manager = ConfigManager(config_path)
        self.agents = self._initialize_agents()
        self.workflows = {}
        self.metrics = {
            "completed_workflows": 0,
            "failed_workflows": 0,
            "active_workflows": 0,
            "total_tasks": 0,
            "completed_tasks": 0
        }
        self.error_handler = ErrorHandler()

    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all agents from configuration."""
        agents = {}
        for agent_name, config in self.config_manager.config["agents"].items():
            agent_class = globals().get(agent_name)
            if agent_class:
                try:
                    agents[agent_name] = agent_class()
                except Exception as e:
                    logger.error(f"Failed to initialize {agent_name}: {e}")
        return agents

    async def orchestrate(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate a workflow across multiple agents."""
        try:
            workflow_id = self._generate_workflow_id()
            self.workflows[workflow_id] = {
                "status": "pending",
                "started_at": datetime.now(),
                "tasks": []
            }
            
            # Validate workflow
            if not self._validate_workflow(workflow):
                raise ValueError("Invalid workflow format")

            # Plan execution
            execution_plan = await self._create_execution_plan(workflow)
            
            # Execute tasks
            results = await self._execute_tasks(execution_plan)
            
            self._update_metrics("completed_workflows")
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results
            }
        except Exception as e:
            self._update_metrics("failed_workflows")
            return self.error_handler.handle_error(e)

    def _generate_workflow_id(self) -> str:
        """Generate a unique workflow ID."""
        import uuid
        return str(uuid.uuid4())

    def _validate_workflow(self, workflow: Dict[str, Any]) -> bool:
        """Validate workflow structure."""
        required_keys = ["name", "tasks", "priority"]
        return all(key in workflow for key in required_keys)

    async def _create_execution_plan(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create an optimized execution plan."""
        tasks = workflow["tasks"]
        execution_plan = []
        
        for task in tasks:
            agent = self._select_agent(task)
            if agent:
                execution_plan.append({
                    "task": task,
                    "agent": agent,
                    "priority": task.get("priority", 1)
                })
        
        return sorted(execution_plan, key=lambda x: x["priority"])

    def _select_agent(self, task: Dict[str, Any]) -> Optional[BaseAgent]:
        """Select the most suitable agent for a task."""
        for agent_name, agent in self.agents.items():
            if self._agent_matches_task(agent, task):
                return agent
        return None

    def _agent_matches_task(self, agent: BaseAgent, task: Dict[str, Any]) -> bool:
        """Check if an agent can handle a task."""
        return any(cap in agent.capabilities for cap in task.get("required_capabilities", []))

    async def _execute_tasks(self, execution_plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tasks concurrently."""
        results = []
        tasks = []
        
        for task_info in execution_plan:
            task = task_info["task"]
            agent = task_info["agent"]
            
            # Create task with error handling
            task_coroutine = self._execute_task_with_retry(agent, task)
            tasks.append(task_coroutine)
            
            self._update_metrics("total_tasks")

        # Execute tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results

    async def _execute_task_with_retry(self, agent: BaseAgent, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with retry logic."""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                result = await agent.perform_task(task)
                self._update_metrics("completed_tasks")
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

    def _update_metrics(self, metric: str) -> None:
        """Update orchestrator metrics."""
        self.metrics[metric] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics."""
        return self.metrics

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow."""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return {"error": f"Workflow {workflow_id} not found"}
        
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "started_at": workflow["started_at"],
            "tasks": len(workflow["tasks"])
        }

class ErrorHandler:
    def __init__(self):
        self.error_count = 0
        self.error_types = {}
        
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle and log errors."""
        self.error_count += 1
        error_type = type(error).__name__
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
        
        return {
            "error": str(error),
            "error_type": error_type,
            "timestamp": datetime.now().isoformat(),
            "error_id": self.error_count
        }

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": self.error_count,
            "error_types": self.error_types
        }
