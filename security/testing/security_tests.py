import unittest
from cryptography.hazmat.primitives.asymmetric import kyber
from cryptography.hazmat.primitives.asymmetric import dilithium
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os
from security.implementation.encryption import QuantumSafeEncryption

class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.encryption = QuantumSafeEncryption()
        self.test_data = b"This is a test message"
        self.test_key = os.urandom(32)

    def test_quantum_safe_encryption(self):
        """Test quantum-safe encryption and decryption."""
        encrypted = self.encryption.encrypt(self.test_data)
        decrypted = self.encryption.decrypt(encrypted)
        self.assertEqual(decrypted, self.test_data)

    def test_key_exchange(self):
        """Test quantum-safe key exchange."""
        # Generate peer key pair
        peer_private_key = kyber.generate_private_key()
        peer_public_key = peer_private_key.public_key()
        
        # Perform key exchange
        shared_secret = self.encryption.kyber_private_key.exchange(
            kyber.ECDH(),
            peer_public_key
        )
        
        # Verify shared secret
        self.assertTrue(len(shared_secret) > 0)

    def test_signature_verification(self):
        """Test quantum-safe signature verification."""
        # Sign data
        signature = self.encryption.dilithium_private_key.sign(self.test_data)
        
        # Verify signature
        try:
            self.encryption.dilithium_private_key.public_key().verify(
                signature,
                self.test_data
            )
            self.assertTrue(True)
        except:
            self.fail("Signature verification failed")

    def test_encryption_performance(self):
        """Test encryption performance."""
        import time
        start_time = time.time()
        
        # Encrypt large data
        large_data = os.urandom(1024 * 1024)  # 1MB
        encrypted = self.encryption.encrypt(large_data)
        
        end_time = time.time()
        encryption_time = end_time - start_time
        
        # Verify performance is within acceptable range
        self.assertLess(encryption_time, 10.0)  # Should take less than 10 seconds

    def test_key_rotation(self):
        """Test key rotation."""
        # Generate new key pair
        old_private_key = self.encryption.kyber_private_key
        self.encryption.kyber_private_key = kyber.generate_private_key()
        
        # Verify old key is different from new key
        self.assertNotEqual(
            old_private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ),
            self.encryption.kyber_private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

if __name__ == '__main__':
    unittest.main()
