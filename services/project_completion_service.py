import logging
from typing import Dict, Any, Optional
import time
from ..core.project_manager import ProjectManager
from ..core.progress_manager import ProgressManager
from ..core.recovery_manager import RecoveryManager
from ..dashboard.completion_dashboard import CompletionDashboard
import dash

class ProjectCompletionService:
    def __init__(self):
        """Initialize project completion service."""
        self.logger = logging.getLogger(__name__)
        self.project_manager = ProjectManager()
        self.progress_manager = ProgressManager()
        self.recovery_manager = RecoveryManager()
        self.dashboard = None
        self._setup_dashboard()
        
    def _setup_dashboard(self):
        """Setup dashboard application."""
        try:
            app = dash.Dash(__name__)
            self.dashboard = CompletionDashboard(app)
            self.logger.info("Dashboard setup complete")
        except Exception as e:
            self.logger.error(f"Failed to setup dashboard: {str(e)}")
            
    def create_project(self, name: str, description: str) -> Dict[str, Any]:
        """Create a new project with completion tracking.
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Project information
        """
        try:
            # Create project
            project = self.project_manager.create_project(name, description)
            
            # Create initial recovery point
            self.recovery_manager.create_recovery_point(
                f"Project {name} creation",
                {"project": project}
            )
            
            # Track progress
            self.progress_manager.add_project_progress(
                project["id"],
                {"status": "created", "timestamp": datetime.now().isoformat()}
            )
            
            self.logger.info(f"Created project: {name}")
            return project
            
        except Exception as e:
            self.logger.error(f"Failed to create project: {str(e)}")
            raise
            
    def add_component(self, project_id: str, component: Dict[str, Any]) -> bool:
        """Add a component to a project with completion tracking.
        
        Args:
            project_id: Project ID
            component: Component information
            
        Returns:
            True if component was added successfully
        """
        try:
            # Add component
            success = self.project_manager.add_component(project_id, component)
            if not success:
                return False
                
            # Create recovery point
            self.recovery_manager.create_recovery_point(
                f"Component {component['name']} added to project",
                {"project_id": project_id, "component": component}
            )
            
            # Track progress
            self.progress_manager.add_project_progress(
                project_id,
                {"component": component["name"], "status": "added"}
            )
            
            self.logger.info(f"Added component {component['name']} to project {project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add component: {str(e)}")
            return False
            
    def mark_component_complete(self, project_id: str, component_id: str) -> bool:
        """Mark a component as complete with completion tracking.
        
        Args:
            project_id: Project ID
            component_id: Component ID
            
        Returns:
            True if component was marked complete
        """
        try:
            # Mark component complete
            success = self.project_manager.mark_component_complete(project_id, component_id)
            if not success:
                return False
                
            # Create recovery point
            self.recovery_manager.create_recovery_point(
                f"Component {component_id} marked complete",
                {"project_id": project_id, "component_id": component_id}
            )
            
            # Track progress
            self.progress_manager.add_project_progress(
                project_id,
                {"component": component_id, "status": "complete"}
            )
            
            self.logger.info(f"Marked component {component_id} complete in project {project_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mark component complete: {str(e)}")
            return False
            
    def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project progress information.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project progress information
        """
        try:
            # Get project data
            project = self.project_manager.get_project(project_id)
            if not project:
                return {
                    "error": "Project not found",
                    "status": "error"
                }
                
            # Get progress data
            progress = self.project_manager.get_project_progress(project_id)
            
            # Get recovery points
            recovery_points = self.recovery_manager.get_recovery_points()
            
            # Get failed operations
            failed_ops = self.recovery_manager.recovery_points["failed_operations"]
            
            return {
                "project": project,
                "progress": progress,
                "recovery_points": recovery_points,
                "failed_operations": failed_ops,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get project progress: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }
            
    def start_dashboard(self, host: str = '0.0.0.0', port: int = 8050) -> None:
        """Start the completion dashboard.
        
        Args:
            host: Host to run on
            port: Port to run on
        """
        if self.dashboard:
            self.dashboard.run(host=host, port=port)
        else:
            self.logger.error("Dashboard not initialized")
            
    def recover_project(self, project_id: str, recovery_id: str) -> bool:
        """Recover a project to a previous state.
        
        Args:
            project_id: Project ID
            recovery_id: Recovery point ID
            
        Returns:
            True if recovery was successful
        """
        try:
            # Restore recovery point
            recovery_data = self.recovery_manager.restore_recovery_point(recovery_id)
            if not recovery_data:
                return False
                
            # Update project
            project = recovery_data["project"]
            self.project_manager.update_project(project_id, project)
            
            # Create recovery point for the recovery operation
            self.recovery_manager.create_recovery_point(
                f"Project {project_id} recovered to {recovery_id}",
                {"project_id": project_id, "recovery_id": recovery_id}
            )
            
            self.logger.info(f"Recovered project {project_id} to {recovery_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to recover project: {str(e)}")
            return False
            
    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Cleanup old project data.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Cleanup statistics
        """
        try:
            # Cleanup recovery points
            recovery_count = self.recovery_manager.cleanup_old_recovery_points(days)
            
            # Cleanup unused projects
            projects = self.project_manager.list_projects()
            inactive_count = 0
            for project in projects:
                last_update = datetime.fromisoformat(project["updated_at"])
                if (datetime.now() - last_update).days > days:
                    self.project_manager.delete_project(project["id"])
                    inactive_count += 1
                    
            return {
                "recovery_points_cleaned": recovery_count,
                "inactive_projects_cleaned": inactive_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }
