from .base import AgentBase
from typing import Dict, List
import random

class CollaborationAgent(AgentBase):
    def __init__(self, name="CollaborationAgent"):
        super().__init__(name, "Peer Learning & Community")
        self.users = {}
        self.groups = {}
        self.events = {}
    
    def match_peer(self, user_id: str, topic: str) -> str:
        if not self.users:
            return f"No peers available for {topic}"
            
        # Simple matching algorithm (in real implementation would use more sophisticated matching)
        peers = [uid for uid, data in self.users.items() 
                if data.get("topics") and topic in data["topics"]]
        
        if not peers:
            return f"No peers found for {topic}"
            
        peer = random.choice(peers)
        self._create_match(user_id, peer, topic)
        return f"Matched {user_id} with {peer} for {topic}"
    
    def _create_match(self, user1: str, user2: str, topic: str) -> None:
        if user1 not in self.users:
            self.users[user1] = {"topics": [topic], "matches": []}
        if user2 not in self.users:
            self.users[user2] = {"topics": [topic], "matches": []}
            
        self.users[user1]["matches"].append({"peer": user2, "topic": topic})
        self.users[user2]["matches"].append({"peer": user1, "topic": topic})
    
    def start_group(self, topic: str) -> str:
        group_id = f"group_{len(self.groups) + 1}"
        self.groups[group_id] = {
            "topic": topic,
            "members": [],
            "created_at": datetime.now().isoformat()
        }
        return f"Started group {group_id} for {topic}"
    
    def organize_event(self, event: Dict) -> str:
        event_id = f"event_{len(self.events) + 1}"
        self.events[event_id] = event
        return f"Organized event: {event['name']}"
    
    def mediate(self, user1: str, user2: str) -> str:
        # Simple mediation logic
        return f"Mediated discussion between {user1} and {user2}"
    
    def get_group_members(self, group_id: str) -> List[str]:
        return self.groups.get(group_id, {}).get("members", [])
    
    def add_to_group(self, group_id: str, user_id: str) -> str:
        if group_id in self.groups:
            self.groups[group_id]["members"].append(user_id)
            return f"Added {user_id} to group {group_id}"
        return f"Group {group_id} not found"
