import logging
import asyncio
import aiohttp
import yaml
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
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

class AuditScheduler:
    def __init__(self, config_file: str = "audit_schedule.yaml"):
        self.config = self._load_config(config_file)
        self.scheduler = AsyncIOScheduler()
        self.metrics = self._initialize_metrics()
        self.tracer = self._initialize_tracer()
        self.audit_tools = AuditTools()
        self.notification_service = NotificationService()
        self.results = {
            'schedules': {},
            'metrics': {},
            'logs': {}
        }

    def _load_config(self, config_file: str) -> Dict:
        """Load audit scheduler configuration."""
        with open(config_file) as f:
            return yaml.safe_load(f)

    def _initialize_metrics(self) -> Dict:
        """Initialize Prometheus metrics."""
        metrics = {}
        
        # Scheduler metrics
        metrics['schedule_count'] = Gauge(
            'schedule_count',
            'Number of active schedules'
        )
        metrics['schedule_duration'] = Histogram(
            'schedule_duration',
            'Schedule execution time',
            ['schedule_name']
        )
        metrics['schedule_success'] = Counter(
            'schedule_success',
            'Successful schedule executions',
            ['schedule_name']
        )
        metrics['schedule_failure'] = Counter(
            'schedule_failure',
            'Failed schedule executions',
            ['schedule_name']
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
            service_name='orchestratex-scheduler'
        )
        return config.initialize_tracer()

    def start(self) -> None:
        """Start the audit scheduler."""
        # Start scheduler
        self.scheduler.start()
        
        # Add all schedules
        for schedule in self.config['schedules']:
            self._add_schedule(schedule)
            
        logger.info("Audit scheduler started with %d schedules", len(self.config['schedules']))

    def _add_schedule(self, schedule: Dict) -> None:
        """Add a schedule to the scheduler."""
        try:
            # Create cron trigger
            trigger = CronTrigger(
                cron=schedule['cron'],
                timezone=schedule['timezone']
            )
            
            # Add job to scheduler
            job = self.scheduler.add_job(
                self._run_schedule,
                trigger=trigger,
                args=[schedule],
                id=schedule['name'],
                name=schedule['description']
            )
            
            logger.info("Added schedule %s: %s", schedule['name'], schedule['description'])
            
        except Exception as e:
            logger.error(f"Failed to add schedule {schedule['name']}: {str(e)}")
            raise

    async def _run_schedule(self, schedule: Dict) -> Dict:
        """Run a scheduled audit."""
        # Start schedule trace
        span = self._start_trace(f"schedule_{schedule['name']}")
        
        try:
            # Run audits
            audit_results = await self.audit_tools.run_audits()
            
            # Process results
            self._process_audit_results(schedule, audit_results)
            
            # Send notifications if needed
            await self._send_notifications(schedule, audit_results)
            
            # Update metrics
            self.metrics['schedule_success'].labels(
                schedule_name=schedule['name']
            ).inc()
            
            return audit_results
            
        except Exception as e:
            logger.error(f"Schedule {schedule['name']} failed: {str(e)}")
            self.metrics['schedule_failure'].labels(
                schedule_name=schedule['name']
            ).inc()
            raise
            
        finally:
            span.finish()

    def _process_audit_results(self, schedule: Dict, results: Dict) -> None:
        """Process audit results and update metrics."""
        # Update schedule metrics
        self.metrics['schedule_count'].set(len(self.scheduler.get_jobs()))
        
        # Calculate audit metrics
        total_findings = sum(
            len(target['findings'])
            for audit in results['audits'].values()
            for target in audit['targets']
        )
        
        high_findings = sum(
            1 for audit in results['audits'].values()
            for target in audit['targets']
            for finding in target['findings']
            if finding['severity'] == 'high'
        )
        
        self.results['schedules'][schedule['name']] = {
            'total_findings': total_findings,
            'high_findings': high_findings,
            'execution_time': datetime.now().isoformat(),
            'status': 'success'
        }

    async def _send_notifications(self, schedule: Dict, results: Dict) -> None:
        """Send notifications for audit results."""
        # Create alerts based on results
        alerts = []
        
        # Check high severity findings
        high_findings = sum(
            1 for audit in results['audits'].values()
            for target in audit['targets']
            for finding in target['findings']
            if finding['severity'] == 'high'
        )
        
        if high_findings > schedule['notifications']['rules']['high_findings']['threshold']:
            alerts.append({
                'severity': 'critical',
                'description': 'High severity findings threshold exceeded',
                'value': high_findings,
                'threshold': schedule['notifications']['rules']['high_findings']['threshold']
            })
        
        # Check coverage
        avg_coverage = sum(
            target['coverage']
            for audit in results['audits'].values()
            for target in audit['targets']
        ) / len(results['audits']) if results['audits'] else 0.0
        
        if avg_coverage < schedule['notifications']['rules']['coverage']['threshold']:
            alerts.append({
                'severity': 'warning',
                'description': 'Low audit coverage',
                'value': avg_coverage,
                'threshold': schedule['notifications']['rules']['coverage']['threshold']
            })
        
        # Send notifications
        if alerts:
            await self.notification_service.send_notifications(alerts)

    def _calculate_metrics(self) -> None:
        """Calculate scheduler metrics."""
        # Calculate total schedules
        total_schedules = len(self.scheduler.get_jobs())
        
        # Calculate successful schedules
        success_count = sum(
            1 for result in self.results['schedules'].values()
            if result['status'] == 'success'
        )
        
        # Calculate failure rate
        failure_rate = (
            (total_schedules - success_count) / total_schedules
            if total_schedules > 0 else 0.0
        )
        
        self.results['metrics']['total_schedules'] = total_schedules
        self.results['metrics']['success_count'] = success_count
        self.results['metrics']['failure_rate'] = failure_rate

    def _start_trace(self, operation_name: str) -> opentracing.Span:
        """Start a new trace."""
        tracer = opentracing.global_tracer()
        return tracer.start_span(operation_name)

if __name__ == "__main__":
    async def main():
        scheduler = AuditScheduler()
        scheduler.start()
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            scheduler.scheduler.shutdown()

    asyncio.run(main())
