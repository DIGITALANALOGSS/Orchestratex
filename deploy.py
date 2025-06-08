import os
import subprocess
import sys
import logging
from pathlib import Path
import shutil
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log'),
        logging.StreamHandler()
    ]
)

class OrchestratexDeployer:
    def __init__(self):
        self.config = {
            "project_name": "Orchestratex",
            "version": "1.0.0",
            "directories": {
                "temp": "temp",
                "logs": "logs",
                "assets": "assets"
            },
            "required_files": [
                "requirements.txt",
                "README.md",
                "DEPLOYMENT.md",
                "config.json"
            ]
        }

    def check_prerequisites(self):
        """Check if all prerequisites are met."""
        logging.info("Checking prerequisites...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            raise Exception("Python 3.8 or higher is required")

        # Check required directories
        for dir_name in self.config["directories"].values():
            if not os.path.exists(dir_name):
                logging.info(f"Creating directory: {dir_name}")
                os.makedirs(dir_name)

        # Check required files
        for file in self.config["required_files"]:
            if not os.path.exists(file):
                raise Exception(f"Required file not found: {file}")

    def setup_virtual_environment(self):
        """Set up virtual environment."""
        logging.info("Setting up virtual environment...")
        
        # Create virtual environment
        if not os.path.exists("venv"):
            subprocess.run(["python", "-m", "venv", "venv"], check=True)
            
        # Activate virtual environment
        if sys.platform == "win32":
            activate_script = "venv\Scripts\activate"
        else:
            activate_script = "source venv/bin/activate"
            
        logging.info("Virtual environment activated")

    def install_dependencies(self):
        """Install project dependencies."""
        logging.info("Installing dependencies...")
        
        # Install requirements
        subprocess.run([
            "python", "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)

    def setup_environment(self):
        """Set up environment variables."""
        logging.info("Setting up environment variables...")
        
        # Create .env file if it doesn't exist
        if not os.path.exists(".env"):
            env_template = {
                "PROJECT_NAME": self.config["project_name"],
                "VERSION": self.config["version"],
                "SECRET_KEY": "your-secret-key-here",
                "DATABASE_URL": "postgresql://user:password@localhost:5432/orchestratex",
                "REDIS_HOST": "localhost",
                "REDIS_PORT": "6379",
                "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
                "PINECONE_API_KEY": "your-pinecone-key"
            }
            
            with open(".env", "w") as f:
                for key, value in env_template.items():
                    f.write(f"{key}={value}\n")
            
            logging.info("Created .env file with template values")

    def setup_assets(self):
        """Set up required assets."""
        logging.info("Setting up assets...")
        
        assets_dir = Path("assets")
        required_assets = [
            "main_image.jpg",
            "logo.png"
        ]
        
        # Create placeholder assets if they don't exist
        for asset in required_assets:
            asset_path = assets_dir / asset
            if not asset_path.exists():
                logging.warning(f"Creating placeholder for: {asset}")
                with open(asset_path, "w") as f:
                    f.write("Placeholder file")

    def run_tests(self):
        """Run unit and integration tests."""
        logging.info("Running tests...")
        
        # Run unit tests
        subprocess.run(["python", "-m", "pytest", "tests/"], check=True)
        
        # Run integration tests
        subprocess.run(["python", "-m", "pytest", "tests/integration/"], check=True)

    def setup_logging(self):
        """Set up logging configuration."""
        logging.info("Setting up logging...")
        
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Set up log rotation
        try:
            import logging.handlers
            handler = logging.handlers.RotatingFileHandler(
                'logs/app.log',
                maxBytes=1024*1024,
                backupCount=5
            )
            logging.getLogger('').addHandler(handler)
        except Exception as e:
            logging.error(f"Failed to set up log rotation: {str(e)}")

    def deploy(self):
        """Main deployment function."""
        try:
            logging.info("Starting deployment process...")
            
            # Run deployment steps
            self.check_prerequisites()
            self.setup_virtual_environment()
            self.install_dependencies()
            self.setup_environment()
            self.setup_assets()
            self.run_tests()
            self.setup_logging()
            
            logging.info("Deployment completed successfully!")
            
        except Exception as e:
            logging.error(f"Deployment failed: {str(e)}")
            raise

if __name__ == "__main__":
    deployer = OrchestratexDeployer()
    deployer.deploy()
