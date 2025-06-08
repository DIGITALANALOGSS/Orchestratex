from google.cloud import storage
from typing import Dict, Any, Optional
from ..management.config import ContentManager
import logging

class GCPStorage:
    def __init__(self, config: Dict[str, Any]):
        """Initialize GCP Cloud Storage.
        
        Args:
            config: Storage configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.bucket = config.get("storage", {}).get("bucket")
        
        if not self.bucket:
            raise ValueError("GCP bucket name is required in configuration")
            
        self.client = storage.Client(
            project=config.get("gcp_project_id")
        )
        self.bucket_obj = self.client.bucket(self.bucket)
        
    def upload(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Upload content to GCP Storage.
        
        Args:
            content: Content data
            metadata: Content metadata
            
        Returns:
            Content ID (GCP object name)
        """
        try:
            content_id = f"content/{metadata.get('type', 'unknown')}/{metadata.get('id', 'unknown')}"
            
            # Convert content to appropriate format
            content_data = self._prepare_content(content)
            
            # Create blob and upload
            blob = self.bucket_obj.blob(content_id)
            blob.metadata = {
                'content_type': metadata.get('type', ''),
                'created_at': str(metadata.get('created_at', '')),
                'version': metadata.get('version', '1')
            }
            blob.upload_from_string(
                content_data,
                content_type=metadata.get('content_type', 'application/octet-stream')
            )
            
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to upload to GCP: {str(e)}")
            raise
            
    def get(self, content_id: str) -> Dict[str, Any]:
        """Get content from GCP Storage.
        
        Args:
            content_id: Content ID (GCP object name)
            
        Returns:
            Content data
        """
        try:
            blob = self.bucket_obj.blob(content_id)
            if not blob.exists():
                raise FileNotFoundError(f"Content not found: {content_id}")
                
            content_data = blob.download_as_bytes()
            metadata = blob.metadata or {}
            
            return {
                'content': content_data,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get content {content_id}: {str(e)}")
            raise
            
    def delete(self, content_id: str) -> bool:
        """Delete content from GCP Storage.
        
        Args:
            content_id: Content ID (GCP object name)
            
        Returns:
            True if deletion was successful
        """
        try:
            blob = self.bucket_obj.blob(content_id)
            if blob.exists():
                blob.delete()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete content {content_id}: {str(e)}")
            raise
            
    def list(self, filters: Dict[str, Any] = None) -> list:
        """List content in GCP Storage.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of content items
        """
        try:
            prefix = f"content/{filters.get('type', '')}" if filters else "content/"
            blobs = self.bucket_obj.list_blobs(prefix=prefix)
            
            return [{
                'id': blob.name,
                'size': blob.size,
                'last_modified': blob.updated
            } for blob in blobs]
            
        except Exception as e:
            self.logger.error(f"Failed to list content: {str(e)}")
            raise
            
    def _prepare_content(self, content: Dict[str, Any]) -> bytes:
        """Prepare content for storage.
        
        Args:
            content: Content data
            
        Returns:
            Content as bytes
        """
        content_type = content.get('type')
        if content_type == 'text':
            return content['text'].encode('utf-8')
        elif content_type in ['image', 'video']:
            return content['data']
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
