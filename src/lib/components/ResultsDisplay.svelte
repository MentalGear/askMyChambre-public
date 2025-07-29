<script lang="ts">
    import type { ResultData } from '../../routes/ResultType'

    import TopBar from './TopBar.svelte'

    import * as Table from '$lib/shadcn_ui/components/ui/table'

    import { Switch } from '$lib/shadcn_ui/components/ui/switch'
    import { Label } from '$lib/shadcn_ui/components/ui/label'

    let { results }: { results: ResultData } = $props()

    let showSqlPath = $state(false)
    let showStartMessage = $state(false)

    $effect(() => {
        if (!showStartMessage && results?.queryResult) {
            // switch
            showStartMessage = true
        }
    })

    $inspect(results)
</script>

<div class="h-full overflow-y-auto">
    <TopBar>
        <div class="flex place-content-between place-items-center">
            <h2>Results</h2>
            <div class="flex items-center gap-2">
                <Label for="show-sql">Edit Query</Label>
                <Switch id="show-sql" disabled bind:checked={showSqlPath} />
            </div>
        </div>
    </TopBar>

    <div class="mainContent flex flex-col place-content-center place-items-center">
        {#if showSqlPath && results?.sqlQuery}
            <div class="sql-query mb-4">
                <h3>SQL Query:</h3>
                {#each results.sqlQuery as query}
                    <pre class="rounded p-2">{query}</pre>
                {/each}
            </div>
        {/if}

        {#if results?.queryError}
            <div class="error-message m-10 rounded-lg bg-red-100 p-4 text-red-700">
                <h3 class="font-bold">Error:</h3>
                <p>{results.queryError}</p>
            </div>
        {:else if results?.queryResult}
            <div class="data-table bg-accent m-10 rounded-lg border">
                {#if results.queryResult.length > 0}
                    <Table.Root>
                        <Table.Header>
                            <Table.Row>
                                {#each Object.keys(results.queryResult[0]) as key}
                                    <Table.Head>{key}</Table.Head>
                                {/each}
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {#each results.queryResult as row}
                                <Table.Row>
                                    {#each Object.values(row) as value}
                                        <Table.Cell>{value}</Table.Cell>
                                    {/each}
                                </Table.Row>
                            {/each}
                        </Table.Body>
                    </Table.Root>
                {:else}
                    <p>No data found for this query.</p>
                {/if}
            </div>
        {/if}

        {#if !showStartMessage}
            <div
                class="bg-background m-10 mx-auto flex max-w-md flex-col gap-2 rounded-lg border p-10 text-center opacity-50"
            >
                <h1 class="mb-2 text-xl font-semibold">Good To Know</h1>
                <ul class="flex flex-col gap-2 text-center">
                    <!-- <li class="text-md">
                        Our method applies <b>no</b> AI processing on the actual data to prevent any
                        hallucination risks.
                    </li> -->
                    <!-- <li class="text-md">
                        Our method <b>does not apply</b> AI processing on the actual data.
                    </li> -->
                    <li class="text-md">
                        To ensure all presented data is authentic and without risk of hallucination,
                        our method <b>does not apply</b> AI processing on the actual data.
                    </li>

                    <li class="text-md italic">
                        However always consider checking the AI-generated query if the displayed
                        data appears inconsistent with your search intention.
                    </li>
                    <!-- <li class="text-md italic">
                        However if the displayed data appears inconsistent with your intented
                        search, consider reviewing the AI-generated query.
                    </li> -->
                </ul>
            </div>
        {/if}
    </div>
</div>
