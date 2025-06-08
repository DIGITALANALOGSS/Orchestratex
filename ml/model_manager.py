import logging
import os
from typing import Dict, Any, Optional
import json
from datetime import datetime
import joblib
from pathlib import Path
import numpy as np
from sklearn.base import BaseEstimator

class ModelManager:
    def __init__(self, model_dir: str = "models"):
        """Initialize the model manager.
        
        Args:
            model_dir: Directory to store models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def save_model(self, model: BaseEstimator, name: str, metadata: Dict[str, Any]) -> str:
        """Save a trained model with metadata.
        
        Args:
            model: Trained model instance
            name: Name of the model
            metadata: Model metadata
        
        Returns:
            Path to saved model
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_name = f"{name}_{timestamp}"
        model_path = self.model_dir / f"{model_name}.joblib"
        metadata_path = self.model_dir / f"{model_name}_metadata.json"
        
        try:
            # Save model
            joblib.dump(model, model_path)
            
            # Save metadata
            metadata["timestamp"] = timestamp
            metadata["model_name"] = name
            metadata["model_path"] = str(model_path)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Model saved: {model_name}")
            return str(model_path)
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {str(e)}")
            raise
            
    def load_model(self, name: str) -> Optional[BaseEstimator]:
        """Load a model by name.
        
        Args:
            name: Model name
        
        Returns:
            Loaded model instance or None if not found
        """
        try:
            model_path = self._get_latest_model_path(name)
            if not model_path:
                return None
                
            model = joblib.load(model_path)
            self.logger.info(f"Model loaded: {name}")
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            return None
            
    def _get_latest_model_path(self, name: str) -> Optional[Path]:
        """Get the latest model path for a given name.
        
        Args:
            name: Model name
        
        Returns:
            Path to latest model or None if not found
        """
        model_files = list(self.model_dir.glob(f"{name}_*.joblib"))
        if not model_files:
            return None
            
        return max(model_files, key=lambda x: x.stat().st_mtime)
        
    def get_model_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a model.
        
        Args:
            name: Model name
        
        Returns:
            Model metadata or None if not found
        """
        try:
            metadata_path = self._get_latest_metadata_path(name)
            if not metadata_path:
                return None
                
            with open(metadata_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to get metadata: {str(e)}")
            return None
            
    def _get_latest_metadata_path(self, name: str) -> Optional[Path]:
        """Get the latest metadata path for a given name.
        
        Args:
            name: Model name
        
        Returns:
            Path to latest metadata or None if not found
        """
        metadata_files = list(self.model_dir.glob(f"{name}_*_metadata.json"))
        if not metadata_files:
            return None
            
        return max(metadata_files, key=lambda x: x.stat().st_mtime)
        
    def list_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available models with their metadata.
        
        Returns:
            Dictionary of models and their metadata
        """
        models = {}
        for metadata_file in self.model_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    model_name = metadata.get("model_name")
                    if model_name:
                        models[model_name] = metadata
            except Exception as e:
                self.logger.error(f"Error reading metadata: {str(e)}")
        return models
        
    def evaluate_model(self, model: BaseEstimator, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate a model's performance.
        
        Args:
            model: Model instance
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Evaluation metrics
        """
        try:
            predictions = model.predict(X_test)
            metrics = {
                "accuracy": float(np.mean(predictions == y_test)),
                "precision": float(np.mean(predictions[predictions == 1] == y_test[predictions == 1])),
                "recall": float(np.mean(predictions[predictions == 1] == y_test[predictions == 1])),
                "f1_score": float(2 * ((np.mean(predictions[predictions == 1] == y_test[predictions == 1]) * 
                                       np.mean(predictions[predictions == 1] == y_test[predictions == 1])) /
                                      (np.mean(predictions[predictions == 1] == y_test[predictions == 1]) + 
                                       np.mean(predictions[predictions == 1] == y_test[predictions == 1]))))
            }
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate model: {str(e)}")
            raise
