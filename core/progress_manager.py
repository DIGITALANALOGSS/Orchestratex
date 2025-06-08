import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import shutil
import tempfile

class ProgressManager:
    def __init__(self, save_dir: str = "data/progress"):
        """Initialize progress manager.
        
        Args:
            save_dir: Directory to save progress
        """
        self.logger = logging.getLogger(__name__)
        self.save_dir = save_dir
        self._ensure_save_dir()
        self.progress = self._load_progress()
        
    def _ensure_save_dir(self):
        """Ensure save directory exists."""
        os.makedirs(self.save_dir, exist_ok=True)
        
    def _load_progress(self) -> Dict[str, Any]:
        """Load progress from file."""
        try:
            progress_file = os.path.join(self.save_dir, "progress.json")
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    return json.load(f)
            return self._initialize_default_progress()
        except Exception as e:
            self.logger.error(f"Failed to load progress: {str(e)}")
            return self._initialize_default_progress()
            
    def _initialize_default_progress(self) -> Dict[str, Any]:
        """Initialize default progress structure."""
        return {
            "version": "1.0",
            "last_save": datetime.now().isoformat(),
            "user_progress": {},
            "project_progress": {},
            "session_data": {},
            "backup_history": []
        }
        
    def save_progress(self, force: bool = False) -> bool:
        """Save current progress.
        
        Args:
            force: Force save even if no changes detected
            
        Returns:
            True if save was successful
        """
        try:
            # Create backup
            self._create_backup()
            
            # Save progress
            progress_file = os.path.join(self.save_dir, "progress.json")
            temp_file = os.path.join(tempfile.gettempdir(), "orchestratex_progress.json")
            
            # Write to temp file first
            with open(temp_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
            
            # Atomically replace the main file
            shutil.move(temp_file, progress_file)
            
            # Update last save time
            self.progress["last_save"] = datetime.now().isoformat()
            
            self.logger.info("Progress saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save progress: {str(e)}")
            return False
            
    def _create_backup(self):
        """Create a backup of the current progress."""
        try:
            backup_dir = os.path.join(self.save_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"progress_{timestamp}.json")
            
            # Copy current progress file
            current_file = os.path.join(self.save_dir, "progress.json")
            if os.path.exists(current_file):
                shutil.copy2(current_file, backup_file)
                
            # Update backup history
            self.progress["backup_history"].append({
                "timestamp": timestamp,
                "file": os.path.basename(backup_file)
            })
            
            # Keep only last 10 backups
            if len(self.progress["backup_history"]) > 10:
                oldest_backup = self.progress["backup_history"][0]
                oldest_file = os.path.join(backup_dir, oldest_backup["file"])
                if os.path.exists(oldest_file):
                    os.remove(oldest_file)
                self.progress["backup_history"] = self.progress["backup_history"][1:]
                
        except Exception as e:
            self.logger.error(f"Failed to create backup: {str(e)}")
            
    def restore_progress(self, backup_id: Optional[str] = None) -> bool:
        """Restore progress from a backup.
        
        Args:
            backup_id: Specific backup ID to restore
            
        Returns:
            True if restore was successful
        """
        try:
            backup_dir = os.path.join(self.save_dir, "backups")
            
            if backup_id:
                # Restore specific backup
                backup_file = os.path.join(backup_dir, f"progress_{backup_id}.json")
                if not os.path.exists(backup_file):
                    raise FileNotFoundError(f"Backup {backup_id} not found")
            else:
                # Restore latest backup
                backups = sorted(
                    [f for f in os.listdir(backup_dir) if f.startswith("progress_")],
                    reverse=True
                )
                if not backups:
                    raise FileNotFoundError("No backups found")
                backup_file = os.path.join(backup_dir, backups[0])
            
            # Restore backup
            current_file = os.path.join(self.save_dir, "progress.json")
            shutil.copy2(backup_file, current_file)
            
            # Load restored progress
            self.progress = self._load_progress()
            self.logger.info(f"Restored progress from {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore progress: {str(e)}")
            return False
            
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """Get list of available backups.
        
        Returns:
            List of backup information
        """
        try:
            backup_dir = os.path.join(self.save_dir, "backups")
            backups = []
            
            for backup in self.progress["backup_history"]:
                backup_file = os.path.join(backup_dir, backup["file"])
                if os.path.exists(backup_file):
                    stat = os.stat(backup_file)
                    backups.append({
                        "id": backup["timestamp"],
                        "file": backup["file"],
                        "size": stat.st_size,
                        "timestamp": backup["timestamp"]
                    })
            
            return backups
            
        except Exception as e:
            self.logger.error(f"Failed to get backup list: {str(e)}")
            return []
            
    def verify_integrity(self) -> bool:
        """Verify progress file integrity.
        
        Returns:
            True if integrity check passes
        """
        try:
            progress_file = os.path.join(self.save_dir, "progress.json")
            if not os.path.exists(progress_file):
                return False
                
            with open(progress_file, 'rb') as f:
                data = f.read()
                
            # Calculate checksum
            checksum = hashlib.sha256(data).hexdigest()
            
            # Verify checksum
            if checksum != self.progress.get("checksum", ""):
                self.logger.warning("Progress file checksum mismatch")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify integrity: {str(e)}")
            return False
            
    def add_user_progress(self, user_id: str, data: Dict[str, Any]) -> None:
        """Add user progress data.
        
        Args:
            user_id: User ID
            data: Progress data
        """
        if user_id not in self.progress["user_progress"]:
            self.progress["user_progress"][user_id] = {}
        self.progress["user_progress"][user_id].update(data)
        self.save_progress()
        
    def add_project_progress(self, project_id: str, data: Dict[str, Any]) -> None:
        """Add project progress data.
        
        Args:
            project_id: Project ID
            data: Progress data
        """
        if project_id not in self.progress["project_progress"]:
            self.progress["project_progress"][project_id] = {}
        self.progress["project_progress"][project_id].update(data)
        self.save_progress()
        
    def add_session_data(self, data: Dict[str, Any]) -> None:
        """Add session data.
        
        Args:
            data: Session data
        """
        self.progress["session_data"].update(data)
        self.save_progress()
        
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user progress.
        
        Args:
            user_id: User ID
            
        Returns:
            User progress data
        """
        return self.progress["user_progress"].get(user_id, {})
        
    def get_project_progress(self, project_id: str) -> Dict[str, Any]:
        """Get project progress.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project progress data
        """
        return self.progress["project_progress"].get(project_id, {})
        
    def get_session_data(self) -> Dict[str, Any]:
        """Get session data.
        
        Returns:
            Session data
        """
        return self.progress["session_data"]
