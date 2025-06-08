from typing import List, Dict, Optional
from pydantic import BaseModel

class QuantumMLData(BaseModel):
    X: List[List[float]]
    y: List[int]

class QuantumMLTrain(BaseModel):
    num_features: int
    data: QuantumMLData

class QuantumMLPredict(BaseModel):
    classifier: str
    X_test: List[List[float]]

class QuantumCluster(BaseModel):
    num_features: int
    num_clusters: int
    data: List[List[float]]

class QuantumKernel(BaseModel):
    num_features: int
    data: List[List[float]]

class QuantumClassifier(BaseModel):
    num_features: int
    data: List[List[float]]
    labels: List[int]
