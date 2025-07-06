"""
Tests for Inventory functionality
"""

import pytest

class TestInventoryFunctionality:
    """Test cases for inventory management"""
    
    def test_product_stock_tracking(self, db_manager):
        """Test product stock tracking"""
        # Add a product
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, price, quantity, min_quantity)
            VALUES (?, ?, ?, ?)
        ''', ('Stock Test Product', 5.00, 50, 10))
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Test stock update
        db_manager.update_product_quantity(product_id, -5)  # Sell 5 items
        
        # Verify stock was updated
        product = db_manager.get_product_by_id(product_id)
        assert product['quantity'] == 45
        
        # Test adding stock
        db_manager.update_product_quantity(product_id, 10)  # Add 10 items
        product = db_manager.get_product_by_id(product_id)
        assert product['quantity'] == 55
    
    def test_low_stock_detection(self, db_manager):
        """Test low stock detection"""
        # Add products with different stock levels
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Low stock product
        cursor.execute('''
            INSERT INTO products (name, price, quantity, min_quantity)
            VALUES (?, ?, ?, ?)
        ''', ('Low Stock Product', 5.00, 3, 10))
        
        # Normal stock product
        cursor.execute('''
            INSERT INTO products (name, price, quantity, min_quantity)
            VALUES (?, ?, ?, ?)
        ''', ('Normal Stock Product', 5.00, 50, 10))
        
        # Out of stock product
        cursor.execute('''
            INSERT INTO products (name, price, quantity, min_quantity)
            VALUES (?, ?, ?, ?)
        ''', ('Out of Stock Product', 5.00, 0, 10))
        
        conn.commit()
        conn.close()
        
        # Get all products
        products = db_manager.get_products()
        
        # Count stock levels
        low_stock = [p for p in products if 0 &lt; p['quantity'] &lt;= p['min_quantity']]
        out_of_stock = [p for p in products if p['quantity'] == 0]
        normal_stock = [p for p in products if p['quantity'] > p['min_quantity']]
        
        assert len(low_stock) >= 1
        assert len(out_of_stock) >= 1
        assert len(normal_stock) >= 1
    
    def test_product_search(self, db_manager):
        """Test product search functionality"""
        # Add test products
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (name, barcode, price, quantity)
            VALUES (?, ?, ?, ?)
        ''', ('Apple Juice', '1111111111111', 3.50, 20))
        
        cursor.execute('''
            INSERT INTO products (name, barcode, price, quantity)
            VALUES (?, ?, ?, ?)
        ''', ('Orange Juice', '2222222222222', 3.75, 15))
        
        conn.commit()
        conn.close()
        
        # Search by name
        products = db_manager.get_products(search_term="Apple")
        apple_products = [p for p in products if 'Apple' in p['name']]
        assert len(apple_products) >= 1
        
        # Search by barcode
        products = db_manager.get_products(search_term="2222222222222")
        barcode_products = [p for p in products if '2222222222222' in (p['barcode'] or '')]
        assert len(barcode_products) >= 1
