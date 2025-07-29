from db_utils import *
from services import *

schema_info_string = get_schema_info_from_db(output_type="json")

print(f"Schema information (string format):\n{schema_info_string}\n")