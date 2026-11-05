
<script lang="ts">

	type Status = 'old' | 'unloaded' | 'loading' | 'loaded'; 

    let { status = $bindable() }: {status: Status} = $props();

</script>

{#if status=='loading'}
    <svg class='spinner' xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><title>load</title><path fill="none" stroke="currentColor" stroke-linecap="square" stroke-width="2" d="M2 12c0 5.523 4.477 10 10 10s10-4.477 10-10S17.523 2 12 2"/></svg>    
{:else if status=='loaded'}
    <section> LOADED</section>

{:else if status=='old'}
    <section class="bad"> OLD</section>

{:else}
    <section class="bad"> UNLOADED</section>
{/if}




<style>
  /* Rotates the entire SVG infinitely */
  .spinner {
    animation: rotate 2s linear infinite;
  }

  @keyframes rotate {
    0%{
        transform: rotate(0deg);
    }
    50% {
        transform:rotate(180deg);
    }
    100% {
        transform: rotate(360deg);
    }
    }

    .bad {
        color: var(--error);
    }
</style>
