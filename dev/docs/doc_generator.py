import os
import sys
import inspect
import json
import yaml
from pathlib import Path
import shutil
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentationGenerator:
    def __init__(self, project_root: str = os.getcwd()):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.api_dir = self.docs_dir / "api"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load documentation configuration."""
        config_path = self.project_root / "docs" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path) as f:
            return yaml.safe_load(f)

    def generate_api_docs(self) -> None:
        """Generate API documentation."""
        logger.info("Generating API documentation...")
        
        # Create API directory
        os.makedirs(self.api_dir, exist_ok=True)
        
        # Generate API reference
        self._generate_api_reference()
        self._generate_swagger_docs()
        self._generate_api_examples()
        self._generate_api_changelog()
        
        logger.info("API documentation generation complete")

    def _generate_api_reference(self) -> None:
        """Generate API reference documentation."""
        api_ref_path = self.api_dir / "reference.md"
        
        with open(api_ref_path, 'w') as f:
            f.write("# API Reference\n\n")
            
            # Get all modules
            for module_name in self.config.get('modules', []):
                try:
                    module = __import__(module_name)
                    f.write(f"## {module_name}\n\n")
                    
                    # Get all classes
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj):
                            f.write(f"### {name}\n\n")
                            doc = inspect.getdoc(obj)
                            if doc:
                                f.write(f"{doc}\n\n")
                            
                            # Get methods
                            for method_name in dir(obj):
                                method = getattr(obj, method_name)
                                if inspect.isfunction(method):
                                    f.write(f"#### {method_name}\n\n")
                                    doc = inspect.getdoc(method)
                                    if doc:
                                        f.write(f"{doc}\n\n")
                except ImportError as e:
                    logger.warning(f"Could not import module {module_name}: {str(e)}")

    def _generate_swagger_docs(self) -> None:
        """Generate Swagger/OpenAPI documentation."""
        swagger_path = self.api_dir / "api.yaml"
        
        with open(swagger_path, 'w') as f:
            f.write("openapi: 3.0.0\n")
            f.write("info:\n")
            f.write("  title: Orchestratex API\n")
            f.write("  version: 1.0.0\n")
            f.write("paths:\n")
            
            # Add endpoints
            for endpoint in self.config.get('endpoints', []):
                f.write(f"  {endpoint['path']}:\n")
                f.write(f"    {endpoint['method']}:\n")
                f.write("      summary: " + endpoint.get('summary', '') + "\n")
                f.write("      description: " + endpoint.get('description', '') + "\n")
                f.write("      responses:\n")
                f.write("        '200':\n")
                f.write("          description: Success\n")

    def _generate_api_examples(self) -> None:
        """Generate API usage examples."""
        examples_path = self.api_dir / "examples.md"
        
        with open(examples_path, 'w') as f:
            f.write("# API Examples\n\n")
            
            # Add examples
            for example in self.config.get('examples', []):
                f.write(f"## {example['title']}\n\n")
                f.write(f"```python\n")
                f.write(f"{example['code']}\n")
                f.write("```\n\n")

    def _generate_api_changelog(self) -> None:
        """Generate API changelog."""
        changelog_path = self.api_dir / "changelog.md"
        
        with open(changelog_path, 'w') as f:
            f.write("# API Changelog\n\n")
            
            # Add changelog entries
            for entry in self.config.get('changelog', []):
                f.write(f"## {entry['version']}\n\n")
                f.write(f"{entry['description']}\n\n")

    def generate_architecture_docs(self) -> None:
        """Generate architecture documentation."""
        logger.info("Generating architecture documentation...")
        
        arch_dir = self.docs_dir / "architecture"
        os.makedirs(arch_dir, exist_ok=True)
        
        # Generate architecture overview
        self._generate_architecture_overview()
        self._generate_component_diagrams()
        self._generate_sequence_diagrams()
        self._generate_system_context_diagram()
        
        logger.info("Architecture documentation generation complete")

    def _generate_architecture_overview(self) -> None:
        """Generate architecture overview documentation."""
        overview_path = self.docs_dir / "architecture" / "overview.md"
        
        with open(overview_path, 'w') as f:
            f.write("# System Architecture\n\n")
            f.write("## Components\n\n")
            
            # Add components
            for component in self.config.get('components', []):
                f.write(f"### {component['name']}\n\n")
                f.write(f"{component['description']}\n\n")
                
                # Add responsibilities
                f.write("#### Responsibilities\n")
                for resp in component.get('responsibilities', []):
                    f.write(f"- {resp}\n")

    def _generate_component_diagrams(self) -> None:
        """Generate component diagrams."""
        diagrams_dir = self.docs_dir / "architecture" / "diagrams"
        os.makedirs(diagrams_dir, exist_ok=True)
        
        # Generate Mermaid diagrams
        diagram_path = diagrams_dir / "components.mmd"
        
        with open(diagram_path, 'w') as f:
            f.write("graph TD\n")
            
            # Add components and relationships
            for component in self.config.get('components', []):
                f.write(f"    {component['id']}[{component['name']}]\n")
                
                # Add relationships
                for rel in component.get('relationships', []):
                    f.write(f"    {component['id']} --> {rel['target']}\n")

    def _generate_sequence_diagrams(self) -> None:
        """Generate sequence diagrams."""
        diagrams_dir = self.docs_dir / "architecture" / "diagrams"
        os.makedirs(diagrams_dir, exist_ok=True)
        
        # Generate Mermaid sequence diagrams
        diagram_path = diagrams_dir / "sequences.mmd"
        
        with open(diagram_path, 'w') as f:
            f.write("sequenceDiagram\n")
            
            # Add participants
            for participant in self.config.get('participants', []):
                f.write(f"    participant {participant['id']} as {participant['name']}\n")
            
            # Add interactions
            for interaction in self.config.get('interactions', []):
                f.write(f"    {interaction['source']} ->> {interaction['target']}: {interaction['message']}\n")

    def _generate_system_context_diagram(self) -> None:
        """Generate system context diagram."""
        diagrams_dir = self.docs_dir / "architecture" / "diagrams"
        os.makedirs(diagrams_dir, exist_ok=True)
        
        # Generate Mermaid system context diagram
        diagram_path = diagrams_dir / "system_context.mmd"
        
        with open(diagram_path, 'w') as f:
            f.write("graph LR\n")
            
            # Add system context
            for context in self.config.get('system_context', []):
                f.write(f"    {context['id']}[{context['name']}]\n")
                
                # Add relationships
                for rel in context.get('relationships', []):
                    f.write(f"    {context['id']} --> {rel['target']}\n")

    def generate_deployment_docs(self) -> None:
        """Generate deployment documentation."""
        logger.info("Generating deployment documentation...")
        
        deploy_dir = self.docs_dir / "deployment"
        os.makedirs(deploy_dir, exist_ok=True)
        
        # Generate deployment guides
        self._generate_cloud_guide()
        self._generate_k8s_guide()
        self._generate_backup_guide()
        self._generate_upgrade_guide()
        
        logger.info("Deployment documentation generation complete")

    def _generate_cloud_guide(self) -> None:
        """Generate cloud deployment guide."""
        guide_path = self.docs_dir / "deployment" / "cloud_guide.md"
        
        with open(guide_path, 'w') as f:
            f.write("# Cloud Deployment Guide\n\n")
            
            # Add cloud providers
            for provider in self.config.get('cloud_providers', []):
                f.write(f"## {provider['name']}\n\n")
                f.write(f"{provider['description']}\n\n")
                
                # Add steps
                f.write("### Steps\n")
                for step in provider.get('steps', []):
                    f.write(f"1. {step}\n")

    def _generate_k8s_guide(self) -> None:
        """Generate Kubernetes deployment guide."""
        guide_path = self.docs_dir / "deployment" / "k8s_guide.md"
        
        with open(guide_path, 'w') as f:
            f.write("# Kubernetes Deployment Guide\n\n")
            
            # Add Kubernetes components
            for component in self.config.get('k8s_components', []):
                f.write(f"## {component['name']}\n\n")
                f.write(f"{component['description']}\n\n")
                
                # Add configuration
                f.write("### Configuration\n")
                f.write(f"```yaml\n")
                f.write(f"{component.get('config', '')}\n")
                f.write("```\n\n")

    def _generate_backup_guide(self) -> None:
        """Generate backup guide."""
        guide_path = self.docs_dir / "deployment" / "backup_guide.md"
        
        with open(guide_path, 'w') as f:
            f.write("# Backup Guide\n\n")
            
            # Add backup strategies
            for strategy in self.config.get('backup_strategies', []):
                f.write(f"## {strategy['name']}\n\n")
                f.write(f"{strategy['description']}\n\n")
                
                # Add procedures
                f.write("### Procedure\n")
                for step in strategy.get('procedure', []):
                    f.write(f"1. {step}\n")

    def _generate_upgrade_guide(self) -> None:
        """Generate upgrade guide."""
        guide_path = self.docs_dir / "deployment" / "upgrade_guide.md"
        
        with open(guide_path, 'w') as f:
            f.write("# Upgrade Guide\n\n")
            
            # Add upgrade steps
            for step in self.config.get('upgrade_steps', []):
                f.write(f"## {step['version']}\n\n")
                f.write(f"{step['description']}\n\n")
                
                # Add procedures
                f.write("### Procedure\n")
                for procedure in step.get('procedure', []):
                    f.write(f"1. {procedure}\n")

    def generate_all(self) -> None:
        """Generate all documentation."""
        logger.info("Generating all documentation...")
        
        # Create docs directory
        os.makedirs(self.docs_dir, exist_ok=True)
        
        # Generate all documentation
        self.generate_api_docs()
        self.generate_architecture_docs()
        self.generate_deployment_docs()
        
        logger.info("All documentation generation complete")

if __name__ == "__main__":
    generator = DocumentationGenerator()
    generator.generate_all()
