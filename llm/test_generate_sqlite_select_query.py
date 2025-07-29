import pytest
from unittest.mock import patch

from . import generate_sql_select_query

@pytest.fixture
def sample_database_context():
    return {
        "tables": [
            {
                "tableName": "customers",
                "columns": [
                    {
                        "name": "id",
                        "desc": "Customer unique identifier",
                        "relatedSchema": []
                    },
                    {
                        "name": "name",
                        "desc": "Customer name",
                        "relatedSchema": []
                    }
                ]
            },
            {
                "tableName": "orders",
                "columns": [
                    {
                        "name": "order_id",
                        "desc": "Order unique identifier",
                        "relatedSchema": []
                    },
                    {
                        "name": "customer_id",
                        "desc": "ID of the customer who placed the order",
                        "relatedSchema": [
                            {
                                "tableName": "customers",
                                "names": ["id"]
                            }
                        ]
                    }
                ]
            }
        ]
    }

def test_mock_generate_sql_select_query(sample_database_context):
    userPrompt = "List all customer names who have placed an order."
    precisionQ = "Do you need high or low priority users"
    userPrecision = "High"
    expected_sql = (
        "SELECT customers.name\n"
        "FROM customers\n"
        "JOIN orders ON customers.id = orders.customer_id;"
    )

    # Mock the Gemini API response
    with patch("generate_sql_select_query.genai.GenerativeModel") as MockModel:
        instance = MockModel.return_value
        instance.generate_content.return_value.text = expected_sql

        sql = generate_sql_select_query(userPrompt, precisionQ, userPrecision, sample_database_context)
        assert sql == expected_sql


def test_generate_sql_select_query(sample_database_context):
    userPrompt = "List all customer names who have placed an order."
    precisionQ = "Do you need high or low priority users"
    userPrecision = "High"
    
    sql = generate_sql_select_query(userPrompt, precisionQ, userPrecision, sample_database_context)

    # Basic checks: SQL should be a SELECT statement and mention both tables
    assert sql.strip().lower().startswith("select")
    assert "customers" in sql.lower()
    assert "orders" in sql.lower()
    assert "join" in sql.lower() or "from customers, orders" in sql.lower()
    assert "name" in sql.lower()