"""
Test file for Security Headers Middleware.
Tests that all required security headers are properly applied.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from middleware.security_headers import SecurityHeadersConfig, CustomSecurityHeadersConfig


class TestSecurityHeaders:
    """Test suite for security headers middleware."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = TestClient(app)
    
    def test_basic_security_headers_present(self):
        """Test that basic security headers are present in responses."""
        response = self.client.get("/")
        
        # Check that all required security headers are present
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
        assert "Content-Security-Policy" in response.headers
        assert "Permissions-Policy" in response.headers
    
    def test_csp_header_format(self):
        """Test that CSP header is properly formatted."""
        response = self.client.get("/")
        csp = response.headers.get("Content-Security-Policy")
        
        assert csp is not None
        assert "default-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "base-uri 'self'" in csp
    
    def test_permissions_policy_present(self):
        """Test that Permissions Policy header is present and formatted correctly."""
        response = self.client.get("/")
        permissions_policy = response.headers.get("Permissions-Policy")
        
        assert permissions_policy is not None
        assert "camera=()" in permissions_policy
        assert "microphone=()" in permissions_policy
        assert "geolocation=()" in permissions_policy
    
    def test_cors_headers_present(self):
        """Test that CORS-related security headers are present."""
        response = self.client.get("/")
        
        assert response.headers.get("Cross-Origin-Embedder-Policy") == "require-corp"
        assert response.headers.get("Cross-Origin-Opener-Policy") == "same-origin"
        assert response.headers.get("Cross-Origin-Resource-Policy") == "cross-origin"
    
    def test_server_header_removed(self):
        """Test that Server header is removed for security."""
        response = self.client.get("/")
        
        # Server header should not be present
        assert "Server" not in response.headers
    
    def test_additional_security_headers(self):
        """Test additional security headers are present."""
        response = self.client.get("/")
        
        assert response.headers.get("X-Permitted-Cross-Domain-Policies") == "none"
    
    @patch('core.config.settings.is_production', True)
    def test_hsts_header_in_production(self):
        """Test that HSTS header is present in production."""
        # This test would need to be run with production settings
        # For now, we'll test the config class directly
        config = SecurityHeadersConfig()
        
        with patch('core.config.settings.is_production', True):
            hsts = config.get_hsts_header()
            assert hsts is not None
            assert "max-age=31536000" in hsts
            assert "includeSubDomains" in hsts
    
    @patch('core.config.settings.is_development', True)
    def test_no_hsts_in_development(self):
        """Test that HSTS header is not present in development."""
        config = SecurityHeadersConfig()
        
        with patch('core.config.settings.is_production', False):
            hsts = config.get_hsts_header()
            assert hsts is None
    
    def test_health_endpoint_has_headers(self):
        """Test that health endpoint also has security headers."""
        response = self.client.get("/health")
        
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert "Content-Security-Policy" in response.headers
    
    def test_custom_config_override(self):
        """Test that custom configuration can override defaults."""
        custom_csp = {"default-src": "'self' example.com"}
        custom_config = CustomSecurityHeadersConfig(
            custom_csp=custom_csp,
            custom_frame_options="SAMEORIGIN"
        )
        
        assert custom_config.csp_directives["default-src"] == "'self' example.com"
        assert custom_config.x_frame_options == "SAMEORIGIN"
    
    def test_development_vs_production_csp(self):
        """Test that CSP is different between development and production."""
        config = SecurityHeadersConfig()
        
        # Test development CSP (more permissive)
        with patch('core.config.settings.is_development', True):
            dev_config = SecurityHeadersConfig()
            dev_csp = dev_config._get_csp_directives()
            assert "'unsafe-inline'" in dev_csp.get("script-src", "")
            assert "localhost:*" in dev_csp.get("script-src", "")
        
        # Test production CSP (more restrictive)
        with patch('core.config.settings.is_development', False):
            prod_config = SecurityHeadersConfig()
            prod_csp = prod_config._get_csp_directives()
            assert "'unsafe-inline'" not in prod_csp.get("script-src", "")
            assert "upgrade-insecure-requests" in prod_csp


class TestSecurityHeadersConfig:
    """Test the SecurityHeadersConfig class."""
    
    def test_default_config_values(self):
        """Test that default configuration values are correct."""
        config = SecurityHeadersConfig()
        
        assert config.x_content_type_options == "nosniff"
        assert config.x_frame_options == "DENY"
        assert config.x_xss_protection == "1; mode=block"
        assert config.hsts_max_age == 31536000
        assert config.hsts_include_subdomains is True
    
    def test_csp_directives_not_empty(self):
        """Test that CSP directives are properly configured."""
        config = SecurityHeadersConfig()
        
        assert len(config.csp_directives) > 0
        assert "default-src" in config.csp_directives
        assert "frame-ancestors" in config.csp_directives
    
    def test_permissions_policy_format(self):
        """Test that permissions policy is properly formatted."""
        config = SecurityHeadersConfig()
        policy = config._get_permissions_policy()
        
        assert "camera=()" in policy
        assert "microphone=()" in policy
        assert ", " in policy  # Check comma separation
    
    def test_custom_config_additional_headers(self):
        """Test custom configuration with additional headers."""
        additional = {"Custom-Header": "custom-value"}
        config = CustomSecurityHeadersConfig(additional_headers=additional)
        
        assert config.get_additional_headers() == additional


if __name__ == "__main__":
    pytest.main([__file__])
