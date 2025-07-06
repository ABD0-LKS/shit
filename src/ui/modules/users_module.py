"""
Users Module - Complete user management system
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                              QFrame, QComboBox, QCheckBox, QMessageBox, QDialog, 
                              QDialogButtonBox, QGridLayout, QGroupBox, QHeaderView,
                              QAbstractItemView, QMenu)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QAction
from datetime import datetime

class UserDialog(QDialog):
    """Dialog for adding/editing users"""
    
    def __init__(self, db_manager, user=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = user
        self.is_edit_mode = user is not None
        self.setup_ui()
        
        if self.is_edit_mode:
            self.load_user_data()
            
    def setup_ui(self):
        """Setup user dialog UI"""
        title = "Edit User" if self.is_edit_mode else "Add New User"
        self.setWindowTitle(title)
        self.setFixedSize(500, 600)
        
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
        
        # User information
        info_group = QGroupBox("User Information")
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
        
        # Username
        info_layout.addWidget(QLabel("Username:"), 0, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        info_layout.addWidget(self.username_input, 0, 1)
        
        # Full name
        info_layout.addWidget(QLabel("Full Name:"), 1, 0)
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Enter full name")
        info_layout.addWidget(self.fullname_input, 1, 1)
        
        # Email
        info_layout.addWidget(QLabel("Email:"), 2, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")
        info_layout.addWidget(self.email_input, 2, 1)
        
        # Role
        info_layout.addWidget(QLabel("Role:"), 3, 0)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "cashier", "stock_manager"])
        info_layout.addWidget(self.role_combo, 3, 1)
        
        # Password
        info_layout.addWidget(QLabel("Password:"), 4, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if self.is_edit_mode:
            self.password_input.setPlaceholderText("Leave empty to keep current password")
        else:
            self.password_input.setPlaceholderText("Enter password")
        info_layout.addWidget(self.password_input, 4, 1)
        
        # Confirm password
        info_layout.addWidget(QLabel("Confirm Password:"), 5, 0)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        if self.is_edit_mode:
            self.confirm_password_input.setPlaceholderText("Confirm new password")
        else:
            self.confirm_password_input.setPlaceholderText("Confirm password")
        info_layout.addWidget(self.confirm_password_input, 5, 1)
        
        # Active status
        self.active_checkbox = QCheckBox("User is active")
        self.active_checkbox.setChecked(True)
        info_layout.addWidget(self.active_checkbox, 6, 0, 1, 2)
        
        info_group.setLayout(info_layout)
        
        # Buttons
        button_box = QDialogButtonBox()
        
        save_button = QPushButton("💾 Save User")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
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
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        
        button_box.addButton(save_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)
        
        button_box.accepted.connect(self.save_user)
        button_box.rejected.connect(self.reject)
        
        # Layout
        layout.addWidget(header_label)
        layout.addWidget(info_group)
        layout.addStretch()
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def load_user_data(self):
        """Load existing user data for editing"""
        if not self.user:
            return
            
        self.username_input.setText(self.user['username'])
        self.fullname_input.setText(self.user['full_name'])
        self.email_input.setText(self.user.get('email', ''))
        
        # Set role
        role_index = self.role_combo.findText(self.user['role'])
        if role_index >= 0:
            self.role_combo.setCurrentIndex(role_index)
            
        self.active_checkbox.setChecked(bool(self.user.get('is_active', True)))
        
    def save_user(self):
        """Save user to database"""
        # Validate input
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            return
            
        fullname = self.fullname_input.text().strip()
        if not fullname:
            QMessageBox.warning(self, "Validation Error", "Full name is required.")
            return
            
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Password validation
        if not self.is_edit_mode:
            if not password:
                QMessageBox.warning(self, "Validation Error", "Password is required for new users.")
                return
        
        if password and password != confirm_password:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            return
            
        if password and len(password) < 6:
            QMessageBox.warning(self, "Validation Error", "Password must be at least 6 characters long.")
            return
        
        # Prepare user data
        user_data = {
            'username': username,
            'full_name': fullname,
            'email': self.email_input.text().strip(),
            'role': self.role_combo.currentText(),
            'is_active': self.active_checkbox.isChecked()
        }
        
        if password:
            user_data['password'] = password
        
        try:
            if self.is_edit_mode:
                self.db_manager.update_user(self.user['id'], user_data)
            else:
                self.db_manager.create_user(user_data)
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save user: {str(e)}")

class UsersModule(QWidget):
    """Users management module"""
    
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.setup_ui()
        self.setup_connections()
        self.load_users()
        
    def setup_ui(self):
        """Setup users management interface"""
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
        
        title_label = QLabel("👥 User Management")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        
        subtitle_label = QLabel("Manage system users and permissions")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Action buttons
        self.add_user_button = QPushButton("➕ Add User")
        self.add_user_button.setStyleSheet("""
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
        button_layout.addWidget(self.add_user_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)
        
        # Search and filter section
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        
        # Search
        search_label = QLabel("🔍 Search Users:")
        search_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by username or full name...")
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
        
        # Role filter
        role_label = QLabel("Role:")
        self.role_filter = QComboBox()
        self.role_filter.addItems(["All Roles", "admin", "cashier", "stock_manager"])
        self.role_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        
        # Status filter
        status_label = QLabel("Status:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Users", "Active", "Inactive"])
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(role_label)
        filter_layout.addWidget(self.role_filter)
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_filter)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Username", "Full Name", "Email", "Role", "Status", "Actions"
        ])
        
        # Table styling
        self.users_table.setStyleSheet("""
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
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.users_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set column widths
        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Username
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Full Name
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Role
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
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
        
        self.total_users_label = QLabel("Total Users: 0")
        self.active_users_label = QLabel("Active Users: 0")
        self.admin_users_label = QLabel("Administrators: 0")
        
        for label in [self.total_users_label, self.active_users_label, self.admin_users_label]:
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setStyleSheet("color: #2c3e50;")
        
        stats_layout.addWidget(self.total_users_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.active_users_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.admin_users_label)
        
        # Add to main layout
        layout.addWidget(header_frame)
        layout.addWidget(filter_frame)
        layout.addWidget(self.users_table, 1)
        layout.addWidget(stats_frame)
        
        self.setLayout(layout)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.add_user_button.clicked.connect(self.add_user)
        self.refresh_button.clicked.connect(self.load_users)
        self.search_input.textChanged.connect(self.filter_users)
        self.role_filter.currentTextChanged.connect(self.filter_users)
        self.status_filter.currentTextChanged.connect(self.filter_users)
        
    def load_users(self):
        """Load users into table"""
        try:
            users = self.db_manager.get_all_users()
            
            self.users_table.setRowCount(len(users))
            
            active_count = 0
            admin_count = 0
            
            for row, user in enumerate(users):
                # ID
                id_item = QTableWidgetItem(str(user['id']))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.users_table.setItem(row, 0, id_item)
                
                # Username
                username_item = QTableWidgetItem(user['username'])
                username_item.setFont(QFont("Arial", 12, QFont.Bold))
                self.users_table.setItem(row, 1, username_item)
                
                # Full Name
                self.users_table.setItem(row, 2, QTableWidgetItem(user['full_name']))
                
                # Email
                email = user.get('email', '') or 'Not provided'
                email_item = QTableWidgetItem(email)
                if email == 'Not provided':
                    email_item.setForeground(Qt.gray)
                self.users_table.setItem(row, 3, email_item)
                
                # Role
                role_item = QTableWidgetItem(user['role'].title())
                role_item.setTextAlignment(Qt.AlignCenter)
                
                if user['role'] == 'admin':
                    role_item.setStyleSheet("background-color: #ffeaa7; color: #2d3436;")
                    admin_count += 1
                elif user['role'] == 'cashier':
                    role_item.setStyleSheet("background-color: #a7f3d0; color: #065f46;")
                else:
                    role_item.setStyleSheet("background-color: #bfdbfe; color: #1e40af;")
                
                self.users_table.setItem(row, 4, role_item)
                
                # Status
                status = "Active" if user.get('is_active', True) else "Inactive"
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignCenter)
                
                if status == "Active":
                    status_item.setForeground(Qt.darkGreen)
                    active_count += 1
                else:
                    status_item.setForeground(Qt.red)
                
                self.users_table.setItem(row, 5, status_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 0, 5, 0)
                
                edit_button = QPushButton("✏️ Edit")
                edit_button.setToolTip("Edit User")
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
                edit_button.clicked.connect(lambda checked, u=dict(user): self.edit_user(u))
                
                delete_button = QPushButton("🗑️ Delete")
                delete_button.setToolTip("Delete User")
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
                delete_button.clicked.connect(lambda checked, u=dict(user): self.delete_user(u))
                
                # Disable delete for current user
                if user['id'] == self.user['id']:
                    delete_button.setEnabled(False)
                    delete_button.setToolTip("Cannot delete current user")
                
                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_layout.addStretch()
                
                self.users_table.setCellWidget(row, 6, actions_widget)
            
            # Update statistics
            self.total_users_label.setText(f"Total Users: {len(users)}")
            self.active_users_label.setText(f"Active Users: {active_count}")
            self.admin_users_label.setText(f"Administrators: {admin_count}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
            
    def filter_users(self):
        """Filter users based on search criteria"""
        search_term = self.search_input.text().lower()
        role_filter = self.role_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.users_table.rowCount()):
            show_row = True
            
            # Search filter
            if search_term:
                username = self.users_table.item(row, 1).text().lower()
                fullname = self.users_table.item(row, 2).text().lower()
                if search_term not in username and search_term not in fullname:
                    show_row = False
            
            # Role filter
            if role_filter != "All Roles" and show_row:
                role = self.users_table.item(row, 4).text().lower()
                if role_filter.lower() != role:
                    show_row = False
            
            # Status filter
            if status_filter != "All Users" and show_row:
                status = self.users_table.item(row, 5).text()
                if status_filter != status:
                    show_row = False
            
            self.users_table.setRowHidden(row, not show_row)
            
    def show_context_menu(self, position):
        """Show context menu for table"""
        if self.users_table.itemAt(position) is None:
            return
            
        menu = QMenu(self)
        
        edit_action = QAction("✏️ Edit User", self)
        delete_action = QAction("🗑️ Delete User", self)
        refresh_action = QAction("🔄 Refresh", self)
        
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(refresh_action)
        
        # Get selected user
        current_row = self.users_table.currentRow()
        if current_row >= 0:
            user_id = int(self.users_table.item(current_row, 0).text())
            username = self.users_table.item(current_row, 1).text()
            fullname = self.users_table.item(current_row, 2).text()
            email = self.users_table.item(current_row, 3).text()
            role = self.users_table.item(current_row, 4).text().lower()
            status = self.users_table.item(current_row, 5).text()
            
            user = {
                'id': user_id,
                'username': username,
                'full_name': fullname,
                'email': email if email != "Not provided" else "",
                'role': role,
                'is_active': status == "Active"
            }
            
            edit_action.triggered.connect(lambda: self.edit_user(user))
            delete_action.triggered.connect(lambda: self.delete_user(user))
            
            # Disable delete for current user
            if user_id == self.user['id']:
                delete_action.setEnabled(False)
        
        refresh_action.triggered.connect(self.load_users)
        
        menu.exec(self.users_table.mapToGlobal(position))
        
    def add_user(self):
        """Add new user"""
        dialog = UserDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()
            QMessageBox.information(self, "Success", "User added successfully!")
            
    def edit_user(self, user):
        """Edit existing user"""
        dialog = UserDialog(self.db_manager, user, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()
            QMessageBox.information(self, "Success", "User updated successfully!")
            
    def delete_user(self, user):
        """Delete user"""
        if user['id'] == self.user['id']:
            QMessageBox.warning(self, "Cannot Delete", "You cannot delete your own account.")
            return
        
        reply = QMessageBox.question(self, "Delete User",
                                   f"Are you sure you want to delete user '{user['username']}'?\n"
                                   "This will deactivate the user account.",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.delete_user(user['id'])
                self.load_users()
                QMessageBox.information(self, "Success", "User deleted successfully!")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
