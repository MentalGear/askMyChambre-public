import { json } from '@sveltejs/kit'
import { Worker } from 'worker_threads'
import { fileURLToPath } from 'url'
import path from 'path'
import { dev } from '$app/environment'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// Define the structure of the data returned by the worker
export type Result = {
    rows: Record<string, unknown>[]
    columns: string[] | null
}

let worker: Worker

const jobQueue: {
    query: string
    params: unknown[]
    resolve: (value: Response) => void
    reject: (reason?: Error) => void
}[] = []
let isWorkerBusy = false

function getWorker() {
    if (!worker) {
        const workerFile = `db-worker.${dev ? 'ts' : 'js'}`
        const workerPath = path.resolve(__dirname, workerFile)
        worker = new Worker(workerPath)

        worker.on(
            'message',
            (result: { type: 'success' | 'error'; data?: Result; error?: string }) => {
                const job = jobQueue.shift()
                if (job) {
                    if (result.type === 'success' && result.data) {
                        job.resolve(json(result.data))
                    } else {
                        console.error('Database query error in worker:', result.error)
                        job.resolve(json({ error: result.error }, { status: 500 }))
                    }
                }
                isWorkerBusy = false
                processNextJob()
            }
        )

        worker.on('error', (error: Error) => {
            console.error('Worker error:', error)
            const job = jobQueue.shift()
            job?.reject(error)
            isWorkerBusy = false
            // In a real-world scenario, you might want to restart the worker.
        })

        worker.on('exit', (code) => {
            if (code !== 0) {
                console.error(`Worker stopped with exit code ${code}`)
                // Reject all pending jobs
                while (jobQueue.length > 0) {
                    const job = jobQueue.shift()
                    job?.reject(new Error(`Worker stopped with exit code ${code}`))
                }
            }
        })
    }
    return worker
}

function processNextJob() {
    if (isWorkerBusy || jobQueue.length === 0) {
        return
    }
    isWorkerBusy = true
    const job = jobQueue[0]
    getWorker().postMessage({ query: job.query, params: job.params })
}

export function executeQuery(query: string, params: unknown[]): Promise<Response> {
    return new Promise((resolve, reject) => {
        jobQueue.push({ query, params, resolve, reject })
        processNextJob()
    })
}
