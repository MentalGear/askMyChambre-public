# db_utils.py

import streamlit as st
import sqlite3
import os

DEFAULT_DB_NAME = "001_sqlite.db"

@st.cache_resource # Caches the database connection across Streamlit reruns
def get_db_connection(db_name: str = DEFAULT_DB_NAME) -> sqlite3.Connection | None:
    """
    Establishes and returns a cached SQLite database connection.
    Enables foreign key support and sets row_factory for named column access.
    """
    # Construct path relative to the directory of this script (db_utils.py)
    # Assuming db_utils.py, app.py, services.py, and the .db file are in the same root project directory.
    project_root = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(project_root, db_name)

    if not os.path.exists(db_path):
        st.error(f"Database file '{db_name}' not found at '{db_path}'. Please ensure it exists.")
        return None
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Access columns by name
        conn.execute('PRAGMA foreign_keys = ON') # Enforce foreign key constraints
        # st.toast(f"Successfully connected to '{db_name}'", icon="🗄️") # Optional: for first connection
        return conn
    except sqlite3.Error as e:
        st.error(f"SQLite error connecting to database '{db_name}': {e}")
        return None

def fetch_query(query: str, params=None, db_name: str = DEFAULT_DB_NAME) -> list[sqlite3.Row]:
    """
    Executes a SELECT query and returns all rows as a list of sqlite3.Row objects.
    Returns an empty list if the connection fails or the query errors.
    """
    conn = get_db_connection(db_name)
    if conn is None:
        return [], None

    try:
        cursor = conn.cursor() # Use a cursor explicitly
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        # Get column names from cursor.description
        # cursor.description is None if the last operation did not return rows (e.g., an empty table)
        # or was not a SELECT statement.
        column_names = [desc[0] for desc in cursor.description] if cursor.description else None
        return rows, column_names
    except sqlite3.Error as e:
        st.error(f"SQLite query error: {e} (Query: {query[:100]}...)")
        return [], None

def execute_CUD_query(query: str, params=None, db_name: str = DEFAULT_DB_NAME) -> int | bool:
    """
    Executes a CUD (Create, Update, Delete) query.
    Commits on success, rolls back on error.
    Returns the number of rows affected on success, or False on failure.
    """
    conn = get_db_connection(db_name)
    if conn is None:
        return False

    try:
        cursor = conn.execute(query, params or ())
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        st.error(f"SQLite modification error: {e} (Query: {query[:100]}...)")
        try:
            conn.rollback()
        except sqlite3.Error as re:
            st.warning(f"SQLite rollback error: {re}")
        return False