"""
Main Window - Primary application interface with improved design and Category Management
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QStackedWidget, QLabel, QPushButton, QFrame,
                              QScrollArea, QMessageBox, QMenuBar, QStatusBar,
                              QToolBar, QSizePolicy, QSpacerItem)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QIcon, QFont, QAction

from src.ui.modules.pos_module import POSModule
from src.ui.modules.inventory_module import InventoryModule
from src.ui.modules.category_module import CategoryModule
from src.ui.modules.reports_module import ReportsModule
from src.ui.modules.users_module import UsersModule
from src.ui.modules.settings_module import SettingsModule
from src.utils.theme_manager import ThemeManager
from src.database.database_manager import DatabaseManager

class SidebarButton(QPushButton):
    """Custom sidebar button with better styling"""
    
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self.setText(f"{icon_text}  {text}")
        self.setCheckable(True)
        self.setMinimumHeight(60)  # Much taller buttons
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 20px 25px;
                border: none;
                background-color: transparent;
                color: #202124;
                font-size: 16px;
                font-weight: 500;
                border-radius: 8px;
                margin: 2px 10px;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
                color: #1a73e8;
            }
            QPushButton:checked {
                background-color: #e8f0fe;
                color: #1a73e8;
                font-weight: bold;
                border-left: 4px solid #1a73e8;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self, user, db_manager):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.theme_manager = ThemeManager()
        self.current_module = None
        
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_connections()
        
        # Load default module
        self.show_pos_module()
        
    def setup_ui(self):
        """Setup the main user interface with better spacing"""
        self.setWindowTitle(f"LKS POS System - Welcome {self.user['full_name']}")
        self.setMinimumSize(1200, 800)  # Larger minimum size
        self.showMaximized()
        
        # Set main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                color: #202124;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        
        # Create content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #ffffff;
                border: none;
            }
        """)
        
        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack, 1)
        
    def create_sidebar(self):
        """Create the sidebar navigation with better design"""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with better styling
        header_frame = QFrame()
        header_frame.setMinimumHeight(120)  # Taller header
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border: none;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Logo and title
        logo_label = QLabel("🏪 LKS POS System")
        logo_label.setFont(QFont("Arial", 18, QFont.Bold))
        logo_label.setStyleSheet("color: white; margin-bottom: 5px;")
        
        # User info
        user_label = QLabel(f"Welcome, {self.user['full_name']}")
        user_label.setFont(QFont("Arial", 12))
        user_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        
        role_label = QLabel(f"Role: {self.user['role'].title()}")
        role_label.setFont(QFont("Arial", 10))
        role_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(user_label)
        header_layout.addWidget(role_label)
        
        # Navigation section
        nav_frame = QFrame()
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 20, 10, 10)
        nav_layout.setSpacing(5)
        
        nav_label = QLabel("NAVIGATION")
        nav_label.setFont(QFont("Arial", 10, QFont.Bold))
        nav_label.setStyleSheet("color: rgba(255, 255, 255, 0.6); margin-bottom: 10px;")
        nav_layout.addWidget(nav_label)
        
        # Create navigation buttons based on user role
        self.nav_buttons = {}
        
        nav_items = [
            ("pos", "🛒 Point of Sale", self.show_pos_module),
            ("inventory", "📦 Inventory", self.show_inventory_module),
            ("categories", "📁 Categories", self.show_category_module),  # NEW
            ("reports", "📊 Reports", self.show_reports_module),
            ("users", "👥 User Management", self.show_users_module),
            ("settings", "⚙️ Settings", self.show_settings_module),
        ]
        
        for key, text, callback in nav_items:
            button = QPushButton(text)
            button.setFixedHeight(45)
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    text-align: left;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.2);
                }
            """)
            button.clicked.connect(callback)
            nav_layout.addWidget(button)
            self.nav_buttons[key] = button
        
        nav_layout.addStretch()
        
        # Logout button with better styling
        logout_button = QPushButton("🚪 Logout")
        logout_button.setFixedHeight(50)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_button.clicked.connect(self.logout)
        
        # Add to sidebar
        layout.addWidget(header_frame)
        layout.addWidget(nav_frame, 1)
        layout.addWidget(logout_button)
        
        return sidebar
        
    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #ffffff;
                color: #202124;
                border-bottom: 1px solid #dadce0;
                padding: 5px;
            }
            QMenuBar::item {
                padding: 8px 12px;
                margin: 2px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #f1f3f4;
            }
        """)
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_sale_action = QAction("New Sale", self)
        new_sale_action.setShortcut("Ctrl+N")
        new_sale_action.triggered.connect(lambda: self.show_pos_module())
        file_menu.addAction(new_sale_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction("Logout", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        toggle_theme_action = QAction("Toggle Theme", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                color: #5f6368;
                border-top: 1px solid #dadce0;
                padding: 5px;
            }
        """)
        
        # Current user label
        user_label = QLabel(f"Logged in as: {self.user['full_name']} ({self.user['role'].title()})")
        user_label.setStyleSheet("color: #5f6368; font-size: 14px;")
        self.status_bar.addPermanentWidget(user_label)
        
        # Current time
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #5f6368; font-size: 14px;")
        self.status_bar.addPermanentWidget(self.time_label)
        
        # Update time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        
    def setup_connections(self):
        """Setup signal connections"""
        pass
        
    def set_active_nav_button(self, active_key):
        """Set active navigation button style"""
        for key, button in self.nav_buttons.items():
            if key == active_key:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0.2);
                        color: white;
                        border: none;
                        padding: 10px 15px;
                        text-align: left;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: bold;
                        border-left: 4px solid white;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.25);
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: white;
                        border: none;
                        padding: 10px 15px;
                        text-align: left;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.1);
                    }
                    QPushButton:pressed {
                        background-color: rgba(255, 255, 255, 0.2);
                    }
                """)
    
    def show_pos_module(self):
        """Show POS module"""
        if not hasattr(self, 'pos_module'):
            self.pos_module = POSModule(self.user, self.db_manager)
            self.content_stack.addWidget(self.pos_module)
        
        self.content_stack.setCurrentWidget(self.pos_module)
        self.set_active_nav_button('pos')
        self.current_module = 'pos'
        
    def show_inventory_module(self):
        """Show inventory module"""
        if not hasattr(self, 'inventory_module'):
            self.inventory_module = InventoryModule(self.user, self.db_manager)
            self.content_stack.addWidget(self.inventory_module)
        
        self.content_stack.setCurrentWidget(self.inventory_module)
        self.set_active_nav_button('inventory')
        self.current_module = 'inventory'
        
    def show_category_module(self):
        """Show category module"""
        if not hasattr(self, 'category_module'):
            self.category_module = CategoryModule(self.user, self.db_manager)
            self.content_stack.addWidget(self.category_module)
        
        self.content_stack.setCurrentWidget(self.category_module)
        self.set_active_nav_button('categories')
        self.current_module = 'categories'
        
    def show_reports_module(self):
        """Show reports module"""
        if not hasattr(self, 'reports_module'):
            self.reports_module = ReportsModule(self.user, self.db_manager)
            self.content_stack.addWidget(self.reports_module)
        
        self.content_stack.setCurrentWidget(self.reports_module)
        self.set_active_nav_button('reports')
        self.current_module = 'reports'
        
    def show_users_module(self):
        """Show users module"""
        if not hasattr(self, 'users_module'):
            self.users_module = UsersModule(self.user, self.db_manager)
            self.content_stack.addWidget(self.users_module)
        
        self.content_stack.setCurrentWidget(self.users_module)
        self.set_active_nav_button('users')
        self.current_module = 'users'
        
    def show_settings_module(self):
        """Show settings module"""
        if not hasattr(self, 'settings_module'):
            self.settings_module = SettingsModule(self.user, self.db_manager)
            self.content_stack.addWidget(self.settings_module)
        
        self.content_stack.setCurrentWidget(self.settings_module)
        self.set_active_nav_button('settings')
        self.current_module = 'settings'
        
    def update_time(self):
        """Update the time display"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
        
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_theme = self.db_manager.get_setting("theme") or "light"
        new_theme = "dark" if current_theme == "light" else "light"
        
        self.theme_manager.apply_theme(new_theme)
        self.db_manager.update_setting("theme", new_theme)
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About LKS POS System", 
                         "Modern POS System v1.0\n\n"
                         "A comprehensive Point of Sale solution\n"
                         "built with Python and PySide6.\n\n"
                         "Features:\n"
                         "• Point of Sale\n"
                         "• Inventory Management\n"
                         "• Category Management\n"
                         "• Sales Reports\n"
                         "• User Management\n"
                         "• Multi-language Support")
        
    def logout(self):
        """Logout and return to login screen"""
        reply = QMessageBox.question(self, "Logout", 
                                   "Are you sure you want to logout?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Log activity
            self.db_manager.log_activity(self.user['id'], "logout", 
                                       f"User {self.user['username']} logged out")
            
            # Close main window and show login
            from src.ui.login_window import LoginWindow
            self.login_window = LoginWindow(self.db_manager)
            self.login_window.show()
            self.close()
            
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(self, "Exit", 
                                   "Are you sure you want to exit?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Log activity
            self.db_manager.log_activity(self.user['id'], "logout", 
                                       f"User {self.user['username']} closed application")
            event.accept()
        else:
            event.ignore()
