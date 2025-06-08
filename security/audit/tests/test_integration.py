import pytest
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Import services
from ..audit_history import AuditHistory
from ..evidence_manager import EvidenceManager
from ..scheduler.scheduler_service import AuditScheduler
from ..compliance.compliance_checker import ComplianceChecker
from ..remediation.remediation_service import RemediationService

@pytest.fixture
def audit_history(tmp_path):
    """Fixture for AuditHistory."""
    return AuditHistory(str(tmp_path / "audit_history"))

@pytest.fixture
def evidence_manager(tmp_path):
    """Fixture for EvidenceManager."""
    return EvidenceManager(str(tmp_path / "evidence"))

@pytest.fixture
def scheduler(tmp_path):
    """Fixture for AuditScheduler."""
    return AuditScheduler(str(tmp_path / "scheduler"))

@pytest.fixture
def compliance_checker(tmp_path):
    """Fixture for ComplianceChecker."""
    return ComplianceChecker(str(tmp_path / "compliance"))

@pytest.fixture
def remediation_service(tmp_path):
    """Fixture for RemediationService."""
    return RemediationService(str(tmp_path / "remediation"))

async def test_audit_lifecycle(
    audit_history, evidence_manager, scheduler, compliance_checker, remediation_service
):
    """Test complete audit lifecycle."""
    # Create audit configuration
    audit_config = {
        "type": "security",
        "target": "api-server",
        "schedule": {
            "type": "interval",
            "hours": 1
        }
    }
    
    # Add audit job
    audit_id = "test_audit_001"
    assert scheduler.add_audit_job(audit_id, audit_config["schedule"], audit_config["type"])
    
    # Add compliance rules
    rule = {
        "id": "test_rule_001",
        "type": "file_permission",
        "description": "Test rule",
        "severity": "medium",
        "parameters": {
            "path": "/etc/test",
            "mode": "0644"
        }
    }
    assert compliance_checker.add_rule(rule)
    
    # Add remediation
    remediation = {
        "id": "test_remediation_001",
        "type": "security",
        "description": "Test remediation",
        "severity": "medium",
        "steps": [
            {
                "type": "command",
                "command": "touch /etc/test"
            }
        ]
    }
    assert remediation_service.add_remediation(remediation)
    
    # Run audit (mocked)
    with patch.object(
        AuditScheduler, "_run_audit", new_callable=AsyncMock
    ) as mock_run_audit:
        mock_run_audit.return_value = {
            "id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "compliant": False,
            "findings": [
                {
                    "rule_id": "test_rule_001",
                    "severity": "medium",
                    "details": "File not found"
                }
            ]
        }
        
        # Trigger audit
        await scheduler._run_audit(audit_id, audit_config["type"])
        
        # Verify audit was recorded
        audit = audit_history.get_audit_by_id(audit_id)
        assert audit is not None
        assert audit["status"] == "completed"
        
        # Verify evidence was stored
        evidence = evidence_manager.get_evidence_history()
        assert len(evidence) > 0
        
        # Verify remediation was executed
        remediation_result = await remediation_service.execute_remediation(
            "test_remediation_001"
        )
        assert remediation_result["status"] == "success"
        
        # Verify compliance check was updated
        compliance = compliance_checker.check_compliance({
            "name": "api-server",
            "type": "service"
        })
        assert compliance["compliant"] is True

async def test_remediation_failure(
    audit_history, evidence_manager, scheduler, compliance_checker, remediation_service
):
    """Test remediation failure handling."""
    # Add failing remediation
    remediation = {
        "id": "test_remediation_002",
        "type": "security",
        "description": "Test failing remediation",
        "severity": "high",
        "steps": [
            {
                "type": "command",
                "command": "rm -rf /"
            }
        ]
    }
    assert remediation_service.add_remediation(remediation)
    
    # Execute remediation
    result = await remediation_service.execute_remediation("test_remediation_002")
    assert result["status"] == "failed"
    assert result["error"] is not None
    
    # Verify evidence of failure
    evidence = evidence_manager.get_evidence_history()
    assert len(evidence) > 0
    assert evidence[0]["status"] == "error"

async def test_schedule_management(
    audit_history, evidence_manager, scheduler, compliance_checker, remediation_service
):
    """Test schedule management."""
    # Add multiple schedules
    schedules = [
        {
            "type": "interval",
            "hours": 1
        },
        {
            "type": "cron",
            "hour": 2,
            "minute": 0
        }
    ]
    
    for i, schedule in enumerate(schedules):
        audit_id = f"test_audit_{i}"
        assert scheduler.add_audit_job(audit_id, schedule, "security")
        
    # Verify jobs were added
    jobs = scheduler.get_audit_jobs()
    assert len(jobs) == len(schedules)
    
    # Update schedule
    updated_schedule = {
        "type": "interval",
        "minutes": 30
    }
    assert scheduler.update_audit_job("test_audit_0", updated_schedule)
    
    # Remove schedule
    assert scheduler.remove_audit_job("test_audit_0")
    
    # Verify job was removed
    jobs = scheduler.get_audit_jobs()
    assert len(jobs) == len(schedules) - 1

async def test_compliance_rules(
    audit_history, evidence_manager, scheduler, compliance_checker, remediation_service
):
    """Test compliance rule management."""
    # Add multiple rules
    rules = [
        {
            "id": "test_rule_002",
            "type": "network_config",
            "description": "Test network rule",
            "severity": "high",
            "parameters": {
                "interface": "eth0",
                "ports": [80, 443]
            }
        },
        {
            "id": "test_rule_003",
            "type": "security_policy",
            "description": "Test policy rule",
            "severity": "medium",
            "parameters": {
                "requirements": ["MFA required", "2FA enabled"]
            }
        }
    ]
    
    for rule in rules:
        assert compliance_checker.add_rule(rule)
    
    # Verify rules were added
    all_rules = compliance_checker.get_rules()
    assert len(all_rules) == len(rules)
    
    # Update rule
    updated_rule = {
        "severity": "critical",
        "parameters": {
            "ports": [22, 80, 443]
        }
    }
    assert compliance_checker.update_rule("test_rule_002", updated_rule)
    
    # Remove rule
    assert compliance_checker.remove_rule("test_rule_002")
    
    # Verify rule was removed
    all_rules = compliance_checker.get_rules()
    assert len(all_rules) == len(rules) - 1

async def test_evidence_validation(
    audit_history, evidence_manager, scheduler, compliance_checker, remediation_service
):
    """Test evidence validation."""
    # Create evidence
    evidence_id = evidence_manager.store_evidence({
        "type": "security",
        "description": "Test evidence",
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "source": "test"
        }
    })
    
    # Verify evidence was stored
    evidence = evidence_manager.get_evidence_by_id(evidence_id)
    assert evidence is not None
    assert evidence["status"] == "valid"
    
    # Create file evidence
    test_file = Path("test_file.txt")
    test_file.write_text("test content")
    
    file_evidence_id = evidence_manager.store_evidence({
        "type": "file",
        "description": "Test file evidence",
        "path": str(test_file)
    }, str(test_file))
    
    # Verify file evidence is valid
    file_evidence = evidence_manager.get_evidence_by_id(file_evidence_id)
    assert file_evidence is not None
    assert file_evidence["status"] == "valid"
    
    # Modify file and verify evidence becomes invalid
    test_file.write_text("modified content")
    assert not evidence_manager.validate_evidence(file_evidence_id, str(test_file))
    
    # Clean up
    test_file.unlink()
