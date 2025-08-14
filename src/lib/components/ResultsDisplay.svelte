<script lang="ts">
	import { onMount } from 'svelte';
	import type { ResultData } from '../../routes/ResultType';

	// State to track if our dynamic, client-side modules have loaded
	let componentsLoaded = $state(false);
	let componentLoadError = $state<string | null>(null);

	// These will hold the component definitions once loaded
	let Table: any, TableIcon: any;
	let Plotly: any;

	// Props
	let {
		results,
		display = 'table' // Default to showing the table
	}: {
		results: (ResultData & { plotSpec?: any }) | null;
		display?: 'table' | 'plot';
	} = $props();

	// --- REFACTORED onMount ---
	// This function is now much simpler and more robust.
	onMount(async () => {
		try {
			// This instance will ONLY load components needed for the table view.
			if (display === 'table') {
				Table = (await import('$lib/shadcn_ui/components/ui/table'));
				TableIcon = (await import('lucide-svelte/icons/table-2')).default;
			}

			// This instance will ONLY load the Plotly library.
			if (display === 'plot') {
				Plotly = (await import('plotly.js-dist-min')).default;
			}

			// --- Success ---
			// Mark components as loaded so the UI can render.
			componentsLoaded = true;
		} catch (e: any) {
			console.error(`Failed to load components for display='${display}':`, e);
			componentLoadError = e.message;
		}
	});

	let plotContainer: HTMLDivElement;

	$effect(() => {
		if (componentsLoaded && display === 'plot' && results?.plotSpec && plotContainer) {
			Plotly.react(
				plotContainer,
				results.plotSpec.data,
				{
					...results.plotSpec.layout,
					autosize: true,
					paper_bgcolor: 'rgba(0,0,0,0)',
					plot_bgcolor: 'rgba(0,0,0,0)',
					font: {
						color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
					}
				},
				{ responsive: true }
			);
		}
	});
</script>

<!-- This is a component-level style block -->
<style>
	@keyframes progress-animation {
		from {
			width: 0%;
		}
		to {
			width: 100%;
		}
	}
	.progress-bar-inner {
		/* Apply the animation here */
		animation: progress-animation 15s cubic-bezier(0.25, 1, 0.5, 1) forwards;
	}
</style>

{#if !componentsLoaded}
	{#if display === 'plot'}
		<div class="flex h-full w-full flex-col items-center justify-center p-4">
			<div class="w-full max-w-xs">
				<div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
					<!-- The progress bar now uses a CSS class for its animation -->
					<div class="bg-blue-600 h-2 rounded-full progress-bar-inner"></div>
				</div>
				<p class="text-sm text-center text-muted-foreground mt-3">
					Initializing visualization engine...
				</p>
			</div>
			{#if componentLoadError}<div
					class="mt-4 text-red-500 text-xs text-center p-2 bg-red-100 dark:bg-red-900/20 rounded-md"
				>
					<strong>Error:</strong><br />{componentLoadError}
				</div>{/if}
		</div>
	{:else}
		<div class="flex h-full w-full items-center justify-center">
			<p class="text-muted-foreground animate-pulse">Loading...</p>
		</div>
	{/if}
{:else}
	<div class="flex flex-col h-full">
		<!-- SECTION 1: View for the Table Panel -->
		{#if display === 'table'}
			<div class="mainContent p-4 md:p-6 space-y-6 overflow-y-auto flex-1">
				{#if results?.queryError}
					<div
						class="error-message rounded-lg bg-red-100 p-4 text-red-700 dark:bg-red-900/30 dark:text-red-300"
					>
						<h3 class="font-bold">Query Error:</h3>
						<p>{results.queryError}</p>
						{#if results.sqlQuery}<pre
								class="bg-red-200 dark:bg-red-800/50 rounded p-3 text-sm mt-4"
							>{results.sqlQuery[0]}</pre>{/if}
					</div>
				{:else if results?.queryResult}
					{#if results.queryResult.length > 0}
						<div class="bg-background border rounded-lg">
							<div class="p-4"><h3 class="font-semibold text-lg">Data Table</h3></div>
							<div class="data-table rounded-b-lg border-t">
								<Table.Root>
									<Table.Header
										><Table.Row>
											{#each Object.keys(results.queryResult[0]) as key}<Table.Head
													>{key}</Table.Head
												>{/each}
										</Table.Row></Table.Header
									>
									<Table.Body>
										{#each results.queryResult as row}<Table.Row>
												{#each Object.values(row) as value}<Table.Cell
														>{value}</Table.Cell
													>{/each}
											</Table.Row>{/each}
									</Table.Body>
								</Table.Root>
							</div>
						</div>
					{:else}
						<p class="text-center text-gray-500 pt-10">The query returned no data.</p>
					{/if}
				{:else}
					<div class="flex h-full items-center justify-center">
						<div
							class="bg-background mx-auto flex max-w-md flex-col gap-2 rounded-lg border p-10 text-center"
						>
							<svelte:component this={TableIcon} class="h-12 w-12 mx-auto text-muted-foreground" />
							<h2 class="text-lg font-semibold mt-4">Results Panel</h2>
							<p class="text-sm text-muted-foreground">
								Ask a question about your data to see the results here.
							</p>
						</div>
					</div>
				{/if}
			</div>
		{/if}

		<!-- SECTION 2: View for the Plot Panel -->
		{#if display === 'plot'}
			{#if results?.plotSpec}
				<div class="p-4 h-full flex flex-col">
					<h3 class="font-semibold text-lg mb-4">{results.plotSpec.layout.title.text || 'Chart'}</h3>
					<div bind:this={plotContainer} class="w-full flex-1 min-h-0"></div>
				</div>
			{:else}
				<div class="flex h-full w-full items-center justify-center">
					<p class="text-muted-foreground">No plot available for this data.</p>
				</div>
			{/if}
		{/if}
	</div>
{/if}
