from typing import Dict, Any, Optional
import logging
from .agent_base import AgentBase
from orchestratex.quantum.crypto import QuantumCrypto
from orchestratex.quantum.entanglement import QuantumEntanglement

logger = logging.getLogger(__name__)

class QuantumCryptoAgent(AgentBase):
    """Quantum-enhanced cryptography agent."""
    
    def __init__(self, name: str, role: str, use_cloud: bool = False):
        """
        Initialize QuantumCryptoAgent.
        
        Args:
            name: Agent name
            role: Agent role
            use_cloud: Whether to use cloud quantum resources
        """
        super().__init__(name, role, use_cloud)
        self.quantum_crypto = QuantumCrypto()
        self.entanglement = QuantumEntanglement(use_cloud=use_cloud)
        
    def perform(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform quantum cryptography tasks.
        
        Args:
            task: Task to perform
            context: Additional context
            
        Returns:
            Dictionary containing task results
        """
        try:
            self.metrics["tasks_executed"] += 1
            
            if task == "encrypt":
                return self.kyber_encrypt(context)
            elif task == "sign":
                return self.dilithium_sign(context)
            elif task == "key_exchange":
                return self.quantum_key_exchange(context)
            elif task == "verify":
                return self.verify_signature(context)
            
            return {"error": f"Unknown task: {task}", "success": False}
            
        except Exception as e:
            logger.error(f"Crypto task failed: {str(e)}")
            raise
            
    def kyber_encrypt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform quantum-safe encryption.
        
        Args:
            context: Encryption context
            
        Returns:
            Encrypted data
        """
        try:
            # Create entanglement for encryption
            entangled = self._create_entanglement(pattern="ghz")
            
            # Perform encryption
            encrypted = self.quantum_crypto.hybrid_encrypt(
                context["data"].encode()
            )
            
            return {
                "encrypted": encrypted,
                "entanglement": entangled,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
            
    def dilithium_sign(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create quantum-safe signature.
        
        Args:
            context: Signing context
            
        Returns:
            Signature
        """
        try:
            # Create entanglement for signature
            entangled = self._create_entanglement(pattern="ring")
            
            # Create signature
            signature = self.quantum_crypto.quantum_safe_sign(
                context["message"].encode()
            )
            
            return {
                "signature": signature,
                "entanglement": entangled,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Signature creation failed: {str(e)}")
            raise
            
    def quantum_key_exchange(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform quantum-safe key exchange.
        
        Args:
            context: Key exchange context
            
        Returns:
            Shared secret
        """
        try:
            # Create entangled state for key exchange
            entangled = self._create_entanglement(pattern="star")
            
            # Perform key exchange
            shared_secret = self.quantum_crypto.key_exchange(
                context["other_public"]
            )
            
            return {
                "shared_secret": shared_secret,
                "entanglement": entangled,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Key exchange failed: {str(e)}")
            raise
            
    def verify_signature(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify quantum-safe signature.
        
        Args:
            context: Verification context
            
        Returns:
            Verification result
        """
        try:
            # Verify entanglement first
            entangled = context["entanglement"]
            verification = self._verify_entanglement(entangled)
            
            if not verification["success"]:
                return {"error": "Entanglement verification failed", "success": False}
            
            # Verify signature
            valid = self.quantum_crypto.verify_signature(
                context["message"].encode(),
                context["signature"]
            )
            
            return {
                "valid": valid,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            raise
            
    def _verify_entanglement(self, entangled: Any) -> Dict[str, Any]:
        """
        Verify quantum entanglement.
        
        Args:
            entangled: Entangled state to verify
            
        Returns:
            Verification result
        """
        try:
            # Verify entanglement quality
            result = self.entanglement.verify_entanglement(entangled)
            
            # Check error rate
            if result["error_rate"] > 0.1:
                return {"error": "High error rate detected", "success": False}
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Entanglement verification failed: {str(e)}")
            raise
