<script lang="ts">
	import { onMount } from "svelte";
	import PdfViewer from "./PdfViewer.svelte";
	import Criteria from "./Criteria.svelte";
	import { createPdfFile, isSameFile, type PdfFile } from "./types";

	let { user } = $props();

	let files = $state<PdfFile[]>([]);
	let activeFileId = $state<number | undefined>(undefined);

	let activeFileIndex = $derived(
		files.findIndex((f) => f.id === activeFileId),
	);
	let activeFile = $derived(
		activeFileIndex !== -1 ? files[activeFileIndex] : undefined,
	);

	function handleFilePicked(file: File) {
		const existing = files.find((f) => isSameFile(f.file, file));
		if (existing) {
			activeFileId = existing.id;
			return;
		}
		const pdfFile = createPdfFile(file);
		files.push(pdfFile);
		activeFileId = pdfFile.id;
	}

	function removeFile(id: number) {
		const idx = files.findIndex((f) => f.id === id);
		if (idx === -1) return;
		files.splice(idx, 1);
		if (activeFileId === id) {
			const next = files[idx] ?? files[idx - 1];
			activeFileId = next?.id;
		}
	}

	onMount(async () => {
		try {
			const response = await fetch("/api/get_user");
			console.log(response);

			const data = await response.json();
			user = data.user;
			console.log(user);
			if (!user) {
				window.location.href = "/#/login";
			}
		} catch (err) {
			console.error(err);
		}
	});
</script>

<div class="outer">

	<aside class="sidebar">
		<header class="sidebar_header">
			<h1 class="title">AI research buddy</h1>
			{#if user}
				<p class="subtitle">Hello: {user}</p>
			{/if}
		</header>

		<section class="files_section">
			<div class="section_header">
				<h2>Files ({files.length})</h2>
			</div>

			{#if files.length === 0}
				<p class="empty_hint">
					No PDFs opened yet. Choose a PDF file on the left to get
					started.
				</p>
			{:else}
				<ul class="file_list">
					{#each files as pdfFile (pdfFile.id)}
						{@const isActive = pdfFile.id === activeFileId}
						{@const isLoading = pdfFile.criteria.some(
							(c) => c.status === "loading",
						)}
						<li class="file_item" class:active={isActive}>
							<button
								type="button"
								class="file_select_btn"
								onclick={() => (activeFileId = pdfFile.id)}
								title={pdfFile.file.name}
							>
								<span class="file_name"
									>{pdfFile.file.name}</span
								>
								<span class="file_meta">
									{#if isLoading}
										<span class="loading_badge">...</span>
									{/if}
									{pdfFile.criteria.length}
								</span>
							</button>
							<button
								type="button"
								class="file_remove_btn"
								aria-label={`Remove ${pdfFile.file.name}`}
								title="Remove file"
								onclick={() => removeFile(pdfFile.id)}
							>
								×
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</section>

		<section class="criteria_section">
			{#if activeFileIndex !== -1}
				<Criteria bind:pdfFile={files[activeFileIndex]}></Criteria>
			{:else}
				<p class="empty_hint">
					Select a file to view and edit its criteria.
				</p>
			{/if}
		</section>
	</aside>
	<div class="pdf_viewer">
		<PdfViewer
			selectedPdf={activeFile?.file}
			onFilePicked={handleFilePicked}
		></PdfViewer>
	</div>
</div>

<style>
	.outer {
		display: flex;
		flex-direction: row;
		height: 100%;
		overflow: hidden;
	}

	.pdf_viewer,
	.sidebar {
		flex: 1;
		min-width: 0;
		height: 100%;
	}

	.sidebar {
		display: flex;
		flex-direction: column;
		border-left: 3px solid var(--border);
		overflow-y: auto;
		padding: 1rem;
		box-sizing: border-box;
		gap: 1rem;
	}

	.sidebar_header {
		border-bottom: 2px solid var(--border);
		padding-bottom: 0.75rem;
	}

	.title {
		margin: 0;
		font-size: 1.5rem;
	}

	.subtitle {
		margin: 0.25rem 0 0;
		opacity: 0.8;
		font-size: 0.95rem;
	}

	.section_header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 0.5rem;
	}

	.section_header h2 {
		margin: 0;
		font-size: 1.05rem;
	}

	.file_list {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
		max-height: 220px;
		overflow-y: auto;
	}

	.file_item {
		display: flex;
		align-items: stretch;
		background-color: var(--bg-inner);
		border: 2px solid var(--border);
		border-radius: 8px;
		overflow: hidden;
	}

	.file_item.active {
		border-color: #3b82f6;
		background-color: #252c38;
	}

	.file_select_btn {
		flex: 1;
		min-width: 0;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
		padding: 0.55rem 0.75rem;
		background: transparent;
		border: none;
		color: var(--text);
		text-align: left;
		cursor: pointer;
		font-size: 0.92rem;
	}

	.file_select_btn:hover {
		background-color: rgba(255, 255, 255, 0.05);
	}

	.file_name {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.file_meta {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		flex-shrink: 0;
		font-size: 0.8rem;
		padding: 0.1rem 0.45rem;
		border-radius: 999px;
		background-color: rgba(255, 255, 255, 0.08);
	}

	.loading_badge {
		color: #60a5fa;
		font-weight: 700;
	}

	.file_remove_btn {
		background: transparent;
		border: none;
		border-left: 1px solid var(--border);
		color: var(--text);
		opacity: 0.7;
		cursor: pointer;
		padding: 0 0.65rem;
		font-size: 1.1rem;
		line-height: 1;
	}

	.file_remove_btn:hover {
		opacity: 1;
		background-color: var(--error);
	}

	.criteria_section {
		flex: 1;
		min-height: 0;
	}

	.empty_hint {
		margin: 0.25rem 0;
		opacity: 0.7;
		font-size: 0.92rem;
	}

	:global(.wrong) {
		color: var(--error);
	}
</style>
