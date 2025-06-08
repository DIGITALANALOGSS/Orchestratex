import logging
import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os
from typing import Dict, List, Optional
import prometheus_client
from prometheus_client import Counter, Gauge, Histogram, Summary
import opentracing
from jaeger_client import Config as JaegerConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, config_file: str = "notification_config.yaml"):
        self.config = self._load_config(config_file)
        self.session = aiohttp.ClientSession()
        self.metrics = self._initialize_metrics()
        self.tracer = self._initialize_tracer()
        
        # Initialize email server
        self.smtp_server = smtplib.SMTP(self.config['smtp']['host'], self.config['smtp']['port'])
        self.smtp_server.starttls()
        self.smtp_server.login(
            self.config['smtp']['username'],
            self.config['smtp']['password']
        )
        
        self.results = {
            'notifications': {},
            'metrics': {},
            'logs': {}
        }

    def _load_config(self, config_file: str) -> Dict:
        """Load notification configuration."""
        with open(config_file) as f:
            return yaml.safe_load(f)

    def _initialize_metrics(self) -> Dict:
        """Initialize Prometheus metrics."""
        metrics = {}
        
        # Notification metrics
        metrics['notification_duration'] = Histogram(
            'notification_duration',
            'Notification sending time',
            ['channel', 'type']
        )
        metrics['notification_success'] = Counter(
            'notification_success',
            'Successful notifications',
            ['channel', 'type']
        )
        metrics['notification_failure'] = Counter(
            'notification_failure',
            'Failed notifications',
            ['channel', 'type']
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
            service_name='orchestratex-notification'
        )
        return config.initialize_tracer()

    async def send_notifications(self, alerts: List[Dict]) -> Dict:
        """Send notifications for all alerts."""
        # Start notification trace
        span = self._start_trace("notifications")
        
        try:
            # Send notifications concurrently
            notification_tasks = [
                self._send_alert(alert)
                for alert in alerts
            ]
            
            notification_results = await asyncio.gather(*notification_tasks)
            
            # Update metrics
            self._calculate_metrics()
            
            return notification_results
            
        except Exception as e:
            logger.error(f"Notification sending failed: {str(e)}")
            self.results['notifications']['status'] = 'failed'
            self.results['notifications']['error'] = str(e)
            raise
            
        finally:
            span.finish()

    async def _send_alert(self, alert: Dict) -> Dict:
        """Send an alert notification to all configured channels."""
        notification_result = {
            'alert': alert,
            'channels': [],
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': None
        }
        
        # Send to all channels concurrently
        channel_tasks = [
            self._send_channel_alert(alert, channel)
            for channel in self.config['channels']
        ]
        
        channel_results = await asyncio.gather(*channel_tasks)
        notification_result['channels'] = channel_results
        
        # Update notification status
        if any(c['status'] == 'failed' for c in channel_results):
            notification_result['status'] = 'failed'
        else:
            notification_result['status'] = 'success'
        
        # Update notification duration
        notification_result['end_time'] = datetime.now().isoformat()
        notification_result['duration'] = (
            datetime.fromisoformat(notification_result['end_time']) -
            datetime.fromisoformat(notification_result['start_time'])
        ).total_seconds()
        
        return notification_result

    async def _send_channel_alert(self, alert: Dict, channel: Dict) -> Dict:
        """Send alert to a specific channel."""
        channel_result = {
            'channel': channel['type'],
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'duration': None,
            'error': None
        }
        
        # Start channel trace
        span = self._start_trace(f"channel_{channel['type']}")
        
        try:
            if channel['type'] == 'slack':
                await self._send_slack_alert(alert, channel)
            elif channel['type'] == 'email':
                await self._send_email_alert(alert, channel)
            elif channel['type'] == 'pagerduty':
                await self._send_pagerduty_alert(alert, channel)
            
            channel_result['status'] = 'success'
            
        except Exception as e:
            channel_result['status'] = 'failed'
            channel_result['error'] = str(e)
            logger.error(f"Failed to send alert to {channel['type']}: {str(e)}")
            
        finally:
            # Update channel duration
            channel_result['end_time'] = datetime.now().isoformat()
            channel_result['duration'] = (
                datetime.fromisoformat(channel_result['end_time']) -
                datetime.fromisoformat(channel_result['start_time'])
            ).total_seconds()
            
            span.finish()
            
        return channel_result

    async def _send_slack_alert(self, alert: Dict, channel: Dict) -> None:
        """Send Slack alert notification."""
        webhook = channel.get('webhook')
        if not webhook:
            raise ValueError("Slack webhook URL not configured")

        payload = {
            "text": f"Audit Alert: {alert['severity']} - {alert['description']}",
            "attachments": [
                {
                    "color": "danger" if alert['severity'] == 'critical' else "warning",
                    "title": alert['description'],
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert['severity'],
                            "short": True
                        },
                        {
                            "title": "Value",
                            "value": str(alert['value']),
                            "short": True
                        },
                        {
                            "title": "Threshold",
                            "value": str(alert['threshold']),
                            "short": True
                        }
                    ]
                }
            ]
        }

        async with self.session.post(webhook, json=payload) as response:
            if response.status != 200:
                raise Exception(f"Failed to send Slack alert: {response.status}")

    async def _send_email_alert(self, alert: Dict, channel: Dict) -> None:
        """Send email alert notification."""
        recipients = channel.get('recipients', [])
        if not recipients:
            raise ValueError("No email recipients configured")

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = self.config['smtp']['from_address']
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"[Orchestratex] Audit Alert - {alert['severity'].upper()}"

        # Create email body
        body = f"""
Audit Alert
===========

Severity: {alert['severity'].upper()}
Description: {alert['description']}
Value: {alert['value']}
Threshold: {alert['threshold']}

Timestamp: {datetime.now().isoformat()}
"""

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        self.smtp_server.send_message(msg)

    async def _send_pagerduty_alert(self, alert: Dict, channel: Dict) -> None:
        """Send PagerDuty alert notification."""
        service_key = channel.get('service_key')
        if not service_key:
            raise ValueError("PagerDuty service key not configured")

        payload = {
            "routing_key": service_key,
            "event_action": "trigger",
            "payload": {
                "summary": f"Audit Alert: {alert['severity']} - {alert['description']}",
                "severity": alert['severity'],
                "source": "orchestratex-audit",
                "custom_details": {
                    "value": alert['value'],
                    "threshold": alert['threshold']
                }
            }
        }

        async with self.session.post(
            "https://events.pagerduty.com/v2/enqueue",
            json=payload
        ) as response:
            if response.status != 202:
                raise Exception(f"Failed to send PagerDuty alert: {response.status}")

    def _calculate_metrics(self) -> None:
        """Calculate notification metrics."""
        # Calculate total notifications
        total_notifications = len(self.results['notifications'])
        
        # Calculate successful notifications
        success_count = sum(
            1 for result in self.results['notifications'].values()
            if result['status'] == 'success'
        )
        
        # Calculate failure rate
        failure_rate = (
            (total_notifications - success_count) / total_notifications
            if total_notifications > 0 else 0.0
        )
        
        self.results['metrics']['total_notifications'] = total_notifications
        self.results['metrics']['success_count'] = success_count
        self.results['metrics']['failure_rate'] = failure_rate

    def _start_trace(self, operation_name: str) -> opentracing.Span:
        """Start a new trace."""
        tracer = opentracing.global_tracer()
        return tracer.start_span(operation_name)

if __name__ == "__main__":
    async def main():
        notification = NotificationService()
        alerts = [
            {
                'severity': 'critical',
                'description': 'High severity findings threshold exceeded',
                'value': 10,
                'threshold': 5
            }
        ]
        results = await notification.send_notifications(alerts)
        print(json.dumps(results, indent=2))

    asyncio.run(main())
