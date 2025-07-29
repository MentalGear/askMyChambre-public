<script lang="ts">
    import { Chat } from '@ai-sdk/svelte'
    import { Button } from '$lib/shadcn_ui/components/ui/button'
    import { Textarea } from '$lib/shadcn_ui/components/ui/textarea/index'
    import { showApiKeyModal } from '$lib/stores/modalStore'

    import TopBar from './TopBar.svelte' // Import the TopBar component

    let { chat = $bindable() }: { chat: Chat } = $props()

    let chatContainer: HTMLElement

    $effect(() => {
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight
        }
    })

    function handleSubmit(event: SubmitEvent) {
        event.preventDefault()
        chat.handleSubmit(event)
    }

    import Markdown from 'svelte-exmarkdown'
    import { gfmPlugin } from 'svelte-exmarkdown/gfm'
    const mdPlugins = [gfmPlugin()]

    $inspect(chat.messages)

    import autoscroll from '@kizivat/svelte-autoscroll'
</script>

<div class="flex h-full flex-col">
    <TopBar>
        <div class="flex w-full place-content-stretch place-items-center gap-2">
            <h1>Chat</h1>

            <Button
                variant="ghost"
                size="icon"
                class="key-button"
                onclick={() => showApiKeyModal.set(true)}>🔑</Button
            >
        </div>
    </TopBar>

    <div
        class="messages flex-grow overflow-y-auto p-4"
        use:autoscroll={{ pauseOnUserScroll: true, behavior: 'auto' }}
        bind:this={chatContainer}
    >
        <ul class="place-items-stretch space-y-4">
            {#each chat.messages as message, messageIndex (messageIndex)}
                <li class="flex flex-col gap-2">
                    <!-- Role -->
                    <div class="font-bold capitalize" class:text-right={message.role === 'user'}>
                        {message.role}
                    </div>
                    <!-- Message -->
                    <div
                        class="prose prose-slate max-w-none {message.role === 'user'
                            ? 'text-right'
                            : ''}"
                    >
                        {#each message.parts as part, partIndex (partIndex)}
                            {#if part.type === 'text'}
                                {@const text = part.text
                                    .replace('```markdown', '')
                                    .replace(/```$/, '')}
                                <Markdown md={text} plugins={mdPlugins} />
                                <!-- <div>{part.text}</div> -->
                            {/if}
                        {/each}
                    </div>
                </li>
            {/each}
        </ul>
    </div>

    <form onsubmit={handleSubmit} class="flex place-items-center gap-2 p-4">
        <Textarea
            autofocus={true}
            bind:value={chat.input}
            class="field-sizing-content max-h-[250px] min-h-auto"
            placeholder="What would you like to know?"
            onkeydown={(event) => {
                // if (event.metaKey && event.key === 'Enter') {
                if (event.key === 'Enter' && !event.shiftKey && !event.ctrlKey) {
                    // allow for new lines with shift or ctrl
                    event.preventDefault()
                    // Trigger the form submission directly
                    event.currentTarget.form?.requestSubmit()
                }
            }}
        />
        <!-- tooltip (CMD/CTRL & ENTER to send message or just tooltip to use shift Enter for new line, or a toggle to allow the user to set the behaviour themselves?) -->
        <Button type="submit">Send</Button>
    </form>
</div>
