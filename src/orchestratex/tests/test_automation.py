import logging
import json
import time
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from .test_report_generator import TestReportGenerator
from .additional_test_scenarios import AdditionalTestScenarios
from .extended_test_scenarios import ExtendedTestScenarios

logger = logging.getLogger(__name__)

class TestAutomation:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.report_generator = TestReportGenerator()
        self.additional_scenarios = AdditionalTestScenarios(self.config)
        self.extended_scenarios = ExtendedTestScenarios(self.config)
        
    def _load_config(self) -> Dict:
        """Load test configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            raise
            
    def run_all_tests(self) -> Dict:
        """Run all test scenarios and generate reports."""
        results = {}
        
        # Run additional test scenarios
        logger.info("Running additional test scenarios...")
        results['additional'] = self.additional_scenarios.run_all_tests()
        
        # Run extended test scenarios
        logger.info("Running extended test scenarios...")
        results['extended'] = self.extended_scenarios.run_all_tests()
        
        # Generate reports
        logger.info("Generating test reports...")
        json_report_path = self.report_generator.generate_report(results)
        html_report_path = self.report_generator.generate_html_report(json_report_path)
        
        # Analyze results
        self._analyze_results(results)
        
        return {
            'results': results,
            'reports': {
                'json': json_report_path,
                'html': html_report_path
            }
        }
        
    def _analyze_results(self, results: Dict) -> None:
        """Analyze test results and generate recommendations."""
        issues = []
        
        # Check for failed tests
        for category, tests in results.items():
            for test in tests:
                if not test.get('result', None):
                    issues.append({
                        'category': category,
                        'test': test['case']['action'],
                        'error': test.get('error', 'Unknown error')
                    })
        
        # Check performance metrics
        perf_metrics = self.report_generator._get_performance_metrics(results)
        if perf_metrics['response_times']['average'] > 1.0:  # More than 1 second average
            issues.append({
                'category': 'performance',
                'test': 'response_time',
                'error': f"Average response time too high: {perf_metrics['response_times']['average']:.2f}s"
            })
        
        # Generate recommendations
        recommendations = []
        if issues:
            recommendations.append("Investigate failed tests and review error logs")
            
        if perf_metrics['memory_usage']['max'] > 0.8:  # More than 80% memory usage
            recommendations.append("Monitor memory usage and consider increasing resources")
            
        # Save analysis
        analysis_path = Path('reports') / f"test_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'issues': issues,
            'recommendations': recommendations,
            'performance_metrics': perf_metrics
        }
        
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=4)
        
        logger.info(f"Test analysis saved to: {analysis_path}")
        
    def run_specific_tests(self, test_type: str) -> Dict:
        """Run specific test scenarios.
        
        Args:
            test_type: Type of tests to run (additional|extended|performance|security|edge)
            
        Returns:
            Dict: Test results
        """
        if test_type == 'additional':
            return self.additional_scenarios.run_all_tests()
        elif test_type == 'extended':
            return self.extended_scenarios.run_all_tests()
        elif test_type == 'performance':
            return self.additional_scenarios.run_performance_tests()
        elif test_type == 'security':
            return self.additional_scenarios.run_security_tests()
        elif test_type == 'edge':
            return self.additional_scenarios.run_edge_cases()
        else:
            raise ValueError(f"Unknown test type: {test_type}")
            
    def run_stress_test(self, duration: int = 60) -> Dict:
        """Run stress test for specified duration.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Dict: Stress test results
        """
        start_time = time.time()
        results = []
        
        while time.time() - start_time < duration:
            try:
                # Run performance tests
                perf_results = self.additional_scenarios.run_performance_tests()
                results.extend(perf_results)
                
                # Run security tests
                security_results = self.additional_scenarios.run_security_tests()
                results.extend(security_results)
                
                # Run edge cases
                edge_results = self.additional_scenarios.run_edge_cases()
                results.extend(edge_results)
                
                # Sleep for 1 second between iterations
                time.sleep(1)
            except Exception as e:
                results.append({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
        return results
