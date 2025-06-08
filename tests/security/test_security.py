from orchestratex.security import APIGateway
import sqlalchemy as sa
import pytest
from orchestratex.config import get_settings
import concurrent.futures
from datetime import datetime

class TestSecurity:
    @pytest.fixture
    def api_gateway(self):
        return APIGateway(rate_limit=1000)

    def test_sql_injection(self, api_gateway):
        malicious_query = "'; DROP TABLE users; --"
        response = api_gateway.handle_request({
            "query": malicious_query,
            "user": "attacker"
        })
        assert "ERROR" not in response
        assert "DROP TABLE" not in response

    def test_rate_limiting(self, api_gateway):
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(api_gateway.ping) for _ in range(150)]
        success_count = sum(f.result().status == 200 for f in futures)
        assert 100 <= success_count <= 110

    def test_api_authentication(self, api_gateway):
        # Test with invalid token
        response = api_gateway.authenticate("invalid_token")
        assert response.status_code == 401

        # Test with valid token
        valid_token = get_settings().API_TOKEN
        response = api_gateway.authenticate(valid_token)
        assert response.status_code == 200

    def test_api_authorization(self, api_gateway):
        # Test unauthorized access
        response = api_gateway.authorize("user", "admin_endpoint")
        assert response.status_code == 403

        # Test authorized access
        response = api_gateway.authorize("admin", "admin_endpoint")
        assert response.status_code == 200

    def test_request_validation(self, api_gateway):
        # Test invalid request format
        with pytest.raises(ValueError):
            api_gateway.validate_request({"invalid": "data"})

        # Test valid request
        valid_request = {
            "endpoint": "valid_endpoint",
            "data": {"key": "value"},
            "timestamp": datetime.now().isoformat()
        }
        assert api_gateway.validate_request(valid_request) is True

    def test_response_validation(self, api_gateway):
        # Test invalid response format
        with pytest.raises(ValueError):
            api_gateway.validate_response("invalid_response")

        # Test valid response
        valid_response = {
            "status": "success",
            "data": {"key": "value"},
            "timestamp": datetime.now().isoformat()
        }
        assert api_gateway.validate_response(valid_response) is True

    def test_session_management(self, api_gateway):
        # Test session creation
        session = api_gateway.create_session("user")
        assert session is not None
        assert "session_id" in session

        # Test session validation
        assert api_gateway.validate_session(session["session_id"]) is True

        # Test session expiration
        expired_session = api_gateway.expire_session(session["session_id"])
        assert api_gateway.validate_session(expired_session) is False

    def test_audit_logging(self, api_gateway):
        # Test log creation
        log = api_gateway.create_audit_log(
            user="user",
            action="test_action",
            status="success"
        )
        assert log is not None
        assert "timestamp" in log

        # Test log retrieval
        logs = api_gateway.get_audit_logs("user")
        assert len(logs) > 0

    def test_error_handling(self, api_gateway):
        # Test error response
        error_response = api_gateway.handle_error("test_error")
        assert error_response.status_code == 500
        assert "error" in error_response.json()

        # Test error logging
        api_gateway.log_error("test_error")
        errors = api_gateway.get_errors()
        assert len(errors) > 0

    def test_cache_security(self, api_gateway):
        # Test cache storage
        api_gateway.cache_data("test_key", "test_value")
        assert api_gateway.get_cached_data("test_key") == "test_value"

        # Test cache invalidation
        api_gateway.invalidate_cache("test_key")
        assert api_gateway.get_cached_data("test_key") is None

    def test_database_security(self, api_gateway):
        # Test SQL injection prevention
        with pytest.raises(sa.exc.SQLAlchemyError):
            api_gateway.execute_query("DROP TABLE users")

        # Test parameterized queries
        result = api_gateway.execute_query(
            "SELECT * FROM users WHERE id = :id",
            params={"id": 1}
        )
        assert result is not None

    def test_file_security(self, api_gateway):
        # Test file upload validation
        with pytest.raises(ValueError):
            api_gateway.validate_file("invalid_file.exe")

        # Test file download security
        with pytest.raises(ValueError):
            api_gateway.download_file("../etc/passwd")

    def test_network_security(self, api_gateway):
        # Test IP blocking
        api_gateway.block_ip("127.0.0.1")
        assert api_gateway.is_blocked("127.0.0.1") is True

        # Test rate limiting
        with pytest.raises(ValueError):
            for _ in range(1000):
                api_gateway.ping()

    def test_cors_security(self, api_gateway):
        # Test CORS validation
        assert api_gateway.validate_cors("https://allowed-domain.com") is True
        assert api_gateway.validate_cors("https://malicious-domain.com") is False

    def test_ssl_security(self, api_gateway):
        # Test SSL verification
        assert api_gateway.verify_ssl("https://valid-ssl.com") is True
        assert api_gateway.verify_ssl("https://invalid-ssl.com") is False

    def test_token_security(self, api_gateway):
        # Test token generation
        token = api_gateway.generate_token("user")
        assert token is not None
        assert len(token) > 0

        # Test token validation
        assert api_gateway.validate_token(token) is True

    def test_password_security(self, api_gateway):
        # Test password hashing
        hashed = api_gateway.hash_password("password123")
        assert hashed != "password123"

        # Test password verification
        assert api_gateway.verify_password("password123", hashed) is True

if __name__ == "__main__":
    pytest.main()
