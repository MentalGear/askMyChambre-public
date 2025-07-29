# script to load CSV files into DuckDB and convert to SQLite; use duckdb's schema inference.

import os
import re
import sqlite3
import duckdb


original = "001_sqlite.db"
query_udpate1 = """UPDATE etat_travaux

SET nature = CASE nature

    WHEN 'PL' THEN 'ProjetDeLoi'

    WHEN 'PPL' THEN 'PropositionDeLoi'

    WHEN 'PRGD' THEN 'ProjetDeReglementGrandDucal'

    WHEN 'PRREG' THEN 'PropositionDeRevisionReglementCHD'

    WHEN 'PRCONS' THEN 'PropositionDeRevisionConstitution'

    WHEN 'DO' THEN 'DebatOrientation'

    WHEN 'RAC' THEN 'RapportsActivites'

    WHEN 'CSI' THEN 'ComptesDuServiceInterieur'

    ELSE nature  -- conserve la valeur actuelle si aucune correspondance

END;
"""

query_udpate2 = """
UPDATE etat_travaux

SET nature = CASE nature

    WHEN 'ProjetDeLoi' THEN 'Projet De Loi'

    WHEN 'PropositionDeLoi' THEN 'Proposition De Loi'

    WHEN 'ProjetDeReglementGrandDucal' THEN 'Projet De Reglement Grand Ducal'

    WHEN 'PropositionDeRevisionReglementCHD' THEN 'Proposition De Revision Reglement CHD'

    WHEN 'PropositionDeRevisionConstitution' THEN 'Proposition De Revision Constitution'

    WHEN 'DebatOrientation' THEN 'Debat Orientation'

    WHEN 'RapportsActivites' THEN 'Rapports Activites'

    WHEN 'ComptesDuServiceInterieur' THEN 'Comptes Du Service Interieur'

    ELSE nature

END;"""



def parse_filename(filename_string):
    """
    remove leading numbers and dashes, replace non-alphanumeric characters by underscores.
    """
    parsed_name = re.sub(r'^\d+-', '', filename_string)
    cleaned_name = re.sub(r'[^a-zA-Z0-9_]', '_', parsed_name)
    return cleaned_name

def load_csv_files_as_separate_tables(csv_folder_path, db_file_path):
    """
    Loads each CSV file from a specified folder into its own separate table
    in a DuckDB database file. The table name will be derived from the CSV filename.

    Args:
        csv_folder_path (str): The path to the folder containing the CSV files.
        db_file_path (str): The path where the DuckDB database file will be created/stored.
    """
    try:
        # Connect to DuckDB. If the file doesn't exist, it will be created.
        con = duckdb.connect(database=db_file_path, read_only=False)

        # Get a list of all CSV files in the specified folder and its subfolders
        csv_files = []
        for root, _, files in os.walk(csv_folder_path):
            for file in files:
                if file.lower().endswith(".csv"):
                    csv_files.append(os.path.join(root, file))

        if not csv_files:
            print(f"No CSV files found in '{csv_folder_path}'.")
            con.close()
            return

        print(f"Found {len(csv_files)} CSV files. Loading them as separate tables...")

        for csv_path in csv_files:
            # Derive a table name from the CSV filename
            # e.g., 'data_2023.csv' -> 'data_2023'
            # e.g., 'subfolder/more_data.csv' -> 'subfolder_more_data' or just 'more_data'
            # Let's use just the base filename without extension for simplicity,
            # replacing non-alphanumeric characters with underscores.
            base_filename = os.path.splitext(os.path.basename(csv_path))[0]
            table_name = parse_filename(base_filename)

            # Ensure table name is valid and unique if there are naming conflicts
            # For simplicity, we'll assume unique base filenames for this example.
            # If filenames can conflict (e.g., 'data.csv' in two different subfolders),
            # you might need a more sophisticated naming strategy (e.g., hash, full path components).
            if not table_name: # Handle case where filename is just an extension or invalid chars
                print(f"Skipping CSV with invalid table name derived from: {csv_path}")
                continue

            # Load each CSV into its own table
            # auto_detect=TRUE is very helpful for inferring schema
            con.execute(f"""
                CREATE OR REPLACE TABLE "{table_name}" AS
                SELECT * FROM read_csv('{csv_path}', auto_detect=TRUE);
            """)
            print(f"  - Loaded '{csv_path}' into table '{table_name}'.")

        print(f"\nSuccessfully loaded all CSV files into '{db_file_path}' as separate tables.")

        # Optional: Verify by listing tables
        print("\nTables created in the database:")
        print(con.execute("SHOW TABLES;").fetchdf())

        # Close the connection
        con.close()

    except Exception as e:
        print(f"what? An error occurred: {e}")


def _convert_duckdb_to_sqlite(duckdb_file, sqlite_file):
    """
    Converts a DuckDB database to a SQLite database by copying all tables.

    Args:
        duckdb_file (str): Path to the existing DuckDB database file.
        sqlite_file (str): Path where the new SQLite database file will be created.
    """
    try:
        con_duck = duckdb.connect(database=duckdb_file)
        con_duck.execute("INSTALL sqlite; LOAD sqlite;")
        con_duck.execute(f"ATTACH '{sqlite_file}' AS new_sqlite_db (TYPE sqlite);")

        duckdb_tables = con_duck.execute("SHOW TABLES;").fetchall()

        for table_name_tuple in duckdb_tables:
            table_name = table_name_tuple[0]
            con_duck.execute(f"CREATE TABLE new_sqlite_db.\"{table_name}\" AS SELECT * FROM \"{table_name}\";")

        con_duck.close()
        print(f"Successfully converted '{duckdb_file}' to '{sqlite_file}'.")

    except Exception as e:
        print(f"An error occurred during the conversion: {e}")


def convert_duckdb_to_sqlite(duckdb_file, sqlite_file):
    """
    Converts a DuckDB database to a SQLite database by copying all tables.

    Args:
        duckdb_file (str): Path to the existing DuckDB database file.
        sqlite_file (str): Path where the new SQLite database file will be created.
    """
    try:
        con_duck = duckdb.connect(database=duckdb_file)
        con_duck.execute("INSTALL sqlite; LOAD sqlite;")
        con_duck.execute(f"ATTACH '{sqlite_file}' AS new_sqlite_db (TYPE sqlite);")
        con_duck.execute(f"ATTACH '{original}' AS original (TYPE sqlite);")
        con_duck.sql("""create or replace table table_metadata as (select * from original.table_metadata)
    """)
        duckdb_tables = con_duck.execute("SHOW TABLES;").fetchall()

        for table_name_tuple in duckdb_tables:
            table_name = table_name_tuple[0]
            con_duck.execute(f"CREATE TABLE new_sqlite_db.\"{table_name}\" AS SELECT * FROM \"{table_name}\";")

        con_duck.close()
        print(f"Successfully converted '{duckdb_file}' to '{sqlite_file}'.")

        with sqlite3.connect(sqlite_file) as con:
            cur = con.cursor()
            cur.execute(query_udpate1)
            cur.execute(query_udpate2)
            con.commit()

    except Exception as e:
        print(f"An error occurred during the conversion: {e}")


if __name__ == "__main__":

    csv_folder_path = "./raw_datasets"  
    db_file_path = "000_duck.db"  
    sqlite_file_path = "001_sqlite.db"

    load_csv_files_as_separate_tables(csv_folder_path, db_file_path)
    convert_duckdb_to_sqlite(db_file_path, sqlite_file_path)
