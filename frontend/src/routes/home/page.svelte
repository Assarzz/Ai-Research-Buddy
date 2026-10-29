<script lang="ts">
	import { onMount } from "svelte";
	import PdfViewer from "./PdfViewer.svelte";

	let selectedPdf = $state<File | undefined>();

	let { user } = $props();

	onMount(async () => {
		try {
			const response = await fetch("/api/hello");
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

	let mode = $state("core_eval_standard");
	let text = $state("");
	let result = $state("");

	async function send() {
		const resp = await fetch("/api/grade_paper", {
			method: "POST",
			headers: {
				"Content-Type": "text/plain",
				"Review-mode": mode,
			},
			body: text,
		});

		result = await resp.text();
	}
</script>

<div class="outer">
	<div class="left">
		<PdfViewer bind:selectedPdf></PdfViewer>
	</div>
	<div class="right">
		<h1 class="title">AI research buddy</h1>
		<h1 class="title">Hello: {user}</h1>

		<div class="center">
			<div class="move-good">
				<select id="grading_type" bind:value={mode}>
					<option value="core_eval_standard"
						>Core eval standard</option
					>
					<option value="just_wing_it">Normal AI review</option>
				</select>
				<button id="send" onclick={send}>FEEDBACK</button>
				<div id="resp">{result}</div>
			</div>
		</div>
	</div>
</div>

<style>
	.outer {
		display: flex;
		flex-direction: row;
		height: 100%;
	}

	.left,
	.right {
		flex: 1; /* each half takes an equal share of the width */
		min-width: 0; /* lets the halves shrink below their content width */
		border: 3px solid var(--border);
		border-radius: 3px;
	}

	embed {
		flex: 1;
		width: 100%;
	}

	.title {
		text-align: center;
	}
	.center {
		display: flex;
		justify-content: center;
		align-items: center;
		border: 3px solid var(--border);
		border-radius: 3px;

		background-color: var(--bg-inner);
		color: #243119;
	}

	:global(.wrong) {
		color: red;
	}

	.move-good {
		text-align: center;
		padding: 2vw;
	}
</style>
