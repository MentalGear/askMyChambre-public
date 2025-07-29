import os

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
# from . import build_schema_description
from .build_schema_description import build_schema_description
import json

# TODO: write script to pull data from db directly
# import sqlite3

# conn = sqlite3.connect('..001_sqlite.db')
# cursor = conn.cursor()
# cursor.execute("SELECT * FROM my_view")
# for row in cursor.fetchall():
#     print(row)
# conn.close()


API_KEY = os.environ.get('GEMINI_API_KEY')  # Returns None if not set

def generate_sql_select_query(userPrompt,precisionQ, userPrecision, databaseContext):
    """
    Calls Gemini API to generate an SQLite SELECT query based on userPrompt and databaseContext.
    """
    # Prepare schema description for the prompt
    print("I am about to go to build_schema_description")
    dbContext = build_schema_description(databaseContext)

    # Compose the prompt for Gemini
    prompt = f"""
You are an expert in SQL query generation. Generate a valid SQLite SELECT query for the following request.

Database Schema:
{dbContext}

User Query:
\"{userPrompt}\"

Questions to precise user query:
\"{precisionQ}\"

User precision of the Query:
\"{userPrecision}\"

Return only the SQL query without any explanation. Use only the tables and columns provided in the Database Schema.
Always use LOWER(column) = LOWER(value) for text comparisons to ensure case-insensitive behavior in SQLite. 
Return just the PURE QUERY, no markdown formating! 
"""
    
    # Configure Gemini API
    genai.configure(api_key=API_KEY)
    print("I am about to go to gemini")
    model = genai.GenerativeModel("gemini-2.5-pro-preview-06-05")
    response = model.generate_content(prompt)

    return response.text.strip()
