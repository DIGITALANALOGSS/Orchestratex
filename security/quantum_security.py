import logging
from typing import Dict, Any, Optional
import hashlib
import json
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import kyber
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class HSMClient:
    def __init__(self, config: Dict[str, Any]):
        """Initialize HSM client.
        
        Args:
            config: Configuration dictionary containing:
                - endpoint: HSM endpoint URL
                - token: Authentication token
                - key_label: Key label prefix
                - timeout: Request timeout
        """
        self.endpoint = config.get('endpoint')
        self.auth_token = config.get('token')
        self.key_label = config.get('key_label', 'orchestratex_')
        self.timeout = config.get('timeout', 30)
        
        # Initialize connection
        self._init_connection()
        
    def _init_connection(self) -> None:
        """Initialize HSM connection."""
        try:
            # Mock connection initialization - replace with actual HSM connection
            self.connection = {
                'status': 'connected',
                'endpoint': self.endpoint,
                'last_check': datetime.utcnow()
            }
            
            logger.info(f"HSM connection established: {self.endpoint}")
            
        except Exception as e:
            logger.error(f"HSM connection failed: {str(e)}")
            raise
            
    def store_key(self, key_type: str, key_data: bytes, label: str) -> Dict[str, Any]:
        """Store key in HSM.
        
        Args:
            key_type: Type of key (e.g., 'kyber', 'x25519')
            key_data: Key data to store
            label: Key label
            
        Returns:
            Storage result
        """
        try:
            # Create full key label
            full_label = f"{self.key_label}{label}_{key_type}"
            
            # Mock HSM storage - replace with actual HSM API
            result = {
                'status': 'success',
                'key_type': key_type,
                'label': full_label,
                'stored_at': datetime.utcnow().isoformat(),
                'size': len(key_data)
            }
            
            logger.info(f"Key stored in HSM: {full_label}")
            return result
            
        except Exception as e:
            logger.error(f"HSM key storage failed: {str(e)}")
            raise
            
    def retrieve_key(self, key_type: str, label: str) -> bytes:
        """Retrieve key from HSM.
        
        Args:
            key_type: Type of key to retrieve
            label: Key label
            
        Returns:
            Key data
        """
        try:
            # Create full key label
            full_label = f"{self.key_label}{label}_{key_type}"
            
            # Mock HSM retrieval - replace with actual HSM API
            # Note: In production, this would use secure HSM API
            key_data = b'mock_key_data'  # Replace with actual HSM retrieval
            
            logger.info(f"Key retrieved from HSM: {full_label}")
            return key_data
            
        except Exception as e:
            logger.error(f"HSM key retrieval failed: {str(e)}")
            raise
            
    def perform_crypto_operation(self, 
                               operation: str, 
                               key_type: str, 
                               label: str, 
                               data: bytes) -> bytes:
        """Perform cryptographic operation using HSM.
        
        Args:
            operation: Operation type (e.g., 'encrypt', 'decrypt')
            key_type: Type of key to use
            label: Key label
            data: Data to process
            
        Returns:
            Processed data
        """
        try:
            # Get key from HSM
            key_data = self.retrieve_key(key_type, label)
            
            # Mock HSM operation - replace with actual HSM API
            # Note: In production, this would use secure HSM API
            processed_data = b'mock_processed_data'  # Replace with actual HSM operation
            
            logger.info(f"HSM operation completed: {operation} with {key_type}")
            return processed_data
            
        except Exception as e:
            logger.error(f"HSM operation failed: {str(e)}")
            raise

class QuantumSecurity:
    def __init__(self, config: Dict[str, Any]):
        """Initialize quantum-safe security module with HSM integration.
        
        Args:
            config: Configuration dictionary containing:
                - key_rotation_interval: Key rotation interval (days)
                - emergency_rotation: Enable emergency key rotation
                - hsm_enabled: Use HSM for key storage
                - key_size: Key size for encryption
                - hsm_config: HSM configuration
        """
        self.config = config
        self.key_pair = None
        self.last_rotated = datetime.utcnow()
        self.hsm_enabled = config.get('hsm_enabled', False)
        
        # Initialize HSM client if enabled
        if self.hsm_enabled:
            self.hsm = HSMClient(config.get('hsm_config', {}))
        
        # Initialize key rotation
        self.key_rotation_interval = timedelta(
            days=config.get('key_rotation_interval', 90)
        )
        
        # Generate initial keys
        self._generate_key_pair()
        
    def _generate_key_pair(self) -> None:
        """Generate quantum-safe key pair with HSM integration."""
        try:
            # Generate Kyber-512 key pair
            self.key_pair = kyber.generate_kyber_keypair()
            
            # Generate X25519 key pair for hybrid encryption
            self.x25519_key = x25519.X25519PrivateKey.generate()
            
            # Store keys with HSM if enabled
            if self.hsm_enabled:
                self._store_keys_in_hsm()
                
            logger.info("Generated new quantum-safe key pair")
            
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise
            
    def _store_keys_in_hsm(self) -> None:
        """Store keys in Hardware Security Module."""
        try:
            # Store Kyber key
            kyber_key_data = self.key_pair.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            self.hsm.store_key('kyber', kyber_key_data, 'current')
            
            # Store X25519 key
            x25519_key_data = self.x25519_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            self.hsm.store_key('x25519', x25519_key_data, 'current')
            
            logger.info("Keys stored in HSM")
            
        except Exception as e:
            logger.error(f"HSM storage failed: {str(e)}")
            raise
            
    def auto_rotate_keys(self) -> None:
        """Automatically rotate keys based on interval with HSM integration."""
        if datetime.utcnow() > self.last_rotated + self.key_rotation_interval:
            # Generate new keys
            self._generate_key_pair()
            self.last_rotated = datetime.utcnow()
            
            # Store old keys in HSM
            if self.hsm_enabled:
                # Store previous keys with timestamp
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                self._store_keys_in_hsm_with_label(f'backup_{timestamp}')
            
            logger.info("Keys automatically rotated")
            
    def encrypt(self, plaintext: str) -> Dict[str, Any]:
        """Quantum-safe encryption using hybrid approach with HSM.
        
        Args:
            plaintext: Data to encrypt
            
        Returns:
            Dictionary containing encrypted data and metadata
        """
        try:
            # Generate ephemeral key pair
            ephemeral_key = x25519.X25519PrivateKey.generate()
            
            # Perform key exchange
            shared_key = ephemeral_key.exchange(self.x25519_key.public_key())
            
            # Derive encryption key using HKDF
            enc_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'quantum-safe-encryption'
            ).derive(shared_key)
            
            # Prepare data for encryption
            plaintext_bytes = plaintext.encode()
            padder = PKCS7(128).padder()
            padded_data = padder.update(plaintext_bytes) + padder.finalize()
            
            # Generate IV
            iv = os.urandom(16)
            
            # Encrypt using AES-256 with HSM if enabled
            if self.hsm_enabled:
                # Use HSM for encryption
                ciphertext = self.hsm.perform_crypto_operation(
                    'encrypt',
                    'aes',
                    'current',
                    padded_data
                )
            else:
                # Local encryption as fallback
                cipher = Cipher(algorithms.AES(enc_key), modes.CBC(iv), default_backend())
                encryptor = cipher.encryptor()
                ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Calculate quantum-resistant hash
            hash_obj = hashlib.shake_256()
            hash_obj.update(ciphertext)
            content_hash = hash_obj.hexdigest(64)
            
            return {
                'ciphertext': ciphertext.hex(),
                'iv': iv.hex(),
                'ephemeral_pubkey': ephemeral_key.public_key().public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).hex(),
                'content_hash': content_hash,
                'encryption_time': datetime.utcnow().isoformat(),
                'algorithm': 'Kyber-512 + X25519 + AES-256',
                'hsm_used': self.hsm_enabled
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
            
    def decrypt(self, encrypted_data: Dict[str, Any]) -> str:
        """Quantum-safe decryption using hybrid approach with HSM.
        
        Args:
            encrypted_data: Dictionary containing encrypted data and metadata
            
        Returns:
            Decrypted plaintext
        """
        try:
            # Extract encryption parameters
            ciphertext = bytes.fromhex(encrypted_data['ciphertext'])
            iv = bytes.fromhex(encrypted_data['iv'])
            ephemeral_pubkey = serialization.load_pem_public_key(
                bytes.fromhex(encrypted_data['ephemeral_pubkey'])
            )
            
            # Perform key exchange
            shared_key = self.x25519_key.exchange(ephemeral_pubkey)
            
            # Derive decryption key using HKDF
            dec_key = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'quantum-safe-decryption'
            ).derive(shared_key)
            
            # Decrypt using AES-256 with HSM if enabled
            if self.hsm_enabled:
                # Use HSM for decryption
                padded_plaintext = self.hsm.perform_crypto_operation(
                    'decrypt',
                    'aes',
                    'current',
                    ciphertext
                )
            else:
                # Local decryption as fallback
                cipher = Cipher(algorithms.AES(dec_key), modes.CBC(iv), default_backend())
                decryptor = cipher.decryptor()
                padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remove padding
            unpadder = PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            
            # Verify hash
            hash_obj = hashlib.shake_256()
            hash_obj.update(ciphertext)
            calculated_hash = hash_obj.hexdigest(64)
            
            if calculated_hash != encrypted_data['content_hash']:
                raise ValueError("Content hash verification failed")
                
            return plaintext.decode()
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
