import { parentPort } from 'worker_threads'
import Database from 'better-sqlite3'
import path from 'path'

if (!parentPort) {
    throw new Error('This script must be run as a worker thread.')
}

const projectRoot = process.cwd()
const DB_PATH = path.join(projectRoot, 'static', '001_sqlite.db')
let db: Database.Database | null = null

function getDbConnection() {
    if (db) {
        return db
    }
    try {
        db = new Database(DB_PATH, { readonly: true, timeout: 10000 })
        db.pragma('foreign_keys = ON')
        console.log(`Worker: Successfully connected to database: ${DB_PATH}`)
        return db
    } catch (error) {
        console.error(`Worker: Error connecting to database at ${DB_PATH}:`, error)
        throw new Error('Worker: Failed to connect to the database.')
    }
}

parentPort.on('message', (message: { query: string; params: unknown[] }) => {
    try {
        const { query, params } = message
        const database = getDbConnection()

        if (!database) {
            throw new Error('Worker: Database connection failed.')
        }

        const stmt = database.prepare(query)
        const rows = stmt.all(params)

        let columns: string[] | null = null
        if (rows.length > 0) {
            columns = Object.keys(rows[0] as object)
        } else if (stmt.columns && stmt.columns.length > 0) {
            columns = stmt.columns().map((col) => col.name)
        }

        parentPort?.postMessage({ type: 'success', data: { rows, columns } })
    } catch (error: unknown) {
        const errorMessage =
            error instanceof Error ? error.message : 'An unknown database error occurred.'
        parentPort?.postMessage({ type: 'error', error: errorMessage })
    }
})
