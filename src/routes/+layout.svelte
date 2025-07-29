<script lang="ts">
    import '../app.css'
    import { ModeWatcher } from 'mode-watcher'
    import TopBar from '$lib/components/TopBar.svelte'
    import ApiKeyModal from '$lib/components/ApiKeyModal.svelte'
    import { browser } from '$app/environment'
    import { showApiKeyModal } from '$lib/stores/modalStore'

    let { children } = $props()

    $effect(() => {
        if (browser) {
            const apiKey = localStorage.getItem('API_KEY_GEMINI')
            if (!apiKey) {
                showApiKeyModal.set(true)
            }
        }
    })

    function onApiKeySaved() {
        showApiKeyModal.set(false)
    }
</script>

<ModeWatcher />

<main class="h-[100dvh]">
    <!-- <TopBar>
        <h1>AskMyChambre</h1>
        <small>SEMANTIC SEARCH FOR PARLIAMENTARY DATA</small>
    </TopBar> -->

    {@render children()}
</main>

<ApiKeyModal show={$showApiKeyModal} onSave={onApiKeySaved} />
