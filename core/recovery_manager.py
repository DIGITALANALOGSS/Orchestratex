import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import shutil
import tempfile

class RecoveryManager:
    def __init__(self, recovery_dir: str = "data/recovery"):
        """Initialize recovery manager.
        
        Args:
            recovery_dir: Directory for recovery data
        """
        self.logger = logging.getLogger(__name__)
        self.recovery_dir = recovery_dir
        self._ensure_recovery_dir()
        self.recovery_points = self._load_recovery_points()
        
    def _ensure_recovery_dir(self):
        """Ensure recovery directory exists."""
        os.makedirs(self.recovery_dir, exist_ok=True)
        
    def _load_recovery_points(self) -> Dict[str, Any]:
        """Load recovery points from file."""
        try:
            recovery_file = os.path.join(self.recovery_dir, "recovery_points.json")
            if os.path.exists(recovery_file):
                with open(recovery_file, 'r') as f:
                    return json.load(f)
            return self._initialize_default_recovery_points()
        except Exception as e:
            self.logger.error(f"Failed to load recovery points: {str(e)}")
            return self._initialize_default_recovery_points()
            
    def _initialize_default_recovery_points(self) -> Dict[str, Any]:
        """Initialize default recovery points structure."""
        return {
            "version": "1.0",
            "last_recovery": datetime.now().isoformat(),
            "recovery_points": [],
            "failed_operations": []
        }
        
    def create_recovery_point(self, description: str, data: Dict[str, Any]) -> str:
        """Create a recovery point.
        
        Args:
            description: Description of recovery point
            data: Data to save
            
        Returns:
            Recovery point ID
        """
        try:
            # Create recovery point ID
            recovery_id = f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create recovery point directory
            recovery_path = os.path.join(self.recovery_dir, recovery_id)
            os.makedirs(recovery_path)
            
            # Save recovery data
            with open(os.path.join(recovery_path, "data.json"), 'w') as f:
                json.dump(data, f, indent=2)
            
            # Update recovery points
            self.recovery_points["recovery_points"].append({
                "id": recovery_id,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "data_path": recovery_path
            })
            
            # Save recovery points
            self._save_recovery_points()
            
            self.logger.info(f"Created recovery point: {recovery_id}")
            return recovery_id
            
        except Exception as e:
            self.logger.error(f"Failed to create recovery point: {str(e)}")
            raise
            
    def _save_recovery_points(self):
        """Save recovery points to file."""
        try:
            recovery_file = os.path.join(self.recovery_dir, "recovery_points.json")
            temp_file = os.path.join(tempfile.gettempdir(), "orchestratex_recovery.json")
            
            # Write to temp file first
            with open(temp_file, 'w') as f:
                json.dump(self.recovery_points, f, indent=2)
            
            # Atomically replace the main file
            shutil.move(temp_file, recovery_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save recovery points: {str(e)}")
            raise
            
    def restore_recovery_point(self, recovery_id: str) -> bool:
        """Restore a recovery point.
        
        Args:
            recovery_id: Recovery point ID
            
        Returns:
            True if restore was successful
        """
        try:
            # Find recovery point
            recovery_point = None
            for point in self.recovery_points["recovery_points"]:
                if point["id"] == recovery_id:
                    recovery_point = point
                    break
            
            if not recovery_point:
                raise ValueError(f"Recovery point {recovery_id} not found")
                
            # Load recovery data
            data_path = recovery_point["data_path"]
            data_file = os.path.join(data_path, "data.json")
            
            if not os.path.exists(data_file):
                raise FileNotFoundError(f"Recovery data not found: {data_file}")
                
            with open(data_file, 'r') as f:
                recovery_data = json.load(f)
                
            # Update recovery points
            self.recovery_points["last_recovery"] = datetime.now().isoformat()
            self._save_recovery_points()
            
            self.logger.info(f"Restored recovery point: {recovery_id}")
            return recovery_data
            
        except Exception as e:
            self.logger.error(f"Failed to restore recovery point: {str(e)}")
            raise
            
    def get_recovery_points(self) -> List[Dict[str, Any]]:
        """Get list of available recovery points.
        
        Returns:
            List of recovery points
        """
        try:
            return sorted(
                self.recovery_points["recovery_points"],
                key=lambda x: x["timestamp"],
                reverse=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get recovery points: {str(e)}")
            return []
            
    def register_failed_operation(self, operation: Dict[str, Any]) -> None:
        """Register a failed operation for recovery.
        
        Args:
            operation: Failed operation details
        """
        try:
            self.recovery_points["failed_operations"].append({
                "operation": operation,
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            })
            self._save_recovery_points()
            
        except Exception as e:
            self.logger.error(f"Failed to register failed operation: {str(e)}")
            raise
            
    def recover_failed_operations(self) -> List[Dict[str, Any]]:
        """Attempt to recover failed operations.
        
        Returns:
            List of recovered operations
        """
        try:
            recovered = []
            
            # Process failed operations
            for op in self.recovery_points["failed_operations"]:
                if op["status"] == "failed":
                    try:
                        # Attempt recovery
                        # This would depend on the specific operation type
                        # For now, just mark as attempted
                        op["status"] = "attempted"
                        recovered.append(op)
                    except:
                        continue
                        
            # Update recovery points
            self._save_recovery_points()
            return recovered
            
        except Exception as e:
            self.logger.error(f"Failed to recover operations: {str(e)}")
            return []
            
    def cleanup_old_recovery_points(self, days: int = 7) -> int:
        """Cleanup old recovery points.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of recovery points cleaned up
        """
        try:
            cleanup_count = 0
            cutoff = datetime.now() - timedelta(days=days)
            
            # Clean up recovery points
            for point in self.recovery_points["recovery_points"]:
                ts = datetime.fromisoformat(point["timestamp"])
                if ts < cutoff:
                    # Remove recovery directory
                    if os.path.exists(point["data_path"]):
                        shutil.rmtree(point["data_path"])
                    
                    # Remove from list
                    self.recovery_points["recovery_points"].remove(point)
                    cleanup_count += 1
                    
            # Save changes
            self._save_recovery_points()
            return cleanup_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup recovery points: {str(e)}")
            return 0
