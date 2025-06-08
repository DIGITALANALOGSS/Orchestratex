import logging
import pytest
import asyncio
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from test_automation import TestAutomation
from test_report_generator import TestReportGenerator

logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self, config_path: str = "tests/test_config.yaml"):
        self.config_path = config_path
        self.automation = TestAutomation(config_path)
        self.report_generator = TestReportGenerator()
        
    def run_all_tests(self) -> Dict:
        """Run all test scenarios and generate reports."""
        try:
            # Run tests
            results = self.automation.run_all_tests()
            
            # Generate reports
            self._generate_reports(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            raise
            
    def run_specific_tests(self, test_type: str) -> Dict:
        """Run specific test scenarios."""
        try:
            # Run specific tests
            results = self.automation.run_specific_tests(test_type)
            
            # Generate report
            self._generate_reports({
                'results': {test_type: results}
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Test {test_type} failed: {str(e)}")
            raise
            
    def run_stress_test(self, duration: int = 60) -> Dict:
        """Run stress test."""
        try:
            # Run stress test
            results = self.automation.run_stress_test(duration)
            
            # Generate report
            self._generate_reports({
                'results': {'stress': results}
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Stress test failed: {str(e)}")
            raise
            
    def _generate_reports(self, results: Dict) -> None:
        """Generate test reports."""
        try:
            # Generate JSON report
            json_report_path = self.report_generator.generate_report(results)
            
            # Generate HTML report
            html_report_path = self.report_generator.generate_html_report(json_report_path)
            
            logger.info(f"Test reports generated:")
            logger.info(f"JSON Report: {json_report_path}")
            logger.info(f"HTML Report: {html_report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate reports: {str(e)}")
            raise
            
    def analyze_results(self, results: Dict) -> Dict:
        """Analyze test results and generate recommendations."""
        try:
            # Analyze results
            analysis = self.automation._analyze_results(results)
            
            # Save analysis
            analysis_path = Path('reports') / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(analysis_path, 'w') as f:
                json.dump(analysis, f, indent=4)
            
            logger.info(f"Analysis saved to: {analysis_path}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze results: {str(e)}")
            raise
            
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Orchestratex tests')
    parser.add_argument('--test_type', choices=['all', 'performance', 'security', 'edge', 'stress'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--duration', type=int, default=60, 
                       help='Duration for stress tests (in seconds)')
    parser.add_argument('--config', default='tests/test_config.yaml', 
                       help='Path to test configuration file')
    
    args = parser.parse_args()
    
    runner = TestRunner(args.config)
    
    if args.test_type == 'all':
        runner.run_all_tests()
    elif args.test_type == 'stress':
        runner.run_stress_test(args.duration)
    else:
        runner.run_specific_tests(args.test_type)
