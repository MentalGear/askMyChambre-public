def build_schema_description(databaseContext):
    """
    Builds a human-readable schema description string from a flat list of column dictionaries.
    It works by first grouping the columns by their table name.
    """
    print("I am inside of build_schema_description")
    
    # A dictionary to hold the grouped data. 
    # Keys will be table names, values will be a list of column lines.
    grouped_tables = {}

    # 1. Iterate through the flat list of columns and group them by table name.
    for column_info in databaseContext['tables']:
        # Correctly access the snake_case key from your data
        table_name = column_info.get('table_name')
        col_name = column_info.get('name')
        col_desc = column_info.get('description', 'No description') # Use a default value

        if not table_name or not col_name:
            continue # Skip if essential information is missing

        # If this is the first time we see this table, initialize its list
        if table_name not in grouped_tables:
            grouped_tables[table_name] = []
        
        # Create the formatted line for this specific column
        column_line = f"{col_name} ({col_desc})"
        
        # Add the column line to the correct table's list
        grouped_tables[table_name].append(column_line)

    # 2. Build the final output string from the grouped data.
    schema_lines = []
    for table_name, column_lines in grouped_tables.items():
        # Join the column lines with indentation
        formatted_columns = "\n  ".join(column_lines)
        schema_lines.append(f"Table {table_name}:\n  {formatted_columns}")
    
    return "\n".join(schema_lines)