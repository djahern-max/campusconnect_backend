"""
Unit tests for authentication and security functions
"""
import pytest
from app.core.security import verify_password, get_password_hash, create_access_token


@pytest.mark.unit
class TestPasswordHashing:
    """Test PBKDF2 password hashing"""
    
    def test_password_hash_and_verify(self):
        """Test password hashing matches your implementation"""
        password = "SuperAdmin123!"
        hashed = get_password_hash(password)
        
        # Should be in format: salt$hash
        assert "$" in hashed
        assert len(hashed) > 64
        assert verify_password(password, hashed)
    
    def test_wrong_password_fails(self):
        """Test wrong password fails verification"""
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)
        
        assert not verify_password(wrong_password, hashed)
    
    def test_same_password_different_hashes(self):
        """Test same password generates different salts"""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Different hashes due to random salts
        assert hash1 != hash2
        # But both should verify
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


@pytest.mark.unit
class TestJWTTokens:
    """Test JWT token creation"""
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "admin@campusconnect.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50
    
    def test_create_token_with_different_data(self):
        """Test token creation with different user data"""
        data1 = {"sub": "user1@example.com"}
        data2 = {"sub": "user2@example.com"}
        
        token1 = create_access_token(data1)
        token2 = create_access_token(data2)
        
        assert token1 is not None
        assert token2 is not None
        assert token1 != token2
