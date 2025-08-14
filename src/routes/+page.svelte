<script lang="ts">
    import { Chat } from '@ai-sdk/svelte';
    import * as Resizable from '$lib/shadcn_ui/components/ui/resizable';
    import ChatWindow from '$lib/components/ChatWindow.svelte';
    import { browser } from '$app/environment';
    
    // Import the new components and the store
    import TableDisplay from '$lib/components/TableDisplay.svelte';
    import PlotDisplay from '$lib/components/PlotDisplay.svelte';
    import { resultStore } from '$lib/stores/resultStore';

    // State for the chat component
    const chat = $state(
        new Chat({
            api: 'api/chat',
            body: {
                apiKey: browser ? localStorage.getItem('API_KEY_GEMINI') : null,
            },
        })
    );

    // This effect now calls the action in the store, keeping the page clean.
    $effect(() => {
        const lastMessage = chat.messages[chat.messages.length - 1];
        if (lastMessage?.role !== 'assistant' || !lastMessage.content) return;

        const sqlMatch = lastMessage.content.match(/```sql\n([\s\S]*?)\n```/);
        const lastUserMessage = chat.messages.findLast(m => m.role === 'user');

        if (sqlMatch && sqlMatch[1] && lastUserMessage) {
            resultStore.fetchResultsAndPlot(sqlMatch[1], lastUserMessage.content);
        }
    });
</script>

<Resizable.PaneGroup direction="horizontal" class="h-full w-full">
    <Resizable.Pane defaultSize={40} minSize={30}>
        <div class="h-full p-4">
            <ChatWindow {chat} />
        </div>
    </Resizable.Pane>

    <Resizable.Handle withHandle />

    <!-- The middle panel now uses the dedicated TableDisplay component -->
    <Resizable.Pane defaultSize={$resultStore.showPlot ? 35 : 60} minSize={30}>
        <div class="bg-muted/50 h-full">
            {#if $resultStore.isLoading}
                <div class="flex h-full w-full items-center justify-center">
                    <p class="text-muted-foreground">Running query and generating visuals...</p>
                </div>
            {:else}
                <TableDisplay />
            {/if}
        </div>
    </Resizable.Pane>
    
    <!-- The third panel only appears when showPlot is true in the store -->
    {#if $resultStore.showPlot}
        <Resizable.Handle withHandle />
        <Resizable.Pane defaultSize={25} minSize={20} collapsible>
            <div class="bg-muted/50 h-full">
                <PlotDisplay />
            </div>
        </Resizable.Pane>
    {/if}
</Resizable.PaneGroup>
