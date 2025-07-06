"""
Pytest configuration and fixtures
"""

import pytest
import sys
import os
import tempfile
from unittest.mock import Mock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)

@pytest.fixture
def db_manager(temp_db):
    """Create a database manager with temporary database"""
    from database.database_manager import DatabaseManager
    db = DatabaseManager(temp_db)
    db.create_tables()
    db.create_default_admin()
    return db

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        'username': 'testuser',
        'password': 'testpass123',
        'full_name': 'Test User',
        'email': 'test@example.com',
        'role': 'cashier',
        'is_active': True
    }

@pytest.fixture
def sample_product():
    """Sample product data for testing"""
    return {
        'name': 'Test Product',
        'barcode': '1234567890123',
        'price': 10.99,
        'cost_price': 7.50,
        'quantity': 100,
        'min_quantity': 10,
        'description': 'A test product',
        'category_id': 1
    }

# /** rest of code here **/
