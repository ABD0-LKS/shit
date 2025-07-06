"""
Tests for POS functionality
"""

import pytest
from datetime import datetime
import uuid

class TestPOSFunctionality:
    """Test cases for Point of Sale functionality"""
    
    def test_create_sale(self, db_manager):
        """Test creating a sale with items"""
        # Create a test user
        user_data = {
            'username': 'cashier_test',
            'password': 'test123',
            'full_name': 'Test Cashier',
            'role': 'cashier'
        }
        user_id = db_manager.create_user(user_data)
        
        # Create a test product
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, price, quantity, barcode)
            VALUES (?, ?, ?, ?)
        ''', ('Test Product', 10.00, 100, '1234567890'))
        product_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Create sale data
        sale_number = f"SALE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        sale_data = {
            'sale_number': sale_number,
            'user_id': user_id,
            'subtotal': 20.00,
            'tax_amount': 0.00,
            'discount_amount': 0.00,
            'total_amount': 20.00,
            'payment_method': 'cash'
        }
        
        sale_items = [{
            'product_id': product_id,
            'quantity': 2,
            'unit_price': 10.00,
            'total_price': 20.00
        }]
        
        # Create the sale
        sale_id = db_manager.create_sale(sale_data, sale_items)
        assert sale_id > 0
        
        # Verify sale was created
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sales WHERE id = ?', (sale_id,))
        sale = cursor.fetchone()
        assert sale is not None
        assert sale['total_amount'] == 20.00
        
        # Verify sale items were created
        cursor.execute('SELECT * FROM sale_items WHERE sale_id = ?', (sale_id,))
        items = cursor.fetchall()
        assert len(items) == 1
        assert items[0]['quantity'] == 2
        
        # Verify inventory was updated
        cursor.execute('SELECT quantity FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        assert product['quantity'] == 98  # 100 - 2
        
        conn.close()
    
    def test_sales_report(self, db_manager):
        """Test sales reporting functionality"""
        # Create test data (user, product, sale)
        user_data = {
            'username': 'report_test',
            'password': 'test123',
            'full_name': 'Report Test User',
            'role': 'cashier'
        }
        user_id = db_manager.create_user(user_data)
        
        # Create sale
        sale_number = f"SALE-TEST-{str(uuid.uuid4())[:8].upper()}"
        sale_data = {
            'sale_number': sale_number,
            'user_id': user_id,
            'subtotal': 15.00,
            'tax_amount': 0.00,
            'discount_amount': 0.00,
            'total_amount': 15.00,
            'payment_method': 'cash'
        }
        
        sale_id = db_manager.create_sale(sale_data, [])
        
        # Get sales report
        today = datetime.now().strftime('%Y-%m-%d')
        sales = db_manager.get_sales_report(today, today)
        
        # Find our test sale
        test_sale = next((s for s in sales if s['sale_number'] == sale_number), None)
        assert test_sale is not None
        assert test_sale['total_amount'] == 15.00
        assert test_sale['cashier_name'] == 'Report Test User'
