import pytest
from . import build_schema_description

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

def test_build_schema_description(sample_database_context):
    expected = (
        "Table customers:\n"
        "  id (Customer unique identifier)\n"
        "  name (Customer name)\n"
        "Table orders:\n"
        "  order_id (Order unique identifier)\n"
        "  customer_id (ID of the customer who placed the order) [Related: customers.id]"
    )
    result = build_schema_description(sample_database_context)
    assert result == expected

def test_build_schema_description_empty():
    context = {"tables": []}
    assert build_schema_description(context) == ""
