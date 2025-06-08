from cryptography.hazmat.primitives.asymmetric import kyber
from cryptography.hazmat.primitives.asymmetric import dilithium
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import os

class QuantumSafeEncryption:
    def __init__(self):
        self.backend = default_backend()
        self.kyber_private_key = kyber.generate_private_key()
        self.dilithium_private_key = dilithium.generate_private_key()
        
    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt data using quantum-safe cryptography."""
        try:
            # Generate shared secret using Kyber
            peer_public_key = kyber.generate_private_key().public_key()
            shared_secret = self.kyber_private_key.exchange(kyber.ECDH(), peer_public_key)
            
            # Derive encryption key
            key = HKDF(
                algorithm=hashes.SHA3_512(),
                length=32,
                salt=None,
                info=b'quantum_encryption'
            ).derive(shared_secret)
            
            # Generate IV
            iv = os.urandom(16)
            
            # Encrypt using AES-GCM
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # Sign the ciphertext
            signature = self.dilithium_private_key.sign(ciphertext)
            
            # Return combined result
            return base64.b64encode(
                peer_public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ) +
                iv +
                ciphertext +
                signature
            )
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
            
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using quantum-safe cryptography."""
        try:
            # Decode base64
            data = base64.b64decode(encrypted_data)
            
            # Extract components
            peer_public_key_bytes = data[:448]  # Length of PEM-encoded public key
            peer_public_key = serialization.load_pem_public_key(
                peer_public_key_bytes,
                backend=self.backend
            )
            
            iv = data[448:464]
            ciphertext = data[464:-256]  # Length of Dilithium signature
            signature = data[-256:]
            
            # Verify signature
            self.dilithium_private_key.public_key().verify(
                signature,
                ciphertext
            )
            
            # Derive shared secret
            shared_secret = self.kyber_private_key.exchange(kyber.ECDH(), peer_public_key)
            
            # Derive key
            key = HKDF(
                algorithm=hashes.SHA3_512(),
                length=32,
                salt=None,
                info=b'quantum_encryption'
            ).derive(shared_secret)
            
            # Decrypt
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
            decryptor = cipher.decryptor()
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
