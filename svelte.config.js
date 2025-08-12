// svelte.config.js
import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
    preprocess: vitePreprocess(),
    kit: {
        adapter: adapter(),
        csp: {
            mode: 'auto',
            directives: {
                // FIX: Removed '%sveltekit.nonce%' as it was not being replaced correctly.
                // We are now relying on 'unsafe-inline' and 'unsafe-eval' which are required for Svelte and Plotly.
                'script-src': ['self', 'unsafe-inline', 'unsafe-eval'],
                
                'style-src': ['self', 'unsafe-inline'],

                'img-src': ['self', 'data:'],
                'font-src': ['self', 'data:'],
                'object-src': ['none'],
                'base-uri': ['self'],
            }
        }
    }
};

export default config;
