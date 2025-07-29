<script lang="ts">
    let { class: className = '', ...restProps } = $$props
</script>

<div class="topbar {className}" {...restProps}>
    <slot />
</div>

<style>
    .topbar {
        padding: 0.5rem 1rem; /* Adjusted padding for more generic use */
        background-color: var(--background);
        font-weight: bold;
        color: var(--foreground);
        border-bottom: 1px solid var(--border);
        backdrop-filter: blur(8px); /* Blurred background */
        -webkit-backdrop-filter: blur(8px); /* For Safari support */
        position: relative; /* Make it sticky for headers */
        top: 0;
        z-index: 10; /* Ensure it stays on top */
    }
</style>
