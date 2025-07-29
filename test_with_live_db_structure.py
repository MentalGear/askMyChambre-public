import pytest
from unittest.mock import patch

# Assuming generate_sql_select_query exists in this path
try:
    from llm.generate_sql_select_query import generate_sql_select_query
except ImportError:
    # Provide a mock or raise an error if the module is truly missing
    # For this fix, we'll assume it exists or needs to be mocked elsewhere
    print("Warning: Could not import generate_sql_select_query. Tests relying on it will fail.")
    # Define a dummy function to allow the test file to load
    def generate_sql_select_query(prompt, schema):
        print(f"Mock generate_sql_select_query called with prompt: {prompt}")
        return "SELECT 'Mock SQL Query';"

from db_utils import *
from services import *

@pytest.fixture(scope="module") # Use module scope if the schema doesn't change during the test run
def live_database_context():
    """Fixture to provide the database schema context."""
    return get_schema_info_from_db(output_type="json")

def test_generate_sql_select_query(live_database_context):
    userPrompt = "List all customer names who have placed an order."
    precisionQ = "Do you need high or low priority users"
    userPrecision = "High"

    sql = generate_sql_select_query(userPrompt,precisionQ,userPrecision, live_database_context)

    # Basic checks: SQL should be a SELECT statement and mention both tables
    assert sql.strip().lower().startswith("select")
    assert "customers" in sql.lower()
    assert "orders" in sql.lower()
    assert "join" in sql.lower() or "from customers, orders" in sql.lower()
    assert "name" in sql.lower()