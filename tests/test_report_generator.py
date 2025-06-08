import logging
import json
import datetime
import os
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

class TestReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_report(self, test_results: Dict) -> str:
        """Generate a comprehensive test report.
        
        Args:
            test_results: Dictionary containing test results
            
        Returns:
            str: Path to generated report
        """
        report = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'system_info': self._get_system_info(),
            'test_summary': self._generate_summary(test_results),
            'detailed_results': test_results,
            'performance_metrics': self._get_performance_metrics(test_results),
            'recommendations': self._generate_recommendations(test_results)
        }
        
        report_path = self.output_dir / f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=4)
        
        return str(report_path)
        
    def _get_system_info(self) -> Dict:
        """Get system information."""
        import platform
        import psutil
        
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu': {
                'count': psutil.cpu_count(),
                'usage': psutil.cpu_percent(interval=1)
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'free': psutil.disk_usage('/').free
            }
        }
        
    def _generate_summary(self, test_results: Dict) -> Dict:
        """Generate test summary statistics."""
        summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'average_duration': 0
        }
        
        durations = []
        
        for category, tests in test_results.items():
            for test in tests:
                summary['total_tests'] += 1
                if test.get('result', None):
                    summary['passed'] += 1
                else:
                    summary['failed'] += 1
                    if test.get('error'):
                        summary['errors'].append({
                            'test': test['case']['action'],
                            'error': test['error']
                        })
                if 'duration' in test:
                    durations.append(test['duration'])
        
        if durations:
            summary['average_duration'] = sum(durations) / len(durations)
        
        return summary
        
    def _get_performance_metrics(self, test_results: Dict) -> Dict:
        """Generate performance metrics."""
        metrics = {
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        
        for category, tests in test_results.items():
            if category == 'performance':
                for test in tests:
                    if 'performance_metrics' in test:
                        metrics['response_times'].append(test['performance_metrics']['response_time'])
                        metrics['memory_usage'].append(test['performance_metrics']['memory_usage'])
                        metrics['cpu_usage'].append(test['performance_metrics']['cpu_usage'])
        
        return {
            'response_times': {
                'average': sum(metrics['response_times']) / len(metrics['response_times']) if metrics['response_times'] else 0,
                'max': max(metrics['response_times']) if metrics['response_times'] else 0,
                'min': min(metrics['response_times']) if metrics['response_times'] else 0
            },
            'memory_usage': {
                'average': sum(metrics['memory_usage']) / len(metrics['memory_usage']) if metrics['memory_usage'] else 0,
                'max': max(metrics['memory_usage']) if metrics['memory_usage'] else 0,
                'min': min(metrics['memory_usage']) if metrics['memory_usage'] else 0
            },
            'cpu_usage': {
                'average': sum(metrics['cpu_usage']) / len(metrics['cpu_usage']) if metrics['cpu_usage'] else 0,
                'max': max(metrics['cpu_usage']) if metrics['cpu_usage'] else 0,
                'min': min(metrics['cpu_usage']) if metrics['cpu_usage'] else 0
            }
        }
        
    def _generate_recommendations(self, test_results: Dict) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Check for failed tests
        if any(not test.get('result', None) for tests in test_results.values() for test in tests):
            recommendations.append("Investigate failed tests and review error logs")
            
        # Check performance metrics
        perf_metrics = self._get_performance_metrics(test_results)
        if perf_metrics['response_times']['average'] > 1.0:  # More than 1 second average
            recommendations.append("Review system performance and consider optimizations")
            
        # Check resource usage
        if perf_metrics['memory_usage']['max'] > 0.8:  # More than 80% memory usage
            recommendations.append("Monitor memory usage and consider increasing resources")
            
        return recommendations
        
    def generate_html_report(self, json_report_path: str) -> str:
        """Generate an HTML version of the report.
        
        Args:
            json_report_path: Path to JSON report file
            
        Returns:
            str: Path to generated HTML report
        """
        import json
        
        with open(json_report_path, 'r') as f:
            report = json.load(f)
            
        html_path = self.output_dir / f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(html_path, 'w') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Orchestratex Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #4CAF50; color: white; padding: 20px; }
        .summary { background-color: #f5f5f5; padding: 20px; margin: 20px 0; }
        .error { color: red; font-weight: bold; }
        .success { color: green; font-weight: bold; }
        .warning { color: orange; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Orchestratex Test Report</h1>
        <p>Generated: {timestamp}</p>
    </div>

    <div class="summary">
        <h2>Test Summary</h2>
        <p>Total Tests: {total_tests}</p>
        <p>Passed: {passed}</p>
        <p>Failed: {failed}</p>
        <p>Average Duration: {average_duration:.2f}s</p>
    </div>

    <div class="details">
        <h2>Detailed Results</h2>
        <div class="system-info">
            <h3>System Information</h3>
            <pre>{system_info}</pre>
        </div>
        
        <div class="performance">
            <h3>Performance Metrics</h3>
            <pre>{performance_metrics}</pre>
        </div>
        
        <div class="recommendations">
            <h3>Recommendations</h3>
            <ul>
                {recommendations}
            </ul>
        </div>
    </div>
</body>
</html>
""".format(
                timestamp=report['timestamp'],
                total_tests=report['test_summary']['total_tests'],
                passed=report['test_summary']['passed'],
                failed=report['test_summary']['failed'],
                average_duration=report['test_summary']['average_duration'],
                system_info=json.dumps(report['system_info'], indent=4),
                performance_metrics=json.dumps(report['performance_metrics'], indent=4),
                recommendations="".join(f"<li>{rec}</li>" for rec in report['recommendations'])
            ))
        
        return str(html_path)
