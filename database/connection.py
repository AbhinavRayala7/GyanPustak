import sqlite3
import os
import sys
from config import Config

# Global variable to track active DB type
DB_TYPE = None # Will be 'SQLSERVER' or 'SQLITE'

def get_db_connection():
    global DB_TYPE
    
    # 1. Try connecting to SQL Server first (if pyodbc is installed)
    try:
        import pyodbc
        # Try to connect with a short timeout to prevent hanging if server is absent
        # T-SQL connection string
        conn = pyodbc.connect(Config.SQL_SERVER_CONN, timeout=3)
        DB_TYPE = 'SQLSERVER'
        return conn
    except Exception as e:
        # If pyodbc is missing or SQL Server connection fails, fall back to SQLite
        print(f"[DB Warning] SQL Server connection failed: {e}. Falling back to SQLite.", file=sys.stderr)
        
        # Ensure database folder exists
        db_dir = os.path.dirname(Config.SQLITE_DB_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        # Enable foreign keys for SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        DB_TYPE = 'SQLITE'
        return conn

def execute_query(query, params=(), fetch=True, commit=False):
    """
    Executes a query and handles connection lifecycle.
    Returns:
        For SELECT queries: A list of dicts representing rows.
        For INSERT/UPDATE/DELETE: The number of affected rows (or lastrowid for insert).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # SQLite uses '?' placeholder, SQL Server also uses '?' for parameterized queries,
        # which is perfect because the SQL syntax remains identical!
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            
        if fetch:
            if DB_TYPE == 'SQLSERVER':
                # Convert pyodbc rows to dictionaries
                if cursor.description:
                    columns = [column[0] for column in cursor.description]
                    return [dict(zip(columns, row)) for row in cursor.fetchall()]
                return []
            else:
                # Convert sqlite3 Row objects to dictionaries
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                return []
        else:
            if commit:
                # Return last insert id or affected row count
                return cursor.lastrowid if hasattr(cursor, 'lastrowid') else cursor.rowcount
            return cursor.rowcount
    except Exception as e:
        if commit:
            conn.rollback()
        print(f"[DB Error] Query failed: {query} with params {params}. Error: {e}", file=sys.stderr)
        raise e
    finally:
        cursor.close()
        conn.close()

def init_db():
    """
    Initializes database schema and seed data if SQLite is used and db is empty.
    If SQL Server is used, assumes schema is created or runs it if possible.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if DB_TYPE == 'SQLITE':
            # Check if schema is already created by querying SQLite system tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Users';")
            if not cursor.fetchone():
                print("[DB Info] SQLite database empty. Initializing schema...", file=sys.stdout)
                
                schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
                seed_path = os.path.join(os.path.dirname(__file__), 'seed_data.sql')
                
                if os.path.exists(schema_path):
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        schema_sql = f.read()
                    # SQLite allows executing multiple statements using executescript
                    cursor.executescript(schema_sql)
                    conn.commit()
                    
                if os.path.exists(seed_path):
                    with open(seed_path, 'r', encoding='utf-8') as f:
                        seed_sql = f.read()
                    cursor.executescript(seed_sql)
                    conn.commit()
                    print("[DB Info] SQLite database successfully initialized and seeded.", file=sys.stdout)
        else:
            print("[DB Info] Using Microsoft SQL Server database.", file=sys.stdout)
    except Exception as e:
        print(f"[DB Error] Failed to initialize database: {e}", file=sys.stderr)
    finally:
        cursor.close()
        conn.close()
