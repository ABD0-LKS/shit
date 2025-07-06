"""
Tests for Authentication
"""

import pytest
from database.database_manager import DatabaseManager

class TestAuthentication:
    """Test cases for authentication functionality"""
    
    def test_password_encryption_with_bcrypt(self, db_manager):
        """Test that passwords are properly encrypted with bcrypt"""
        password = "secure_password_123"
        hashed = db_manager.hash_password(password)
        
        # Check that hash is different from original password
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hashes are long
        assert hashed.startswith('$2b$')  # bcrypt identifier
        
        # Verify password works
        assert db_manager.verify_password(password, hashed)
        assert not db_manager.verify_password("wrong_password", hashed)
    
    def test_user_authentication_flow(self, db_manager):
        """Test complete user authentication flow"""
        # Create user
        user_data = {
            'username': 'authtest',
            'password': 'secure123',
            'full_name': 'Auth Test User',
            'role': 'cashier'
        }
        user_id = db_manager.create_user(user_data)
        assert user_id > 0
        
        # Test successful login
        authenticated_user = db_manager.authenticate_user('authtest', 'secure123')
        assert authenticated_user is not None
        assert authenticated_user['username'] == 'authtest'
        assert authenticated_user['full_name'] == 'Auth Test User'
        assert 'password_hash' not in authenticated_user  # Should not return hash
        
        # Test failed login with wrong password
        failed_auth = db_manager.authenticate_user('authtest', 'wrongpass')
        assert failed_auth is None
        
        # Test failed login with non-existent user
        failed_auth = db_manager.authenticate_user('nonexistent', 'anypass')
        assert failed_auth is None
    
    def test_inactive_user_cannot_login(self, db_manager):
        """Test that inactive users cannot login"""
        # Create and then deactivate user
        user_data = {
            'username': 'inactive_user',
            'password': 'test123',
            'full_name': 'Inactive User',
            'role': 'cashier'
        }
        user_id = db_manager.create_user(user_data)
        db_manager.delete_user(user_id)  # This deactivates the user
        
        # Try to authenticate
        result = db_manager.authenticate_user('inactive_user', 'test123')
        assert result is None
