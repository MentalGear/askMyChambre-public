import type { RowObject } from './getSchemaFromDb'

// Define the signature for the fetchQuery function that will be passed in
export type FetchQueryFunction = (
    query: string,
    params?: unknown[], // Use unknown[] for parameters
    dbName?: string,
    baseUrl?: string, // Add baseUrl to the type definition
    fetchFn?: typeof fetch // Add fetchFn parameter
) => Promise<[RowObject[], string[] | null]>

export const fetchQuery: FetchQueryFunction = async (
    query,
    params = [],
    dbName,
    baseUrl,
    fetchFn = fetch
) => {
    try {
        const url = baseUrl ? `${baseUrl}/api/db-query` : '/api/db-query'
        console.log(`Attempting to fetch from URL: ${url}`) // Debugging line
        const response = await fetchFn(url, {
            // Use fetchFn here
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, params, dbName }), // dbName is currently unused on the server, but passed for consistency
        })
        console.log('Fetch response:', response) // Debugging line

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.error || 'Failed to fetch data from database.')
        }

        const data = await response.json()
        // The backend should return an object with 'rows' and 'columns'
        return [data.rows as RowObject[], data.columns as string[] | null]
    } catch (error) {
        console.error('Error in fetchQueryFn:', error)
        throw error // Re-throw the error to be caught by the caller
    }
}
