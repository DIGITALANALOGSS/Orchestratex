import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import os
import hashlib
import shutil
from pathlib import Path

class ProjectManager:
    def __init__(self, projects_dir: str = "projects"):
        """Initialize project manager.
        
        Args:
            projects_dir: Directory to store projects
        """
        self.logger = logging.getLogger(__name__)
        self.projects_dir = projects_dir
        self._ensure_projects_dir()
        self.projects = self._load_projects()
        
    def _ensure_projects_dir(self):
        """Ensure projects directory exists."""
        os.makedirs(self.projects_dir, exist_ok=True)
        
    def _load_projects(self) -> Dict[str, Any]:
        """Load projects from file."""
        try:
            projects_file = os.path.join(self.projects_dir, "projects.json")
            if os.path.exists(projects_file):
                with open(projects_file, 'r') as f:
                    return json.load(f)
            return self._initialize_default_projects()
        except Exception as e:
            self.logger.error(f"Failed to load projects: {str(e)}")
            return self._initialize_default_projects()
            
    def _initialize_default_projects(self) -> Dict[str, Any]:
        """Initialize default projects structure."""
        return {
            "version": "1.0",
            "last_update": datetime.now().isoformat(),
            "projects": {}
        }
        
    def create_project(self, name: str, description: str) -> Dict[str, Any]:
        """Create a new project.
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Project information
        """
        try:
            # Generate project ID
            project_id = f"project_{hashlib.sha256(name.encode()).hexdigest()[:8]}"
            
            # Create project directory
            project_dir = os.path.join(self.projects_dir, project_id)
            os.makedirs(project_dir)
            
            # Create project structure
            project_data = {
                "id": project_id,
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active",
                "components": {},
                "dependencies": {},
                "progress": {
                    "completed": 0,
                    "total": 0,
                    "percentage": 0
                },
                "metadata": {}
            }
            
            # Initialize project files
            self._create_project_files(project_dir, project_data)
            
            # Add to projects
            self.projects["projects"][project_id] = project_data
            self._save_projects()
            
            self.logger.info(f"Created project: {name}")
            return project_data
            
        except Exception as e:
            self.logger.error(f"Failed to create project: {str(e)}")
            raise
            
    def _create_project_files(self, project_dir: str, project_data: Dict[str, Any]):
        """Create initial project files.
        
        Args:
            project_dir: Project directory
            project_data: Project data
        """
        try:
            # Create README
            with open(os.path.join(project_dir, "README.md"), 'w') as f:
                f.write(f"# {project_data['name']}\n\n{project_data['description']}")
            
            # Create requirements file
            with open(os.path.join(project_dir, "requirements.txt"), 'w') as f:
                f.write("# Project dependencies\n")
            
            # Create gitignore
            with open(os.path.join(project_dir, ".gitignore"), 'w') as f:
                f.write("\n".join([
                    "__pycache__/*",
                    "*.pyc",
                    ".env",
                    "*.log",
                    "data/*",
                    "temp/*"
                ]))
            
            # Create project structure
            for dir_name in ["src", "tests", "docs", "data", "temp"]:
                os.makedirs(os.path.join(project_dir, dir_name))
                
        except Exception as e:
            self.logger.error(f"Failed to create project files: {str(e)}")
            raise
            
    def _save_projects(self):
        """Save projects to file."""
        try:
            projects_file = os.path.join(self.projects_dir, "projects.json")
            temp_file = os.path.join(self.projects_dir, "temp_projects.json")
            
            # Write to temp file first
            with open(temp_file, 'w') as f:
                json.dump(self.projects, f, indent=2)
            
            # Atomically replace the main file
            shutil.move(temp_file, projects_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save projects: {str(e)}")
            raise
            
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project information.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project information or None if not found
        """
        return self.projects["projects"].get(project_id)
        
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update project information.
        
        Args:
            project_id: Project ID
            updates: Updates to apply
            
        Returns:
            True if update was successful
        """
        try:
            project = self.get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
                
            project.update(updates)
            project["updated_at"] = datetime.now().isoformat()
            self._save_projects()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update project: {str(e)}")
            return False
            
    def delete_project(self, project_id: str) -> bool:
        """Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deletion was successful
        """
        try:
            # Remove from projects
            if project_id in self.projects["projects"]:
                del self.projects["projects"][project_id]
                
            # Remove project directory
            project_dir = os.path.join(self.projects_dir, project_id)
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
                
            self._save_projects()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete project: {str(e)}")
            return False
            
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects.
        
        Returns:
            List of project information
        """
        return list(self.projects["projects"].values())
        
    def add_component(self, project_id: str, component: Dict[str, Any]) -> bool:
        """Add a component to a project.
        
        Args:
            project_id: Project ID
            component: Component information
            
        Returns:
            True if component was added successfully
        """
        try:
            project = self.get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
                
            component_id = f"component_{hashlib.sha256(component['name'].encode()).hexdigest()[:8]}"
            project["components"][component_id] = component
            
            # Update progress
            project["progress"]["total"] += 1
            self._save_projects()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add component: {str(e)}")
            return False
            
    def mark_component_complete(self, project_id: str, component_id: str) -> bool:
        """Mark a component as complete.
        
        Args:
            project_id: Project ID
            component_id: Component ID
            
        Returns:
            True if component was marked complete
        """
        try:
            project = self.get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
                
            if component_id not in project["components"]:
                raise ValueError(f"Component {component_id} not found")
                
            project["components"][component_id]["status"] = "complete"
            project["progress"]["completed"] += 1
            project["progress"]["percentage"] = (
                project["progress"]["completed"] / project["progress"]["total"] * 100
            )
            
            self._save_projects()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to mark component complete: {str(e)}")
            return False
            
    def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get project progress.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project progress information
        """
        project = self.get_project(project_id)
        if not project:
            return {
                "completed": 0,
                "total": 0,
                "percentage": 0
            }
            
        return project["progress"]
