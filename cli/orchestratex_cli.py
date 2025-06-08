import logging
import click
import json
from datetime import datetime
from ..services.project_completion_service import ProjectCompletionService
from ..core.progress_manager import ProgressManager
from ..core.recovery_manager import RecoveryManager
from ..ai.qwen_coder import QwenCoder

class OrchestratexCLI:
    def __init__(self):
        """Initialize CLI interface."""
        self.logger = logging.getLogger(__name__)
        self.project_service = ProjectCompletionService()
        self.progress_manager = ProgressManager()
        self.recovery_manager = RecoveryManager()
        self.qwen = QwenCoder()
        self._setup_commands()
        
    def _setup_commands(self):
        """Setup CLI commands."""
        @click.group()
        @click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
        def cli(verbose):
            """Orchestratex CLI interface."""
            if verbose:
                logging.basicConfig(level=logging.DEBUG)
            else:
                logging.basicConfig(level=logging.INFO)
                
        @cli.command()
        @click.argument('name')
        @click.argument('description')
        def create(name, description):
            """Create a new project."""
            try:
                project = self.project_service.create_project(name, description)
                click.echo(f"Created project: {project['name']}")
                click.echo(json.dumps(project, indent=2))
                
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        @cli.command()
        @click.argument('project_id')
        @click.argument('component_name')
        @click.argument('description')
        def add_component(project_id, component_name, description):
            """Add a component to a project."""
            try:
                component = {
                    "name": component_name,
                    "description": description,
                    "status": "pending"
                }
                success = self.project_service.add_component(project_id, component)
                if success:
                    click.echo(f"Added component {component_name} to project {project_id}")
                else:
                    click.echo("Failed to add component", err=True)
                    
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        @cli.command()
        @click.argument('project_id')
        @click.argument('component_id')
        def mark_complete(project_id, component_id):
            """Mark a component as complete."""
            try:
                success = self.project_service.mark_component_complete(project_id, component_id)
                if success:
                    click.echo(f"Marked component {component_id} complete")
                else:
                    click.echo("Failed to mark component complete", err=True)
                    
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        @cli.command()
        @click.argument('project_id')
        def get_progress(project_id):
            """Get project progress."""
            try:
                progress = self.project_service.get_project_progress(project_id)
                click.echo(json.dumps(progress, indent=2))
                
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        @cli.command()
        @click.argument('prompt')
        @click.option('--max-tokens', default=256, help='Maximum tokens to generate')
        @click.option('--temperature', default=0.7, help='Sampling temperature')
        def generate_code(prompt, max_tokens, temperature):
            """Generate code using Qwen Coder."""
            try:
                result = self.qwen.generate_code(
                    prompt,
                    max_new_tokens=max_tokens,
                    temperature=temperature
                )
                click.echo("Generated code:")
                click.echo(result["code"])
                
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        @cli.command()
        @click.argument('project_id')
        @click.argument('recovery_id')
        def recover(project_id, recovery_id):
            """Recover a project to a previous state."""
            try:
                success = self.project_service.recover_project(project_id, recovery_id)
                if success:
                    click.echo(f"Recovered project {project_id} to {recovery_id}")
                else:
                    click.echo("Recovery failed", err=True)
                    
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        @cli.command()
        @click.option('--days', default=30, help='Number of days to keep')
        def cleanup(days):
            """Cleanup old data."""
            try:
                stats = self.project_service.cleanup_old_data(days)
                click.echo(f"Cleaned up {stats['recovery_points_cleaned']} recovery points")
                click.echo(f"Cleaned up {stats['inactive_projects_cleaned']} inactive projects")
                
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        @cli.command()
        def list_projects():
            """List all projects."""
            try:
                projects = self.project_service.project_manager.list_projects()
                for project in projects:
                    click.echo(f"Project: {project['name']}")
                    click.echo(f"  ID: {project['id']}")
                    click.echo(f"  Created: {project['created_at']}")
                    click.echo(f"  Status: {project['status']}")
                    click.echo("")
                    
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        @cli.command()
        def start_dashboard():
            """Start the dashboard."""
            try:
                self.project_service.start_dashboard()
                click.echo("Dashboard started at http://localhost:8050")
                
            except Exception as e:
                click.echo(f"Error: {str(e)}", err=True)
                
        self.cli = cli
        
    def run(self):
        """Run the CLI."""
        self.cli()
