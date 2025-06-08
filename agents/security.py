from .base import AgentBase
from cryptography.fernet import Fernet
import hashlib

class SecurityAgent(AgentBase):
    def __init__(self, name="SecurityAgent"):
        super().__init__(name, "Security & Compliance Guardian")
        self._key = Fernet.generate_key()
        self._fernet = Fernet(self._key)
    
    def enforce_rbac(self, user_role):
        allowed_roles = ["admin", "mentor", "learner"]
        if user_role not in allowed_roles:
            raise PermissionError(f"Access denied: Role '{user_role}' is not authorized")
        return "Access granted"
    
    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self._fernet.encrypt(data).decode()
    
    def decrypt(self, token):
        return self._fernet.decrypt(token.encode()).decode()
    
    def audit(self, action, user_id):
        return f"Audit: {action} by {user_id}"
    
    def teach_security(self, topic):
        return f"Security lesson on: {topic}"
    
    def generate_token(self, user_id, role):
        token_data = f"{user_id}:{role}:{hashlib.sha256(user_id.encode()).hexdigest()}"
        return self.encrypt(token_data)
    
    def validate_token(self, token):
        try:
            decrypted = self.decrypt(token)
            user_id, role, _ = decrypted.split(':')
            return self.enforce_rbac(role)
        except:
            raise PermissionError("Invalid or expired token")
