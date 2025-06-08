import logging
import asyncio
import aiohttp
import yaml
import json
from datetime import datetime
import subprocess
import os
import tempfile
import hashlib
import re
import prometheus_client
from prometheus_client import Counter, Gauge, Histogram, Summary
import opentracing
from jaeger_client import Config as JaegerConfig
from audit_tools import AuditTools
from notification_service import NotificationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComplianceService:
    def __init__(self, config_file: str = "compliance_report.yaml"):
        self.config = self._load_config(config_file)
        self.audit_tools = AuditTools()
        self.notification_service = NotificationService()
        self.metrics = self._initialize_metrics()
        self.tracer = self._initialize_tracer()
        self.results = {
            'compliance': {},
            'metrics': {},
            'logs': {}
        }

    def _load_config(self, config_file: str) -> Dict:
        """Load compliance configuration."""
        with open(config_file) as f:
            return yaml.safe_load(f)

    def _initialize_metrics(self) -> Dict:
        """Initialize Prometheus metrics."""
        metrics = {}
        
        # Compliance metrics
        metrics['compliance_score'] = Gauge(
            'compliance_score',
            'Overall compliance score',
            ['standard', 'requirement']
        )
        metrics['requirement_coverage'] = Gauge(
            'requirement_coverage',
            'Requirement coverage',
            ['standard', 'requirement']
        )
        metrics['evidence_validity'] = Gauge(
            'evidence_validity',
            'Evidence validity',
            ['standard', 'requirement']
        )
        metrics['remediation_success'] = Counter(
            'remediation_success',
            'Successful remediations',
            ['standard', 'requirement']
        )
        metrics['remediation_failure'] = Counter(
            'remediation_failure',
            'Failed remediations',
            ['standard', 'requirement']
        )
        
        return metrics

    def _initialize_tracer(self) -> opentracing.Tracer:
        """Initialize Jaeger tracer."""
        config = JaegerConfig(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'local_agent': {
                    'reporting_host': 'jaeger-agent.orchestratex.svc.cluster.local',
                    'reporting_port': 6831,
                },
                'logging': True,
            },
            service_name='orchestratex-compliance'
        )
        return config.initialize_tracer()

    async def check_compliance(self) -> Dict:
        """Check compliance against all standards."""
        # Start compliance trace
        span = self._start_trace("compliance_check")
        
        try:
            # Run compliance checks concurrently
            compliance_tasks = [
                self._check_standard(standard)
                for standard in self.config['standards']
            ]
            
            compliance_results = await asyncio.gather(*compliance_tasks)
            
            # Generate compliance report
            self._generate_report(compliance_results)
            
            # Check for remediations
            await self._check_remediations(compliance_results)
            
            # Send notifications if needed
            await self._send_notifications(compliance_results)
            
            return compliance_results
            
        except Exception as e:
            logger.error(f"Compliance check failed: {str(e)}")
            self.results['compliance']['status'] = 'failed'
            self.results['compliance']['error'] = str(e)
            raise
            
        finally:
            span.finish()

    async def _check_standard(self, standard: Dict) -> Dict:
        """Check compliance for a specific standard."""
        standard_result = {
            'standard': standard['name'],
            'description': standard['description'],
            'requirements': [],
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': None,
            'score': None
        }
        
        # Run requirement checks concurrently
        requirement_tasks = [
            self._check_requirement(requirement)
            for requirement in standard['requirements']
        ]
        
        requirement_results = await asyncio.gather(*requirement_tasks)
        standard_result['requirements'] = requirement_results
        
        # Calculate standard score
        total_requirements = len(requirement_results)
        compliant_requirements = sum(
            1 for req in requirement_results
            if req['status'] == 'compliant'
        )
        
        standard_result['score'] = (
            compliant_requirements / total_requirements * 100
            if total_requirements > 0 else 0.0
        )
        
        # Update standard status
        if any(req['status'] == 'non_compliant' for req in requirement_results):
            standard_result['status'] = 'non_compliant'
        else:
            standard_result['status'] = 'compliant'
        
        # Update standard duration
        standard_result['end_time'] = datetime.now().isoformat()
        standard_result['duration'] = (
            datetime.fromisoformat(standard_result['end_time']) -
            datetime.fromisoformat(standard_result['start_time'])
        ).total_seconds()
        
        return standard_result

    async def _check_requirement(self, requirement: Dict) -> Dict:
        """Check compliance for a specific requirement."""
        requirement_result = {
            'name': requirement['name'],
            'description': requirement['description'],
            'category': requirement['category'],
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': None,
            'evidence': [],
            'findings': []
        }
        
        # Start requirement trace
        span = self._start_trace(f"requirement_{requirement['name']}")
        
        try:
            # Check evidence
            evidence_tasks = [
                self._check_evidence(evidence)
                for evidence in requirement['evidence']
            ]
            
            evidence_results = await asyncio.gather(*evidence_tasks)
            requirement_result['evidence'] = evidence_results
            
            # Run audits if needed
            if requirement['audit_required']:
                audit_results = await self.audit_tools.run_audits()
                requirement_result['findings'] = audit_results['audits']
            
            # Update requirement status
            if any(e['status'] == 'invalid' for e in evidence_results):
                requirement_result['status'] = 'non_compliant'
            elif any(f['severity'] == 'high' for audit in requirement_result['findings']
                     for target in audit['targets']
                     for finding in target['findings']):
                requirement_result['status'] = 'non_compliant'
            else:
                requirement_result['status'] = 'compliant'
            
        except Exception as e:
            requirement_result['status'] = 'error'
            requirement_result['error'] = str(e)
            
        finally:
            # Update requirement duration
            requirement_result['end_time'] = datetime.now().isoformat()
            requirement_result['duration'] = (
                datetime.fromisoformat(requirement_result['end_time']) -
                datetime.fromisoformat(requirement_result['start_time'])
            ).total_seconds()
            
            span.finish()
            
        return requirement_result

    async def _check_evidence(self, evidence: Dict) -> Dict:
        """Check validity of evidence."""
        evidence_result = {
            'type': evidence['type'],
            'path': evidence['path'],
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': None,
            'errors': []
        }
        
        try:
            if evidence['type'] == 'document':
                await self._check_document_evidence(evidence)
            elif evidence['type'] == 'audit':
                await self._check_audit_evidence(evidence)
            
            evidence_result['status'] = 'valid'
            
        except Exception as e:
            evidence_result['status'] = 'invalid'
            evidence_result['errors'].append(str(e))
            
        finally:
            evidence_result['end_time'] = datetime.now().isoformat()
            evidence_result['duration'] = (
                datetime.fromisoformat(evidence_result['end_time']) -
                datetime.fromisoformat(evidence_result['start_time'])
            ).total_seconds()
            
        return evidence_result

    async def _check_document_evidence(self, evidence: Dict) -> None:
        """Check validity of document evidence."""
        # Check if file exists
        if not os.path.exists(evidence['path']):
            raise FileNotFoundError(f"Document not found: {evidence['path']}")
            
        # Check file integrity
        with open(evidence['path'], 'rb') as f:
            content = f.read()
            checksum = hashlib.sha256(content).hexdigest()
            
            if checksum != evidence.get('checksum'):
                raise ValueError("Document checksum mismatch")

    async def _check_audit_evidence(self, evidence: Dict) -> None:
        """Check validity of audit evidence."""
        # Check audit reference
        if not evidence.get('reference'):
            raise ValueError("Audit reference not found")
            
        # Check audit results
        audit_results = await self.audit_tools.run_audits()
        if not audit_results:
            raise ValueError("Audit results not found")

    async def _check_remediations(self, compliance_results: List[Dict]) -> None:
        """Check for required remediations."""
        remediation_tasks = []
        
        for result in compliance_results:
            if result['status'] == 'non_compliant':
                for requirement in result['requirements']:
                    if requirement['status'] == 'non_compliant':
                        remediation_tasks.append(
                            self._remediate_requirement(requirement)
                        )
        
        if remediation_tasks:
            await asyncio.gather(*remediation_tasks)

    async def _remediate_requirement(self, requirement: Dict) -> None:
        """Remediate a non-compliant requirement."""
        try:
            # Get remediation plan
            remediation = requirement.get('remediation')
            if not remediation:
                logger.warning(f"No remediation plan for {requirement['name']}")
                return
                
            # Execute remediation steps
            for step in remediation['steps']:
                await self._execute_remediation_step(step)
                
            # Verify remediation
            await self._verify_remediation(requirement)
            
            # Update metrics
            self.metrics['remediation_success'].labels(
                standard=requirement['category'],
                requirement=requirement['name']
            ).inc()
            
        except Exception as e:
            logger.error(f"Remediation failed for {requirement['name']}: {str(e)}")
            self.metrics['remediation_failure'].labels(
                standard=requirement['category'],
                requirement=requirement['name']
            ).inc()
            raise

    async def _execute_remediation_step(self, step: Dict) -> None:
        """Execute a single remediation step."""
        if step['type'] == 'command':
            await self._run_remediation_command(step)
        elif step['type'] == 'script':
            await self._run_remediation_script(step)
        elif step['type'] == 'api':
            await self._call_remediation_api(step)

    async def _run_remediation_command(self, step: Dict) -> None:
        """Run a remediation command."""
        result = subprocess.run(
            step['command'],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Command failed: {result.stderr}")

    async def _run_remediation_script(self, step: Dict) -> None:
        """Run a remediation script."""
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            f.write(step['script'])
            script_path = f.name
            
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True
        )
        
        os.unlink(script_path)
        
        if result.returncode != 0:
            raise Exception(f"Script failed: {result.stderr}")

    async def _call_remediation_api(self, step: Dict) -> None:
        """Call a remediation API."""
        async with aiohttp.ClientSession() as session:
            async with session.request(
                step['method'],
                step['url'],
                headers=step.get('headers', {}),
                json=step.get('body', {})
            ) as response:
                if response.status != 200:
                    raise Exception(f"API call failed: {response.status}")

    async def _verify_remediation(self, requirement: Dict) -> None:
        """Verify remediation success."""
        # Re-check requirement
        result = await self._check_requirement(requirement)
        
        if result['status'] != 'compliant':
            raise Exception(f"Remediation verification failed for {requirement['name']}")

    def _generate_report(self, compliance_results: List[Dict]) -> None:
        """Generate compliance report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'standards': compliance_results,
            'metrics': self.results['metrics'],
            'summary': {
                'total_standards': len(compliance_results),
                'compliant_standards': sum(
                    1 for result in compliance_results
                    if result['status'] == 'compliant'
                ),
                'total_requirements': sum(
                    len(result['requirements'])
                    for result in compliance_results
                ),
                'non_compliant_requirements': sum(
                    1 for result in compliance_results
                    for req in result['requirements']
                    if req['status'] == 'non_compliant'
                )
            }
        }
        
        # Save report
        with open('compliance_report.json', 'w') as f:
            json.dump(report, f, indent=2)

    async def _send_notifications(self, compliance_results: List[Dict]) -> None:
        """Send compliance notifications."""
        # Create alerts for non-compliant requirements
        alerts = []
        
        for result in compliance_results:
            if result['status'] == 'non_compliant':
                for requirement in result['requirements']:
                    if requirement['status'] == 'non_compliant':
                        alerts.append({
                            'severity': 'critical',
                            'description': f"Non-compliant requirement: {requirement['name']}",
                            'standard': result['standard'],
                            'category': requirement['category']
                        })
        
        if alerts:
            await self.notification_service.send_notifications(alerts)

    def _calculate_metrics(self) -> None:
        """Calculate compliance metrics."""
        # Calculate compliance scores
        for result in self.results['compliance'].values():
            self.metrics['compliance_score'].labels(
                standard=result['standard'],
                requirement=result['name']
            ).set(result['score'])
            
            # Calculate requirement coverage
            total_reqs = len(result['requirements'])
            compliant_reqs = sum(
                1 for req in result['requirements']
                if req['status'] == 'compliant'
            )
            
            self.metrics['requirement_coverage'].labels(
                standard=result['standard'],
                requirement=result['name']
            ).set(
                (compliant_reqs / total_reqs * 100) if total_reqs > 0 else 0.0
            )

    def _start_trace(self, operation_name: str) -> opentracing.Span:
        """Start a new trace."""
        tracer = opentracing.global_tracer()
        return tracer.start_span(operation_name)

if __name__ == "__main__":
    async def main():
        compliance = ComplianceService()
        results = await compliance.check_compliance()
        print(json.dumps(results, indent=2))

    asyncio.run(main())
