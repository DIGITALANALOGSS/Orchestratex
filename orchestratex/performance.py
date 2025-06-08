import time
import asyncio
import statistics
from typing import Dict, Any, List, Callable
import logging
from orchestratex.agents.quantum_agent import QuantumAgent
from orchestratex.agents.voice_agent import VoiceAgent
from orchestratex.agents.security_agent import SecurityAgent

logger = logging.getLogger(__name__)

class Benchmark:
    """Performance benchmarking for Orchestratex components."""
    
    def __init__(self):
        self.metrics = {
            "avg_time": 0,
            "throughput": 0,
            "errors": 0,
            "success_rate": 0
        }
        
    async def run_quantum_simulation(self, 
                                    num_circuits: int = 100,
                                    circuit_depth: int = 10,
                                    num_qubits: int = 5) -> Dict[str, Any]:
        """Benchmark quantum circuit simulation performance."""
        try:
            # Initialize quantum agent
            quantum_agent = QuantumAgent()
            
            # Generate circuit descriptions
            circuits = []
            for _ in range(num_circuits):
                circuit = " + ".join(["Hadamard"] * circuit_depth)
                circuits.append(circuit)
            
            # Run benchmarks
            times = []
            for circuit in circuits:
                start = time.time()
                await quantum_agent.simulate_circuit(circuit)
                times.append(time.time() - start)
            
            # Calculate metrics
            self.metrics["avg_time"] = statistics.mean(times) * 1000  # ms
            self.metrics["throughput"] = num_circuits / sum(times)
            self.metrics["errors"] = 0  # No errors in this example
            self.metrics["success_rate"] = 100.0
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Quantum benchmark failed: {str(e)}")
            self.metrics["errors"] = 1
            self.metrics["success_rate"] = 0
            raise

class LoadTester:
    """Load testing for Orchestratex components."""
    
    def __init__(self, concurrency: int = 10, duration: int = 300, ramp_up: int = 60):
        self.concurrency = concurrency
        self.duration = duration
        self.ramp_up = ramp_up
        self.results = {
            "max_rps": 0,
            "error_rate": 0,
            "latency_95p": 0,
            "throughput": 0
        }
        
    async def run(self, target: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run load test on specified target."""
        try:
            # Initialize tasks
            tasks = []
            start_time = time.time()
            
            # Create concurrent tasks
            for _ in range(self.concurrency):
                task = asyncio.create_task(self._run_test(target, params))
                tasks.append(task)
            
            # Wait for completion
            await asyncio.gather(*tasks)
            
            # Calculate results
            total_time = time.time() - start_time
            self.results["max_rps"] = self.concurrency / total_time
            self.results["error_rate"] = (self.results["errors"] / self.concurrency) * 100
            self.results["latency_95p"] = self._calculate_percentile()
            self.results["throughput"] = self.concurrency / total_time
            
            return self.results
            
        except Exception as e:
            logger.error(f"Load test failed: {str(e)}")
            raise
            
    async def _run_test(self, target: str, params: Dict[str, Any]) -> None:
        """Run individual test instance."""
        try:
            if target == "quantum_simulation":
                quantum_agent = QuantumAgent()
                await quantum_agent.simulate_circuit(params["circuit"])
            elif target == "voice_processing":
                voice_agent = VoiceAgent()
                await voice_agent.transcribe(params["audio_file"])
            elif target == "security_check":
                security_agent = SecurityAgent()
                await security_agent.verify_quantum_parameters(params["data"])
            
        except Exception as e:
            logger.error(f"Test instance failed: {str(e)}")
            self.results["errors"] += 1
            raise

class PerformanceMonitor:
    """Comprehensive performance monitoring for Orchestratex components."""
    
    def __init__(self, 
                 metrics: List[str], 
                 interval: int = 5,
                 threshold_configs: Optional[Dict[str, Any]] = None):
        """
        Initialize PerformanceMonitor with advanced monitoring capabilities.
        
        Args:
            metrics: List of metrics to monitor
            interval: Monitoring interval in seconds
            threshold_configs: Dictionary of threshold configurations
        """
        self.metrics = metrics
        self.interval = interval
        self.threshold_configs = threshold_configs or {}
        self.current_metrics = {}
        self.history = []
        self.alerts = []
        self._initialize_thresholds()
        
    def _initialize_thresholds(self) -> None:
        """Initialize threshold configurations."""
        self.default_thresholds = {
            "cpu_usage": {
                "warning": 80.0,
                "critical": 90.0,
                "window": 60  # seconds
            },
            "memory_usage": {
                "warning": 85.0,
                "critical": 95.0,
                "window": 60
            },
            "network_latency": {
                "warning": 100.0,  # ms
                "critical": 200.0,
                "window": 30
            },
            "throughput": {
                "warning": 0.8,  # 80% of max
                "critical": 0.5,  # 50% of max
                "window": 120
            },
            "quantum_simulation_time": {
                "warning": 1000.0,  # ms
                "critical": 2000.0,
                "window": 30
            },
            "voice_processing_time": {
                "warning": 500.0,  # ms
                "critical": 1000.0,
                "window": 30
            },
            "security_check_time": {
                "warning": 100.0,  # ms
                "critical": 200.0,
                "window": 30
            }
        }
        
        # Update with user-defined thresholds
        for metric, config in self.threshold_configs.items():
            if metric in self.default_thresholds:
                self.default_thresholds[metric].update(config)
        
    def start(self) -> None:
        """Start monitoring with threshold checking."""
        asyncio.create_task(self._monitor())
        asyncio.create_task(self._check_thresholds())
        
    def stop(self) -> None:
        """Stop monitoring and generate report."""
        self.history.append(self.current_metrics)
        return self.generate_report()
        
    async def _monitor(self) -> None:
        """Monitor specified metrics with advanced collection."""
        while True:
            self.current_metrics = await self._collect_metrics()
            self.history.append(self.current_metrics)
            await asyncio.sleep(self.interval)
            
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive performance metrics."""
        metrics = {}
        
        # System metrics
        if "cpu_usage" in self.metrics:
            metrics["cpu_usage"] = await self._get_cpu_usage()
        if "memory_usage" in self.metrics:
            metrics["memory_usage"] = await self._get_memory_usage()
        if "disk_usage" in self.metrics:
            metrics["disk_usage"] = await self._get_disk_usage()
        if "network_latency" in self.metrics:
            metrics["network_latency"] = await self._get_network_latency()
        
        # Component-specific metrics
        if "quantum_simulation_time" in self.metrics:
            metrics["quantum_simulation_time"] = await self._measure_quantum_simulation()
        if "voice_processing_time" in self.metrics:
            metrics["voice_processing_time"] = await self._measure_voice_processing()
        if "security_check_time" in self.metrics:
            metrics["security_check_time"] = await self._measure_security_check()
        
        # Throughput metrics
        if "throughput" in self.metrics:
            metrics["throughput"] = await self._get_throughput()
        if "quantum_throughput" in self.metrics:
            metrics["quantum_throughput"] = await self._get_quantum_throughput()
        if "voice_throughput" in self.metrics:
            metrics["voice_throughput"] = await self._get_voice_throughput()
        
        # Error rates
        if "error_rate" in self.metrics:
            metrics["error_rate"] = await self._get_error_rate()
        if "quantum_error_rate" in self.metrics:
            metrics["quantum_error_rate"] = await self._get_quantum_error_rate()
        if "voice_error_rate" in self.metrics:
            metrics["voice_error_rate"] = await self._get_voice_error_rate()
        
        return metrics
        
    async def _check_thresholds(self) -> None:
        """Continuously check metrics against thresholds."""
        while True:
            await asyncio.sleep(self.interval)
            if self.history:
                self._check_threshold_violations()
                
    def _check_threshold_violations(self) -> None:
        """Check for threshold violations and generate alerts."""
        current = self.history[-1]
        
        for metric, value in current.items():
            if metric in self.default_thresholds:
                config = self.default_thresholds[metric]
                
                # Calculate rolling average
                window = config["window"] // self.interval
                values = [h.get(metric, 0) for h in self.history[-window:]]
                avg = sum(values) / len(values)
                
                # Check thresholds
                if avg >= config["critical"]:
                    self._generate_alert(metric, "CRITICAL", avg)
                elif avg >= config["warning"]:
                    self._generate_alert(metric, "WARNING", avg)
                    
    def _generate_alert(self, metric: str, severity: str, value: float) -> None:
        """Generate performance alert."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "metric": metric,
            "severity": severity,
            "value": value,
            "thresholds": self.default_thresholds[metric]
        }
        self.alerts.append(alert)
        logger.warning(f"Performance alert: {metric} {severity} - Value: {value}")
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            "metrics": self.current_metrics,
            "history": self.history,
            "alerts": self.alerts,
            "thresholds": self.default_thresholds,
            "summary": self._generate_summary()
        }
        return report
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary."""
        if not self.history:
            return {}
            
        summary = {}
        
        # Calculate statistics for each metric
        for metric in self.metrics:
            values = [h.get(metric, 0) for h in self.history]
            if values:
                summary[metric] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "95th_percentile": self._calculate_percentile(values, 95),
                    "alerts": len([a for a in self.alerts if a["metric"] == metric])
                }
        
        return summary
        
    @staticmethod
    def _calculate_percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
            
        values.sort()
        index = (len(values) - 1) * (percentile / 100)
        floor = int(index)
        ceil = min(len(values) - 1, floor + 1)
        if floor == ceil:
            return values[int(index)]
            
        return values[floor] * (ceil - index) + values[ceil] * (index - floor)
        
    async def _get_cpu_usage(self) -> float:
        """Get detailed CPU usage metrics."""
        try:
            import psutil
            usage = psutil.cpu_percent(interval=1, percpu=True)
            return sum(usage) / len(usage)
        except ImportError:
            return 0.0
            
    async def _get_memory_usage(self) -> Dict[str, float]:
        """Get detailed memory usage metrics."""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "total": mem.total / (1024 * 1024),  # MB
                "used": mem.used / (1024 * 1024),
                "percent": mem.percent,
                "available": mem.available / (1024 * 1024)
            }
        except ImportError:
            return {"percent": 0.0}
            
    async def _get_disk_usage(self) -> Dict[str, float]:
        """Get disk usage metrics."""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            return {
                "total": disk.total / (1024 * 1024 * 1024),  # GB
                "used": disk.used / (1024 * 1024 * 1024),
                "percent": disk.percent,
                "free": disk.free / (1024 * 1024 * 1024)
            }
        except ImportError:
            return {"percent": 0.0}
            
    async def _get_network_latency(self) -> Dict[str, Any]:
        """Get comprehensive network metrics."""
        try:
            import psutil
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errors_sent": net_io.errout,
                "errors_recv": net_io.errin
            }
        except ImportError:
            return {"latency": 0.0}
            
    async def _measure_quantum_simulation(self) -> Dict[str, float]:
        """Measure quantum simulation performance."""
        quantum_agent = QuantumAgent()
        start = time.time()
        await quantum_agent.simulate_circuit("Hadamard + CNOT")
        duration = time.time() - start
        return {
            "time_ms": duration * 1000,
            "throughput": 1.0 / duration
        }
            
    async def _measure_voice_processing(self) -> Dict[str, float]:
        """Measure voice processing performance."""
        voice_agent = VoiceAgent()
        start = time.time()
        await voice_agent.transcribe("test.wav")
        duration = time.time() - start
        return {
            "time_ms": duration * 1000,
            "throughput": 1.0 / duration
        }
            
    async def _measure_security_check(self) -> Dict[str, float]:
        """Measure security check performance."""
        security_agent = SecurityAgent()
        start = time.time()
        await security_agent.verify_quantum_parameters("test_data")
        duration = time.time() - start
        return {
            "time_ms": duration * 1000,
            "throughput": 1.0 / duration
        }
            
    async def _get_throughput(self) -> Dict[str, float]:
        """Get overall system throughput."""
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            mem = psutil.virtual_memory()
            return {
                "cpu": cpu_count * (100 - mem.percent),
                "memory": mem.available / mem.total * 100
            }
        except ImportError:
            return {"overall": 0.0}
            
    async def _get_quantum_throughput(self) -> float:
        """Get quantum processing throughput."""
        quantum_agent = QuantumAgent()
        start = time.time()
        await quantum_agent.simulate_circuit("Hadamard + CNOT")
        duration = time.time() - start
        return 1.0 / duration
            
    async def _get_voice_throughput(self) -> float:
        """Get voice processing throughput."""
        voice_agent = VoiceAgent()
        start = time.time()
        await voice_agent.transcribe("test.wav")
        duration = time.time() - start
        return 1.0 / duration
            
    async def _get_error_rate(self) -> Dict[str, float]:
        """Get overall error rate."""
        return {
            "quantum": await self._get_quantum_error_rate(),
            "voice": await self._get_voice_error_rate(),
            "security": await self._get_security_error_rate()
        }
            
    async def _get_quantum_error_rate(self) -> float:
        """Get quantum simulation error rate."""
        quantum_agent = QuantumAgent()
        return quantum_agent.metrics.get("errors", 0) / \
               (quantum_agent.metrics.get("simulations", 1) + 1)
            
    async def _get_voice_error_rate(self) -> float:
        """Get voice processing error rate."""
        voice_agent = VoiceAgent()
        return voice_agent.metrics.get("errors", 0) / \
               (voice_agent.metrics.get("transcriptions", 1) + 1)
            
    async def _get_security_error_rate(self) -> float:
        """Get security check error rate."""
        security_agent = SecurityAgent()
        return security_agent.metrics.get("errors", 0) / \
               (security_agent.metrics.get("checks", 1) + 1)
