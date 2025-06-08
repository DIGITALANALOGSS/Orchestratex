import os
import subprocess
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DevTools:
    def __init__(self, project_root: str = os.getcwd()):
        self.project_root = Path(project_root)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load development configuration."""
        config_path = self.project_root / "dev" / "config" / "dev_env.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path) as f:
            return json.load(f)

    def setup_ide(self) -> None:
        """Set up IDE configuration."""
        logger.info("Setting up IDE configuration...")
        
        # Create VS Code settings
        settings_path = self.project_root / ".vscode" / "settings.json"
        settings = {
            "python.analysis.typeCheckingMode": "basic",
            "python.linting.enabled": True,
            "python.formatting.provider": "black",
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            }
        }
        
        os.makedirs(settings_path.parent, exist_ok=True)
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        logger.info("IDE configuration complete")

    def setup_linting(self) -> None:
        """Set up linting tools."""
        logger.info("Setting up linting tools...")
        
        # Create pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        pyproject = {
            "tool": {
                "black": {
                    "line-length": 100,
                    "target-version": ["py310"]
                },
                "flake8": {
                    "max-line-length": 100,
                    "ignore": ["E501"]
                },
                "isort": {
                    "profile": "black",
                    "line_length": 100
                }
            }
        }
        
        with open(pyproject_path, 'w') as f:
            json.dump(pyproject, f, indent=2)
        
        logger.info("Linting configuration complete")

    def setup_debugging(self) -> None:
        """Set up debugging tools."""
        logger.info("Setting up debugging tools...")
        
        # Create launch configuration
        launch_path = self.project_root / ".vscode" / "launch.json"
        launch_config = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal",
                    "justMyCode": True
                },
                {
                    "name": "Python: Remote Attach",
                    "type": "python",
                    "request": "attach",
                    "port": 5678,
                    "host": "localhost",
                    "pathMappings": [
                        {
                            "localRoot": "${workspaceFolder}",
                            "remoteRoot": "/app"
                        }
                    ]
                }
            ]
        }
        
        os.makedirs(launch_path.parent, exist_ok=True)
        with open(launch_path, 'w') as f:
            json.dump(launch_config, f, indent=2)
        
        logger.info("Debugging configuration complete")

    def setup_version_control(self) -> None:
        """Set up version control configuration."""
        logger.info("Setting up version control...")
        
        # Create gitignore
        gitignore_path = self.project_root / ".gitignore"
        gitignore_content = """
        # Python
        __pycache__/
        *.py[cod]
        *.so
        .Python
        build/
        develop-eggs/
        dist/
        downloads/
        eggs/
        .eggs/
        lib/
        lib64/
        parts/
        sdist/
        var/
        *.egg-info/
        .installed.cfg
        *.egg

        # IDE
        .vscode/
        .idea/
        *.swp
        *.swo

        # Environment
        .env
        .venv
        env/
        venv/
        ENV/

        # Logs
        *.log
        logs/
        
        # Monitoring
        .prometheus/
        .grafana/
        
        # Test
        test_data/
        
        # Security
        .secrets/
        
        # Development
        .dev/
        """
        
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        
        logger.info("Version control configuration complete")

    def setup_all(self) -> None:
        """Set up all development tools."""
        logger.info("Setting up all development tools...")
        self.setup_ide()
        self.setup_linting()
        self.setup_debugging()
        self.setup_version_control()
        logger.info("All development tools setup complete")

if __name__ == "__main__":
    dev_tools = DevTools()
    dev_tools.setup_all()
