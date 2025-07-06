"""
Database Manager - Handles all database operations with bcrypt encryption
"""

import sqlite3
import bcrypt
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def __init__(self, db_path: str = "pos_system.db"):
        self.db_path = db_path
        self.init_database()
        print(f"Database initialized at: {os.path.abspath(self.db_path)}")
    
    def init_database(self):
        """Initialize database connection"""
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def create_tables(self):
        """Create all necessary tables"""
        print("Creating database tables...")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('admin', 'cashier', 'stock_manager')),
                    full_name TEXT NOT NULL,
                    email TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    barcode TEXT UNIQUE,
                    category_id INTEGER,
                    price DECIMAL(10,2) NOT NULL,
                    cost_price DECIMAL(10,2),
                    quantity INTEGER DEFAULT 0,
                    min_quantity INTEGER DEFAULT 5,
                    description TEXT,
                    image_path TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
            # Sales table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_number TEXT UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    customer_name TEXT,
                    subtotal DECIMAL(10,2) NOT NULL,
                    tax_amount DECIMAL(10,2) DEFAULT 0,
                    discount_amount DECIMAL(10,2) DEFAULT 0,
                    total_amount DECIMAL(10,2) NOT NULL,
                    payment_method TEXT CHECK (payment_method IN ('cash', 'card', 'mixed')),
                    payment_status TEXT DEFAULT 'completed',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Sale items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sale_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sale_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total_price DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (sale_id) REFERENCES sales (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Returns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS returns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    return_number TEXT UNIQUE NOT NULL,
                    sale_id INTEGER,
                    user_id INTEGER NOT NULL,
                    reason TEXT,
                    total_amount DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sale_id) REFERENCES sales (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Activity logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("Database tables created successfully!")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise
    
    def create_default_admin(self):
        """Create default admin user if not exists"""
        print("Checking for default admin user...")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                print("Creating default admin user...")
                password_hash = self.hash_password("admin123")
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, full_name, email)
                    VALUES (?, ?, ?, ?, ?)
                ''', ("admin", password_hash, "admin", "System Administrator", "admin@lkspos.com"))
                
                # Insert default categories
                default_categories = [
                    ("Electronics", "Electronic devices and accessories"),
                    ("Clothing", "Apparel and fashion items"),
                    ("Food & Beverages", "Food and drink items"),
                    ("Books", "Books and educational materials"),
                    ("Home & Garden", "Home improvement and garden items")
                ]
                
                cursor.executemany('''
                    INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)
                ''', default_categories)
                
                # Insert default settings
                default_settings = [
                    ("currency", "DZD", "Default currency"),
                    ("language", "en", "Default language"),
                    ("theme", "light", "Default theme"),
                    ("receipt_printer", "", "Receipt printer name"),
                    ("company_name", "LKS POS System", "Company name for receipts"),
                    ("company_address", "123 Main St, Algiers, Algeria", "Company address"),
                    ("company_phone", "+213-XXX-XXX-XXX", "Company phone number"),
                    ("company_email", "info@lkspos.com", "Company email"),
                    ("tax_rate", "0.0", "Tax rate percentage"),
                    ("receipt_footer", "Thank you for your business!", "Receipt footer message")
                ]
                
                cursor.executemany('''
                    INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)
                ''', default_settings)
                
                conn.commit()
                print("Default admin user and data created successfully!")
            else:
                print("Admin user already exists")
                # Check if we need to update the password hash format
                cursor.execute("SELECT password_hash FROM users WHERE username = 'admin'")
                result = cursor.fetchone()
                if result:
                    current_hash = result['password_hash']
                    # Check if it's an old hashlib hash (64 characters) vs bcrypt hash (starts with $2b$)
                    if len(current_hash) == 64 and not current_hash.startswith('$2b$'):
                        print("Updating admin password to bcrypt format...")
                        new_hash = self.hash_password("admin123")
                        cursor.execute("UPDATE users SET password_hash = ? WHERE username = 'admin'", (new_hash,))
                        conn.commit()
                        print("Password updated to bcrypt format!")
            
            conn.close()
            
        except Exception as e:
            print(f"Error creating default admin: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash - supports both bcrypt and legacy hashlib"""
        try:
            # Check if it's a bcrypt hash (starts with $2b$)
            if password_hash.startswith('$2b$'):
                return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            else:
                # Legacy hashlib verification for backward compatibility
                import hashlib
                return hashlib.sha256(password.encode()).hexdigest() == password_hash
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        print(f"Authenticating user: {username}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, password_hash, role, full_name, email, is_active
                FROM users WHERE username = ? AND is_active = 1
            ''', (username,))
            
            user = cursor.fetchone()
            print(f"User found in database: {user is not None}")
            
            if user:
                print(f"Verifying password for user: {user['username']}")
                if self.verify_password(password, user['password_hash']):
                    print("Password verification successful!")
                    
                    # Update last login
                    cursor.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
                    ''', (user['id'],))
                    conn.commit()
                    
                    # Log activity
                    self.log_activity(user['id'], "login", f"User {username} logged in")
                    
                    conn.close()
                    return dict(user)
                else:
                    print("Password verification failed!")
            else:
                print("User not found in database!")
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def log_activity(self, user_id: int, action: str, details: str = "", ip_address: str = ""):
        """Log user activity"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO activity_logs (user_id, action, details, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (user_id, action, details, ip_address))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def get_products(self, search_term: str = "", category_id: int = None) -> List[Dict]:
        """Get products with optional search and category filter"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1
            '''
            params = []
            
            if search_term:
                query += " AND (p.name LIKE ? OR p.barcode LIKE ?)"
                params.extend([f"%{search_term}%", f"%{search_term}%"])
            
            if category_id:
                query += " AND p.category_id = ?"
                params.append(category_id)
            
            query += " ORDER BY p.name"
            
            cursor.execute(query, params)
            products = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return products
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Get product by barcode"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.barcode = ? AND p.is_active = 1
            ''', (barcode,))
            
            product = cursor.fetchone()
            conn.close()
            
            return dict(product) if product else None
        except Exception as e:
            print(f"Error getting product by barcode: {e}")
            return None
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = ? AND p.is_active = 1
            ''', (product_id,))
        
            product = cursor.fetchone()
            conn.close()
        
            return dict(product) if product else None
        except Exception as e:
            print(f"Error getting product by ID: {e}")
            return None
    
    def update_product_quantity(self, product_id: int, quantity_change: int):
        """Update product quantity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE products 
            SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (quantity_change, product_id))
        
        conn.commit()
        conn.close()
    
    def create_sale(self, sale_data: Dict, sale_items: List[Dict]) -> int:
        """Create a new sale with items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert sale
            cursor.execute('''
                INSERT INTO sales (sale_number, user_id, customer_name, subtotal, 
                                 tax_amount, discount_amount, total_amount, payment_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sale_data['sale_number'], sale_data['user_id'], sale_data.get('customer_name', ''),
                sale_data['subtotal'], sale_data['tax_amount'], sale_data['discount_amount'],
                sale_data['total_amount'], sale_data['payment_method']
            ))
            
            sale_id = cursor.lastrowid
            
            # Insert sale items and update inventory
            for item in sale_items:
                cursor.execute('''
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price)
                    VALUES (?, ?, ?, ?, ?)
                ''', (sale_id, item['product_id'], item['quantity'], 
                     item['unit_price'], item['total_price']))
                
                # Update product quantity
                cursor.execute('''
                    UPDATE products SET quantity = quantity - ? WHERE id = ?
                ''', (item['quantity'], item['product_id']))
            
            conn.commit()
            return sale_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_sales_report(self, start_date: str, end_date: str) -> List[Dict]:
        """Get sales report for date range"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.*, u.full_name as cashier_name
                FROM sales s
                JOIN users u ON s.user_id = u.id
                WHERE DATE(s.created_at) BETWEEN ? AND ?
                ORDER BY s.created_at DESC
            ''', (start_date, end_date))
            
            sales = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return sales
        except Exception as e:
            print(f"Error getting sales report: {e}")
            return []
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get setting value by key"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            
            conn.close()
            return result['value'] if result else None
        except Exception as e:
            print(f"Error getting setting: {e}")
            return None
    
    def update_setting(self, key: str, value: str):
        """Update setting value"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating setting: {e}")
    
    # User management methods
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, full_name, email, role, is_active, created_at, last_login
                FROM users ORDER BY created_at DESC
            ''')
            
            users = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def create_user(self, user_data: Dict) -> int:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(user_data['password'])
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, full_name, email, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_data['username'],
                password_hash,
                user_data['full_name'],
                user_data.get('email', ''),
                user_data['role'],
                user_data.get('is_active', True)
            ))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
            
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    def update_user(self, user_id: int, user_data: Dict):
        """Update user information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if 'password' in user_data and user_data['password']:
                password_hash = self.hash_password(user_data['password'])
                cursor.execute('''
                    UPDATE users 
                    SET username=?, full_name=?, email=?, role=?, is_active=?, password_hash=?
                    WHERE id=?
                ''', (
                    user_data['username'],
                    user_data['full_name'],
                    user_data.get('email', ''),
                    user_data['role'],
                    user_data.get('is_active', True),
                    password_hash,
                    user_id
                ))
            else:
                cursor.execute('''
                    UPDATE users 
                    SET username=?, full_name=?, email=?, role=?, is_active=?
                    WHERE id=?
                ''', (
                    user_data['username'],
                    user_data['full_name'],
                    user_data.get('email', ''),
                    user_data['role'],
                    user_data.get('is_active', True),
                    user_id
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating user: {e}")
            raise
    
    def delete_user(self, user_id: int):
        """Deactivate user (soft delete)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            raise

    # Category management methods
    def get_all_categories(self) -> List[Dict]:
        """Get all categories"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.*, COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id AND p.is_active = 1
                GROUP BY c.id, c.name, c.description, c.created_at
                ORDER BY c.name
            ''')
            
            categories = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return categories
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def create_category(self, category_data: Dict) -> int:
        """Create a new category"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            ''', (category_data['name'], category_data.get('description', '')))
            
            category_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return category_id
            
        except Exception as e:
            print(f"Error creating category: {e}")
            raise
    
    def update_category(self, category_id: int, category_data: Dict):
        """Update category information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE categories 
                SET name=?, description=?
                WHERE id=?
            ''', (category_data['name'], category_data.get('description', ''), category_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating category: {e}")
            raise
    
    def delete_category(self, category_id: int):
        """Delete category and handle products"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # First, set products in this category to have no category
            cursor.execute('UPDATE products SET category_id = NULL WHERE category_id = ?', (category_id,))
            
            # Then delete the category
            cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error deleting category: {e}")
            raise
