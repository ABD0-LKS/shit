"""
Category Management Module - Complete category management system
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                              QFrame, QMessageBox, QDialog, QDialogButtonBox, 
                              QTextEdit, QGridLayout, QGroupBox, QHeaderView,
                              QAbstractItemView, QMenu)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QAction

class CategoryDialog(QDialog):
    """Dialog for adding/editing categories"""
    
    def __init__(self, db_manager, category=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.category = category
        self.is_edit_mode = category is not None
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_category_data()
            
    def setup_ui(self):
        """Setup category dialog UI"""
        title = "Edit Category" if self.is_edit_mode else "Add New Category"
        self.setWindowTitle(title)
        self.setFixedSize(450, 350)
        
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel(title)
        header_label.setFont(QFont("Arial", 16, QFont.Bold))
        header_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        
        # Category information
        info_group = QGroupBox("Category Information")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        info_layout = QGridLayout()
        
        # Name
        name_label = QLabel("Category Name:")
        name_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addWidget(name_label, 0, 0)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter category name")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        info_layout.addWidget(self.name_input, 0, 1)
        
        # Description
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addWidget(desc_label, 1, 0, Qt.AlignTop)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Enter category description (optional)")
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #007bff;
            }
        """)
        info_layout.addWidget(self.description_input, 1, 1)
        
        info_group.setLayout(info_layout)
        
        # Buttons
        button_box = QDialogButtonBox()
        
        save_button = QPushButton("💾 Save Category")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        
        button_box.addButton(save_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)
        
        button_box.accepted.connect(self.save_category)
        button_box.rejected.connect(self.reject)
        
        # Layout
        layout.addWidget(header_label)
        layout.addWidget(info_group)
        layout.addStretch()
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Focus on name input
        self.name_input.setFocus()
        
    def load_category_data(self):
        """Load existing category data for editing"""
        if not self.category:
            return
            
        self.name_input.setText(self.category['name'])
        self.description_input.setPlainText(self.category.get('description', ''))
        
    def save_category(self):
        """Save category to database"""
        # Validate input
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Category name is required.")
            self.name_input.setFocus()
            return
            
        if len(name) < 2:
            QMessageBox.warning(self, "Validation Error", "Category name must be at least 2 characters long.")
            self.name_input.setFocus()
            return
            
        description = self.description_input.toPlainText().strip()
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            if self.is_edit_mode:
                # Check if name already exists (excluding current category)
                cursor.execute('SELECT id FROM categories WHERE name = ? AND id != ?', (name, self.category['id']))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Validation Error", "A category with this name already exists.")
                    conn.close()
                    return
                
                # Update existing category
                cursor.execute('''
                    UPDATE categories 
                    SET name=?, description=?
                    WHERE id=?
                ''', (name, description, self.category['id']))
            else:
                # Check if name already exists
                cursor.execute('SELECT id FROM categories WHERE name = ?', (name,))
                if cursor.fetchone():
                    QMessageBox.warning(self, "Validation Error", "A category with this name already exists.")
                    conn.close()
                    return
                
                # Insert new category
                cursor.execute('''
                    INSERT INTO categories (name, description)
                    VALUES (?, ?)
                ''', (name, description))
            
            conn.commit()
            conn.close()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save category: {str(e)}")

class CategoryModule(QWidget):
    """Category management module"""
    
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.setup_ui()
        self.setup_connections()
        self.load_categories()
        
    def setup_ui(self):
        """Setup category management interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_label = QLabel("📁 Category Management")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        subtitle_label = QLabel("Organize your products with categories")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Action buttons
        self.add_category_button = QPushButton("➕ Add Category")
        self.add_category_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.add_category_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)
        
        # Search section
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        
        search_label = QLabel("🔍 Search Categories:")
        search_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by category name...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #007bff;
            }
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        
        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(5)
        self.categories_table.setHorizontalHeaderLabels([
            "ID", "Category Name", "Description", "Products Count", "Actions"
        ])
        
        # Table styling
        self.categories_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #dee2e6;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #e9ecef;
                padding: 12px;
                border: none;
                font-weight: bold;
                font-size: 14px;
                color: #495057;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #dee2e6;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
            }
        """)
        
        # Configure table
        self.categories_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.categories_table.setAlternatingRowColors(True)
        self.categories_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.categories_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set column widths
        header = self.categories_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Count
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Actions
        
        # Statistics section
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.total_categories_label = QLabel("Total Categories: 0")
        self.total_products_label = QLabel("Total Products: 0")
        self.empty_categories_label = QLabel("Empty Categories: 0")
        
        for label in [self.total_categories_label, self.total_products_label, self.empty_categories_label]:
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setStyleSheet("color: #2c3e50;")
        
        stats_layout.addWidget(self.total_categories_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.total_products_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.empty_categories_label)
        
        # Add to main layout
        layout.addWidget(header_frame)
        layout.addWidget(search_frame)
        layout.addWidget(self.categories_table, 1)
        layout.addWidget(stats_frame)
        
        self.setLayout(layout)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.add_category_button.clicked.connect(self.add_category)
        self.refresh_button.clicked.connect(self.load_categories)
        self.search_input.textChanged.connect(self.filter_categories)
        
    def load_categories(self):
        """Load categories into table"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get categories with product count
            cursor.execute('''
                SELECT c.id, c.name, c.description, c.created_at,
                       COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id AND p.is_active = 1
                GROUP BY c.id, c.name, c.description, c.created_at
                ORDER BY c.name
            ''')
            
            categories = cursor.fetchall()
            conn.close()
            
            self.categories_table.setRowCount(len(categories))
            
            total_products = 0
            empty_categories = 0
            
            for row, category in enumerate(categories):
                # ID
                id_item = QTableWidgetItem(str(category['id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.categories_table.setItem(row, 0, id_item)
                
                # Name
                name_item = QTableWidgetItem(category['name'])
                name_item.setFont(QFont("Arial", 12, QFont.Bold))
                self.categories_table.setItem(row, 1, name_item)
                
                # Description
                desc_text = category['description'] or "No description"
                desc_item = QTableWidgetItem(desc_text)
                if not category['description']:
                    desc_item.setForeground(Qt.gray)
                self.categories_table.setItem(row, 2, desc_item)
                
                # Product count
                count = category['product_count']
                count_item = QTableWidgetItem(str(count))
                count_item.setTextAlignment(Qt.AlignCenter)
                
                if count == 0:
                    count_item.setForeground(Qt.red)
                    empty_categories += 1
                else:
                    count_item.setForeground(Qt.darkGreen)
                
                self.categories_table.setItem(row, 3, count_item)
                total_products += count
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                
                edit_button = QPushButton("✏️ Edit")
                edit_button.setToolTip("Edit Category")
                edit_button.setStyleSheet("""
                    QPushButton {
                        background-color: #007bff;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #0056b3;
                    }
                """)
                edit_button.clicked.connect(lambda checked, c=dict(category): self.edit_category(c))
                
                delete_button = QPushButton("🗑️ Delete")
                delete_button.setToolTip("Delete Category")
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                delete_button.clicked.connect(lambda checked, c=dict(category): self.delete_category(c))
                
                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_layout.addStretch()
                
                self.categories_table.setCellWidget(row, 4, actions_widget)
            
            # Update statistics
            self.total_categories_label.setText(f"Total Categories: {len(categories)}")
            self.total_products_label.setText(f"Total Products: {total_products}")
            self.empty_categories_label.setText(f"Empty Categories: {empty_categories}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load categories: {str(e)}")
            
    def filter_categories(self):
        """Filter categories based on search term"""
        search_term = self.search_input.text().lower()
        
        for row in range(self.categories_table.rowCount()):
            name_item = self.categories_table.item(row, 1)
            desc_item = self.categories_table.item(row, 2)
            
            show_row = False
            if search_term in name_item.text().lower():
                show_row = True
            elif desc_item and search_term in desc_item.text().lower():
                show_row = True
            
            self.categories_table.setRowHidden(row, not show_row)
            
    def show_context_menu(self, position):
        """Show context menu for table"""
        if self.categories_table.itemAt(position) is None:
            return
            
        menu = QMenu(self)
        
        edit_action = QAction("✏️ Edit Category", self)
        delete_action = QAction("🗑️ Delete Category", self)
        refresh_action = QAction("🔄 Refresh", self)
        
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(refresh_action)
        
        # Get selected category
        current_row = self.categories_table.currentRow()
        if current_row >= 0:
            category_id = int(self.categories_table.item(current_row, 0).text())
            category_name = self.categories_table.item(current_row, 1).text()
            category_desc = self.categories_table.item(current_row, 2).text()
            
            category = {
                'id': category_id,
                'name': category_name,
                'description': category_desc if category_desc != "No description" else ""
            }
            
            edit_action.triggered.connect(lambda: self.edit_category(category))
            delete_action.triggered.connect(lambda: self.delete_category(category))
        
        refresh_action.triggered.connect(self.load_categories)
        
        menu.exec(self.categories_table.mapToGlobal(position))
        
    def add_category(self):
        """Add new category"""
        dialog = CategoryDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_categories()
            QMessageBox.information(self, "Success", "Category added successfully!")
            
    def edit_category(self, category):
        """Edit existing category"""
        dialog = CategoryDialog(self.db_manager, category, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_categories()
            QMessageBox.information(self, "Success", "Category updated successfully!")
            
    def delete_category(self, category):
        """Delete category"""
        # Check if category has products
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM products WHERE category_id = ? AND is_active = 1', (category['id'],))
        product_count = cursor.fetchone()[0]
        conn.close()
        
        if product_count > 0:
            reply = QMessageBox.question(self, "Delete Category",
                                       f"Category '{category['name']}' contains {product_count} products.\n"
                                       "Deleting this category will remove the category assignment from these products.\n\n"
                                       "Are you sure you want to continue?",
                                       QMessageBox.Yes | QMessageBox.No)
        else:
            reply = QMessageBox.question(self, "Delete Category",
                                       f"Are you sure you want to delete category '{category['name']}'?\n"
                                       "This action cannot be undone.",
                                       QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                # Remove category assignment from products
                cursor.execute('UPDATE products SET category_id = NULL WHERE category_id = ?', (category['id'],))
                
                # Delete category
                cursor.execute('DELETE FROM categories WHERE id = ?', (category['id'],))
                
                conn.commit()
                conn.close()
                
                self.load_categories()
                QMessageBox.information(self, "Success", "Category deleted successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete category: {str(e)}")
