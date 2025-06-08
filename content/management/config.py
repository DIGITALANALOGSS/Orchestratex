import logging
from typing import Dict, Any, List
from ..core.environment_manager import EnvironmentManager

class ContentManager:
    def __init__(self):
        """Initialize content manager."""
        self.logger = logging.getLogger(__name__)
        self.env_manager = EnvironmentManager()
        self.config = self.env_manager.get_content_config()
        self._setup_storage()
        self._setup_replication()
        
    def _setup_storage(self):
        """Setup content storage based on environment."""
        storage_type = self.config.get("storage", {}).get("type", "local")
        
        if storage_type == "local":
            self.storage = LocalStorage(self.config)
        elif storage_type == "cloud":
            provider = self.config.get("storage", {}).get("provider", "aws")
            if provider == "aws":
                self.storage = AWSStorage(self.config)
            elif provider == "gcp":
                self.storage = GCPStorage(self.config)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
            
    def _setup_replication(self):
        """Setup content replication."""
        if self.config.get("replication", {}).get("enabled", False):
            self.replication = ReplicationManager(self.config)
        else:
            self.replication = None
            
    def upload_content(self, content: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Upload content to storage.
        
        Args:
            content: Content data
            metadata: Content metadata
            
        Returns:
            Content ID
        """
        try:
            content_id = self.storage.upload(content, metadata)
            
            if self.replication:
                self.replication.replicate_content(content_id)
                
            return content_id
            
        except Exception as e:
            self.logger.error(f"Failed to upload content: {str(e)}")
            raise
            
    def get_content(self, content_id: str) -> Dict[str, Any]:
        """Get content by ID.
        
        Args:
            content_id: Content ID
            
        Returns:
            Content data
        """
        try:
            return self.storage.get(content_id)
            
        except Exception as e:
            self.logger.error(f"Failed to get content {content_id}: {str(e)}")
            raise
            
    def delete_content(self, content_id: str) -> bool:
        """Delete content.
        
        Args:
            content_id: Content ID
            
        Returns:
            True if deletion was successful
        """
        try:
            if self.replication:
                self.replication.delete_content(content_id)
                
            return self.storage.delete(content_id)
            
        except Exception as e:
            self.logger.error(f"Failed to delete content {content_id}: {str(e)}")
            raise
            
    def list_content(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List content with optional filters.
        
        Args:
            filters: Optional filters
            
        Returns:
            List of content items
        """
        try:
            return self.storage.list(filters)
            
        except Exception as e:
            self.logger.error(f"Failed to list content: {str(e)}")
            raise
            
    def validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate content before upload.
        
        Args:
            content: Content data
            
        Returns:
            True if content is valid
        """
        try:
            # Basic validation
            if not content:
                return False
                
            # Type-specific validation
            content_type = content.get("type")
            if content_type == "text":
                return self._validate_text_content(content)
            elif content_type == "image":
                return self._validate_image_content(content)
            elif content_type == "video":
                return self._validate_video_content(content)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to validate content: {str(e)}")
            return False
            
    def _validate_text_content(self, content: Dict[str, Any]) -> bool:
        """Validate text content.
        
        Args:
            content: Text content
            
        Returns:
            True if valid
        """
        try:
            # Check length
            if len(content.get("text", "")) > 1000000:
                return False
                
            # Check format
            if not isinstance(content.get("text"), str):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate text content: {str(e)}")
            return False
            
    def _validate_image_content(self, content: Dict[str, Any]) -> bool:
        """Validate image content.
        
        Args:
            content: Image content
            
        Returns:
            True if valid
        """
        try:
            # Check size
            if content.get("size", 0) > 100 * 1024 * 1024:  # 100MB
                return False
                
            # Check format
            allowed_formats = ["jpg", "jpeg", "png", "gif"]
            if content.get("format") not in allowed_formats:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate image content: {str(e)}")
            return False
            
    def _validate_video_content(self, content: Dict[str, Any]) -> bool:
        """Validate video content.
        
        Args:
            content: Video content
            
        Returns:
            True if valid
        """
        try:
            # Check size
            if content.get("size", 0) > 1000 * 1024 * 1024:  # 1GB
                return False
                
            # Check format
            allowed_formats = ["mp4", "webm", "mov"]
            if content.get("format") not in allowed_formats:
                return False
                
            # Check duration
            if content.get("duration", 0) > 3600:  # 1 hour
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate video content: {str(e)}")
            return False
