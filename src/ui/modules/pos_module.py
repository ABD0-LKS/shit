"""
POS Module - Point of Sale interface - FIXED UI
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                              QFrame, QSpinBox, QDoubleSpinBox, QComboBox,
                              QMessageBox, QDialog, QDialogButtonBox, QTextEdit,
                              QGridLayout, QGroupBox, QScrollArea)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap
from datetime import datetime
import uuid

class PaymentDialog(QDialog):
    """Payment processing dialog - CASH ONLY"""
    
    def __init__(self, total_amount, parent=None):
        super().__init__(parent)
        self.total_amount = total_amount
        self.setup_ui()
        
    def setup_ui(self):
        """Setup payment dialog UI"""
        self.setWindowTitle("Process Payment")
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        
        # Total amount
        total_label = QLabel(f"Total Amount: {self.total_amount:.2f} DZD")
        total_label.setFont(QFont("Arial", 16, QFont.Bold))
        total_label.setAlignment(Qt.AlignCenter)
        total_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        
        # Cash payment details
        cash_frame = QFrame()
        cash_layout = QVBoxLayout(cash_frame)
        
        cash_received_label = QLabel("Cash Received:")
        self.cash_received_input = QDoubleSpinBox()
        self.cash_received_input.setRange(0, 99999)
        self.cash_received_input.setValue(self.total_amount)
        self.cash_received_input.setDecimals(2)
        self.cash_received_input.setSuffix(" DZD")
        self.cash_received_input.valueChanged.connect(self.calculate_change)
        
        self.change_label = QLabel("Change: 0.00 DZD")
        self.change_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        cash_layout.addWidget(cash_received_label)
        cash_layout.addWidget(self.cash_received_input)
        cash_layout.addWidget(self.change_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Layout
        layout.addWidget(total_label)
        layout.addWidget(cash_frame)
        layout.addStretch()
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        self.calculate_change()
        
    def calculate_change(self):
        """Calculate change amount"""
        cash_received = self.cash_received_input.value()
        change = cash_received - self.total_amount
        self.change_label.setText(f"Change: {change:.2f} DZD")
            
    def get_payment_info(self):
        """Get payment information"""
        return {
            'method': 'cash',
            'cash_received': self.cash_received_input.value(),
            'change': self.cash_received_input.value() - self.total_amount
        }

class POSModule(QWidget):
    """Point of Sale module - FIXED"""
    
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.cart_items = []
        self.current_product = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Setup POS interface"""
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Left panel - Product search and selection
        left_panel = self.create_left_panel()
        
        # Right panel - Cart and checkout
        right_panel = self.create_right_panel()
        
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
    def create_left_panel(self):
        """Create left panel with product search"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("🛒 Product Selection")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px; background-color: #e9ecef; border-radius: 5px;")
        
        # Search section
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        
        # Barcode input
        barcode_label = QLabel("Barcode:")
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scan or enter barcode")
        self.barcode_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        
        # Search button
        self.search_button = QPushButton("🔍 Search")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        search_layout.addWidget(barcode_label)
        search_layout.addWidget(self.barcode_input, 1)
        search_layout.addWidget(self.search_button)
        
        # Product display
        self.product_info_frame = QFrame()
        self.product_info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        
        product_layout = QVBoxLayout(self.product_info_frame)
        
        self.product_name_label = QLabel("No product selected")
        self.product_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.product_price_label = QLabel("")
        self.product_stock_label = QLabel("")
        
        # Quantity and add to cart
        quantity_frame = QFrame()
        quantity_layout = QHBoxLayout(quantity_frame)
        
        quantity_label = QLabel("Quantity:")
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 999)
        self.quantity_spinbox.setValue(1)
        
        self.add_to_cart_button = QPushButton("➕ Add to Cart")
        self.add_to_cart_button.setEnabled(False)
        self.add_to_cart_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_spinbox)
        quantity_layout.addStretch()
        quantity_layout.addWidget(self.add_to_cart_button)
        
        product_layout.addWidget(self.product_name_label)
        product_layout.addWidget(self.product_price_label)
        product_layout.addWidget(self.product_stock_label)
        product_layout.addWidget(quantity_frame)
        
        # Quick access products - FIXED
        quick_access_label = QLabel("Quick Access")
        quick_access_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Create scroll area for quick products
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: white;
            }
        """)
        
        self.quick_products_widget = QWidget()
        self.quick_products_layout = QGridLayout(self.quick_products_widget)
        scroll_area.setWidget(self.quick_products_widget)
        
        self.load_quick_products()
        
        layout.addWidget(header)
        layout.addWidget(search_frame)
        layout.addWidget(self.product_info_frame)
        layout.addWidget(quick_access_label)
        layout.addWidget(scroll_area)
        layout.addStretch()
        
        return panel
        
    def create_right_panel(self):
        """Create right panel with cart and checkout"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Header
        header = QLabel("🛍️ Shopping Cart")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px; background-color: #e9ecef; border-radius: 5px;")
        
        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Price", "Qty", "Total", "Action"])
        self.cart_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Totals section
        totals_frame = QFrame()
        totals_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 15px;
                margin: 10px 0;
            }
        """)
        
        totals_layout = QVBoxLayout(totals_frame)
        
        self.total_label = QLabel("Total: 0.00 DZD")
        self.total_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.total_label.setStyleSheet("color: #2c3e50; padding: 10px; text-align: center;")
        
        totals_layout.addWidget(self.total_label)
        
        # Action buttons
        buttons_frame = QFrame()
        buttons_layout = QVBoxLayout(buttons_frame)
        
        self.checkout_button = QPushButton("💳 Checkout")
        self.checkout_button.setEnabled(False)
        self.checkout_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        
        self.clear_cart_button = QPushButton("🗑️ Clear Cart")
        self.clear_cart_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        buttons_layout.addWidget(self.checkout_button)
        buttons_layout.addWidget(self.clear_cart_button)
        
        layout.addWidget(header)
        layout.addWidget(self.cart_table, 1)
        layout.addWidget(totals_frame)
        layout.addWidget(buttons_frame)
        
        return panel
        
    def setup_connections(self):
        """Setup signal connections"""
        self.barcode_input.returnPressed.connect(self.search_product)
        self.search_button.clicked.connect(self.search_product)
        self.add_to_cart_button.clicked.connect(self.add_to_cart)
        self.checkout_button.clicked.connect(self.process_checkout)
        self.clear_cart_button.clicked.connect(self.clear_cart)
        
    def load_quick_products(self):
        """Load quick access products - FIXED"""
        # Clear existing buttons
        for i in reversed(range(self.quick_products_layout.count())):
            child = self.quick_products_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get recent products
        products = self.db_manager.get_products()[:8]
        
        if not products:
            no_products_label = QLabel("No products available")
            no_products_label.setAlignment(Qt.AlignCenter)
            no_products_label.setStyleSheet("color: #6c757d; padding: 20px;")
            self.quick_products_layout.addWidget(no_products_label, 0, 0, 1, 2)
            return
        
        row, col = 0, 0
        for product in products:
            button = QPushButton(f"{product['name']}\n{product['price']:.2f} DZD")
            button.setFixedSize(150, 80)
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #dee2e6;
                    border-radius: 5px;
                    font-size: 10px;
                    text-align: center;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border-color: #007bff;
                }
            """)
            button.clicked.connect(lambda checked, p=product: self.quick_select_product(p))
            
            self.quick_products_layout.addWidget(button, row, col)
            col += 1
            if col >= 2:
                col = 0
                row += 1
                
    def search_product(self):
        """Search for product by barcode"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
            
        product = self.db_manager.get_product_by_barcode(barcode)
        
        if product:
            self.display_product(product)
        else:
            QMessageBox.warning(self, "Product Not Found", 
                              f"No product found with barcode: {barcode}")
            self.clear_product_display()
            
    def quick_select_product(self, product):
        """Quick select product from buttons"""
        self.display_product(product)
        self.barcode_input.setText(product.get('barcode', ''))
        
    def display_product(self, product):
        """Display product information"""
        self.current_product = product
        
        self.product_name_label.setText(product['name'])
        self.product_price_label.setText(f"Price: {product['price']:.2f} DZD")
        self.product_stock_label.setText(f"Stock: {product['quantity']} units")
        
        # Set max quantity based on stock
        self.quantity_spinbox.setMaximum(min(product['quantity'], 999))
        self.quantity_spinbox.setValue(1)
        
        # Enable add to cart if stock available
        self.add_to_cart_button.setEnabled(product['quantity'] > 0)
        
        if product['quantity'] <= 0:
            self.product_stock_label.setStyleSheet("color: #dc3545; font-weight: bold;")
            self.product_stock_label.setText("OUT OF STOCK")
        else:
            self.product_stock_label.setStyleSheet("color: #28a745;")
            
    def clear_product_display(self):
        """Clear product display"""
        self.current_product = None
        self.product_name_label.setText("No product selected")
        self.product_price_label.setText("")
        self.product_stock_label.setText("")
        self.add_to_cart_button.setEnabled(False)
        
    def add_to_cart(self):
        """Add product to cart"""
        if not self.current_product:
            return
            
        product = self.current_product
        quantity = self.quantity_spinbox.value()
        
        # Check if product already in cart
        for i, item in enumerate(self.cart_items):
            if item['product_id'] == product['id']:
                # Update quantity
                new_quantity = item['quantity'] + quantity
                if new_quantity <= product['quantity']:
                    self.cart_items[i]['quantity'] = new_quantity
                    self.cart_items[i]['total'] = new_quantity * product['price']
                else:
                    QMessageBox.warning(self, "Insufficient Stock", 
                                      f"Only {product['quantity']} units available")
                    return
                break
        else:
            # Add new item
            cart_item = {
                'product_id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'total': quantity * product['price']
            }
            self.cart_items.append(cart_item)
        
        self.update_cart_display()
        self.clear_product_display()
        self.barcode_input.clear()
        self.barcode_input.setFocus()
        
    def update_cart_display(self):
        """Update cart table display"""
        self.cart_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            # Product name
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            
            # Price
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item['price']:.2f} DZD"))
            
            # Quantity
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))
            
            # Total
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{item['total']:.2f} DZD"))
            
            # Remove button
            remove_button = QPushButton("❌")
            remove_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                }
            """)
            remove_button.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            self.cart_table.setCellWidget(row, 4, remove_button)
        
        # Resize columns
        self.cart_table.resizeColumnsToContents()
        
        # Update totals
        self.update_totals()
        
    def remove_from_cart(self, row):
        """Remove item from cart"""
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self.update_cart_display()
            
    def update_totals(self):
        """Update total calculations"""
        total = sum(item['total'] for item in self.cart_items)
        
        self.total_label.setText(f"Total: {total:.2f} DZD")
        
        # Enable checkout if cart has items
        self.checkout_button.setEnabled(len(self.cart_items) > 0)
        
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items:
            reply = QMessageBox.question(self, "Clear Cart", 
                                       "Are you sure you want to clear all items from the cart?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.cart_items.clear()
                self.update_cart_display()
        
    def process_checkout(self):
        """Process checkout and payment"""
        if not self.cart_items:
            return
            
        # Calculate totals
        total = sum(item['total'] for item in self.cart_items)
        
        # Show payment dialog
        payment_dialog = PaymentDialog(total, self)
        
        if payment_dialog.exec() == QDialog.Accepted:
            payment_info = payment_dialog.get_payment_info()
            
            # Create sale record
            sale_number = f"SALE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            sale_data = {
                'sale_number': sale_number,
                'user_id': self.user['id'],
                'subtotal': total,
                'tax_amount': 0,
                'discount_amount': 0,
                'total_amount': total,
                'payment_method': 'cash'
            }
            
            sale_items = []
            for item in self.cart_items:
                sale_items.append({
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'unit_price': item['price'],
                    'total_price': item['total']
                })
            
            try:
                # Save sale to database
                sale_id = self.db_manager.create_sale(sale_data, sale_items)
                
                # Log activity
                self.db_manager.log_activity(self.user['id'], "sale_completed", 
                                           f"Sale {sale_number} completed for {total:.2f} DZD")
                
                # Show success message
                QMessageBox.information(self, "Sale Completed", 
                                      f"Sale completed successfully!\n"
                                      f"Sale Number: {sale_number}\n"
                                      f"Total: {total:.2f} DZD\n"
                                      f"Payment: Cash")
                
                # Clear cart
                self.cart_items.clear()
                self.update_cart_display()
                
                # Reload quick products to update stock
                self.load_quick_products()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to process sale: {str(e)}")
