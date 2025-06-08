import logging
from typing import Dict, Any
import json
import os
from datetime import datetime
import hashlib
import boto3
from google.cloud import storage

class AuditLogger:
    def __init__(self, config: Dict[str, Any]):
        """Initialize audit logger.
        
        Args:
            config: Configuration dictionary containing:
                - storage_type: Type of storage (local, aws, gcp)
                - storage_config: Storage-specific configuration
                - retention_policy: Audit log retention policy
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize storage
        self.storage_type = config.get('storage_type', 'local')
        self._init_storage()
        
        # Initialize retention policy
        self.retention_policy = config.get('retention_policy', {
            'max_days': 365,
            'cleanup_interval': 'daily'
        })
        
    def _init_storage(self):
        """Initialize storage backend."""
        storage_config = self.config.get('storage_config', {})
        
        if self.storage_type == 'aws':
            self.storage = boto3.client(
                's3',
                aws_access_key_id=storage_config.get('aws_access_key_id'),
                aws_secret_access_key=storage_config.get('aws_secret_access_key'),
                region_name=storage_config.get('aws_region', 'us-east-1')
            )
            self.bucket = storage_config.get('bucket_name')
            
        elif self.storage_type == 'gcp':
            self.storage = storage.Client(
                project=storage_config.get('gcp_project_id')
            )
            self.bucket = storage_config.get('bucket_name')
            
        else:  # local
            self.storage_dir = storage_config.get('local_dir', 'audit_logs')
            os.makedirs(self.storage_dir, exist_ok=True)
            
    def log(self, audit_data: Dict[str, Any]) -> None:
        """Log audit entry.
        
        Args:
            audit_data: Audit data to log
        """
        try:
            # Generate log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'data': audit_data,
                'log_id': hashlib.sha256(
                    json.dumps(audit_data, sort_keys=True).encode()
                ).hexdigest()
            }
            
            # Store log
            self._store_log(log_entry)
            
            # Clean up old logs if needed
            self._cleanup_old_logs()
            
        except Exception as e:
            self.logger.error(f"Audit logging failed: {str(e)}")
            
    def _store_log(self, log_entry: Dict[str, Any]) -> None:
        """Store log entry in configured storage.
        
        Args:
            log_entry: Log entry to store
        """
        if self.storage_type == 'aws':
            self._store_to_aws(log_entry)
        elif self.storage_type == 'gcp':
            self._store_to_gcp(log_entry)
        else:  # local
            self._store_to_local(log_entry)
            
    def _store_to_aws(self, log_entry: Dict[str, Any]) -> None:
        """Store log entry to AWS S3.
        
        Args:
            log_entry: Log entry to store
        """
        try:
            key = f"audit_logs/{log_entry['timestamp']}/{log_entry['log_id']}.json"
            self.storage.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(log_entry).encode(),
                ContentType='application/json'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store log to AWS: {str(e)}")
            
    def _store_to_gcp(self, log_entry: Dict[str, Any]) -> None:
        """Store log entry to GCP Cloud Storage.
        
        Args:
            log_entry: Log entry to store
        """
        try:
            bucket = self.storage.bucket(self.bucket)
            blob = bucket.blob(f"audit_logs/{log_entry['timestamp']}/{log_entry['log_id']}.json")
            blob.upload_from_string(
                json.dumps(log_entry),
                content_type='application/json'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store log to GCP: {str(e)}")
            
    def _store_to_local(self, log_entry: Dict[str, Any]) -> None:
        """Store log entry to local storage.
        
        Args:
            log_entry: Log entry to store
        """
        try:
            date_dir = os.path.join(self.storage_dir, log_entry['timestamp'][:10])
            os.makedirs(date_dir, exist_ok=True)
            
            with open(os.path.join(date_dir, f"{log_entry['log_id']}.json"), 'w') as f:
                json.dump(log_entry, f)
            
        except Exception as e:
            self.logger.error(f"Failed to store log locally: {str(e)}")
            
    def _cleanup_old_logs(self) -> None:
        """Clean up old audit logs based on retention policy."""
        try:
            if self.storage_type == 'aws':
                self._cleanup_aws_logs()
            elif self.storage_type == 'gcp':
                self._cleanup_gcp_logs()
            else:  # local
                self._cleanup_local_logs()
                
        except Exception as e:
            self.logger.error(f"Failed to clean up old logs: {str(e)}")
            
    def _cleanup_aws_logs(self) -> None:
        """Clean up old logs in AWS S3."""
        try:
            # Get list of objects
            response = self.storage.list_objects_v2(
                Bucket=self.bucket,
                Prefix='audit_logs/'
            )
            
            # Delete old objects
            for obj in response.get('Contents', []):
                if self._is_old_log(obj['LastModified']):
                    self.storage.delete_object(
                        Bucket=self.bucket,
                        Key=obj['Key']
                    )
            
        except Exception as e:
            self.logger.error(f"Failed to clean up AWS logs: {str(e)}")
            
    def _cleanup_gcp_logs(self) -> None:
        """Clean up old logs in GCP Cloud Storage."""
        try:
            bucket = self.storage.bucket(self.bucket)
            blobs = bucket.list_blobs(prefix='audit_logs/')
            
            for blob in blobs:
                if self._is_old_log(blob.updated):
                    blob.delete()
            
        except Exception as e:
            self.logger.error(f"Failed to clean up GCP logs: {str(e)}")
            
    def _cleanup_local_logs(self) -> None:
        """Clean up old logs in local storage."""
        try:
            for root, dirs, files in os.walk(self.storage_dir):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if self._is_old_log(mtime):
                            os.remove(file_path)
            
        except Exception as e:
            self.logger.error(f"Failed to clean up local logs: {str(e)}")
            
    def _is_old_log(self, timestamp: datetime) -> bool:
        """Check if log is older than retention period.
        
        Args:
            timestamp: Log timestamp
            
        Returns:
            True if log is old
        """
        max_days = self.retention_policy.get('max_days', 365)
        return (datetime.utcnow() - timestamp).days > max_days
