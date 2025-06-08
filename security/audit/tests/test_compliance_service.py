import pytest
import asyncio
import os
import tempfile
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch
from compliance_service import ComplianceService
from audit_tools import AuditTools
from notification_service import NotificationService

@pytest.fixture
def compliance_config():
    return {
        'standards': [
            {
                'name': 'ISO 27001',
                'description': 'Information security management',
                'requirements': [
                    {
                        'name': 'A.5.1.1',
                        'description': 'Information security policies',
                        'category': 'Security policy',
                        'status': 'implemented',
                        'evidence': [
                            {
                                'type': 'document',
                                'path': 'test_policy.pdf'
                            }
                        ]
                    }
                ]
            }
        ],
        'notifications': {
            'enabled': True,
            'channels': [
                {
                    'type': 'slack',
                    'webhook': 'test_webhook'
                }
            ]
        }
    }

@pytest.fixture
def mock_audit_tools():
    audit_tools = AsyncMock(spec=AuditTools)
    audit_tools.run_audits.return_value = {
        'audits': {
            'code': {
                'targets': [
                    {
                        'name': 'test_target',
                        'findings': []
                    }
                ]
            }
        }
    }
    return audit_tools

@pytest.fixture
def mock_notification_service():
    notification_service = AsyncMock(spec=NotificationService)
    notification_service.send_notifications.return_value = []
    return notification_service

@pytest.fixture
def compliance_service(mock_audit_tools, mock_notification_service):
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        json.dump(compliance_config(), f)
        config_path = f.name
        
    service = ComplianceService(config_path)
    service.audit_tools = mock_audit_tools
    service.notification_service = mock_notification_service
    
    yield service
    
    os.unlink(config_path)

@pytest.mark.asyncio
async def test_check_compliance(compliance_service, mock_audit_tools):
    """Test compliance check execution."""
    result = await compliance_service.check_compliance()
    
    assert len(result) == 1
    assert result[0]['standard'] == 'ISO 27001'
    assert result[0]['status'] == 'compliant'
    
    mock_audit_tools.run_audits.assert_called_once()

@pytest.mark.asyncio
async def test_check_requirement(compliance_service):
    """Test requirement check execution."""
    requirement = {
        'name': 'A.5.1.1',
        'description': 'Information security policies',
        'category': 'Security policy',
        'status': 'implemented',
        'evidence': [
            {
                'type': 'document',
                'path': 'test_policy.pdf'
            }
        ]
    }
    
    result = await compliance_service._check_requirement(requirement)
    
    assert result['status'] == 'compliant'
    assert result['name'] == 'A.5.1.1'

@pytest.mark.asyncio
async def test_check_document_evidence(compliance_service):
    """Test document evidence validation."""
    evidence = {
        'type': 'document',
        'path': 'test_policy.pdf',
        'checksum': 'test_checksum'
    }
    
    with tempfile.NamedTemporaryFile('w', delete=False) as f:
        f.write('test content')
        evidence_path = f.name
        
    evidence['path'] = evidence_path
    
    result = await compliance_service._check_document_evidence(evidence)
    
    assert result['status'] == 'valid'
    assert result['type'] == 'document'
    
    os.unlink(evidence_path)

@pytest.mark.asyncio
async def test_check_audit_evidence(compliance_service, mock_audit_tools):
    """Test audit evidence validation."""
    evidence = {
        'type': 'audit',
        'reference': 'test_audit_001'
    }
    
    result = await compliance_service._check_audit_evidence(evidence)
    
    assert result['status'] == 'valid'
    assert result['type'] == 'audit'

@pytest.mark.asyncio
async def test_check_remediations(compliance_service):
    """Test remediation workflow."""
    compliance_results = [
        {
            'standard': 'ISO 27001',
            'requirements': [
                {
                    'name': 'A.5.1.1',
                    'status': 'non_compliant',
                    'remediation': {
                        'steps': [
                            {
                                'type': 'command',
                                'command': 'echo test'
                            }
                        ]
                    }
                }
            ]
        }
    ]
    
    await compliance_service._check_remediations(compliance_results)

@pytest.mark.asyncio
async def test_execute_remediation_step(compliance_service):
    """Test remediation step execution."""
    step = {
        'type': 'command',
        'command': 'echo test'
    }
    
    await compliance_service._execute_remediation_step(step)

@pytest.mark.asyncio
async def test_generate_report(compliance_service):
    """Test compliance report generation."""
    compliance_results = [
        {
            'standard': 'ISO 27001',
            'requirements': [
                {
                    'name': 'A.5.1.1',
                    'status': 'compliant'
                }
            ]
        }
    ]
    
    compliance_service._generate_report(compliance_results)
    
    assert os.path.exists('compliance_report.json')
    os.unlink('compliance_report.json')

@pytest.mark.asyncio
async def test_send_notifications(compliance_service, mock_notification_service):
    """Test notification sending."""
    compliance_results = [
        {
            'standard': 'ISO 27001',
            'requirements': [
                {
                    'name': 'A.5.1.1',
                    'status': 'non_compliant'
                }
            ]
        }
    ]
    
    await compliance_service._send_notifications(compliance_results)
    
    mock_notification_service.send_notifications.assert_called_once()
