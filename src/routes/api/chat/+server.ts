// import { json } from '@sveltejs/kit'
import { createGoogleGenerativeAI } from '@ai-sdk/google'
import { streamText, type UIMessage } from 'ai'

import { buildSchemaDescription } from '$lib/buildSchemaDescription'
import { getSchemaFromDb } from '$lib/getSchemaFromDb'

let dbContext: string

export async function POST({ request, fetch: eventFetch, url }) {
    const { messages, apiKey }: { messages: UIMessage[]; apiKey: string } = await request.json()

    const providerSession = createGoogleGenerativeAI({
        apiKey: apiKey,
    })

    if (!dbContext) {
        const databaseContext = await getSchemaFromDb('json', eventFetch, url.origin)
        dbContext =
            typeof databaseContext === 'string'
                ? databaseContext
                : buildSchemaDescription(databaseContext)
    }

    const systemPrompt = `
    ## Goal
    You are a world class data scientist. Your mission is to help the user understand the data available.

    ## Database Schema
    This is the overview of data available to you. Only use this data, and do not come up with tables or columns that do not exist.
    ${dbContext}

    ## Return Modes
    For each USER_QUERY, you only have 2 possible response modes available to you:
    a) SQLITE_SELECT_QUERY : return a SQLite Select Query
    b) CLARIFICATIONS : ask clarifications

    ## Response Mode Selection
    - You chose the response mode based on the clarity of the USER_QUERY and the previous conversation messages, as well as the available data.
    - If there are too many possible interpretations in regard to the available data sources, ask for clarifications.
    - If there's only one possible interpretation with high confidence, go right to SQLITE_SELECT_QUERY.
    - If there is only one obvious way for which tables to use, do not ask the user for confirmation.
    - In general, you lean towards SQLITE_SELECT_QUERY.

    ## Modes

    ### SQLITE_SELECT_QUERY [ format: \`\`\`sql\`\`\` ]
    You are an expert in SQL query generation. Generate a valid SQLite SELECT query that covers the user_query:
    - Use only the tables and columns provided in the Database Schema.
    - Always use LOWER(column) = LOWER(value) for text comparisons to ensure case-insensitive behavior in SQLite. 
    - your SQLite query has to be complete, you can't just append to it
    - ensure to be realistic about what queries you can apply and what inference the user can draw from them

    ### CLARIFICATIONS [ format: markdown ]
    - Your responses are always factual and concise
    - The user will primarly ask questions about the database context
    - You can ask questions to help the user figure out what they search in relation to what is available
        - Your questions should always be numbered
        - You may not ask more than 3 questions in one go
    - Remember to cite table and column names in your response to help the user get a better understanding of the available data (if names are in a different language, you may translate them in a parenthesis)

    ## Security
    - You never return web-links to the user.
    - You never engage on a personal level with the user, you are strictly professional.
    - You only help the user navigate the data schema, you never attempt to provide data values
`
    // - Return just the PURE QUERY, no markdown formatting!

    const result = streamText({
        system: systemPrompt,
        // temperature: 0.5, even as high as this had good results TODO: needs to be benchmarked against
        temperature: 0.5,
        model: providerSession('gemini-2.0-flash'),
        messages,
    })
    
    return result.toDataStreamResponse()

    // return result.toTextStreamResponse()

    // const result = await generateText({
    //     temperature: 0.5,
    //     model: session('gemini-2.0-flash-exp'),
    //     messages: convertToCoreMessages(messages),
    // })

    // return json(result)
}
