import logging
from cryptography.hazmat.primitives.asymmetric import dilithium, kyber, x25519, x448
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from typing import Dict, Any, Optional
import base64
import json

logger = logging.getLogger(__name__)

class PostQuantumCrypto:
    def __init__(self):
        """Initialize post-quantum cryptography system."""
        self.kyber = kyber.Kyber512()
        self.dilithium = dilithium.Dilithium2()
        
    def generate_key_pair(self) -> Dict[str, Any]:
        """Generate post-quantum key pair.
        
        Returns:
            Dict containing public and private keys
        """
        try:
            # Generate Kyber key pair
            kyber_private = self.kyber.generate_private_key()
            kyber_public = kyber_private.public_key()
            
            # Generate Dilithium key pair
            dilithium_private = self.dilithium.generate_private_key()
            dilithium_public = dilithium_private.public_key()
            
            return {
                'kyber_private': kyber_private,
                'kyber_public': kyber_public,
                'dilithium_private': dilithium_private,
                'dilithium_public': dilithium_public
            }
            
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise
            
    def hybrid_encrypt(self, plaintext: bytes, public_key: Any) -> bytes:
        """Encrypt data using hybrid encryption.
        
        Args:
            plaintext: Data to encrypt
            public_key: Public key for encryption
            
        Returns:
            Encrypted data
        """
        try:
            # Generate ephemeral key pair
            ephemeral_private = x25519.X25519PrivateKey.generate()
            ephemeral_public = ephemeral_private.public_key()
            
            # Perform key exchange
            shared_key = ephemeral_private.exchange(public_key)
            
            # Derive encryption key
            kdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'orchestratex-encryption'
            )
            encryption_key = kdf.derive(shared_key)
            
            # Encrypt data
            iv = os.urandom(12)
            cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # Return encrypted data with IV and ephemeral public key
            return {
                'ciphertext': base64.b64encode(ciphertext).decode(),
                'iv': base64.b64encode(iv).decode(),
                'ephemeral_public': base64.b64encode(ephemeral_public.public_bytes()).decode()
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
            
    def hybrid_decrypt(self, encrypted_data: Dict[str, str], private_key: Any) -> bytes:
        """Decrypt data using hybrid encryption.
        
        Args:
            encrypted_data: Encrypted data dictionary
            private_key: Private key for decryption
            
        Returns:
            Decrypted data
        """
        try:
            # Extract components
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            iv = base64.b64decode(encrypted_data['iv'])
            ephemeral_public = base64.b64decode(encrypted_data['ephemeral_public'])
            
            # Perform key exchange
            shared_key = private_key.exchange(x25519.X25519PublicKey.from_public_bytes(ephemeral_public))
            
            # Derive encryption key
            kdf = HKDF(
                algorithm=hashes.SHA256(),
                length=32,
                salt=None,
                info=b'orchestratex-encryption'
            )
            encryption_key = kdf.derive(shared_key)
            
            # Decrypt data
            cipher = Cipher(algorithms.AES(encryption_key), modes.GCM(iv))
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
            
    def sign_message(self, message: bytes, private_key: Any) -> bytes:
        """Sign a message using Dilithium.
        
        Args:
            message: Message to sign
            private_key: Private key for signing
            
        Returns:
            Signature
        """
        try:
            signature = private_key.sign(message)
            return signature
            
        except Exception as e:
            logger.error(f"Signing failed: {str(e)}")
            raise
            
    def verify_signature(self, message: bytes, signature: bytes, public_key: Any) -> bool:
        """Verify a message signature.
        
        Args:
            message: Message to verify
            signature: Signature to verify
            public_key: Public key for verification
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            public_key.verify(signature, message)
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {str(e)}")
            return False
