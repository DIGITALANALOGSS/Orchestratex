import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AuditHistory:
    def __init__(self, history_dir: str = "/var/lib/orchestratex/audit_history"):
        """Initialize audit history tracking."""
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_audit_file(self, audit_id: str) -> Path:
        """Get audit history file path."""
        return self.history_dir / f"audit_{audit_id}.json"

    def _get_latest_audit_id(self) -> Optional[str]:
        """Get latest audit ID from history."""
        audit_files = sorted(
            self.history_dir.glob("audit_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if audit_files:
            return audit_files[0].stem.replace("audit_", "")
        return None

    def _generate_audit_id(self) -> str:
        """Generate unique audit ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{os.urandom(8).hex()}"

    def record_audit(self, audit_data: Dict) -> str:
        """Record audit data to history."""
        try:
            audit_id = self._generate_audit_id()
            audit_file = self._get_audit_file(audit_id)
            
            audit_record = {
                "id": audit_id,
                "timestamp": datetime.now().isoformat(),
                "data": audit_data,
                "status": "completed"
            }
            
            with open(audit_file, 'w') as f:
                json.dump(audit_record, f, indent=2)
            
            logger.info(f"Audit recorded with ID: {audit_id}")
            return audit_id
            
        except Exception as e:
            logger.error(f"Failed to record audit: {str(e)}")
            raise

    def get_audit_by_id(self, audit_id: str) -> Optional[Dict]:
        """Get audit record by ID."""
        audit_file = self._get_audit_file(audit_id)
        
        if not audit_file.exists():
            logger.warning(f"Audit not found: {audit_id}")
            return None
            
        try:
            with open(audit_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to read audit: {str(e)}")
            return None

    def get_audit_history(self, limit: int = 100) -> List[Dict]:
        """Get audit history."""
        audit_files = sorted(
            self.history_dir.glob("audit_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        history = []
        for audit_file in audit_files[:limit]:
            try:
                with open(audit_file, 'r') as f:
                    history.append(json.load(f))
            except Exception as e:
                logger.error(f"Failed to read audit file: {str(e)}")
                continue
        
        return history

    def get_audit_stats(self) -> Dict:
        """Get audit statistics."""
        audit_files = list(self.history_dir.glob("audit_*.json"))
        total_audits = len(audits)
        
        if total_audits == 0:
            return {
                "total_audits": 0,
                "success_rate": 0.0,
                "average_duration": 0.0,
                "latest_audit": None,
                "audit_types": {}
            }
        
        success_count = 0
        total_duration = 0
        audit_types = {}
        latest_audit = None
        
        for audit_file in audit_files:
            try:
                with open(audit_file, 'r') as f:
                    audit = json.load(f)
                    
                    if audit["status"] == "completed":
                        success_count += 1
                        
                    if "duration" in audit["data"]:
                        total_duration += audit["data"]["duration"]
                        
                    audit_type = audit["data"].get("type", "unknown")
                    audit_types[audit_type] = audit_types.get(audit_type, 0) + 1
                    
                    if not latest_audit or audit["timestamp"] > latest_audit["timestamp"]:
                        latest_audit = audit
                        
            except Exception as e:
                logger.error(f"Failed to process audit file: {str(e)}")
                continue
        
        return {
            "total_audits": total_audits,
            "success_rate": (success_count / total_audits) * 100 if total_audits > 0 else 0,
            "average_duration": total_duration / total_audits if total_audits > 0 else 0,
            "latest_audit": latest_audit,
            "audit_types": audit_types
        }

    def get_audit_trends(self, days: int = 30) -> Dict:
        """Get audit trends over time."""
        audit_files = list(self.history_dir.glob("audit_*.json"))
        
        trends = {
            "daily_audits": {},
            "success_rates": {},
            "average_durations": {},
            "finding_counts": {}
        }
        
        for audit_file in audit_files:
            try:
                with open(audit_file, 'r') as f:
                    audit = json.load(f)
                    
                    audit_date = datetime.fromisoformat(audit["timestamp"]).date()
                    days_ago = (datetime.now().date() - audit_date).days
                    
                    if days_ago <= days:
                        date_str = audit_date.isoformat()
                        
                        if date_str not in trends["daily_audits"]:
                            trends["daily_audits"][date_str] = 0
                            trends["success_rates"][date_str] = []
                            trends["average_durations"][date_str] = []
                            trends["finding_counts"][date_str] = 0
                        
                        trends["daily_audits"][date_str] += 1
                        
                        if audit["status"] == "completed":
                            trends["success_rates"][date_str].append(1)
                        else:
                            trends["success_rates"][date_str].append(0)
                        
                        if "duration" in audit["data"]:
                            trends["average_durations"][date_str].append(audit["data"]["duration"])
                        
                        if "findings" in audit["data"]:
                            trends["finding_counts"][date_str] += len(audit["data"]["findings"])
                            
            except Exception as e:
                logger.error(f"Failed to process audit file: {str(e)}")
                continue
        
        # Calculate averages
        for date_str in trends["daily_audits"]:
            if trends["daily_audits"][date_str] > 0:
                success_rate = sum(trends["success_rates"][date_str]) / len(trends["success_rates"][date_str]) * 100
                avg_duration = sum(trends["average_durations"][date_str]) / len(trends["average_durations"][date_str])
                trends["success_rates"][date_str] = success_rate
                trends["average_durations"][date_str] = avg_duration
            else:
                trends["success_rates"][date_str] = 0
                trends["average_durations"][date_str] = 0
        
        return trends

    def cleanup_old_audits(self, days_to_keep: int = 90):
        """Cleanup old audit records."""
        audit_files = list(self.history_dir.glob("audit_*.json"))
        
        for audit_file in audit_files:
            try:
                audit_date = datetime.fromtimestamp(audit_file.stat().st_mtime)
                age = (datetime.now() - audit_date).days
                
                if age > days_to_keep:
                    audit_file.unlink()
                    logger.info(f"Removed old audit: {audit_file.name}")
                    
            except Exception as e:
                logger.error(f"Failed to cleanup audit: {str(e)}")
                continue

if __name__ == "__main__":
    # Example usage
    audit_history = AuditHistory()
    
    # Record a new audit
    audit_data = {
        "type": "security",
        "target": "api-server",
        "findings": [
            {"severity": "high", "description": "Vulnerability found"},
            {"severity": "medium", "description": "Configuration issue"}
        ],
        "duration": 120.5
    }
    audit_id = audit_history.record_audit(audit_data)
    
    # Get audit by ID
    audit = audit_history.get_audit_by_id(audit_id)
    print(f"Audit: {json.dumps(audit, indent=2)}")
    
    # Get audit history
    history = audit_history.get_audit_history()
    print(f"History: {json.dumps(history, indent=2)}")
    
    # Get audit stats
    stats = audit_history.get_audit_stats()
    print(f"Stats: {json.dumps(stats, indent=2)}")
    
    # Get audit trends
    trends = audit_history.get_audit_trends()
    print(f"Trends: {json.dumps(trends, indent=2)}")
