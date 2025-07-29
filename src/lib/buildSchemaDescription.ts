export interface ColumnInfo {
    table_name: string
    name: string
    description?: string // description is optional
}

interface DatabaseContext {
    tables: ColumnInfo[]
}

export function buildSchemaDescription(databaseContext: DatabaseContext): string {
    const groupedTables: { [key: string]: string[] } = {}

    for (const columnInfo of databaseContext.tables) {
        const tableName = columnInfo.table_name
        const colName = columnInfo.name
        const colDesc = columnInfo.description ?? 'No description' // Use nullish coalescing for default value

        if (!tableName || !colName) {
            continue // Skip if essential information is missing
        }

        if (!(tableName in groupedTables)) {
            groupedTables[tableName] = []
        }

        const columnLine = `${colName} (${colDesc})`
        groupedTables[tableName].push(columnLine)
    }

    const schemaLines: string[] = []
    for (const tableName in groupedTables) {
        const columnLines = groupedTables[tableName]
        const formattedColumns = columnLines.map((line) => `  ${line}`).join('\n') // Add indentation
        schemaLines.push(`Table ${tableName}:\n${formattedColumns}`)
    }

    return schemaLines.join('\n')
}
