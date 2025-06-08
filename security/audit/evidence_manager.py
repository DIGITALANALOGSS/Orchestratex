import logging
import json
import os
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EvidenceManager:
    def __init__(self, evidence_dir: str = "/var/lib/orchestratex/evidence"):
        """Initialize evidence manager."""
        self.evidence_dir = Path(evidence_dir)
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_evidence_file(self, evidence_id: str) -> Path:
        """Get evidence file path."""
        return self.evidence_dir / f"evidence_{evidence_id}.json"

    def _generate_evidence_id(self) -> str:
        """Generate unique evidence ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}_{os.urandom(8).hex()}"

    def _calculate_hash(self, data: bytes) -> str:
        """Calculate SHA-256 hash of data."""
        return hashlib.sha256(data).hexdigest()

    def store_evidence(self, evidence_data: Dict, file_path: Optional[str] = None) -> str:
        """Store evidence data."""
        try:
            evidence_id = self._generate_evidence_id()
            evidence_file = self._get_evidence_file(evidence_id)
            
            evidence_record = {
                "id": evidence_id,
                "timestamp": datetime.now().isoformat(),
                "data": evidence_data,
                "type": evidence_data.get("type", "unknown"),
                "status": "valid",
                "validation": {}
            }
            
            if file_path:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    evidence_record["file_hash"] = self._calculate_hash(file_data)
                    evidence_record["file_size"] = len(file_data)
                    
            with open(evidence_file, 'w') as f:
                json.dump(evidence_record, f, indent=2)
            
            logger.info(f"Evidence stored with ID: {evidence_id}")
            return evidence_id
            
        except Exception as e:
            logger.error(f"Failed to store evidence: {str(e)}")
            raise

    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict]:
        """Get evidence record by ID."""
        evidence_file = self._get_evidence_file(evidence_id)
        
        if not evidence_file.exists():
            logger.warning(f"Evidence not found: {evidence_id}")
            return None
            
        try:
            with open(evidence_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Failed to read evidence: {str(e)}")
            return None

    def validate_evidence(self, evidence_id: str, file_path: Optional[str] = None) -> bool:
        """Validate evidence integrity."""
        evidence = self.get_evidence_by_id(evidence_id)
        if not evidence:
            return False
            
        if file_path and "file_hash" in evidence:
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    current_hash = self._calculate_hash(file_data)
                    
                if current_hash != evidence["file_hash"]:
                    evidence["status"] = "invalid"
                    evidence["validation"] = {
                        "status": "failed",
                        "reason": "File hash mismatch",
                        "expected_hash": evidence["file_hash"],
                        "current_hash": current_hash
                    }
                    
                    self._update_evidence(evidence_id, evidence)
                    return False
                    
            except Exception as e:
                logger.error(f"Failed to validate evidence: {str(e)}")
                return False
                
        return True

    def _update_evidence(self, evidence_id: str, evidence_data: Dict):
        """Update evidence record."""
        evidence_file = self._get_evidence_file(evidence_id)
        
        try:
            with open(evidence_file, 'w') as f:
                json.dump(evidence_data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to update evidence: {str(e)}")
            raise

    def get_evidence_history(self, limit: int = 100) -> List[Dict]:
        """Get evidence history."""
        evidence_files = sorted(
            self.evidence_dir.glob("evidence_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        history = []
        for evidence_file in evidence_files[:limit]:
            try:
                with open(evidence_file, 'r') as f:
                    history.append(json.load(f))
            except Exception as e:
                logger.error(f"Failed to read evidence file: {str(e)}")
                continue
        
        return history

    def get_evidence_stats(self) -> Dict:
        """Get evidence statistics."""
        evidence_files = list(self.evidence_dir.glob("evidence_*.json"))
        total_evidence = len(evidence_files)
        
        if total_evidence == 0:
            return {
                "total_evidence": 0,
                "valid_rate": 0.0,
                "average_size": 0.0,
                "latest_evidence": None,
                "evidence_types": {}
            }
        
        valid_count = 0
        total_size = 0
        evidence_types = {}
        latest_evidence = None
        
        for evidence_file in evidence_files:
            try:
                with open(evidence_file, 'r') as f:
                    evidence = json.load(f)
                    
                    if evidence["status"] == "valid":
                        valid_count += 1
                        
                    if "file_size" in evidence:
                        total_size += evidence["file_size"]
                        
                    evidence_type = evidence.get("type", "unknown")
                    evidence_types[evidence_type] = evidence_types.get(evidence_type, 0) + 1
                    
                    if not latest_evidence or evidence["timestamp"] > latest_evidence["timestamp"]:
                        latest_evidence = evidence
                        
            except Exception as e:
                logger.error(f"Failed to process evidence file: {str(e)}")
                continue
        
        return {
            "total_evidence": total_evidence,
            "valid_rate": (valid_count / total_evidence) * 100 if total_evidence > 0 else 0,
            "average_size": total_size / total_evidence if total_evidence > 0 else 0,
            "latest_evidence": latest_evidence,
            "evidence_types": evidence_types
        }

    def get_evidence_trends(self, days: int = 30) -> Dict:
        """Get evidence trends over time."""
        evidence_files = list(self.evidence_dir.glob("evidence_*.json"))
        
        trends = {
            "daily_evidence": {},
            "valid_rates": {},
            "average_sizes": {},
            "type_counts": {}
        }
        
        for evidence_file in evidence_files:
            try:
                with open(evidence_file, 'r') as f:
                    evidence = json.load(f)
                    
                    evidence_date = datetime.fromisoformat(evidence["timestamp"]).date()
                    days_ago = (datetime.now().date() - evidence_date).days
                    
                    if days_ago <= days:
                        date_str = evidence_date.isoformat()
                        
                        if date_str not in trends["daily_evidence"]:
                            trends["daily_evidence"][date_str] = 0
                            trends["valid_rates"][date_str] = []
                            trends["average_sizes"][date_str] = []
                            trends["type_counts"][date_str] = {}
                        
                        trends["daily_evidence"][date_str] += 1
                        
                        if evidence["status"] == "valid":
                            trends["valid_rates"][date_str].append(1)
                        else:
                            trends["valid_rates"][date_str].append(0)
                        
                        if "file_size" in evidence:
                            trends["average_sizes"][date_str].append(evidence["file_size"])
                        
                        evidence_type = evidence.get("type", "unknown")
                        trends["type_counts"][date_str][evidence_type] = \
                            trends["type_counts"][date_str].get(evidence_type, 0) + 1
                            
            except Exception as e:
                logger.error(f"Failed to process evidence file: {str(e)}")
                continue
        
        # Calculate averages
        for date_str in trends["daily_evidence"]:
            if trends["daily_evidence"][date_str] > 0:
                valid_rate = sum(trends["valid_rates"][date_str]) / len(trends["valid_rates"][date_str]) * 100
                avg_size = sum(trends["average_sizes"][date_str]) / len(trends["average_sizes"][date_str])
                trends["valid_rates"][date_str] = valid_rate
                trends["average_sizes"][date_str] = avg_size
            else:
                trends["valid_rates"][date_str] = 0
                trends["average_sizes"][date_str] = 0
        
        return trends

    def cleanup_old_evidence(self, days_to_keep: int = 180):
        """Cleanup old evidence records."""
        evidence_files = list(self.evidence_dir.glob("evidence_*.json"))
        
        for evidence_file in evidence_files:
            try:
                evidence_date = datetime.fromtimestamp(evidence_file.stat().st_mtime)
                age = (datetime.now() - evidence_date).days
                
                if age > days_to_keep:
                    evidence_file.unlink()
                    logger.info(f"Removed old evidence: {evidence_file.name}")
                    
            except Exception as e:
                logger.error(f"Failed to cleanup evidence: {str(e)}")
                continue

if __name__ == "__main__":
    # Example usage
    evidence_manager = EvidenceManager()
    
    # Store evidence
    evidence_data = {
        "type": "compliance",
        "description": "Security policy document",
        "metadata": {
            "version": "1.0",
            "author": "security-team",
            "review_date": "2025-06-08"
        }
    }
    evidence_id = evidence_manager.store_evidence(evidence_data)
    
    # Get evidence by ID
    evidence = evidence_manager.get_evidence_by_id(evidence_id)
    print(f"Evidence: {json.dumps(evidence, indent=2)}")
    
    # Get evidence history
    history = evidence_manager.get_evidence_history()
    print(f"History: {json.dumps(history, indent=2)}")
    
    # Get evidence stats
    stats = evidence_manager.get_evidence_stats()
    print(f"Stats: {json.dumps(stats, indent=2)}")
    
    # Get evidence trends
    trends = evidence_manager.get_evidence_trends()
    print(f"Trends: {json.dumps(trends, indent=2)}")
