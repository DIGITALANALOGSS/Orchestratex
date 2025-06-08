from .base import AgentBase
from datetime import datetime
import statistics

class AnalyticsAgent(AgentBase):
    def __init__(self, name="AnalyticsAgent"):
        super().__init__(name, "Observability & Insights")
        self.activity_log = []
        self.metrics = {}
    
    def track_activity(self, user_id: str, action: str) -> str:
        timestamp = datetime.now().isoformat()
        self.activity_log.append({
            "user_id": user_id,
            "action": action,
            "timestamp": timestamp
        })
        return f"Tracked {action} for {user_id}"
    
    def detect_anomaly(self, data: List[float]) -> str:
        if not data:
            return "No data available for anomaly detection"
        
        mean = statistics.mean(data)
        stdev = statistics.stdev(data)
        
        for value in data:
            if abs(value - mean) > 3 * stdev:
                return f"Anomaly detected: Value {value} is outside normal range"
        
        return "No anomalies detected"
    
    def generate_report(self) -> Dict:
        report = {
            "total_users": len(set(log["user_id"] for log in self.activity_log)),
            "total_actions": len(self.activity_log),
            "most_common_actions": self._get_most_common_actions(),
            "user_engagement": self._calculate_engagement_metrics()
        }
        return report
    
    def optimize(self) -> str:
        suggestions = []
        if len(self.activity_log) > 100:
            suggestions.append("Consider implementing user segmentation")
        if len(self.metrics) > 50:
            suggestions.append("Monitor key metrics for optimization")
        return f"Suggested optimizations: {', '.join(suggestions)}"
    
    def _get_most_common_actions(self) -> Dict:
        action_counts = {}
        for log in self.activity_log:
            action = log["action"]
            action_counts[action] = action_counts.get(action, 0) + 1
        return {k: v for k, v in sorted(action_counts.items(), 
                                       key=lambda item: item[1], 
                                       reverse=True)[:5]}
    
    def _calculate_engagement_metrics(self) -> Dict:
        user_actions = {}
        for log in self.activity_log:
            user_id = log["user_id"]
            user_actions[user_id] = user_actions.get(user_id, 0) + 1
        
        avg_engagement = statistics.mean(user_actions.values())
        return {
            "average_engagement": avg_engagement,
            "highly_engaged_users": len([u for u in user_actions.values() 
                                        if u > avg_engagement * 1.5])
        }
