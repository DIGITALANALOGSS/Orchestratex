import logging
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, kyber
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MockHSM:
    def __init__(self, config):
        """Initialize mock HSM.
        
        Args:
            config: HSM configuration dictionary
        """
        self.config = config
        self.keys = {}
        self.key_metadata = {}
        self.audit_log = []
        self._initialize_keys()
        
    def _initialize_keys(self):
        """Initialize default keys for testing."""
        # Generate Kyber-512 key pair
        kyber_key = kyber.Kyber512PrivateKey.generate()
        self.keys['kyber'] = kyber_key
        self.key_metadata['kyber'] = {
            'type': 'kyber',
            'strength': 512,
            'created': datetime.utcnow(),
            'last_used': datetime.utcnow()
        }
        
        # Generate RSA key pair
        rsa_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096
        )
        self.keys['rsa'] = rsa_key
        self.key_metadata['rsa'] = {
            'type': 'rsa',
            'strength': 4096,
            'created': datetime.utcnow(),
            'last_used': datetime.utcnow()
        }
        
    def generate_key(self, key_type: str, key_size: int = None):
        """Generate new key pair.
        
        Args:
            key_type: Type of key (kyber, rsa)
            key_size: Size of key (optional)
            
        Returns:
            Tuple of (private_key, public_key)
        """
        try:
            if key_type == 'kyber':
                key = kyber.Kyber512PrivateKey.generate()
            elif key_type == 'rsa':
                key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size or 4096
                )
            else:
                raise ValueError(f"Unsupported key type: {key_type}")
                
            self.keys[key_type] = key
            self.key_metadata[key_type] = {
                'type': key_type,
                'strength': key_size or 512,
                'created': datetime.utcnow(),
                'last_used': datetime.utcnow()
            }
            
            self._log_audit(f"Generated new {key_type} key")
            return key, key.public_key()
            
        except Exception as e:
            logger.error(f"Failed to generate key: {str(e)}")
            raise
            
    def encrypt(self, data: bytes, public_key: bytes):
        """Encrypt data using HSM.
        
        Args:
            data: Data to encrypt
            public_key: Public key for encryption
            
        Returns:
            Encrypted data
        """
        try:
            # Load public key
            key = serialization.load_pem_public_key(public_key)
            
            # Encrypt using appropriate algorithm
            if isinstance(key, kyber.Kyber512PublicKey):
                encrypted = key.encrypt(data)
            else:
                encrypted = key.encrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
            self._log_audit(f"Encrypted data using {type(key).__name__}")
            return encrypted
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
            
    def decrypt(self, data: bytes, key_id: str):
        """Decrypt data using HSM.
        
        Args:
            data: Data to decrypt
            key_id: ID of key to use
            
        Returns:
            Decrypted data
        """
        try:
            key = self.keys[key_id]
            
            if isinstance(key, kyber.Kyber512PrivateKey):
                decrypted = key.decrypt(data)
            else:
                decrypted = key.decrypt(
                    data,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
            self._log_audit(f"Decrypted data using {type(key).__name__}")
            return decrypted
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
            
    def _log_audit(self, action: str):
        """Log audit entry.
        
        Args:
            action: Action performed
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'user': self.config.get('auth_config', {}).get('admin_user', 'unknown'),
            'instance': self.config.get('instance_id', 'unknown')
        }
        self.audit_log.append(entry)
        logger.info(f"AUDIT: {action}")
