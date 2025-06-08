import subprocess
import json
import logging
from pathlib import Path
import yaml
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityScanner:
    def __init__(self, project_root: str = os.getcwd()):
        self.project_root = Path(project_root)
        self.scanners = {
            'bandit': self._run_bandit,
            'safety': self._run_safety,
            'trivy': self._run_trivy,
            'owasp': self._run_owasp,
            'sonarqube': self._run_sonarqube
        }
        self.results: Dict[str, Dict] = {}

    def scan(self, scanners: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Run security scans using specified scanners."""
        if scanners is None:
            scanners = list(self.scanners.keys())

        for scanner in scanners:
            if scanner in self.scanners:
                logger.info(f"Running {scanner} scan...")
                result = self.scanners[scanner]()
                self.results[scanner] = result
            else:
                logger.warning(f"Scanner {scanner} not available")

        return self.results

    def _run_bandit(self) -> Dict:
        """Run Bandit security scanner."""
        try:
            result = subprocess.run(
                ['bandit', '-r', str(self.project_root)],
                capture_output=True,
                text=True
            )
            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'errors': result.stderr
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _run_safety(self) -> Dict:
        """Run Safety security scanner."""
        try:
            result = subprocess.run(
                ['safety', 'check', '--full-report'],
                capture_output=True,
                text=True
            )
            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'errors': result.stderr
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _run_trivy(self) -> Dict:
        """Run Trivy container scanner."""
        try:
            result = subprocess.run(
                ['trivy', 'image', '--severity', 'HIGH,CRITICAL'],
                capture_output=True,
                text=True
            )
            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'errors': result.stderr
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _run_owasp(self) -> Dict:
        """Run OWASP ZAP security scanner."""
        try:
            result = subprocess.run(
                ['zap-api-scan.py', '-t', 'api.yaml', '-f', 'openapi'],
                capture_output=True,
                text=True
            )
            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'errors': result.stderr
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _run_sonarqube(self) -> Dict:
        """Run SonarQube security scanner."""
        try:
            result = subprocess.run(
                ['sonar-scanner', 
                 '-Dsonar.projectKey=orchestratex',
                 '-Dsonar.sources=.',
                 '-Dsonar.host.url=http://sonarqube:9000'],
                capture_output=True,
                text=True
            )
            return {
                'status': 'success' if result.returncode == 0 else 'failed',
                'output': result.stdout,
                'errors': result.stderr
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def generate_report(self, output_file: str = 'security_report.md') -> None:
        """Generate security scan report."""
        report = "# Security Scan Report\n\n"
        
        for scanner, result in self.results.items():
            report += f"## {scanner.capitalize()}\n\n"
            report += f"Status: {result['status']}\n\n"
            
            if result['status'] == 'success':
                report += "### Results\n\n"
                report += f"```
{result['output']}
```
\n"
            elif result['status'] == 'failed':
                report += "### Errors\n\n"
                report += f"```
{result['errors']}
```
\n"
            else:
                report += "### Error\n\n"
                report += f"```
{result['error']}
```
\n"

        with open(output_file, 'w') as f:
            f.write(report)

    def get_vulnerabilities(self) -> List[Dict]:
        """Get vulnerabilities from all scans."""
        vulnerabilities = []
        
        for scanner, result in self.results.items():
            if result['status'] == 'success':
                # Parse vulnerabilities based on scanner format
                if scanner == 'bandit':
                    # Parse Bandit JSON output
                    try:
                        vulns = json.loads(result['output'])
                        vulnerabilities.extend(vulns)
                    except:
                        pass
                elif scanner == 'safety':
                    # Parse Safety output
                    lines = result['output'].split('\n')
                    for line in lines:
                        if line.startswith('PYSEC'):
                            vulnerabilities.append({
                                'scanner': scanner,
                                'vulnerability': line
                            })
                elif scanner == 'trivy':
                    # Parse Trivy output
                    lines = result['output'].split('\n')
                    for line in lines:
                        if 'Vulnerability' in line:
                            vulnerabilities.append({
                                'scanner': scanner,
                                'vulnerability': line
                            })

        return vulnerabilities

if __name__ == "__main__":
    scanner = SecurityScanner()
    results = scanner.scan()
    scanner.generate_report()
    vulnerabilities = scanner.get_vulnerabilities()
