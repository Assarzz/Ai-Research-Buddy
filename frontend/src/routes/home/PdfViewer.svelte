<script lang="ts">
    let { selectedPdf = $bindable() } = $props();
    let pdfList = $state<FileList | undefined>(undefined);

    $effect(() => {
        selectedPdf = pdfList?.item(0);
    });

    let objectUrl = $state("");

    $effect(() => {
        if (selectedPdf) {
            // Revoke the old URL before creating a new one
            if (objectUrl) URL.revokeObjectURL(objectUrl);

            objectUrl = URL.createObjectURL(selectedPdf);
        } else {
            if (objectUrl) URL.revokeObjectURL(objectUrl);
            objectUrl = "";
        }
    });
</script>

<label>
    <input type="file" bind:files={pdfList} accept="application/pdf" />
    {#if selectedPdf}
        <embed src={objectUrl} />
    {:else}
        <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 1000 1000"
            width="100%"
            height="100%"
            fill="none"
        >
            <!-- dashed square perimeter -->
            <rect
                x="20"
                y="20"
                width="960"
                height="960"
                rx="48"
                stroke="currentColor"
                stroke-width="8"
                stroke-dasharray="32 24"
                stroke-linecap="round"
            />

            <!-- file icon -->
            <g
                stroke="currentColor"
                stroke-width="16"
                stroke-linejoin="round"
                stroke-linecap="round"
            >
                <!-- page with folded corner -->
                <path
                    d="M380 260 H560 L660 360 V700 Q660 740 620 740 H380 Q340 740 340 700 V300 Q340 260 380 260 Z"
                />
                <!-- fold -->
                <path d="M560 260 V340 Q560 360 580 360 H660" />
                <!-- plus sign -->
                <path d="M500 470 V630 M420 550 H580" />
            </g>

            <!-- label -->
            <text
                x="500"
                y="840"
                text-anchor="middle"
                font-family="system-ui, -apple-system, Segoe UI, sans-serif"
                font-size="44"
                fill="currentColor">Click to choose a PDF file</text
            >
        </svg>
    {/if}
</label>


<style>

  label:hover { color: #3b82f6; }

input[type="file"]::file-selector-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #3b82f6;
  color: var(--text);
  cursor: pointer;
}

  embed{
    width: 100%;
    height: 100vh;
  }
</style>