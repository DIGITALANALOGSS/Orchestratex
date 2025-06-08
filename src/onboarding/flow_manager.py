from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OnboardingStage(Enum):
    WELCOME = "welcome"
    ACCOUNT_SETUP = "account_setup"
    BRAND_CUSTOMIZATION = "brand_customization"
    AGENT_CONFIGURATION = "agent_configuration"
    WORKFLOW_DESIGN = "workflow_design"
    INTEGRATION_SETUP = "integration_setup"
    TESTING = "testing"
    PRODUCTION_READY = "production_ready"

@dataclass
class OnboardingStep:
    id: str
    title: str
    description: str
    stage: OnboardingStage
    required: bool = True
    estimated_time: int = 5  # minutes
    prerequisites: List[str] = field(default_factory=list)
    completion_handler: Optional[Callable] = None
    auto_advance: bool = False

@dataclass
class UserProgress:
    user_id: str
    current_stage: OnboardingStage
    completed_steps: List[str] = field(default_factory=list)
    skipped_steps: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    completion_time: Optional[datetime] = None

class OnboardingFlowManager:
    def __init__(self):
        self.steps = self._initialize_steps()
        self.user_progress: Dict[str, UserProgress] = {}
        
    def _initialize_steps(self) -> List[OnboardingStep]:
        """Define all onboarding steps"""
        return [
            # Welcome Stage
            OnboardingStep(
                id="welcome_video",
                title="Welcome to OrchestrateX",
                description="Watch our 2-minute introduction video",
                stage=OnboardingStage.WELCOME,
                estimated_time=2,
                auto_advance=True
            ),
            OnboardingStep(
                id="platform_overview",
                title="Platform Overview",
                description="Interactive tour of the main dashboard",
                stage=OnboardingStage.WELCOME,
                estimated_time=5
            ),
            
            # Account Setup
            OnboardingStep(
                id="profile_setup",
                title="Complete Your Profile",
                description="Add your organization details and preferences",
                stage=OnboardingStage.ACCOUNT_SETUP,
                estimated_time=3
            ),
            OnboardingStep(
                id="team_invitation",
                title="Invite Team Members",
                description="Add colleagues to your workspace",
                stage=OnboardingStage.ACCOUNT_SETUP,
                required=False,
                estimated_time=5
            ),
            
            # Brand Customization
            OnboardingStep(
                id="upload_logo",
                title="Upload Your Logo",
                description="Customize the platform with your brand",
                stage=OnboardingStage.BRAND_CUSTOMIZATION,
                estimated_time=2
            ),
            OnboardingStep(
                id="customize_theme",
                title="Choose Your Theme",
                description="Select colors and styling preferences",
                stage=OnboardingStage.BRAND_CUSTOMIZATION,
                required=False,
                estimated_time=3
            ),
            
            # Agent Configuration
            OnboardingStep(
                id="first_agent",
                title="Create Your First Agent",
                description="Set up a simple task automation agent",
                stage=OnboardingStage.AGENT_CONFIGURATION,
                estimated_time=10,
                prerequisites=["profile_setup"]
            ),
            OnboardingStep(
                id="voice_agent_setup",
                title="Configure Voice Agent",
                description="Enable and customize your AI voice assistant",
                stage=OnboardingStage.AGENT_CONFIGURATION,
                estimated_time=8,
                prerequisites=["first_agent"]
            ),
            
            # Workflow Design
            OnboardingStep(
                id="visual_workflow",
                title="Design Your First Workflow",
                description="Use the visual builder to create agent workflows",
                stage=OnboardingStage.WORKFLOW_DESIGN,
                estimated_time=15,
                prerequisites=["first_agent"]
            ),
            
            # Integration Setup
            OnboardingStep(
                id="connect_tools",
                title="Connect Your Tools",
                description="Integrate with your existing business tools",
                stage=OnboardingStage.INTEGRATION_SETUP,
                required=False,
                estimated_time=10
            ),
            
            # Testing
            OnboardingStep(
                id="test_workflow",
                title="Test Your Setup",
                description="Run a test workflow to verify everything works",
                stage=OnboardingStage.TESTING,
                estimated_time=5,
                prerequisites=["visual_workflow"]
            ),
            
            # Production Ready
            OnboardingStep(
                id="monitoring_setup",
                title="Enable Monitoring",
                description="Set up alerts and monitoring dashboards",
                stage=OnboardingStage.PRODUCTION_READY,
                estimated_time=5
            ),
            OnboardingStep(
                id="success_celebration",
                title="You're Ready!",
                description="Congratulations! Your OrchestrateX platform is ready",
                stage=OnboardingStage.PRODUCTION_READY,
                estimated_time=1,
                auto_advance=True
            )
        ]
    
    async def start_onboarding(self, user_id: str) -> UserProgress:
        """Initialize onboarding for a new user"""
        progress = UserProgress(
            user_id=user_id,
            current_stage=OnboardingStage.WELCOME
        )
        self.user_progress[user_id] = progress
        
        # Send welcome email/notification
        await self._send_welcome_notification(user_id)
        
        return progress
    
    async def complete_step(self, user_id: str, step_id: str) -> bool:
        """Mark a step as completed and advance if possible"""
        if user_id not in self.user_progress:
            raise ValueError(f"No onboarding progress found for user {user_id}")
        
        progress = self.user_progress[user_id]
        step = self._get_step(step_id)
        
        if not step:
            raise ValueError(f"Step {step_id} not found")
        
        # Check prerequisites
        if not self._check_prerequisites(progress, step):
            return False
        
        # Mark as completed
        if step_id not in progress.completed_steps:
            progress.completed_steps.append(step_id)
        
        # Auto-advance if applicable
        if step.auto_advance:
            await self._advance_to_next_stage(user_id)
        
        # Check if stage is complete
        if self._is_stage_complete(progress, step.stage):
            await self._advance_to_next_stage(user_id)
        
        # Execute completion handler if present
        if step.completion_handler:
            await step.completion_handler(user_id, step_id)
        
        return True
    
    async def get_current_steps(self, user_id: str) -> List[OnboardingStep]:
        """Get available steps for user's current stage"""
        if user_id not in self.user_progress:
            return []
        
        progress = self.user_progress[user_id]
        current_steps = [
            step for step in self.steps 
            if step.stage == progress.current_stage
            and step.id not in progress.completed_steps
            and self._check_prerequisites(progress, step)
        ]
        
        return current_steps
    
    def get_progress_summary(self, user_id: str) -> Dict:
        """Get detailed progress summary"""
        if user_id not in self.user_progress:
            return {}
        
        progress = self.user_progress[user_id]
        total_steps = len([s for s in self.steps if s.required])
        completed_required = len([
            s for s in self.steps 
            if s.required and s.id in progress.completed_steps
        ])
        
        return {
            "user_id": user_id,
            "current_stage": progress.current_stage.value,
            "progress_percentage": (completed_required / total_steps) * 100,
            "total_steps": total_steps,
            "completed_steps": len(progress.completed_steps),
            "estimated_time_remaining": self._calculate_remaining_time(progress)
        }
    
    def _get_step(self, step_id: str) -> Optional[OnboardingStep]:
        """Find step by ID"""
        return next((s for s in self.steps if s.id == step_id), None)
    
    def _check_prerequisites(self, progress: UserProgress, step: OnboardingStep) -> bool:
        """Check if step prerequisites are met"""
        return all(
            prereq in progress.completed_steps 
            for prereq in step.prerequisites
        )
    
    def _is_stage_complete(self, progress: UserProgress, stage: OnboardingStage) -> bool:
        """Check if all required steps in stage are complete"""
        stage_steps = [s for s in self.steps if s.stage == stage and s.required]
        return all(
            step.id in progress.completed_steps 
            for step in stage_steps
        )
    
    async def _advance_to_next_stage(self, user_id: str):
        """Move user to the next onboarding stage"""
        progress = self.user_progress[user_id]
        stages = list(OnboardingStage)
        current_index = stages.index(progress.current_stage)
        
        if current_index < len(stages) - 1:
            progress.current_stage = stages[current_index + 1]
            await self._send_stage_notification(user_id, progress.current_stage)
    
    async def _send_welcome_notification(self, user_id: str):
        """Send welcome notification to user"""
        logger.info(f"Sending welcome notification to user {user_id}")
        # Implementation for sending notification
        pass
    
    async def _send_stage_notification(self, user_id: str, stage: OnboardingStage):
        """Send stage advancement notification"""
        logger.info(f"Sending stage notification to user {user_id} for stage {stage.value}")
        # Implementation for sending notification
        pass
    
    def _calculate_remaining_time(self, progress: UserProgress) -> int:
        """Calculate estimated time remaining in minutes"""
        remaining_steps = [
            s for s in self.steps 
            if s.required and s.id not in progress.completed_steps
        ]
        return sum(step.estimated_time for step in remaining_steps)
