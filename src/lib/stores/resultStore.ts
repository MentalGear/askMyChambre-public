import { writable } from 'svelte/store';
import type { ResultData } from '../../routes/ResultType';

// Define the shape of our store's state
export type ResultStore = {
    isLoading: boolean;
    showPlot: boolean;
    results: (ResultData & { plotSpec?: any }) | null;
};

// Create the writable store with an initial state.
// This is the classic Svelte store that works in any .ts/.js file.
const { subscribe, set, update } = writable<ResultStore>({
    isLoading: false,
    showPlot: false,
    results: null,
});

// --- Public API for our store ---
export const resultStore = {
    // Expose the subscribe method for reactive access in components ($resultStore)
    subscribe,

    // Action to fetch data and update the store
    fetchResultsAndPlot: async (sqlQuery: string, userPrompt: string) => {
        // Set loading state
        update(store => ({ ...store, isLoading: true, showPlot: true, results: null }));

        try {
            const response = await fetch('/api/execute-and-plot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sqlQuery, userPrompt })
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`API Error: ${response.status} ${errorText}`);
            }

            const data = await response.json();
            
            // Set the new state. We keep showPlot: false so the user must explicitly click the button.
            set({ isLoading: false, showPlot: true, results: data });

        } catch (error: unknown) {
            console.error('Error fetching query results:', error);
            const errorResult = {
                sqlQuery: [sqlQuery],
                queryResult: null,
                queryError: error instanceof Error ? error.message : 'A network or unknown error occurred.',
                plotSpec: null,
            };
            // Update store with the error state
            set({ isLoading: false, showPlot: true, results: errorResult });
        }
    },

    // Action to toggle the plot visibility
    togglePlot: () => {
        update(store => ({ ...store, showPlot: !store.showPlot }));
    }
};
