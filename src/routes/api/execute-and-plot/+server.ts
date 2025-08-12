import { json, error } from '@sveltejs/kit';
import { spawn } from 'child_process';
import { executeQuery } from '$lib/server/db-worker-manager';

function executePythonScript(scriptPath: string, args: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', [scriptPath, ...args]);
        let result = '';
        let errorOutput = '';

        pythonProcess.stdout.on('data', (data) => {
            result += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                console.error(`Python script stderr: ${errorOutput}`);
                // Reject with the actual error from the script
                reject(new Error(errorOutput || `Python script exited with code ${code}`));
            } else {
                resolve(result);
            }
        });
    });
}

export async function POST({ request }) {
    const { sqlQuery, userPrompt } = await request.json();

    if (!sqlQuery || !userPrompt) {
        throw error(400, 'Missing sqlQuery or userPrompt in the request body');
    }

    try {
        const dbResponse = await executeQuery(sqlQuery, []);

        if (!dbResponse.ok) {
            const errorData = await dbResponse.json();
            throw new Error(errorData.error || 'Database query failed');
        }

        const { rows: queryResult } = await dbResponse.json();

        let plotSpec = null;
        if (queryResult && queryResult.length > 0) {
            const plotJsonString = await executePythonScript(
                'llm/generate_plot.py',
                [userPrompt, JSON.stringify(queryResult)]
            );
            plotSpec = JSON.parse(plotJsonString);
        }

        return json({
            queryResult,
            plotSpec,
            sqlQuery: [sqlQuery],
            queryError: null
        });

    } catch (e: any) {
        console.error('Error in execute-and-plot endpoint:', e);
        // Ensure a consistent error shape that the frontend can handle
        return json({
            queryResult: null,
            plotSpec: null,
            sqlQuery: [sqlQuery],
            queryError: e.message || 'An internal server error occurred.'
        }, { status: 500 });
    }
}
