import subprocess
import logging
from pathlib import Path
import yaml
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeFormatter:
    def __init__(self, project_root: str = os.getcwd()):
        self.project_root = Path(project_root)
        self.formatters = {
            'black': self._run_black,
            'isort': self._run_isort,
            'flake8': self._run_flake8,
            'autopep8': self._run_autopep8,
            'yapf': self._run_yapf
        }
        self.results: Dict[str, Dict] = {}

    def format_code(self, formatters: Optional[List[str]] = None) -> Dict[str, Dict]:
        """Format code using specified formatters."""
        if formatters is None:
            formatters = list(self.formatters.keys())

        for formatter in formatters:
            if formatter in self.formatters:
                logger.info(f"Running {formatter} formatter...")
                result = self.formatters[formatter]()
                self.results[formatter] = result
            else:
                logger.warning(f"Formatter {formatter} not available")

        return self.results

    def _run_black(self) -> Dict:
        """Run Black formatter."""
        try:
            result = subprocess.run(
                ['black', str(self.project_root), '--check'],
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

    def _run_isort(self) -> Dict:
        """Run isort formatter."""
        try:
            result = subprocess.run(
                ['isort', str(self.project_root), '--check-only'],
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

    def _run_flake8(self) -> Dict:
        """Run flake8 linter."""
        try:
            result = subprocess.run(
                ['flake8', str(self.project_root), '--max-line-length=88'],
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

    def _run_autopep8(self) -> Dict:
        """Run autopep8 formatter."""
        try:
            result = subprocess.run(
                ['autopep8', str(self.project_root), '--in-place', '--aggressive'],
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

    def _run_yapf(self) -> Dict:
        """Run yapf formatter."""
        try:
            result = subprocess.run(
                ['yapf', str(self.project_root), '--in-place', '--style=pep8'],
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

    def generate_report(self, output_file: str = 'formatting_report.md') -> None:
        """Generate formatting report."""
        report = "# Code Formatting Report\n\n"
        
        for formatter, result in self.results.items():
            report += f"## {formatter.capitalize()}\n\n"
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

    def get_issues(self) -> List[Dict]:
        """Get formatting issues from all formatters."""
        issues = []
        
        for formatter, result in self.results.items():
            if result['status'] == 'failed':
                # Parse issues based on formatter format
                if formatter == 'flake8':
                    # Parse flake8 output
                    lines = result['output'].split('\n')
                    for line in lines:
                        if line:
                            parts = line.split(':')
                            if len(parts) >= 4:
                                issues.append({
                                    'formatter': formatter,
                                    'file': parts[0],
                                    'line': parts[1],
                                    'column': parts[2],
                                    'message': parts[3]
                                })
                elif formatter == 'black':
                    # Parse Black output
                    if result['output']:
                        issues.append({
                            'formatter': formatter,
                            'message': result['output']
                        })

        return issues

if __name__ == "__main__":
    formatter = CodeFormatter()
    results = formatter.format_code()
    formatter.generate_report()
    issues = formatter.get_issues()
