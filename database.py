import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'app.db')

def get_db_connection():
    """Establish and return a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database tables if they do not exist."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        
        # Assessments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                company TEXT,
                job_role TEXT,
                offer_status TEXT,
                joining_date TEXT,
                background_status TEXT,
                resignation_status TEXT,
                safety_score INTEGER,
                risk_level TEXT,
                recommendation TEXT
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                filename TEXT,
                company TEXT,
                analysis TEXT,
                risk_level TEXT
            )
        ''')
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def save_assessment(data):
    """Save a new job transition assessment."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO assessments (
                created_at, company, job_role, offer_status, joining_date,
                background_status, resignation_status, safety_score, risk_level, recommendation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            created_at,
            data.get('new_company', 'N/A'),
            data.get('new_job_title', 'N/A'),
            data.get('offer_received', 'No'),
            data.get('joining_date', 'Not Set'),
            data.get('background_verification', 'Not Started'),
            data.get('resignation_submitted', 'No'),
            data.get('safety_score', 0),
            data.get('risk_level', 'UNKNOWN'),
            data.get('recommendation', '')
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def get_assessments():
    """Retrieve all assessments ordered by newest first."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM assessments ORDER BY id DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def save_document_analysis(filename, company, analysis, risk_level):
    """Save a document analysis result."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO documents (
                created_at, filename, company, analysis, risk_level
            ) VALUES (?, ?, ?, ?, ?)
        ''', (created_at, filename, company, analysis, risk_level))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def get_documents():
    """Retrieve all document analyses."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM documents ORDER BY id DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def create_user(username, password_hash):
    """Create a new user."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Username already exists
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    """Get user by username."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

