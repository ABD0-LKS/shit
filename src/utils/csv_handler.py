"""
CSV Handler - Import/Export functionality for products and data
"""

import csv
import os
from typing import List, Dict, Optional
from PySide6.QtWidgets import QFileDialog, QMessageBox

class CSVHandler:
    """Handle CSV import/export operations"""
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def get_import_file(self) -> Optional[str]:
        """Get file path for import"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Select CSV file to import",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)"
        )
        return file_path if file_path else None
        
    def get_export_file(self, default_name: str = "export.csv") -> Optional[str]:
        """Get file path for export"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent,
            "Save CSV file",
            default_name,
            "CSV Files (*.csv);;All Files (*)"
        )
        return file_path if file_path else None
        
    def import_products(self, file_path: str) -> List[Dict]:
        """Import products from CSV file"""
        products = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Try to detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Clean and validate data
                        product = self._clean_product_data(row)
                        if product:
                            products.append(product)
                    except Exception as e:
                        print(f"Error processing row {row_num}: {e}")
                        continue
                        
        except Exception as e:
            raise Exception(f"Failed to read CSV file: {str(e)}")
            
        return products
        
    def _clean_product_data(self, row: Dict) -> Optional[Dict]:
        """Clean and validate product data from CSV row"""
        # Map common column names
        name_fields = ['name', 'product_name', 'item_name', 'title']
        price_fields = ['price', 'selling_price', 'sale_price', 'unit_price']
        cost_fields = ['cost', 'cost_price', 'purchase_price']
        quantity_fields = ['quantity', 'stock', 'qty', 'inventory']
        barcode_fields = ['barcode', 'sku', 'code', 'product_code']
        category_fields = ['category', 'category_name', 'type']
        description_fields = ['description', 'desc', 'details']
        
        # Find values using flexible field matching
        name = self._find_field_value(row, name_fields)
        if not name:
            return None  # Name is required
            
        price = self._find_numeric_field(row, price_fields)
        if price is None or price <= 0:
            return None  # Valid price is required
            
        cost_price = self._find_numeric_field(row, cost_fields, default=0)
        quantity = self._find_numeric_field(row, quantity_fields, default=0, is_int=True)
        min_quantity = self._find_numeric_field(row, ['min_quantity', 'minimum', 'reorder_level'], default=5, is_int=True)
        
        barcode = self._find_field_value(row, barcode_fields)
        category = self._find_field_value(row, category_fields)
        description = self._find_field_value(row, description_fields, default="")
        
        return {
            'name': name.strip(),
            'price': float(price),
            'cost_price': float(cost_price),
            'quantity': int(quantity),
            'min_quantity': int(min_quantity),
            'barcode': barcode.strip() if barcode else None,
            'category': category.strip() if category else None,
            'description': description.strip()
        }
        
    def _find_field_value(self, row: Dict, field_names: List[str], default: str = None) -> Optional[str]:
        """Find field value using flexible field name matching"""
        for field in field_names:
            # Try exact match
            if field in row and row[field]:
                return str(row[field]).strip()
            
            # Try case-insensitive match
            for key in row.keys():
                if key.lower() == field.lower() and row[key]:
                    return str(row[key]).strip()
                    
        return default
        
    def _find_numeric_field(self, row: Dict, field_names: List[str], default: float = None, is_int: bool = False) -> Optional[float]:
        """Find numeric field value using flexible field name matching"""
        value_str = self._find_field_value(row, field_names)
        
        if value_str is None:
            return default
            
        try:
            # Clean numeric string
            cleaned = value_str.replace(',', '').replace('$', '').replace('DZD', '').strip()
            value = float(cleaned)
            return int(value) if is_int else value
        except (ValueError, TypeError):
            return default
            
    def export_products(self, products: List[Dict], file_path: str):
        """Export products to CSV file"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'id', 'name', 'barcode', 'category_name', 'price', 
                    'cost_price', 'quantity', 'min_quantity', 'description'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in products:
                    # Prepare row data
                    row = {
                        'id': product.get('id', ''),
                        'name': product.get('name', ''),
                        'barcode': product.get('barcode', ''),
                        'category_name': product.get('category_name', ''),
                        'price': product.get('price', 0),
                        'cost_price': product.get('cost_price', 0),
                        'quantity': product.get('quantity', 0),
                        'min_quantity': product.get('min_quantity', 5),
                        'description': product.get('description', '')
                    }
                    writer.writerow(row)
                    
        except Exception as e:
            raise Exception(f"Failed to write CSV file: {str(e)}")
            
    def export_sales_report(self, sales: List[Dict], file_path: str):
        """Export sales report to CSV file"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'sale_number', 'date', 'cashier_name', 'customer_name',
                    'subtotal', 'tax_amount', 'discount_amount', 'total_amount',
                    'payment_method', 'payment_status'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for sale in sales:
                    row = {
                        'sale_number': sale.get('sale_number', ''),
                        'date': sale.get('created_at', ''),
                        'cashier_name': sale.get('cashier_name', ''),
                        'customer_name': sale.get('customer_name', ''),
                        'subtotal': sale.get('subtotal', 0),
                        'tax_amount': sale.get('tax_amount', 0),
                        'discount_amount': sale.get('discount_amount', 0),
                        'total_amount': sale.get('total_amount', 0),
                        'payment_method': sale.get('payment_method', ''),
                        'payment_status': sale.get('payment_status', '')
                    }
                    writer.writerow(row)
                    
        except Exception as e:
            raise Exception(f"Failed to write sales report: {str(e)}")
            
    def create_sample_products_csv(self, file_path: str):
        """Create a sample products CSV file for import reference"""
        sample_products = [
            {
                'name': 'Sample Product 1',
                'barcode': '1234567890123',
                'category': 'Electronics',
                'price': 99.99,
                'cost_price': 75.00,
                'quantity': 50,
                'min_quantity': 10,
                'description': 'This is a sample product for demonstration'
            },
            {
                'name': 'Sample Product 2',
                'barcode': '2345678901234',
                'category': 'Clothing',
                'price': 29.99,
                'cost_price': 15.00,
                'quantity': 100,
                'min_quantity': 20,
                'description': 'Another sample product'
            }
        ]
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'barcode', 'category', 'price', 'cost_price', 'quantity', 'min_quantity', 'description']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in sample_products:
                    writer.writerow(product)
                    
        except Exception as e:
            raise Exception(f"Failed to create sample CSV: {str(e)}")
