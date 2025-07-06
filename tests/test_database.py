"""
Tests for Database Manager
"""

import pytest
from database.database_manager import DatabaseManager

class TestDatabaseManager:
    """Test cases for DatabaseManager"""
    
    def test_database_initialization(self, temp_db):
        """Test database initialization"""
        db = DatabaseManager(temp_db)
        db.create_tables()
        
        # Check if database file exists
        import os
        assert os.path.exists(temp_db)
        
        # Check if tables are created
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        expected_tables = ['users', 'categories', 'products', 'sales', 'sale_items', 'returns', 'activity_logs', 'settings']
        for table in expected_tables:
            assert table in tables
    
    def test_password_hashing(self, db_manager):
        """Test password hashing and verification"""
        password = "test123"
        hashed = db_manager.hash_password(password)
        
        assert hashed != password
        assert db_manager.verify_password(password, hashed)
        assert not db_manager.verify_password("wrong", hashed)
    
    def test_create_user(self, db_manager, sample_user):
        """Test user creation"""
        user_id = db_manager.create_user(sample_user)
        assert user_id > 0
        
        users = db_manager.get_all_users()
        assert len(users) >= 2  # admin + test user
        
        # Find our test user
        test_user = next((u for u in users if u['username'] == 'testuser'), None)
        assert test_user is not None
        assert test_user['full_name'] == 'Test User'
    
    def test_authenticate_user(self, db_manager, sample_user):
        """Test user authentication"""
        # Create a test user
        db_manager.create_user(sample_user)
        
        # Test successful authentication
        user = db_manager.authenticate_user("testuser", "testpass123")
        assert user is not None
        assert user['username'] == "testuser"
        assert 'password_hash' not in user
        
        # Test failed authentication
        user = db_manager.authenticate_user("testuser", "wrongpassword")
        assert user is None
    
    def test_admin_user_creation(self, db_manager):
        """Test that admin user is created automatically"""
        users = db_manager.get_all_users()
        admin_users = [u for u in users if u['role'] == 'admin']
        assert len(admin_users) >= 1
        
        admin_user = admin_users[0]
        assert admin_user['username'] == 'admin'
    
    def test_product_operations(self, db_manager):
        """Test product CRUD operations"""
        # Add a product
        product_data = {
            'name': 'Test Product',
            'barcode': '1234567890123',
            'price': 10.99,
            'cost_price': 7.50,
            'quantity': 100,
            'min_quantity': 10,
            'description': 'A test product',
            'category_id': None
        }
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, barcode, price, cost_price, quantity, min_quantity, description, category_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(product_data.values()))
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        assert product_id > 0
        
        # Get products
        products = db_manager.get_products()
        assert len(products) >= 1
        
        # Find our test product
        test_product = next((p for p in products if p['name'] == 'Test Product'), None)
        assert test_product is not None
        assert test_product['price'] == 10.99
        
        # Get product by barcode
        product = db_manager.get_product_by_barcode('1234567890123')
        assert product is not None
        assert product['name'] == 'Test Product'
        
        # Get product by ID
        product = db_manager.get_product_by_id(product_id)
        assert product is not None
        assert product['name'] == 'Test Product'
    
    def test_settings_operations(self, db_manager):
        """Test settings operations"""
        # Update a setting
        db_manager.update_setting("test_key", "test_value")
        
        # Get the setting
        value = db_manager.get_setting("test_key")
        assert value == "test_value"
        
        # Get non-existent setting
        value = db_manager.get_setting("non_existent")
        assert value is None
    
    def test_activity_logging(self, db_manager):
        """Test activity logging"""
        # Create a test user first
        user_data = {
            'username': 'logtest',
            'password': 'test123',
            'full_name': 'Log Test User',
            'role': 'cashier'
        }
        user_id = db_manager.create_user(user_data)
        
        # Log an activity
        db_manager.log_activity(user_id, "test_action", "Test details")
        
        # Verify activity was logged
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM activity_logs WHERE user_id = ? AND action = ?", (user_id, "test_action"))
        log = cursor.fetchone()
        conn.close()
        
        assert log is not None
        assert log['details'] == "Test details"
