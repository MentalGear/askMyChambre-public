// Define a type for a row object, mimicking sqlite3.Row's dictionary-like access
import type { ColumnInfo } from './buildSchemaDescription'
import { fetchQuery } from './fetchQuery' // Import the actual fetchQuery implementation

// Define a type for a row object, mimicking sqlite3.Row's dictionary-like access
export type RowObject = {
    [key: string]: unknown // Use unknown for values to be safer than any
    keys: () => string[] // Method to get column names
}

// Define the signature for the fetchQuery function that will be passed in
export type FetchQueryFunction = (
    query: string,
    params?: unknown[], // Use unknown[] for parameters
    dbName?: string,
    baseUrl?: string // Add baseUrl to the type definition
) => Promise<[RowObject[], string[] | null]>

/**
 * Fetches the full content of 'table_metadata' and formats it either
 * as a descriptive string (for LLM prompt) or as a JSON string.
 *
 * @param outputType Desired output format, "str" (default) or "json".
 * @returns Formatted schema information.
 */
export async function getSchemaFromDb(
    outputType: 'str' | 'json' = 'str',
    fetchFn: typeof fetch = fetch, // Add fetchFn parameter with a default of global fetch
    baseUrl?: string
): Promise<string | { tables: ColumnInfo[] }> {
    // Use ColumnInfo[] for tables
    // Now directly use the imported fetchQuery, passing the fetchFn
    const [actualRowsData] = await fetchQuery(
        'SELECT * FROM table_metadata;',
        [],
        undefined,
        baseUrl,
        fetchFn
    )
    if (!actualRowsData || actualRowsData.length === 0) {
        if (outputType === 'json') {
            return { tables: [] } // Return empty JSON array object
        } else {
            return (
                'Default schema information: The system can access general data. ' +
                "(Could not fetch schema from 'table_metadata' or it is empty)."
            )
        }
    }

    if (outputType === 'json') {
        // Convert list of RowObject to a list of plain objects, casting to ColumnInfo
        const listOfDicts: ColumnInfo[] = actualRowsData.map((rowItem) => {
            // Explicitly create a ColumnInfo object from the rowItem
            return {
                table_name: rowItem['table_name'] as string,
                name: rowItem['name'] as string,
                description: rowItem['description'] as string | undefined,
            }
        })
        return { tables: listOfDicts }
    } else {
        // "str" output (default)
        const schemaParts: string[] = []
        actualRowsData.forEach((rowItem, index) => {
            const rowDetails: string[] = []
            for (const colName of rowItem.keys()) {
                const value = rowItem[colName]
                rowDetails.push(
                    `${colName}: ${value !== null && value !== undefined ? String(value) : 'N/A'}`
                )
            }

            if (rowDetails.length > 0) {
                schemaParts.push(`- Schema Entry ${index + 1}: ${rowDetails.join(', ')}`)
            }
        })

        if (schemaParts.length > 0) {
            return (
                "The 'table_metadata' contains the following information which describes the available data structures:\n" +
                schemaParts.join('\n')
            )
        } else {
            return (
                'Default schema information: The system can access general data. ' +
                "('table_metadata' was found but its content could not be formatted into a descriptive string)."
            )
        }
    }
}
