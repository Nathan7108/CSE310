import sqlite3
import hashlib

class Database:
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        # Create users table if it doesn't exist
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) 
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password, email=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (username, password_hash, email))
            
            conn.commit()
            return True, "User registered successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, f"Registration failed: {str(e)}"
        finally:
            conn.close()
    
    def login_user(self, username, password):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, username, email FROM users 
                WHERE username = ? AND password_hash = ?
            ''', (username, password_hash))
            
            user = cursor.fetchone()
            if user:
                return True, f"Login successful! Welcome {user[1]}"
            else:
                return False, "Invalid username or password"
        except Exception as e:
            return False, f"Login failed: {str(e)}"
        finally:
            conn.close()
    
    def get_user_info(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, email, created_at FROM users 
                WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'created_at': user[3]
                }
            return None
        except Exception as e:
            return None
        finally:
            conn.close()
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id, username, email, created_at FROM users ORDER BY created_at DESC')
            return cursor.fetchall()
        except Exception as e:
            return []
        finally:
            conn.close()
    
    def delete_user(self, username):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "User deleted successfully"
            else:
                return False, "User not found"
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
        finally:
            conn.close()
    
    def update_user_email(self, username, new_email):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET email = ? WHERE username = ?', (new_email, username))
            conn.commit()
            if cursor.rowcount > 0:
                return True, "Email updated successfully"
            else:
                return False, "User not found"
        except Exception as e:
            return False, f"Update failed: {str(e)}"
        finally:
            conn.close()
    
    def get_user_count(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]
        except Exception as e:
            return 0
        finally:
            conn.close()
