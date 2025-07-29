# services.py

from __future__ import annotations
import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json # <--- Add this import

# Import database utility functions
from db_utils import fetch_query

# Load environment variables for Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("API_KEY")
MODEL_NAME_FROM_ENV = os.getenv("MODEL_NAME")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in .env. Gemini calls will fail.")

# --- New Function to Get and Format Schema Information ---
def get_schema_info_from_db(output_type: str = "str") -> str:
    """
    Fetches the full content of 'table_metadata' and formats it either
    as a descriptive string (for LLM prompt) or as a JSON string.

    Args:
        output_type (str): Desired output format, "str" (default) or "json".

    Returns:
        str: Formatted schema information.
    """
    # fetch_query returns a tuple: (actual_row_data_list, column_names_list)
    # Unpack the tuple correctly:
    actual_rows_data, _ = fetch_query("SELECT * FROM table_metadata;") # We don't need column_names_list here as row.keys() will be used

    if not actual_rows_data: # Check if the list of actual row data is empty
        if output_type == "json":
            return json.dumps([])  # Return empty JSON array string
        else:  # "str" output
            return ("Default schema information: The system can access general data. "
                    "(Could not fetch schema from 'table_metadata' or it is empty).")

    if output_type == "json":
        # Convert list of sqlite3.Row objects to a list of dicts
        list_of_dicts = [dict(row_item) for row_item in actual_rows_data]
        # Return the data structured as a dictionary, as expected by the consumer functions.
        # This is more efficient as it avoids serialization/deserialization.
        return {"tables": list_of_dicts}
    else:  # "str" output (default)
        schema_parts = []
        # Iterate over actual_rows_data, where each item is an sqlite3.Row object
        for row_index, row_item in enumerate(actual_rows_data):
            row_details = []
            # row_item is an sqlite3.Row object, so row_item.keys() is valid
            for col_name in row_item.keys():
                value = row_item[col_name]
                row_details.append(f"{col_name}: {str(value) if value is not None else 'N/A'}")
            
            if row_details:
                schema_parts.append(f"- Schema Entry {row_index + 1}: {', '.join(row_details)}")
        
        if schema_parts:
            return ("The 'table_metadata' contains the following information which describes the available data structures:\n"
                    + "\n".join(schema_parts))
        else:
            # This case might occur if table_metadata had rows, but they were effectively empty.
            return ("Default schema information: The system can access general data. "
                    "('table_metadata' was found but its content could not be formatted into a descriptive string).")

# --- Existing functions (get_gemini_completion, clarify, process_user_query) ---

def get_gemini_completion(prompt: str, model_name: str | None = None) -> str | None:
    """
    Sends a prompt to the specified Gemini model and returns the text completion.
    """
    current_model_name = model_name if model_name else MODEL_NAME_FROM_ENV

    if not GEMINI_API_KEY:
        print("Gemini API Key not configured. Cannot make API call.")
        return "Error: Gemini API Key not configured."

    if not current_model_name:
        print("Gemini Model name not specified. Cannot make API call.")
        return "Error: Gemini Model name not specified."
        
    try:
        model = genai.GenerativeModel(current_model_name)
        response = model.generate_content(prompt)
        
        if response.parts:
            return response.text
        else:
            print("Warning: Gemini received an empty response or content was blocked.")
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                print(f"Prompt feedback: {response.prompt_feedback}")
                if response.prompt_feedback.block_reason:
                    return f"Blocked: {response.prompt_feedback.block_reason.name}"
            return None
    except Exception as e:
        print(f"An error occurred during Gemini API call: {e}")
        return f"Error during Gemini API call: {str(e)}"

def clarify(user_query: str) -> str:
    """
    Return a clarifying question or statement for the user's first query,
    using schema information from the database (formatted as a string).
    """
    # Use the new function to get schema info as a string for the prompt
    schema_info_string = get_schema_info_from_db(output_type="str")
    # The debug print for schema_info_string is removed here, but you can add it back if needed during development.
    print(schema_info_string)
    prompt = (
        f"Your goal is to guide the user to make their query more precise based on the available data. "
        f"The following information from the 'table_metadata' table describes the available data structures:\n---SCHEMA START---\n{schema_info_string}\n---SCHEMA END---\n\n"
        f"User query: \"{user_query}\"\n\n"
        "Follow up with up to 3 relevant clarifying questions to help narrow down the user's request. "
        "Do not answer the user query directly; just ask questions. "
        "If the user's query is already very clear and seems actionable based on the schema, "
        "you can state your understanding of the query and ask for user confirmation. "
        "Assume the user does not know the exact content of the data, so keep questions high-level. "
        "The idea is to narrow down the user's demand to something that we have available, "
        "without asking for precision that we will not be able to match."
        "Give the user enough context to choose from (including examples and SQL variables), because you have only one chance to ask for precisions."
    )

    completion = get_gemini_completion(prompt)
    
    if completion:
        return completion
    else:
        # Fallback if Gemini call fails or returns no content
        return ("I'm having a bit of trouble formulating a clarification right now. "
                "Could you please try rephrasing your query or try again shortly?")

def process_user_query(
    user_query: str,
    clarification_prompt_from_ai: str,
    user_response_to_clarification: str,
) -> tuple[str, pd.DataFrame | None]:
    """
    Processes the user's full query (initial + clarification response)
    to fetch data from the database and summarize it.
    """
    # For demonstration, let's assume the schema (in JSON) might be useful here
    # or for another LLM call that generates SQL.
    # schema_json_for_sql_generation = get_schema_info_from_db(output_type="json")
    # print(f"Schema in JSON for SQL generation (example): {schema_json_for_sql_generation}") # Debugging

    from llm.generate_sql_select_query import generate_sql_select_query

    print("I am about to go to get_schema_info_from_db function")
    databaseContext = get_schema_info_from_db(output_type="json")
    print("I am about to go to generate_sql_select_query function")
    generated_sql_query = generate_sql_select_query(user_query, clarification_prompt_from_ai, user_response_to_clarification,databaseContext)
    print(f"Generated SQL Query: {generated_sql_query}")  # Debugging output
    # ADD the generate_sql_select_query func here
    # generated_sql_query = "SELECT * FROM table_metadata LIMIT 3;" # Example
    sql_params = None

    # fetch_query now returns (rows, column_names)
    query_results_rows, column_names = fetch_query(generated_sql_query, sql_params)

    response_table: pd.DataFrame | None = None
    table_summary_for_prompt: str

    if query_results_rows: # Check if rows were returned
        # column_names are now directly available from fetch_query
        response_table = pd.DataFrame(query_results_rows, columns=column_names if column_names else []) # Use empty list if column_names is None
        table_summary_for_prompt = f"The query returned a table with {len(query_results_rows)} rows"
        if column_names:
            table_summary_for_prompt += f" and columns: {', '.join(column_names)}."
        else:
            table_summary_for_prompt += "."
    elif column_names is not None and not query_results_rows : # Table exists (has columns) but is empty
        table_summary_for_prompt = f"The query executed successfully and the table has columns: {', '.join(column_names)}, but it returned no data."
        response_table = pd.DataFrame([], columns=column_names) # Create empty DataFrame with columns
    else: # Query failed, returned no rows and no column names (error shown by fetch_query)
        table_summary_for_prompt = "The query did not return any data or schema from the database."

    # >>>>> provide a pandas table "response_table" and a string "table_summary_for_prompt"

    summary_prompt_context = (
        f"Initial user query: '{user_query}'\n"
        f"AI's clarifying question/statement: '{clarification_prompt_from_ai}'\n"
        f"User's response to clarification: '{user_response_to_clarification}'\n"
        f"Database query result summary: {table_summary_for_prompt}\n\n"
        "Based on all the information above, provide a concise, user-friendly text response. "
        "If data was found, start with 'Based on your request, here's what I found:' "
        "and briefly describe the nature of the data in the table. "
        "If no data was found, explain that. Keep the explanation to one or two sentences. "
        "Do not repeat the raw inputs extensively."
    )
    
    text_response = get_gemini_completion(summary_prompt_context)

    if not text_response:
        text_response = "I've processed your request. "
        text_response += "Data is displayed below." if response_table is not None and not response_table.empty else "However, no specific data was found for your criteria."
        
    return text_response, response_table