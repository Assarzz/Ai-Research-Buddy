<script lang="ts">
	let {
		selectedPdf,
		onFilePicked,
	}: {
		selectedPdf: File | undefined;
		onFilePicked: (file: File) => void;
	} = $props();

	let objectUrl = $state("");

	// When selectedPdf changes, create a fresh object URL for the embed and revoke the old one.
	$effect(() => {
		if (!selectedPdf) {
			objectUrl = "";
			return;
		}
		const url = URL.createObjectURL(selectedPdf);
		objectUrl = url;

		return () => {
			URL.revokeObjectURL(url);
		};
	});

	function handleFileChange(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.item(0);
		if (file) {
			onFilePicked(file);
		}
		// Reset so re-picking the same file from disk still fires onchange
		input.value = "";
	}
</script>

<div class="viewer_container">
	{#if objectUrl && selectedPdf}
		<div class="viewer_toolbar">
			<label class="open_btn">
				Open PDF
				<input
					type="file"
					accept="application/pdf"
					onchange={handleFileChange}
				/>
			</label>
			<span class="active_filename" title={selectedPdf.name}>
				{selectedPdf.name}
			</span>
		</div>
		{#key objectUrl}
			<embed src={objectUrl} type="application/pdf" />
		{/key}
	{:else}
		<label class="empty_dropzone">
			<input
				type="file"
				accept="application/pdf"
				onchange={handleFileChange}
			/>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 1000 1000"
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
		</label>
	{/if}
</div>

<style>
	.viewer_container {
		display: flex;
		flex-direction: column;
		height: 100%;
		min-height: 0;
	}

	.viewer_toolbar {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.6rem 0.9rem;
		background-color: var(--bg-inner);
		border-bottom: 2px solid var(--border);
		flex-shrink: 0;
	}

	.open_btn {
		display: inline-flex;
		align-items: center;
		padding: 0.45rem 0.9rem;
		border-radius: 6px;
		background: #3b82f6;
		color: var(--text);
		cursor: pointer;
		font-size: 0.9rem;
		font-weight: 600;
		flex-shrink: 0;
	}

	.open_btn:hover {
		filter: brightness(1.15);
	}

	.open_btn input,
	.empty_dropzone input {
		display: none;
	}

	.active_filename {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-size: 0.95rem;
		opacity: 0.9;
	}

	.empty_dropzone {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem;
		cursor: pointer;
		min-height: 0;
	}

	.empty_dropzone:hover {
		color: #3b82f6;
	}

	.empty_dropzone svg {
		max-width: 100%;
		max-height: 100%;
		width: min(500px, 90%);
		height: auto;
	}

	embed {
		flex: 1;
		width: 100%;
		min-height: 0;
		border: none;
	}
</style>
