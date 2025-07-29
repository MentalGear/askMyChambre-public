import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { fetchQuery } from './fetchQuery'
import type { RowObject } from './getSchemaFromDb' // Assuming RowObject is still needed for types

describe('fetchQuery', () => {
    // Mock the global fetch function
    const mockFetch = vi.fn()

    beforeEach(() => {
        // Mock global fetch
        global.fetch = mockFetch
        // Mock window.location.origin to allow relative URLs in fetch
        Object.defineProperty(global, 'window', {
            value: {
                location: {
                    origin: 'http://localhost:5173', // Or any base URL for testing
                },
            },
            writable: true,
            configurable: true,
        })
    })

    afterEach(() => {
        vi.restoreAllMocks()
    })

    it('should successfully fetch data and return rows and columns', async () => {
        const mockRows: RowObject[] = [
            { id: 1, name: 'Test1', keys: () => ['id', 'name'] },
            { id: 2, name: 'Test2', keys: () => ['id', 'name'] },
        ]
        const mockColumns = ['id', 'name']

        mockFetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ rows: mockRows, columns: mockColumns }),
        })

        const query = 'SELECT * FROM test_table;'
        const params: unknown[] = [] // Explicitly type params
        const [rows, columns] = await fetchQuery(query, params)

        expect(mockFetch).toHaveBeenCalledWith('/api/db-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, params, dbName: undefined }),
        })
        expect(rows).toEqual(mockRows)
        expect(columns).toEqual(mockColumns)
    })

    it('should handle API errors gracefully', async () => {
        const errorMessage = 'Database query failed'
        mockFetch.mockResolvedValueOnce({
            ok: false,
            json: async () => ({ error: errorMessage }),
        })

        const query = 'SELECT * FROM non_existent_table;'
        const params: unknown[] = [] // Explicitly type params
        const [rows, columns] = await fetchQuery(query, params)

        expect(mockFetch).toHaveBeenCalledWith('/api/db-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, params: [], dbName: undefined }),
        })
        expect(rows).toEqual([])
        expect(columns).toBeNull()
        // Optionally, you might check if console.error was called
        // vi.spyOn(console, 'error').mockImplementation(() => {});
        // expect(console.error).toHaveBeenCalled();
    })

    it('should return empty data on network error', async () => {
        mockFetch.mockRejectedValueOnce(new Error('Network down'))

        const query = 'SELECT * FROM some_table;'
        const [rows, columns] = await fetchQuery(query)

        expect(mockFetch).toHaveBeenCalledWith('/api/db-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, params: [], dbName: undefined }),
        })
        expect(rows).toEqual([])
        expect(columns).toBeNull()
    })

    it('should pass dbName if provided', async () => {
        const mockRows: RowObject[] = []
        const mockColumns: string[] = []

        mockFetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ rows: mockRows, columns: mockColumns }),
        })

        const query = 'SELECT * FROM another_table;'
        const dbName = 'another.db'
        await fetchQuery(query, [], dbName)

        expect(mockFetch).toHaveBeenCalledWith('/api/db-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query, params: [], dbName: dbName }),
        })
    })
})

// Integration test to fetch real data (requires SvelteKit dev server running)
describe.skip('fetchQuery (Integration Test)', () => {
    // Re-added .skip
    it('should fetch real data from the API endpoint and log it', async () => {
        // No mocking of fetch here, we want to hit the actual API
        const query = 'SELECT * FROM table_metadata;' // Use a query that should return data if the DB is populated
        const params: unknown[] = []
        const baseUrl = 'http://localhost:5173' // Assuming SvelteKit dev server runs on this port

        const [rows, columns] = await fetchQuery(query, params, undefined, baseUrl)

        console.log('Real fetchQuery Data (rows):', JSON.stringify(rows, null, 2))
        console.log('Real fetchQuery Data (columns):', JSON.stringify(columns, null, 2))

        expect(rows).toBeDefined()
        expect(Array.isArray(rows)).toBe(true)
        // Expect some data if the database is populated, otherwise it will be empty
        // expect(rows.length).toBeGreaterThan(0); // This might fail if table_metadata is empty
        expect(columns).toBeDefined()
        expect(Array.isArray(columns)).toBe(true)
    })
})
