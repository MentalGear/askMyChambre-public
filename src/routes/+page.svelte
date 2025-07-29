<script lang="ts">
    import { Chat } from '@ai-sdk/svelte'
    import * as Resizable from '$lib/shadcn_ui/components/ui/resizable'
    import ChatWindow from '$lib/components/ChatWindow.svelte'
    import ResultsDisplay from '$lib/components/ResultsDisplay.svelte'
    import { fetchQuery } from '$lib/fetchQuery'
    import type { ResultData } from './ResultType'
    import { browser } from '$app/environment'

    const chat = $state(
        new Chat({
            api: 'api/chat',
            body: {
                apiKey: browser ? localStorage.getItem('API_KEY_GEMINI') : null,
            },
        })
    )

    let results: ResultData = $state({})

    $effect(() => {
        const lastMessage = chat.messages[chat.messages.length - 1]
        if (!lastMessage || !lastMessage.content) return

        const sqlMatch = lastMessage.content.match(/```sql\n([\s\S]*?)\n```/)

        if (sqlMatch && sqlMatch[1]) {
            results.sqlQuery = [sqlMatch[1]]
        }
    })

    $effect(() => {
        if (results.sqlQuery) {
            getQueryResults()
        }
    })

    async function getQueryResults() {
        if (!results.sqlQuery) return

        const query = results.sqlQuery[0]
        try {
            const [rows, columns] = await fetchQuery(query)
            results.queryResult = rows
            results.queryError = null // Clear any previous error
        } catch (error: unknown) {
            console.error('Error fetching query results:', error)
            results.queryResult = null
            results.queryError =
                error instanceof Error ? error.message : 'An unknown error occurred.'
        }
    }
</script>

<Resizable.PaneGroup direction="horizontal">
    <Resizable.Pane defaultSize={50}>
        <div class="h-full p-4">
            <ChatWindow {chat} />
        </div>
    </Resizable.Pane>

    <Resizable.Handle />

    <Resizable.Pane defaultSize={50}>
        <div class="bg-muted/50 h-full p-4">
            <ResultsDisplay {results} />
        </div>
    </Resizable.Pane>
</Resizable.PaneGroup>
