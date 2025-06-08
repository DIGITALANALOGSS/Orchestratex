import boto3
from typing import Dict, Any, Optional
from ..management.config import ContentManager
import logging

class AWSStorage:
    def __init__(self, config: Dict[str, Any]):
        """Initialize AWS S3 storage.
        
        Args:
            config: Storage configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.region = config.get("storage", {}).get("region", "us-east-1")
        self.bucket = config.get("storage", {}).get("bucket")
        
        if not self.bucket:
            raise ValueError("S3 bucket name is required in configuration")
            
        self.s3 = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=config.get("aws_access_key_id"),
            aws_secret_access_key=config.get("aws_secret_access_key")
        )
        
    def upload(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Upload content to S3.
        
        Args:
            content: Content data
            metadata: Content metadata
            
        Returns:
            Content ID (S3 key)
        """
        try:
            content_id = f"content/{metadata.get('type', 'unknown')}/{metadata.get('id', 'unknown')}"
            
            # Convert content to appropriate format
            content_data = self._prepare_content(content)
            
            # Upload to S3
            self.s3.put_object(
                Bucket=self.bucket,
                Key=content_id,
                Body=content_data,
                Metadata={
                    'content_type': metadata.get('type', ''),
                    'created_at': str(metadata.get('created_at', '')),
                    'version': metadata.get('version', '1')
                }
            )
            
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to upload to S3: {str(e)}")
            raise
            
    def get(self, content_id: str) -> Dict[str, Any]:
        """Get content from S3.
        
        Args:
            content_id: Content ID (S3 key)
            
        Returns:
            Content data
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=content_id)
            content_data = self._parse_content(response['Body'].read())
            metadata = response.get('Metadata', {})
            
            return {
                'content': content_data,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get content {content_id}: {str(e)}")
            raise
            
    def delete(self, content_id: str) -> bool:
        """Delete content from S3.
        
        Args:
            content_id: Content ID (S3 key)
            
        Returns:
            True if deletion was successful
        """
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=content_id)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete content {content_id}: {str(e)}")
            raise
            
    def list(self, filters: Dict[str, Any] = None) -> list:
        """List content in S3.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of content items
        """
        try:
            prefix = filters.get('type', '') if filters else ''
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=f"content/{prefix}" if prefix else "content/"
            )
            
            return [{
                'id': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified']
            } for obj in response.get('Contents', [])]
            
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
            
    def _parse_content(self, content_data: bytes) -> Dict[str, Any]:
        """Parse stored content.
        
        Args:
            content_data: Content as bytes
            
        Returns:
            Content data dictionary
        """
        # Implementation depends on content type
        return {'data': content_data}
