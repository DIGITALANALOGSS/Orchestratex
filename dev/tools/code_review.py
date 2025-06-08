import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional
import yaml
import json
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeReview:
    def __init__(self, config_file: str = "code_review_config.yaml"):
        self.config = self._load_config(config_file)
        self.session = aiohttp.ClientSession()

    def _load_config(self, config_file: str) -> Dict:
        """Load code review configuration."""
        with open(config_file) as f:
            return yaml.safe_load(f)

    async def analyze_code(self, code: str, filename: str) -> Dict:
        """Analyze code for review criteria."""
        results = {
            'issues': [],
            'metrics': {},
            'suggestions': []
        }

        # Check code style
        style_issues = self._check_code_style(code, filename)
        results['issues'].extend(style_issues)

        # Check security
        security_issues = await self._check_security(code, filename)
        results['issues'].extend(security_issues)

        # Check performance
        performance_issues = self._check_performance(code, filename)
        results['issues'].extend(performance_issues)

        # Calculate metrics
        results['metrics'] = self._calculate_metrics(code)

        # Generate suggestions
        results['suggestions'] = self._generate_suggestions(results['issues'])

        return results

    def _check_code_style(self, code: str, filename: str) -> List[Dict]:
        """Check code style against configured rules."""
        issues = []
        style_rules = self.config.get('style_rules', {})

        # Check line length
        max_line_length = style_rules.get('max_line_length', 88)
        for i, line in enumerate(code.split('\n')):
            if len(line) > max_line_length:
                issues.append({
                    'type': 'style',
                    'rule': 'line_length',
                    'line': i + 1,
                    'message': f'Line exceeds {max_line_length} characters'
                })

        # Check imports
        if filename.endswith('.py'):
            import_lines = [line for line in code.split('\n') if line.startswith('import') or line.startswith('from')]
            if len(import_lines) > style_rules.get('max_imports', 20):
                issues.append({
                    'type': 'style',
                    'rule': 'imports',
                    'message': 'Too many imports'
                })

        return issues

    async def _check_security(self, code: str, filename: str) -> List[Dict]:
        """Check code for security issues."""
        issues = []
        security_rules = self.config.get('security_rules', {})

        # Check for hardcoded secrets
        if any(secret in code.lower() for secret in security_rules.get('secrets', [])):
            issues.append({
                'type': 'security',
                'rule': 'hardcoded_secret',
                'message': 'Hardcoded secret detected'
            })

        # Check for unsafe operations
        if any(op in code for op in security_rules.get('unsafe_operations', [])):
            issues.append({
                'type': 'security',
                'rule': 'unsafe_operation',
                'message': 'Unsafe operation detected'
            })

        return issues

    def _check_performance(self, code: str, filename: str) -> List[Dict]:
        """Check code for performance issues."""
        issues = []
        perf_rules = self.config.get('performance_rules', {})

        # Check for inefficient loops
        if 'for' in code and 'in' in code and len(code.split('for')) > perf_rules.get('max_loops', 3):
            issues.append({
                'type': 'performance',
                'rule': 'too_many_loops',
                'message': 'Too many nested loops'
            })

        # Check for large data structures
        if any(ds in code for ds in perf_rules.get('large_data_structures', [])):
            issues.append({
                'type': 'performance',
                'rule': 'large_data_structure',
                'message': 'Large data structure detected'
            })

        return issues

    def _calculate_metrics(self, code: str) -> Dict:
        """Calculate code metrics."""
        metrics = {
            'lines_of_code': len(code.split('\n')),
            'complexity': self._calculate_complexity(code),
            'maintainability': self._calculate_maintainability(code)
        }
        return metrics

    def _calculate_complexity(self, code: str) -> int:
        """Calculate code complexity."""
        # Simple complexity calculation based on number of branches
        return len([line for line in code.split('\n') if 'if' in line or 'else' in line or 'for' in line])

    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index."""
        # Simple maintainability calculation
        loc = len(code.split('\n'))
        comments = len([line for line in code.split('\n') if line.strip().startswith('#')])
        return (comments / loc) * 100 if loc > 0 else 0

    def _generate_suggestions(self, issues: List[Dict]) -> List[Dict]:
        """Generate suggestions for identified issues."""
        suggestions = []
        
        for issue in issues:
            rule = issue['rule']
            if rule in self.config.get('suggestions', {}):
                suggestions.append({
                    'type': issue['type'],
                    'rule': rule,
                    'message': self.config['suggestions'][rule]
                })

        return suggestions

    async def send_review(self, review_data: Dict, pr_id: str) -> Dict:
        """Send review to configured platform."""
        platform = self.config.get('platform', 'github')
        
        if platform == 'github':
            return await self._send_to_github(review_data, pr_id)
        elif platform == 'gitlab':
            return await self._send_to_gitlab(review_data, pr_id)
        else:
            return {'status': 'error', 'message': f'Unsupported platform: {platform}'}

    async def _send_to_github(self, review_data: Dict, pr_id: str) -> Dict:
        """Send review to GitHub."""
        token = self.config['github']['token']
        repo = self.config['github']['repo']
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/repos/{repo}/pulls/{pr_id}/reviews'
        
        payload = {
            'body': self._format_review_message(review_data),
            'event': 'COMMENT'
        }
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            return await response.json()

    async def _send_to_gitlab(self, review_data: Dict, pr_id: str) -> Dict:
        """Send review to GitLab."""
        token = self.config['gitlab']['token']
        project_id = self.config['gitlab']['project_id']
        
        headers = {
            'PRIVATE-TOKEN': token
        }
        
        url = f'https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{pr_id}/notes'
        
        payload = {
            'body': self._format_review_message(review_data)
        }
        
        async with self.session.post(url, headers=headers, json=payload) as response:
            return await response.json()

    def _format_review_message(self, review_data: Dict) -> str:
        """Format review message for display."""
        message = "# Code Review Results\n\n"
        
        # Add metrics
        message += "## Metrics\n\n"
        for metric, value in review_data['metrics'].items():
            message += f"- {metric}: {value}\n"
        
        # Add issues
        if review_data['issues']:
            message += "\n## Issues Found\n\n"
            for issue in review_data['issues']:
                message += f"- **{issue['type']}**: {issue['message']}\n"
        
        # Add suggestions
        if review_data['suggestions']:
            message += "\n## Suggestions\n\n"
            for suggestion in review_data['suggestions']:
                message += f"- **{suggestion['rule']}**: {suggestion['message']}\n"
        
        return message

    async def review_pr(self, pr_id: str, code: str, filename: str) -> Dict:
        """Review a pull request."""
        try:
            review_data = await self.analyze_code(code, filename)
            review_result = await self.send_review(review_data, pr_id)
            return {
                'status': 'success',
                'review_data': review_data,
                'platform_response': review_result
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

if __name__ == "__main__":
    # Example usage
    async def main():
        reviewer = CodeReview()
        
        # Example code to review
        code = """
def process_data(data):
    if len(data) > 1000:
        for item in data:
            if item > 0:
                print(item)
            else:
                print(-item)
"""
        
        # Review a PR
        result = await reviewer.review_pr('123', code, 'example.py')
        print(json.dumps(result, indent=2))

    asyncio.run(main())
