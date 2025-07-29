import { executeQuery } from '$lib/server/db-worker-manager'

export async function POST({ request }) {
    const { query, params } = await request.json()
    return executeQuery(query, params)
}
