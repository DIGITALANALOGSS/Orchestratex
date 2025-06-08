import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, kyber
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)

class ProductionHSMManager:
    def __init__(self, config: Dict[str, Any]):
        """Initialize production HSM manager.
        
        Args:
            config: HSM configuration dictionary
        """
        self.config = config
        self.base_url = f"https://{config['network_config']['ip']}:{config['network_config']['port']}"
        self.auth_token = None
        self.last_auth_time = None
        self.key_cache = {}
        self._initialize_connection()
        
    def _initialize_connection(self) -> None:
        """Initialize connection to HSM."""
        try:
            # Authenticate with HSM
            self._authenticate()
            logger.info("HSM connection initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize HSM connection: {str(e)}")
            raise
            
    def _authenticate(self) -> None:
        """Authenticate with HSM."""
        try:
            auth_data = {
                "username": self.config['auth_config']['admin_user'],
                "password": self.config['auth_config']['unlock_passphrase']
            }
            
            response = requests.post(
                f"{self.base_url}/auth",
                json=auth_data,
                verify=self.config['network_config']['tls_cert'],
                timeout=5
            )
            
            if response.status_code == 200:
                self.auth_token = response.json().get('token')
                self.last_auth_time = datetime.utcnow()
                logger.info("HSM authentication successful")
            else:
                raise Exception(f"Authentication failed: {response.text}")
                
        except Exception as e:
            logger.error(f"HSM authentication failed: {str(e)}")
            raise
            
    def _check_auth(self) -> None:
        """Check if authentication is still valid."""
        if not self.auth_token or \
           (datetime.utcnow() - self.last_auth_time) > timedelta(hours=1):
            self._authenticate()
            
    def generate_key(self, 
                    key_type: str, 
                    key_size: Optional[int] = None, 
                    key_label: Optional[str] = None) -> Dict[str, Any]:
        """Generate new key in HSM.
        
        Args:
            key_type: Type of key (kyber, rsa)
            key_size: Size of key (optional)
            key_label: Label for key (optional)
            
        Returns:
            Key metadata
        """
        try:
            self._check_auth()
            
            key_data = {
                "type": key_type,
                "size": key_size,
                "label": key_label or f"{key_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/keys",
                json=key_data,
                headers=headers,
                verify=self.config['network_config']['tls_cert'],
                timeout=5
            )
            
            if response.status_code == 200:
                key_info = response.json()
                self.key_cache[key_info['id']] = key_info
                return key_info
            else:
                raise Exception(f"Key generation failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to generate key: {str(e)}")
            raise
            
    def encrypt(self, 
               data: bytes, 
               key_id: str, 
               key_type: str) -> bytes:
        """Encrypt data using HSM.
        
        Args:
            data: Data to encrypt
            key_id: ID of key to use
            key_type: Type of key
            
        Returns:
            Encrypted data
        """
        try:
            self._check_auth()
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/keys/{key_id}/encrypt",
                json={
                    "data": data.hex(),
                    "type": key_type
                },
                headers=headers,
                verify=self.config['network_config']['tls_cert'],
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return bytes.fromhex(result['encrypted_data'])
            else:
                raise Exception(f"Encryption failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
            
    def decrypt(self, 
               data: bytes, 
               key_id: str, 
               key_type: str) -> bytes:
        """Decrypt data using HSM.
        
        Args:
            data: Data to decrypt
            key_id: ID of key to use
            key_type: Type of key
            
        Returns:
            Decrypted data
        """
        try:
            self._check_auth()
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/keys/{key_id}/decrypt",
                json={
                    "data": data.hex(),
                    "type": key_type
                },
                headers=headers,
                verify=self.config['network_config']['tls_cert'],
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                return bytes.fromhex(result['decrypted_data'])
            else:
                raise Exception(f"Decryption failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
            
    def rotate_keys(self, key_type: str) -> None:
        """Rotate keys of specified type.
        
        Args:
            key_type: Type of keys to rotate
        """
        try:
            self._check_auth()
            
            # Get all keys of specified type
            keys = self._get_keys_by_type(key_type)
            
            for key_info in keys:
                # Generate new key
                new_key = self.generate_key(
                    key_type=key_type,
                    key_size=key_info['size'],
                    key_label=f"{key_type}_rotated_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                )
                
                # Update references to old key
                self._update_key_references(key_info['id'], new_key['id'])
                
                # Archive old key
                self._archive_key(key_info['id'])
                
            logger.info(f"Successfully rotated {len(keys)} {key_type} keys")
            
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise
            
    def _get_keys_by_type(self, key_type: str) -> List[Dict[str, Any]]:
        """Get all keys of specified type.
        
        Args:
            key_type: Type of keys to get
            
        Returns:
            List of key metadata
        """
        try:
            self._check_auth()
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/keys?type={key_type}",
                headers=headers,
                verify=self.config['network_config']['tls_cert'],
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get keys: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to get keys: {str(e)}")
            raise
            
    def _update_key_references(self, old_key_id: str, new_key_id: str) -> None:
        """Update references to old key with new key.
        
        Args:
            old_key_id: ID of old key
            new_key_id: ID of new key
        """
        try:
            self._check_auth()
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/keys/update_references",
                json={
                    "old_key_id": old_key_id,
                    "new_key_id": new_key_id
                },
                headers=headers,
                verify=self.config['network_config']['tls_cert'],
                timeout=5
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to update references: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to update key references: {str(e)}")
            raise
            
    def _archive_key(self, key_id: str) -> None:
        """Archive a key.
        
        Args:
            key_id: ID of key to archive
        """
        try:
            self._check_auth()
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/keys/{key_id}/archive",
                headers=headers,
                verify=self.config['network_config']['tls_cert'],
                timeout=5
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to archive key: {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to archive key: {str(e)}")
            raise
