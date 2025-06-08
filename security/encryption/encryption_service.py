import logging
import os
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EncryptionService:
    def __init__(self, key_size: int = 2048):
        """Initialize encryption service with RSA key pair."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
    def encrypt(self, data: str, key: bytes = None) -> str:
        """Encrypt data using RSA-OAEP padding."""
        if key is None:
            key = self.public_key
            
        # Convert data to bytes
        data_bytes = data.encode('utf-8')
        
        # Encrypt using RSA-OAEP
        encrypted = key.encrypt(
            data_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Return base64 encoded result
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data using RSA-OAEP padding."""
        try:
            # Decode base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt using RSA-OAEP
            decrypted = self.private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return decrypted.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    def sign(self, data: str) -> str:
        """Sign data using RSA-PSS."""
        # Convert data to bytes
        data_bytes = data.encode('utf-8')
        
        # Sign using RSA-PSS
        signature = self.private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Return base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')

    def verify(self, data: str, signature: str) -> bool:
        """Verify signature using RSA-PSS."""
        try:
            # Convert data and signature to bytes
            data_bytes = data.encode('utf-8')
            signature_bytes = base64.b64decode(signature)
            
            # Verify using RSA-PSS
            self.public_key.verify(
                signature_bytes,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except InvalidSignature:
            return False
            
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False

    def generate_key_pair(self) -> tuple:
        """Generate new RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        return (private_key, public_key)

    def export_keys(self, private_key_path: str, public_key_path: str, password: str = None):
        """Export key pair to files."""
        # Export private key
        encryption = None
        if password:
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode())
            encryption = serialization.BestAvailableEncryption(key)
        
        private_bytes = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        
        with open(private_key_path, 'wb') as f:
            f.write(private_bytes)
            
        # Export public key
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(public_key_path, 'wb') as f:
            f.write(public_bytes)

    def import_keys(self, private_key_path: str, public_key_path: str, password: str = None):
        """Import key pair from files."""
        # Import private key
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=password.encode() if password else None,
                backend=default_backend()
            )
            
        # Import public key
        with open(public_key_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )

    def encrypt_config(self, config: dict, key: bytes = None) -> dict:
        """Encrypt configuration dictionary."""
        encrypted_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                encrypted_config[key] = self.encrypt_config(value)
            elif isinstance(value, str):
                encrypted_config[key] = self.encrypt(value, key)
            else:
                encrypted_config[key] = value
        return encrypted_config

    def decrypt_config(self, encrypted_config: dict) -> dict:
        """Decrypt configuration dictionary."""
        config = {}
        for key, value in encrypted_config.items():
            if isinstance(value, dict):
                config[key] = self.decrypt_config(value)
            elif isinstance(value, str):
                config[key] = self.decrypt(value)
            else:
                config[key] = value
        return config

if __name__ == "__main__":
    # Example usage
    encryption = EncryptionService()
    private_key_path = 'private_key.pem'
    public_key_path = 'public_key.pem'
    
    # Generate and export keys
    encryption.export_keys(private_key_path, public_key_path, 'your-password')
    
    # Encrypt and decrypt data
    data = "sensitive information"
    encrypted = encryption.encrypt(data)
    decrypted = encryption.decrypt(encrypted)
    
    # Sign and verify data
    signature = encryption.sign(data)
    verified = encryption.verify(data, signature)
    
    print(f"Original: {data}")
    print(f"Encrypted: {encrypted}")
    print(f"Decrypted: {decrypted}")
    print(f"Signature verified: {verified}")
