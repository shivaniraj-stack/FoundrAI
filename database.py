import sqlite3
import hashlib
import os
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_NAME = "foundrai.db"

def get_connection(db_path=DB_NAME):
    """Returns a SQLite connection with dict factory set."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=DB_NAME):
    """Initializes the database schema if tables don't exist."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Create Users table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create Reports table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                startup_name TEXT NOT NULL,
                industry TEXT NOT NULL,
                description TEXT NOT NULL,
                report_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            
            conn.commit()
            
            # Seed default admin account if users table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            if count == 0:
                admin_hash, salt = hash_password("admin123")
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                    ("admin", "admin@example.com", admin_hash, salt)
                )
                conn.commit()
                logger.info("Default admin user created (username: 'admin', password: 'admin123')")
                
            logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e

def hash_password(password, salt=None):
    """Hashes a password using PBKDF2-HMAC-SHA256 from Python standard library."""
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # Number of iterations
    )
    return hashed.hex(), salt

def verify_password(password, stored_hash, salt):
    """Verifies a password against the stored hash and salt."""
    hash_val, _ = hash_password(password, salt)
    return hash_val == stored_hash

def create_user(username, email, password, db_path=DB_NAME):
    """
    Creates a new user.
    Returns (True, user_id) on success.
    Returns (False, error_message) on failure.
    """
    if not username or not email or not password:
        return False, "All fields are required."
    
    username = username.strip().lower()
    email = email.strip().lower()
    
    password_hash, salt = hash_password(password)
    
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                (username, email, password_hash, salt)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return True, user_id
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "username" in err_msg:
            return False, "Username is already taken."
        elif "email" in err_msg:
            return False, "Email address is already registered."
        return False, "User already exists."
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return False, f"An unexpected database error occurred: {e}"

def authenticate_user(username_or_email, password, db_path=DB_NAME):
    """
    Authenticates a user.
    Returns user dict on success, None on failure.
    """
    if not username_or_email or not password:
        return None
        
    username_or_email = username_or_email.strip().lower()
    
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            # Search by username or email
            cursor.execute(
                "SELECT * FROM users WHERE username = ? OR email = ?",
                (username_or_email, username_or_email)
            )
            row = cursor.fetchone()
            
            if row:
                user = dict(row)
                if verify_password(password, user['password_hash'], user['salt']):
                    # Return user details without password hash and salt
                    return {
                        "id": user["id"],
                        "username": user["username"],
                        "email": user["email"],
                        "created_at": user["created_at"]
                    }
            return None
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None

def save_report(user_id, startup_name, industry, description, report_data, db_path=DB_NAME):
    """
    Saves a report to the database.
    report_data must be a dictionary.
    Returns the report_id on success, None on failure.
    """
    try:
        report_json = json.dumps(report_data)
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reports (user_id, startup_name, industry, description, report_json) VALUES (?, ?, ?, ?, ?)",
                (user_id, startup_name, industry, description, report_json)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error saving report: {e}")
        return None

def get_user_reports(user_id, db_path=DB_NAME):
    """
    Retrieves all reports for a specific user.
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, startup_name, industry, description, created_at FROM reports WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching user reports: {e}")
        return []

def get_report_by_id(report_id, db_path=DB_NAME):
    """
    Retrieves a single report by its ID.
    Returns the report dict (with parsed JSON) or None.
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            if row:
                report = dict(row)
                report["report_data"] = json.loads(report["report_json"])
                return report
            return None
    except Exception as e:
        logger.error(f"Error fetching report by ID: {e}")
        return None

def delete_report(report_id, db_path=DB_NAME):
    """
    Deletes a report from the database.
    """
    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error deleting report: {e}")
        return False

# Self-initialization check
if __name__ == "__main__":
    init_db()
