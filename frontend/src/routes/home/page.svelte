<script lang="ts">
	import { onMount } from "svelte";
	import PdfViewer from "./PdfViewer.svelte";
	import Criteria from "./Criteria.svelte";
	let selectedPdf = $state<File | undefined>();

	let { user } = $props();

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

	let mode = $state("core_eval_standard");
	



	let showPopup = $state(false);
    let customCriterion = $state("");
	
	async function saveCriterion() {
    const response = await fetch("/api/add_criteria", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            criteria: customCriterion
        })
    });

    console.log(await response.text());

    showPopup = false;
    customCriterion = "";
	}
	

</script>

<button onclick={() => showPopup = true}>
    Create Custom Criteria
</button>

{#if showPopup}
    <div class="popup">
        <h3>Create Custom Criterion</h3>

        <input
            bind:value={customCriterion}
            placeholder="Enter criterion"
        >
        <button onclick={saveCriterion}>
            Save
        </button>

        <button onclick={() => showPopup = false}>
            Cancel
        </button>
    </div>
{/if}

<div class="outer">
	<div class="left">
		<PdfViewer bind:selectedPdf></PdfViewer>
	</div>
	<div class="right">
		<h1 class="title">AI research buddy</h1>
		<h1 class="title">Hello: {user}</h1>
		
		<Criteria bind:selectedPdf></Criteria>

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
