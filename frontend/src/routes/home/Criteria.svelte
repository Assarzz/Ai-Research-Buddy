<script lang="ts">
	import Status from "./Status.svelte";
	import {
		type PdfFile,
		newCriterion,
		getCriterion,
	} from "./types";

	let { pdfFile = $bindable() }: { pdfFile: PdfFile } = $props();

	// Refresh the specified criteria for the current pdfFile.
	// Captures pdfFile locally so switching to another file mid-request still updates the right file.
	async function send(ids_to_update: number[]) {
		const targetFile = pdfFile;
		if (!targetFile || ids_to_update.length === 0) {
			return;
		}

		const targetCriteria = targetFile.criteria;
		const validIds: number[] = [];

		// Update the status of each criterion object
		for (const id of ids_to_update) {
			const c = getCriterion(id, targetCriteria);
			if (c) {
				c.status = "loading";
				validIds.push(id);
			}
		}

		if (validIds.length === 0) {
			return;
		}

		// Get feedback
		const formData = new FormData();
		formData.append("pdfFile", targetFile.file);
		for (const id of validIds) {
			const c = getCriterion(id, targetCriteria);
			if (c) {
				formData.append("criteria", c.text);
			}
		}

		try {
			const resp = await fetch("/api/grade_paper", {
				method: "POST",
				body: formData,
			});

			if (!resp.ok || !resp.body) {
				throw new Error(`Request failed with status ${resp.status}`);
			}

			const reader = resp.body
				.pipeThrough(new TextDecoderStream())
				.getReader();
			let buffer = "";
			let looking_for = 0;

			while (looking_for < validIds.length) {
				const { value, done } = await reader.read();
				if (done) break;
				buffer += value;
				const lines = buffer.split("\n");
				buffer = lines.pop()!;
				for (const line of lines) {
					if (!line.trim()) continue;
					const res = JSON.parse(line);
					const c = getCriterion(
						validIds[looking_for++],
						targetCriteria,
					);
					if (!c) continue;
					c.verdict = res.verdict;
					c.explanation = res.explanation;
					c.status = "loaded";
					c.last_updated = c.text;
				}
			}

			// Handle any trailing line without a final newline
			if (buffer.trim() && looking_for < validIds.length) {
				const res = JSON.parse(buffer);
				const c = getCriterion(validIds[looking_for++], targetCriteria);
				if (c) {
					c.verdict = res.verdict;
					c.explanation = res.explanation;
					c.status = "loaded";
					c.last_updated = c.text;
				}
			}
		} catch (err) {
			console.error("Failed to fetch criteria feedback:", err);
			for (const id of validIds) {
				const c = getCriterion(id, targetCriteria);
				if (c && c.status === "loading") {
					c.status = c.last_updated ? "old" : "unloaded";
				}
			}
		}
	}
</script>

<div class="criteria_panel">
	<div class="criteria_header">
		<h2>Criteria</h2>
	</div>

	<div class="criteria_list">
		{#each pdfFile.criteria as criterion, i (criterion.id)}
			<div class="criterion">
				<aside class="button_sidebar">
					<!-- minus button https://allsvgicons.com/search/?q=minus -->
					<button
						type="button"
						title="Remove criterion"
						onclick={() => {
							pdfFile.criteria.splice(i, 1);
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="1em"
							height="1em"
							viewBox="0 0 24 24"
							><title>baseline-minus</title><path
								fill="currentColor"
								d="M19 12.998H5v-2h14z"
							/></svg
						>
					</button>

					<!-- redo button -->
					<button
						type="button"
						title="Re-evaluate criterion"
						disabled={criterion.status === "loading"}
						onclick={async () => {
							await send([criterion.id]);
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							width="1em"
							height="1em"
							viewBox="0 0 24 24"
							><title>redo</title><g
								fill="none"
								stroke="currentColor"
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="1.5"
								><path
									d="M18.364 18.364A9 9 0 1 1 12 3c4.058 0 6.518 2.705 9 5.5"
								/><path d="M21 4.5v4h-4" /></g
							></svg
						>
					</button>
				</aside>

				<div class="criterion_item">
					<div class="criterion_header">
						<input
							type="text"
							bind:value={criterion.text}
							oninput={() => {
								if (!criterion.last_updated) {
									// We haven't loaded the criterion yet, keep it unloaded
									return;
								}
								if (criterion.text !== criterion.last_updated) {
									criterion.status = "old";
								} else {
									criterion.status = "loaded";
								}
							}}
						/>
						<div class="corner_item">
							<Status status={criterion.status}></Status>
						</div>
					</div>

					<section class="criterion_feedback">
						<span class="verdict">[{criterion.verdict}]</span>
						{criterion.explanation}
					</section>
				</div>
			</div>
		{/each}
	</div>

	<div class="criteria_actions">
		<!-- plus button -->
		<button
			type="button"
			class="action_btn add_btn"
			title="Add criterion"
			onclick={() => {
				pdfFile.criteria.push(newCriterion("..."));
			}}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				width="1em"
				height="1em"
				viewBox="0 0 24 24"
				><title>baseline-plus</title><path
					fill="currentColor"
					d="M19 12.998h-6v6h-2v-6H5v-2h6v-6h2v6h6z"
				/></svg
			>
			Add Criterion
		</button>
		<button
			type="button"
			id="send"
			class="action_btn send_btn"
			disabled={pdfFile.criteria.length === 0}
			onclick={async () => {
				await send(pdfFile.criteria.map((criterion) => criterion.id));
			}}>Get All New Feedback</button
		>
	</div>
</div>

<style>
	.criteria_panel {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.criteria_header h2 {
		margin: 0;
		font-size: 1.05rem;
		display: flex;
		align-items: baseline;
		gap: 0.4rem;
		min-width: 0;
	}

	.criteria_filename {
		font-weight: 400;
		opacity: 0.75;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.criteria_list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.criterion {
		overflow: hidden;
		display: flex;
		flex-direction: row;
		background-color: var(--bg-inner);
		padding: 0;
		border: 2px solid var(--border);
		border-radius: 10px;
	}

	.button_sidebar {
		display: flex;
		flex-direction: column;
		border-right: 2px solid var(--border);
		align-items: stretch;
	}

	.button_sidebar button {
		background-color: var(--bg-inner);
		color: var(--text);
		border: none;
		flex: 1;
		padding: 0.45rem 0.6rem;
		cursor: pointer;
	}

	.button_sidebar button:hover:not(:disabled) {
		filter: brightness(1.5);
	}

	.button_sidebar button:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.criterion_item {
		flex: 1;
		min-width: 0;
		padding: 0.65rem 0.75rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.criterion_header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		flex-direction: row;
	}

	.corner_item {
		flex-shrink: 0;
		font-size: 0.8rem;
		font-weight: 600;
	}

	.criterion_header > :first-child {
		flex: 1;
		min-width: 0;
	}

	input {
		padding: 0.35rem 0.5rem;
		margin: 0;
		background-color: var(--bg);
		color: var(--text);
		border: 1px solid var(--border);
		border-radius: 5px;
		font-size: 0.92rem;
	}

	.criterion_feedback {
		font-size: 0.88rem;
		line-height: 1.4;
		opacity: 0.9;
		word-break: break-word;
	}

	.verdict {
		font-weight: 600;
		margin-right: 0.25rem;
	}

	.criteria_actions {
		display: flex;
		gap: 0.6rem;
		align-items: center;
	}

	.action_btn {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.5rem 0.85rem;
		border-radius: 6px;
		border: 2px solid var(--border);
		background-color: var(--bg-inner);
		color: var(--text);
		cursor: pointer;
		font-size: 0.9rem;
	}

	.action_btn:hover:not(:disabled) {
		filter: brightness(1.25);
	}

	.action_btn:disabled {
		opacity: 0.45;
		cursor: not-allowed;
	}

	.send_btn {
		background-color: #3b82f6;
		border-color: #3b82f6;
		font-weight: 600;
	}
</style>
