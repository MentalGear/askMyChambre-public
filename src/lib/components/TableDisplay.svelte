<script lang="ts">
	import { onMount } from 'svelte';
	import { resultStore } from '$lib/stores/resultStore'; // Import our new store

	// --- Dynamically import UI components ---
	let componentsLoaded = $state(false);
	let Table: any, Switch: any, Label: any, Button: any, TopBar: any, Charting: any, TableIcon: any;

	onMount(async () => {
		try {
			TopBar = (await import('./TopBar.svelte')).default;
			Table = (await import('$lib/shadcn_ui/components/ui/table'));
			Switch = (await import('$lib/shadcn_ui/components/ui/switch')).Switch;
			Label = (await import('$lib/shadcn_ui/components/ui/label')).Label;
			Button = (await import('$lib/shadcn_ui/components/ui/button')).Button;
			Charting = (await import('lucide-svelte/icons/bar-chart-2')).default;
			TableIcon = (await import('lucide-svelte/icons/table-2')).default;
			componentsLoaded = true;
		} catch (e) {
			console.error('Failed to load table display components:', e);
		}
	});

	let showSqlQuery = $state(false);
    
</script>

{#if componentsLoaded}
	<div class="flex flex-col h-full">
		<TopBar>
			<div class="flex place-content-between place-items-center w-full">
				<h2 class="font-semibold">Results</h2>
				<div class="flex items-center gap-4">
					<div class="flex items-center gap-2">
						<Label for="show-sql">Show Query</Label>
						<Switch id="show-sql" bind:checked={showSqlQuery} />
					</div>
					<!-- This button now calls the action in the store -->
					{#if $resultStore.results?.plotSpec}
						<div class="flex items-center gap-2">
							<Label for="show-plot">Show Plot</Label>
							<Switch
								id="show-plot"
								checked={$resultStore.showPlot}
								on:click={resultStore.togglePlot}
							/>
						</div>
					{/if}
				</div>
			</div>
		</TopBar>

		<div class="mainContent p-4 md:p-6 space-y-6 overflow-y-auto flex-1">
			{#if $resultStore.results?.queryError}
				<div class="error-message rounded-lg bg-red-100 p-4 text-red-700 dark:bg-red-900/30 dark:text-red-300">
					<h3 class="font-bold">Query Error:</h3>
					<p>{$resultStore.results.queryError}</p>
					{#if $resultStore.results.sqlQuery}<pre class="bg-red-200 dark:bg-red-800/50 rounded p-3 text-sm mt-4">{$resultStore.results.sqlQuery[0]}</pre>{/if}
				</div>
			{:else if $resultStore.results?.queryResult}
				{#if showSqlQuery && $resultStore.results.sqlQuery}
					<div class="bg-background border rounded-lg p-4">
						<h3 class="font-semibold mb-2 text-lg">Generated SQL Query</h3>
						<pre class="bg-gray-100 dark:bg-gray-800 rounded p-3 text-sm">{$resultStore.results.sqlQuery[0]}</pre>
					</div>
				{/if}
				{#if $resultStore.results.queryResult.length > 0}
					<div class="bg-background border rounded-lg">
						<div class="p-4"><h3 class="font-semibold text-lg">Data Table</h3></div>
						<div class="data-table rounded-b-lg border-t">
							<Table.Root><Table.Header><Table.Row>
								{#each Object.keys($resultStore.results.queryResult[0]) as key}<Table.Head>{key}</Table.Head>{/each}
							</Table.Row></Table.Header><Table.Body>
								{#each $resultStore.results.queryResult as row}<Table.Row>
									{#each Object.values(row) as value}<Table.Cell>{value}</Table.Cell>{/each}
								</Table.Row>{/each}
							</Table.Body></Table.Root>
						</div>
					</div>
				{:else}
					<p class="text-center text-gray-500 pt-10">The query returned no data.</p>
				{/if}
			{:else}
				<div class="flex h-full items-center justify-center">
					<div class="bg-background mx-auto flex max-w-md flex-col gap-2 rounded-lg border p-10 text-center">
						<!-- FIX: Use the modern Svelte 5 syntax for dynamic components -->
						<svelte:component this={TableIcon} class="h-12 w-12 mx-auto text-muted-foreground" />
						<h2 class="text-lg font-semibold mt-4">Results Panel</h2>
						<p class="text-sm text-muted-foreground">Ask a question to see the results here.</p>
					</div>
				</div>
			{/if}
		</div>
	</div>
{:else}
	<div class="flex h-full w-full items-center justify-center"><p class="text-muted-foreground animate-pulse">Loading...</p></div>
{/if}
