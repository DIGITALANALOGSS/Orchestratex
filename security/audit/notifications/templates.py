import logging
import json
import os
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, Template

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NotificationTemplates:
    def __init__(self, template_dir: str = "/etc/orchestratex/templates"):
        """Initialize notification templates."""
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
    def _get_template_path(self, template_name: str) -> str:
        """Get template file path."""
        return os.path.join(self.template_dir, f"{template_name}.j2")

    def _render_template(self, template_name: str, context: Dict) -> str:
        """Render template with context."""
        try:
            template = self.env.get_template(f"{template_name}.j2")
            return template.render(context)
            
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            raise

    def get_available_templates(self) -> List[str]:
        """Get list of available templates."""
        templates = []
        for file in os.listdir(self.template_dir):
            if file.endswith('.j2'):
                templates.append(file[:-3])
        return templates

    def create_template(self, template_name: str, content: str):
        """Create new template."""
        template_path = self._get_template_path(template_name)
        
        try:
            with open(template_path, 'w') as f:
                f.write(content)
            logger.info(f"Created template: {template_name}")
            
        except Exception as e:
            logger.error(f"Failed to create template {template_name}: {str(e)}")
            raise

    def update_template(self, template_name: str, content: str):
        """Update existing template."""
        template_path = self._get_template_path(template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_name}")
            
        try:
            with open(template_path, 'w') as f:
                f.write(content)
            logger.info(f"Updated template: {template_name}")
            
        except Exception as e:
            logger.error(f"Failed to update template {template_name}: {str(e)}")
            raise

    def delete_template(self, template_name: str):
        """Delete template."""
        template_path = self._get_template_path(template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_name}")
            
        try:
            os.remove(template_path)
            logger.info(f"Deleted template: {template_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete template {template_name}: {str(e)}")
            raise

    def get_template_content(self, template_name: str) -> str:
        """Get template content."""
        template_path = self._get_template_path(template_name)
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_name}")
            
        try:
            with open(template_path, 'r') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to read template {template_name}: {str(e)}")
            raise

    def render_alert_template(self, alert: Dict) -> str:
        """Render alert notification template."""
        context = {
            "alert": alert,
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "severity_color": {
                "critical": "#FF0000",
                "high": "#FFA500",
                "medium": "#FFFF00",
                "low": "#00FF00"
            }
        }
        return self._render_template("alert", context)

    def render_compliance_template(self, compliance: Dict) -> str:
        """Render compliance notification template."""
        context = {
            "compliance": compliance,
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "status_color": {
                "compliant": "#00FF00",
                "non_compliant": "#FF0000",
                "pending": "#FFFF00"
            }
        }
        return self._render_template("compliance", context)

    def render_audit_template(self, audit: Dict) -> str:
        """Render audit notification template."""
        context = {
            "audit": audit,
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "status_color": {
                "passed": "#00FF00",
                "failed": "#FF0000",
                "warning": "#FFFF00"
            }
        }
        return self._render_template("audit", context)

    def render_remediation_template(self, remediation: Dict) -> str:
        """Render remediation notification template."""
        context = {
            "remediation": remediation,
            "timestamp": datetime.now().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "production"),
            "status_color": {
                "success": "#00FF00",
                "failed": "#FF0000",
                "in_progress": "#FFFF00"
            }
        }
        return self._render_template("remediation", context)

if __name__ == "__main__":
    # Example usage
    templates = NotificationTemplates()
    
    # Create templates directory if it doesn't exist
    os.makedirs("/etc/orchestratex/templates", exist_ok=True)
    
    # Create example templates
    templates.create_template("alert", """
        # Alert Notification
        
        {% if alert.severity == 'critical' %}
        <div style="background-color: {{ severity_color[alert.severity] }}; padding: 10px;">
        {% else %}
        <div style="background-color: {{ severity_color[alert.severity] }}; padding: 10px;">
        {% endif %}
            <h2>Alert: {{ alert.title }}</h2>
            <p>Severity: <strong>{{ alert.severity }}</strong></p>
            <p>Description: {{ alert.description }}</p>
            <p>Timestamp: {{ timestamp }}</p>
            <p>Environment: {{ environment }}</p>
        </div>
    """)
    
    templates.create_template("compliance", """
        # Compliance Notification
        
        <div style="background-color: {{ status_color[compliance.status] }}; padding: 10px;">
            <h2>Compliance Status: {{ compliance.standard }}</h2>
            <p>Status: <strong>{{ compliance.status }}</strong></p>
            <p>Score: {{ compliance.score }}%</p>
            <p>Timestamp: {{ timestamp }}</p>
            <p>Environment: {{ environment }}</p>
        </div>
    """)
    
    # Render templates
    alert = {
        "title": "Security Alert",
        "severity": "critical",
        "description": "High severity vulnerability detected"
    }
    
    compliance = {
        "standard": "ISO 27001",
        "status": "compliant",
        "score": 95
    }
    
    print("Alert Template:")
    print(templates.render_alert_template(alert))
    
    print("\nCompliance Template:")
    print(templates.render_compliance_template(compliance))
