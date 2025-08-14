<script lang="ts">
	import { onMount } from 'svelte';
	import { resultStore } from '$lib/stores/resultStore'; // Import our new store

	let Plotly: any;
	let plotContainer: HTMLDivElement;
	let componentsLoaded = $state(false);

	onMount(async () => {
		try {
			Plotly = (await import('plotly.js-dist-min')).default;
			componentsLoaded = true;
		} catch (e) {
			console.error('Failed to load Plotly:', e);
		}
	});

	$effect(() => {
		if (componentsLoaded && $resultStore.results?.plotSpec && plotContainer) {
			Plotly.react(
				plotContainer,
				$resultStore.results.plotSpec.data,
				{
					...$resultStore.results.plotSpec.layout,
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

<style>
	@keyframes progress-animation {
		from { width: 0%; }
		to { width: 100%; }
	}
	.progress-bar-inner {
		animation: progress-animation 15s cubic-bezier(0.25, 1, 0.5, 1) forwards;
	}
</style>

{#if !componentsLoaded}
	<div class="flex h-full w-full flex-col items-center justify-center p-4">
		<div class="w-full max-w-xs">
			<div class="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
				<div class="bg-blue-600 h-2 rounded-full progress-bar-inner"></div>
			</div>
			<p class="text-sm text-center text-muted-foreground mt-3">Initializing visualization engine...</p>
		</div>
	</div>
{:else}
	<div class="p-4 h-full flex flex-col">
		{#if $resultStore.results?.plotSpec}
			<h3 class="font-semibold text-lg mb-4">{$resultStore.results.plotSpec.layout.title.text || 'Chart'}</h3>
			<div bind:this={plotContainer} class="w-full flex-1 min-h-0"></div>
		{:else}
			<div class="flex h-full w-full items-center justify-center">
				<p class="text-muted-foreground">No plot available for this data.</p>
			</div>
		{/if}
	</div>
{/if}
