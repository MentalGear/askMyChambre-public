<script lang="ts">
    import * as Dialog from '$lib/shadcn_ui/components/ui/dialog'
    import { Input } from '$lib/shadcn_ui/components/ui/input'
    import { Label } from '$lib/shadcn_ui/components/ui/label'
    import { Button } from '$lib/shadcn_ui/components/ui/button'

    import { showApiKeyModal } from '$lib/stores/modalStore'

    let { onSave } = $props()
    let apiKey = $state(undefined)

    function saveApiKey() {
        if (!apiKey) return
        localStorage.setItem('API_KEY_GEMINI', apiKey)
        onSave()
    }
</script>

<Dialog.Root bind:open={$showApiKeyModal}>
    <Dialog.Content
        class="sm:max-w-[425px]"
        showCloseButton={false}
        trapFocus={true}
        onFocusOutside={(e) => {
            e.preventDefault()
            e.stopPropagation()
        }}
    >
        <Dialog.Header>
            <Dialog.Title>Enter Gemini API Key</Dialog.Title>
            <Dialog.Description>
                <p class="mb-2">
                    Please enter your Gemini API key or get your <a
                        class="link accent text-primary"
                        target="_blank"
                        href="https://aistudio.google.com/apikey"
                        >free personal API key here
                    </a>.
                </p>
                <p class="italic">The key will ONLY be stored in your browser's local storage.</p>
            </Dialog.Description>
        </Dialog.Header>
        <div class="grid gap-4 py-4">
            <div class="grid grid-cols-4 items-center gap-4">
                <Label for="api-key" class="text-right">API Key</Label>
                <Input id="api-key" bind:value={apiKey} class="col-span-3" />
            </div>
        </div>
        <Dialog.Footer>
            <Button onclick={saveApiKey}>Save</Button>
        </Dialog.Footer>
    </Dialog.Content>
</Dialog.Root>
