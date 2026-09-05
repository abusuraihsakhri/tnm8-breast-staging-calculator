"""
Security-focused tests for tnm8-breast-staging-calculator.
Validates path traversal protection, input sanitization, and PHI guard.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import pytest
from tnm8_breast import calculate_metrics, _validate_input_path
from agents.base import PHIGuard, SecurityException, AuditTrail


class TestPathTraversalProtection:
    """Ensure file path validation prevents directory traversal."""

    def test_rejects_dotdot_path(self):
        with pytest.raises(ValueError, match="path traversal"):
            _validate_input_path("../../../etc/passwd")

    def test_rejects_escaped_relative_path(self):
        with pytest.raises(ValueError, match="path traversal"):
            _validate_input_path("foo/../../../etc/shadow")

    def test_accepts_safe_relative_path(self):
        result = _validate_input_path("data/sample.csv")
        assert os.path.isabs(result)

    def test_accepts_simple_filename(self):
        result = _validate_input_path("sample.csv")
        assert os.path.isabs(result)


class TestInputSanitization:
    """Verify calculate_metrics handles malformed or dangerous inputs."""

    def test_handles_none_values(self):
        res = calculate_metrics(v1=None, v2=5.0)
        assert res["score"] > 0

    def test_handles_empty_string(self):
        res = calculate_metrics(v1="", v2=5.0)
        assert "score" in res

    def test_handles_control_characters(self):
        res = calculate_metrics(v1="12\x00\x01\x02", v2=5.0)
        assert "score" in res

    def test_handles_very_long_string(self):
        res = calculate_metrics(v1="A" * 10000, v2=5.0)
        assert "score" in res

    def test_handles_special_characters(self):
        res = calculate_metrics(v1="<script>alert('xss')</script>", v2=5.0)
        assert "score" in res

    def test_handles_sql_injection_pattern(self):
        res = calculate_metrics(v1="'; DROP TABLE users; --", v2=5.0)
        assert "score" in res

    def test_handles_negative_numbers(self):
        res = calculate_metrics(v1=-10.0, v2=-5.0)
        assert "score" in res

    def test_handles_zero_values(self):
        res = calculate_metrics(v1=0.0, v2=0.0)
        assert res["score"] == 0.0


class TestPHIGuard:
    """Validate PHI detection patterns."""

    def test_detects_mrn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_detects_ssn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_detects_phone(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_detects_email(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Email: patient@example.com")

    def test_detects_dob(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("DOB: 01/15/1985")

    def test_allows_safe_text(self):
        PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")
        PHIGuard.assert_no_phi("Tumor size 2.3 cm, node negative")

    def test_redact_phi(self):
        redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567")
        assert "555-123-4567" not in redacted
        assert "[REDACTED_IDENTIFIER]" in redacted


class TestAuditTrailSecurity:
    """Verify audit trail uses secure defaults."""

    def test_generates_ephemeral_key_without_env(self):
        """Without AUDIT_SECRET_KEY, should use ephemeral random key."""
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            trail = AuditTrail()
        assert len(trail.secret_key) > 0

    def test_uses_provided_key_when_set(self):
        trail = AuditTrail(secret_key="test-key-123")
        assert trail.secret_key == b"test-key-123"

    def test_uses_env_var_when_set(self):
        os.environ["AUDIT_SECRET_KEY"] = "env-key-456"
        try:
            trail = AuditTrail()
            assert trail.secret_key == b"env-key-456"
        finally:
            del os.environ["AUDIT_SECRET_KEY"]

    def test_audit_integrity_verification(self):
        trail = AuditTrail(secret_key="integrity-test-key")
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value1"})
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value2"})
        assert trail.verify_integrity() is True

    def test_audit_tamper_detection(self):
        trail = AuditTrail(secret_key="tamper-test-key")
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value1"})
        trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value2"})
        # Tamper with a log entry
        trail.logs[0]["payload_hash"] = "tampered_hash"
        assert trail.verify_integrity() is False
