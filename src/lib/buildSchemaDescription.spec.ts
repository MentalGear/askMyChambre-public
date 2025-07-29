import { describe, it, expect } from 'vitest'
import { buildSchemaDescription } from './buildSchemaDescription'

interface ColumnInfo {
    table_name: string
    name: string
    description?: string
}

interface DatabaseContext {
    tables: ColumnInfo[]
}

const sampleDatabaseContext: DatabaseContext = {
    tables: [
        {
            table_name: 'customers',
            name: 'id',
            description: 'Customer unique identifier',
        },
        {
            table_name: 'customers',
            name: 'name',
            description: 'Customer name',
        },
        {
            table_name: 'orders',
            name: 'order_id',
            description: 'Order unique identifier',
        },
        {
            table_name: 'orders',
            name: 'customer_id',
            description: 'ID of the customer who placed the order',
        },
    ],
}

describe('buildSchemaDescription', () => {
    it('should build a correct schema description from sample data', () => {
        const expected = `Table customers:
  id (Customer unique identifier)
  name (Customer name)
Table orders:
  order_id (Order unique identifier)
  customer_id (ID of the customer who placed the order)`
        const result = buildSchemaDescription(sampleDatabaseContext)
        expect(result).toBe(expected)
    })

    it('should return an empty string for an empty database context', () => {
        const context: DatabaseContext = { tables: [] }
        expect(buildSchemaDescription(context)).toBe('')
    })

    it('should handle columns with no description', () => {
        const context: DatabaseContext = {
            tables: [
                {
                    table_name: 'products',
                    name: 'product_id',
                },
                {
                    table_name: 'products',
                    name: 'product_name',
                    description: 'Name of the product',
                },
            ],
        }
        const expected = `Table products:
  product_id (No description)
  product_name (Name of the product)`
        const result = buildSchemaDescription(context)
        expect(result).toBe(expected)
    })
})
