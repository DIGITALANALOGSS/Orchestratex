import logging
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import subprocess
import requests
from cryptography.fernet import Fernet

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RemediationService:
    def __init__(self, config_dir: str = "/etc/orchestratex/remediation"):
        """Initialize remediation service."""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.remediations = self._load_remediations()
        self.encryption_key = self._load_encryption_key()
        
    def _load_encryption_key(self) -> bytes:
        """Load or generate encryption key."""
        key_file = self.config_dir / "encryption.key"
        if not key_file.exists():
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        else:
            with open(key_file, 'rb') as f:
                key = f.read()
        return key

    def _load_remediations(self) -> Dict:
        """Load remediation configurations."""
        remediations = {}
        for file in self.config_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    remediations[data["id"]] = data
            except Exception as e:
                logger.error(f"Failed to load remediation {file}: {str(e)}")
        return remediations

    def _save_remediation(self, remediation_id: str, data: Dict):
        """Save remediation configuration."""
        try:
            file = self.config_dir / f"{remediation_id}.json"
            with open(file, 'w') as f:
                json.dump(data, f, indent=2)
            self.remediations[remediation_id] = data
            logger.info(f"Remediation saved: {remediation_id}")
        except Exception as e:
            logger.error(f"Failed to save remediation: {str(e)}")
            raise

    def add_remediation(self, remediation_data: Dict) -> bool:
        """Add new remediation."""
        try:
            remediation_id = remediation_data.get("id")
            if not remediation_id:
                raise ValueError("Remediation ID is required")
                
            # Validate remediation data
            required_fields = ["type", "description", "steps"]
            if not all(field in remediation_data for field in required_fields):
                raise ValueError(f"Missing required fields: {required_fields}")
                
            # Encrypt sensitive data
            if "secrets" in remediation_data:
                fernet = Fernet(self.encryption_key)
                remediation_data["secrets"] = {
                    k: fernet.encrypt(v.encode()).decode()
                    for k, v in remediation_data["secrets"].items()
                }
            
            self._save_remediation(remediation_id, remediation_data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add remediation: {str(e)}")
            return False

    def remove_remediation(self, remediation_id: str) -> bool:
        """Remove remediation."""
        try:
            if remediation_id in self.remediations:
                file = self.config_dir / f"{remediation_id}.json"
                if file.exists():
                    file.unlink()
                del self.remediations[remediation_id]
                logger.info(f"Remediation removed: {remediation_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove remediation: {str(e)}")
            return False

    def update_remediation(self, remediation_id: str, data: Dict) -> bool:
        """Update remediation."""
        try:
            if remediation_id in self.remediations:
                # Merge new data with existing
                self.remediations[remediation_id].update(data)
                # Re-encrypt secrets if they exist
                if "secrets" in data:
                    fernet = Fernet(self.encryption_key)
                    self.remediations[remediation_id]["secrets"] = {
                        k: fernet.encrypt(v.encode()).decode()
                        for k, v in data["secrets"].items()
                    }
                self._save_remediation(remediation_id, self.remediations[remediation_id])
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update remediation: {str(e)}")
            return False

    async def execute_remediation(self, remediation_id: str, context: Dict = None) -> Dict:
        """Execute remediation steps."""
        try:
            if remediation_id not in self.remediations:
                raise ValueError(f"Remediation not found: {remediation_id}")
                
            remediation = self.remediations[remediation_id]
            results = {
                "id": remediation_id,
                "status": "in_progress",
                "steps": [],
                "timestamp": datetime.now().isoformat()
            }
            
            # Decrypt secrets if they exist
            if "secrets" in remediation:
                fernet = Fernet(self.encryption_key)
                remediation["secrets"] = {
                    k: fernet.decrypt(v.encode()).decode()
                    for k, v in remediation["secrets"].items()
                }
            
            for step in remediation["steps"]:
                step_result = {
                    "type": step["type"],
                    "status": "failed",
                    "output": None,
                    "error": None
                }
                
                try:
                    if step["type"] == "command":
                        result = await self._execute_command(step, context)
                    elif step["type"] == "script":
                        result = await self._execute_script(step, context)
                    elif step["type"] == "api":
                        result = await self._execute_api(step, context)
                    else:
                        raise ValueError(f"Unknown step type: {step["type"]}")
                        
                    step_result.update(result)
                    
                except Exception as e:
                    step_result["error"] = str(e)
                    logger.error(f"Step failed: {step["type"]} - {str(e)}")
                    break
                
                results["steps"].append(step_result)
            
            # Determine overall status
            results["status"] = "success" if all(
                step["status"] == "success" for step in results["steps"]
            ) else "failed"
            
            logger.info(f"Remediation completed: {remediation_id} - {results["status"]}")
            return results
            
        except Exception as e:
            logger.error(f"Remediation failed: {str(e)}")
            return {
                "id": remediation_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _execute_command(self, step: Dict, context: Dict) -> Dict:
        """Execute command step."""
        try:
            command = step["command"].format(**context) if context else step["command"]
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            return {
                "status": "success" if process.returncode == 0 else "failed",
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _execute_script(self, step: Dict, context: Dict) -> Dict:
        """Execute script step."""
        try:
            script_path = step["script"]
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script not found: {script_path}")
                
            # Read and execute script
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            # Execute script with context
            exec_globals = {
                "context": context,
                "secrets": step.get("secrets", {})
            }
            exec(script_content, exec_globals)
            
            return {
                "status": "success",
                "output": "Script executed successfully"
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    async def _execute_api(self, step: Dict, context: Dict) -> Dict:
        """Execute API step."""
        try:
            url = step["url"].format(**context) if context else step["url"]
            method = step.get("method", "GET")
            headers = step.get("headers", {})
            data = step.get("data")
            
            # Add context to headers and data
            for key in headers:
                headers[key] = headers[key].format(**context) if context else headers[key]
            if data:
                data = data.format(**context) if context else data
                
            response = requests.request(method, url, headers=headers, data=data)
            
            return {
                "status": "success" if response.status_code < 400 else "failed",
                "output": response.json() if response.text else None,
                "error": response.text if response.status_code >= 400 else None
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    def get_remediation(self, remediation_id: str) -> Optional[Dict]:
        """Get remediation configuration."""
        return self.remediations.get(remediation_id)

    def get_remediations(self) -> Dict:
        """Get all remediations."""
        return self.remediations

    def get_remediation_stats(self) -> Dict:
        """Get remediation statistics."""
        stats = {
            "total": len(self.remediations),
            "types": {},
            "severity": {},
            "last_updated": datetime.now().isoformat()
        }
        
        for remediation in self.remediations.values():
            remediation_type = remediation.get("type", "unknown")
            severity = remediation.get("severity", "medium")
            
            stats["types"][remediation_type] = stats["types"].get(remediation_type, 0) + 1
            stats["severity"][severity] = stats["severity"].get(severity, 0) + 1
        
        return stats

if __name__ == "__main__":
    # Example usage
    service = RemediationService()
    
    # Add example remediation
    remediation = {
        "id": "fix_file_perms",
        "type": "security",
        "description": "Fix critical file permissions",
        "severity": "high",
        "steps": [
            {
                "type": "command",
                "command": "chmod 0600 /etc/ssh/sshd_config"
            },
            {
                "type": "command",
                "command": "chown root:root /etc/ssh/sshd_config"
            },
            {
                "type": "api",
                "url": "https://api.security-system.com/audit-log",
                "method": "POST",
                "headers": {
                    "Authorization": "Bearer {token}"
                },
                "data": {
                    "action": "remediation",
                    "target": "/etc/ssh/sshd_config"
                }
            }
        ]
    }
    
    # Add remediation
    service.add_remediation(remediation)
    
    # Execute remediation
    context = {
        "token": "your-security-token"
    }
    
    result = asyncio.run(service.execute_remediation("fix_file_perms", context))
    print(json.dumps(result, indent=2))
    
    # Get remediation stats
    stats = service.get_remediation_stats()
    print(json.dumps(stats, indent=2))
