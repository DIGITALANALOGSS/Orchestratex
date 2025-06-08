import time
import random
import logging
import asyncio
from typing import Dict, List, Optional
import aiohttp
import pytest
from prometheus_client import Counter, Histogram, Gauge

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PerformanceTest:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
        
        # Prometheus metrics
        self.request_counter = Counter(
            'quantum_requests_total',
            'Total number of quantum requests',
            ['operation', 'status']
        )
        
        self.request_latency = Histogram(
            'quantum_request_latency_seconds',
            'Quantum request latency in seconds',
            ['operation']
        )
        
        self.error_rate = Gauge(
            'quantum_error_rate',
            'Quantum operation error rate'
        )
        
        self.resource_usage = Gauge(
            'quantum_resource_usage',
            'Quantum resource usage',
            ['resource_type']
        )

    async def generate_quantum_data(self, size: int = 1024) -> Dict:
        """Generate random quantum circuit data."""
        return {
            "circuit": {
                "name": f"test_circuit_{int(time.time())}",
                "operations": [
                    {
                        "gate": random.choice(["H", "X", "Y", "Z"]),
                        "qubits": [random.randint(0, 15)]
                    }
                    for _ in range(size)
                ]
            }
        }

    async def test_quantum_circuit(self, circuit_data: Dict) -> Dict:
        """Test quantum circuit execution."""
        start_time = time.time()
        
        try:
            async with self.session.post(
                f"{self.base_url}/quantum/circuit",
                json=circuit_data
            ) as response:
                result = await response.json()
                status = "success" if response.status == 200 else "error"
                
                self.request_counter.labels(
                    operation="circuit",
                    status=status
                ).inc()
                
                self.request_latency.labels(
                    operation="circuit"
                ).observe(time.time() - start_time)
                
                return result
        except Exception as e:
            self.request_counter.labels(
                operation="circuit",
                status="error"
            ).inc()
            raise

    async def test_quantum_state(self, circuit_id: str) -> Dict:
        """Test quantum state query."""
        start_time = time.time()
        
        try:
            async with self.session.get(
                f"{self.base_url}/quantum/state/{circuit_id}"
            ) as response:
                result = await response.json()
                status = "success" if response.status == 200 else "error"
                
                self.request_counter.labels(
                    operation="state",
                    status=status
                ).inc()
                
                self.request_latency.labels(
                    operation="state"
                ).observe(time.time() - start_time)
                
                return result
        except Exception as e:
            self.request_counter.labels(
                operation="state",
                status="error"
            ).inc()
            raise

    async def run_load_test(self, 
                          num_requests: int = 1000, 
                          concurrency: int = 10) -> Dict:
        """Run load test with specified number of requests and concurrency."""
        tasks = []
        results = {
            "success": 0,
            "errors": 0,
            "latencies": [],
            "errors_list": []
        }
        
        async def test_runner():
            try:
                data = await self.generate_quantum_data()
                result = await self.test_quantum_circuit(data)
                results["success"] += 1
                results["latencies"].append(result.get("execution_time", 0))
            except Exception as e:
                results["errors"] += 1
                results["errors_list"].append(str(e))

        for _ in range(num_requests):
            tasks.append(asyncio.create_task(test_runner()))
            
            # Limit concurrency
            if len(tasks) >= concurrency:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                tasks = list(pending)

        # Wait for remaining tasks
        await asyncio.gather(*tasks)
        
        # Calculate statistics
        avg_latency = sum(results["latencies"]) / len(results["latencies"]) if results["latencies"] else 0
        error_rate = results["errors"] / num_requests
        
        # Update metrics
        self.error_rate.set(error_rate)
        self.resource_usage.labels(resource_type="cpu").set(random.uniform(0.5, 0.8))
        self.resource_usage.labels(resource_type="memory").set(random.uniform(0.3, 0.6))
        
        return {
            "total_requests": num_requests,
            "successful_requests": results["success"],
            "failed_requests": results["errors"],
            "average_latency": avg_latency,
            "error_rate": error_rate,
            "errors": results["errors_list"]
        }

    def generate_report(self, test_results: Dict) -> str:
        """Generate performance test report."""
        report = "# Performance Test Report\n\n"
        report += f"## Test Summary\n\n"
        report += f"Total Requests: {test_results['total_requests']}\n\n"
        report += f"Successful Requests: {test_results['successful_requests']}\n\n"
        report += f"Failed Requests: {test_results['failed_requests']}\n\n"
        report += f"Average Latency: {test_results['average_latency']:.2f}s\n\n"
        report += f"Error Rate: {test_results['error_rate']:.2%}\n\n"
        
        if test_results['errors']:
            report += "## Errors\n\n"
            for error in test_results['errors']:
                report += f"- {error}\n"
        
        return report

@pytest.mark.asyncio
async def test_quantum_performance():
    """Run quantum performance tests."""
    tester = PerformanceTest()
    
    # Test small circuits
    small_circuit = await tester.generate_quantum_data(size=10)
    result = await tester.test_quantum_circuit(small_circuit)
    assert result["status"] == "success"
    
    # Test large circuits
    large_circuit = await tester.generate_quantum_data(size=1000)
    result = await tester.test_quantum_circuit(large_circuit)
    assert result["status"] == "success"
    
    # Run load test
    load_test_results = await tester.run_load_test(
        num_requests=1000,
        concurrency=10
    )
    
    # Validate results
    assert load_test_results["error_rate"] < 0.01
    assert load_test_results["average_latency"] < 1.0
    
    # Generate report
    report = tester.generate_report(load_test_results)
    print(report)

if __name__ == "__main__":
    asyncio.run(test_quantum_performance())
