import { describe, it, expect, vi } from 'vitest'
import { getSchemaFromDb, type RowObject } from './getSchemaFromDb' // Corrected import path
import * as fetchQueryModule from './fetchQuery' // Import the module to mock it

describe('getSchemaFromDb', () => {
    // Mock RowObject implementation for testing
    const createMockRow = (data: { [key: string]: unknown }): RowObject => ({
        ...data,
        keys: () => Object.keys(data),
    })

    // Spy on the fetchQuery function from the module
    const fetchQuerySpy = vi.spyOn(fetchQueryModule, 'fetchQuery')

    it('should return formatted string schema when outputType is "str" and data is present', async () => {
        const mockRows: RowObject[] = [
            createMockRow({ table_name: 'users', name: 'id', description: 'User ID' }),
            createMockRow({ table_name: 'users', name: 'name', description: 'User Name' }),
            createMockRow({
                table_name: 'products',
                name: 'product_id',
                description: 'Product ID',
            }),
        ]
        fetchQuerySpy.mockResolvedValueOnce([mockRows, ['table_name', 'name', 'description']])

        const expected = `The 'table_metadata' contains the following information which describes the available data structures:
- Schema Entry 1: table_name: users, name: id, description: User ID
- Schema Entry 2: table_name: users, name: name, description: User Name
- Schema Entry 3: table_name: products, name: product_id, description: Product ID`

        const result = await getSchemaFromDb('str')
        expect(result).toBe(expected)
        expect(fetchQuerySpy).toHaveBeenCalledWith('SELECT * FROM table_metadata;')
    })

    it('should return JSON schema when outputType is "json" and data is present', async () => {
        const mockRows: RowObject[] = [
            createMockRow({ table_name: 'users', name: 'id', description: 'User ID' }),
            createMockRow({
                table_name: 'products',
                name: 'product_id',
                description: 'Product ID',
            }),
        ]
        fetchQuerySpy.mockResolvedValueOnce([mockRows, ['table_name', 'name', 'description']])

        const expected = {
            tables: [
                { table_name: 'users', name: 'id', description: 'User ID' },
                { table_name: 'products', name: 'product_id', description: 'Product ID' },
            ],
        }

        const result = await getSchemaFromDb('json')
        expect(result).toEqual(expected)
        expect(fetchQuerySpy).toHaveBeenCalledWith('SELECT * FROM table_metadata;')
    })

    it('should return default string message when no data is fetched', async () => {
        fetchQuerySpy.mockResolvedValueOnce([[], null])

        const expected =
            "Default schema information: The system can access general data. (Could not fetch schema from 'table_metadata' or it is empty)."
        const result = await getSchemaFromDb('str')
        expect(result).toBe(expected)
    })

    it('should return empty JSON array when no data is fetched and outputType is "json"', async () => {
        fetchQuerySpy.mockResolvedValueOnce([[], null])

        const expected = { tables: [] }
        const result = await getSchemaFromDb('json')
        expect(result).toEqual(expected)
    })

    it('should handle rows with null or undefined descriptions gracefully', async () => {
        const mockRows: RowObject[] = [
            createMockRow({ table_name: 'items', name: 'item_id', description: null }),
            createMockRow({ table_name: 'items', name: 'item_name', description: undefined }),
            createMockRow({ table_name: 'items', name: 'price', description: 'Item price' }),
        ]
        fetchQuerySpy.mockResolvedValueOnce([mockRows, ['table_name', 'name', 'description']])

        const expected = `The 'table_metadata' contains the following information which describes the available data structures:
- Schema Entry 1: table_name: items, name: item_id, description: N/A
- Schema Entry 2: table_name: items, name: item_name, description: N/A
- Schema Entry 3: table_name: items, name: price, description: Item price`

        const result = await getSchemaFromDb('str')
        expect(result).toBe(expected)
    })

    it('should handle rows where keys() returns an empty array for string output', async () => {
        const mockRows: RowObject[] = [
            { keys: () => [] }, // A row with no keys
        ]
        fetchQuerySpy.mockResolvedValueOnce([mockRows, []])

        const expected =
            "Default schema information: The system can access general data. ('table_metadata' was found but its content could not be formatted into a descriptive string)."
        const result = await getSchemaFromDb('str')
        expect(result).toBe(expected)
    })

    it('should handle rows where keys() returns an empty array for json output', async () => {
        const mockRows: RowObject[] = [
            { keys: () => [] }, // A row with no keys
        ]
        fetchQuerySpy.mockResolvedValueOnce([mockRows, []])

        const expected = { tables: [{}] } // Expect an object with no properties
        const result = await getSchemaFromDb('json')
        expect(result).toEqual(expected)
    })
})

// Integration test to fetch real data (requires SvelteKit dev server running)
describe('getSchemaFromDb (Integration Test)', () => {
    it('should fetch real schema data and log it', async () => {
        // No mocking here, we want to hit the actual API
        const result = await getSchemaFromDb('json')
        console.log('Real Schema Data:', JSON.stringify(result, null, 2))
        expect(result).toBeDefined()
        expect(result).toHaveProperty('tables')
        expect((result as { tables: unknown[] }).tables.length).toBeGreaterThan(0)
    })
})
