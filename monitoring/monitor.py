import logging
import time
from datetime import datetime
import threading
from typing import Dict, Any, Callable, List
import psutil
import platform
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    CUSTOM = "custom"

@dataclass
class Metric:
    name: str
    value: float
    unit: str
    timestamp: datetime
    metric_type: MetricType
    tags: Dict[str, str]

class Monitor:
    def __init__(self, interval: float = 1.0):
        """Initialize the monitor.
        
        Args:
            interval: Monitoring interval in seconds
        """
        self.interval = interval
        self.metrics: List[Metric] = []
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._last_metrics: Dict[str, float] = {}
        
    def start(self):
        """Start monitoring."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            logger.info("Monitoring started")
            
    def stop(self):
        """Stop monitoring."""
        if self._running:
            self._running = False
            if self._thread:
                self._thread.join()
            logger.info("Monitoring stopped")
            
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                self._collect_metrics()
                time.sleep(self.interval)
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                time.sleep(self.interval)
                
    def _collect_metrics(self):
        """Collect system metrics."""
        with self._lock:
            metrics = {
                MetricType.CPU: self._get_cpu_metrics(),
                MetricType.MEMORY: self._get_memory_metrics(),
                MetricType.DISK: self._get_disk_metrics(),
                MetricType.NETWORK: self._get_network_metrics()
            }
            
            for metric_type, metric_data in metrics.items():
                for name, value in metric_data.items():
                    metric = Metric(
                        name=name,
                        value=value,
                        unit=self._get_unit(metric_type),
                        timestamp=datetime.utcnow(),
                        metric_type=metric_type,
                        tags={
                            "hostname": platform.node(),
                            "os": platform.system()
                        }
                    )
                    self.metrics.append(metric)
                    self._last_metrics[name] = value
                    
    def _get_cpu_metrics(self) -> Dict[str, float]:
        """Get CPU metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(logical=True)
        }
        
    def _get_memory_metrics(self) -> Dict[str, float]:
        """Get memory metrics."""
        mem = psutil.virtual_memory()
        return {
            "memory_percent": mem.percent,
            "memory_total": mem.total / (1024 * 1024),  # Convert to MB
            "memory_available": mem.available / (1024 * 1024)
        }
        
    def _get_disk_metrics(self) -> Dict[str, float]:
        """Get disk metrics."""
        disk = psutil.disk_usage('/')
        return {
            "disk_percent": disk.percent,
            "disk_total": disk.total / (1024 * 1024 * 1024),  # Convert to GB
            "disk_free": disk.free / (1024 * 1024 * 1024)
        }
        
    def _get_network_metrics(self) -> Dict[str, float]:
        """Get network metrics."""
        net_io = psutil.net_io_counters()
        return {
            "network_bytes_sent": net_io.bytes_sent,
            "network_bytes_recv": net_io.bytes_recv,
            "network_packets_sent": net_io.packets_sent,
            "network_packets_recv": net_io.packets_recv
        }
        
    def _get_unit(self, metric_type: MetricType) -> str:
        """Get appropriate unit for metric type."""
        units = {
            MetricType.CPU: "%",
            MetricType.MEMORY: "MB",
            MetricType.DISK: "GB",
            MetricType.NETWORK: "bytes",
            MetricType.CUSTOM: ""
        }
        return units.get(metric_type, "")

class PerformanceMonitor(Monitor):
    def __init__(self, interval: float = 0.5):
        super().__init__(interval)
        self._last_metrics: Dict[str, float] = {}
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        with self._lock:
            metrics = {
                "cpu": self._get_cpu_metrics(),
                "memory": self._get_memory_metrics(),
                "disk": self._get_disk_metrics(),
                "network": self._get_network_metrics()
            }
            return metrics

class HealthCheck:
    def __init__(self):
        self._checks = []
        
    def add_check(self, name: str, check_func: Callable[[], bool], interval: float = 60.0):
        """Add a health check.
        
        Args:
            name: Name of the check
            check_func: Function that returns True if healthy
            interval: Check interval in seconds
        """
        self._checks.append({
            "name": name,
            "func": check_func,
            "interval": interval,
            "last_check": 0,
            "healthy": True
        })
        
    def run_checks(self) -> Dict[str, bool]:
        """Run all health checks."""
        results = {}
        current_time = time.time()
        
        for check in self._checks:
            if current_time - check["last_check"] >= check["interval"]:
                try:
                    healthy = check["func"]()
                    check["healthy"] = healthy
                    check["last_check"] = current_time
                    results[check["name"]] = healthy
                except Exception as e:
                    logger.error(f"Health check {check['name']} failed: {str(e)}")
                    check["healthy"] = False
                    results[check["name"]] = False
        
        return results

class ResourceMonitor:
    def __init__(self):
        self._resources = {}
        
    def track_resource(self, name: str, resource: Any):
        """Track a resource.
        
        Args:
            name: Resource name
            resource: Resource object
        """
        self._resources[name] = {
            "resource": resource,
            "usage": 0,
            "peak": 0,
            "timestamp": time.time()
        }
        
    def update_resource_usage(self, name: str, usage: float):
        """Update resource usage.
        
        Args:
            name: Resource name
            usage: Current usage
        """
        if name in self._resources:
            resource = self._resources[name]
            resource["usage"] = usage
            if usage > resource["peak"]:
                resource["peak"] = usage
            resource["timestamp"] = time.time()
