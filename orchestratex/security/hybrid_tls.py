from cryptography.hazmat.primitives.asymmetric import kyber, ec
from cryptography.hazmat.primitives import hashes, hmac, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from typing import Dict, Tuple, Optional
import os
import json
import logging

logger = logging.getLogger(__name__)

class HybridTLS:
    """Hybrid TLS implementation using Kyber + ECDH for quantum-safe key exchange."""
    
    def __init__(self):
        self.kyber_private_key = None
        self.kyber_public_key = None
        self.ecdh_private_key = None
        self.ecdh_public_key = None
        self.shared_secrets = {}
        self.session_keys = {}
        self.backend = default_backend()
        
    def generate_keys(self) -> Dict[str, bytes]:
        """Generate hybrid key pair."""
        try:
            # Generate Kyber key pair
            self.kyber_private_key = kyber.generate_private_key()
            self.kyber_public_key = self.kyber_private_key.public_key()
            
            # Generate ECDH key pair
            self.ecdh_private_key = ec.generate_private_key(ec.SECP384R1(), self.backend)
            self.ecdh_public_key = self.ecdh_private_key.public_key()
            
            # Prepare public keys for exchange
            public_keys = {
                "kyber": self.kyber_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ),
                "ecdh": self.ecdh_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            }
            
            return public_keys
            
        except Exception as e:
            logger.error(f"Key generation failed: {str(e)}")
            raise

    def exchange_keys(self, peer_public_keys: Dict[str, bytes]) -> Tuple[bytes, bytes]:
        """Perform key exchange with peer."""
        try:
            # Extract peer public keys
            peer_kyber_pub = serialization.load_pem_public_key(
                peer_public_keys["kyber"],
                backend=self.backend
            )
            peer_ecdh_pub = serialization.load_pem_public_key(
                peer_public_keys["ecdh"],
                backend=self.backend
            )
            
            # Key encapsulation using Kyber
            ciphertext, shared_secret_kyber = peer_kyber_pub.encrypt(
                b"",  # Empty message for key exchange
                kyber.KEMMode.DIRECT
            )
            
            # ECDH shared secret
            shared_secret_ecdh = self.ecdh_private_key.exchange(
                ec.ECDH(),
                peer_ecdh_pub
            )
            
            # Combine secrets using HKDF
            combined_secret = self._combine_secrets(
                shared_secret_kyber,
                shared_secret_ecdh
            )
            
            return ciphertext, combined_secret
            
        except Exception as e:
            logger.error(f"Key exchange failed: {str(e)}")
            raise

    def _combine_secrets(self, secret_kyber: bytes, secret_ecdh: bytes) -> bytes:
        """Combine secrets using HKDF."""
        try:
            # Concatenate secrets
            combined_secret = secret_kyber + secret_ecdh
            
            # Use HKDF to derive final shared secret
            derived_key = HKDF(
                algorithm=hashes.SHA384(),
                length=32,  # 256-bit key
                salt=None,
                info=b"Orchestratex_Hybrid_TLS",
                backend=self.backend
            ).derive(combined_secret)
            
            return derived_key
            
        except Exception as e:
            logger.error(f"Secret combination failed: {str(e)}")
            raise

    def encrypt(self, plaintext: bytes, shared_secret: bytes) -> bytes:
        """Encrypt data using hybrid encryption."""
        try:
            # Generate IV
            iv = os.urandom(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(shared_secret),
                modes.CBC(iv),
                backend=self.backend
            )
            
            # Encrypt with padding
            encryptor = cipher.encryptor()
            padder = PKCS7(128).padder()
            padded_data = padder.update(plaintext) + padder.finalize()
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Create authentication tag
            h = hmac.HMAC(shared_secret, hashes.SHA384(), backend=self.backend)
            h.update(ciphertext)
            tag = h.finalize()
            
            # Return encrypted data with IV and tag
            return iv + tag + ciphertext
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt(self, data: bytes, shared_secret: bytes) -> bytes:
        """Decrypt data using hybrid encryption."""
        try:
            # Extract IV, tag, and ciphertext
            iv = data[:16]
            tag = data[16:52]  # SHA-384 tag is 48 bytes
            ciphertext = data[52:]
            
            # Verify authentication tag
            h = hmac.HMAC(shared_secret, hashes.SHA384(), backend=self.backend)
            h.update(ciphertext)
            h.verify(tag)
            
            # Decrypt with padding removal
            cipher = Cipher(
                algorithms.AES(shared_secret),
                modes.CBC(iv),
                backend=self.backend
            )
            
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise

    def generate_session_key(self, shared_secret: bytes) -> bytes:
        """Generate session key from shared secret."""
        try:
            # Derive session key using HKDF
            session_key = HKDF(
                algorithm=hashes.SHA384(),
                length=32,  # 256-bit key
                salt=None,
                info=b"Orchestratex_Session_Key",
                backend=self.backend
            ).derive(shared_secret)
            
            return session_key
            
        except Exception as e:
            logger.error(f"Session key generation failed: {str(e)}")
            raise

# Example usage
def demo_hybrid_tls():
    """Demonstrate hybrid TLS handshake and encryption."""
    try:
        # Initialize two parties
        alice = HybridTLS()
        bob = HybridTLS()
        
        # Generate keys
        alice_keys = alice.generate_keys()
        bob_keys = bob.generate_keys()
        
        # Exchange keys
        alice_ciphertext, alice_shared = alice.exchange_keys(bob_keys)
        bob_ciphertext, bob_shared = bob.exchange_keys(alice_keys)
        
        # Verify shared secrets match
        assert alice_shared == bob_shared
        
        # Generate session keys
        alice_session = alice.generate_session_key(alice_shared)
        bob_session = bob.generate_session_key(bob_shared)
        
        # Verify session keys match
        assert alice_session == bob_session
        
        # Test encryption/decryption
        message = b"Hello, this is a secure message!"
        
        # Alice encrypts
        encrypted = alice.encrypt(message, alice_session)
        
        # Bob decrypts
        decrypted = bob.decrypt(encrypted, bob_session)
        
        assert decrypted == message
        
        print("Hybrid TLS handshake and encryption successful!")
        
    except Exception as e:
        logger.error(f"Hybrid TLS demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    demo_hybrid_tls()
