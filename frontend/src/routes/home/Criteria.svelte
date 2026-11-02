<script lang="ts">

    let { selectedPdf = $bindable() } = $props();

	type Criterion = {
		id: number;
		text: string;
		status: 'old' | 'unloaded' | 'loading' | 'loaded';
		verdict: string;
		explanation: string;
	};

	let nextId = 0;
	function newCriterion(text: string): Criterion {
		const id = nextId;
		nextId += 1
		return {id, text, status: "unloaded", verdict: "...", explanation: "..."}
	}
	function getCriterion(id: number): Criterion{
		for (const c of criteria){
			if (id == c.id){
				return c
			}
		}
		// If id doesn't exist, return first criterion
		return criteria[0]
	}
    let criteria = $state([newCriterion('The Paper has an abstract'), newCriterion('Abstract is good')]);

	async function send(ids_to_update: number[]) {
		if (!selectedPdf){
			return
		}

		// Update the status of each criterion object
		for (const id of ids_to_update){
			getCriterion(id).status = "loading"
		}

		// Get feedback
		const formData = new FormData();
		formData.append("pdfFile", selectedPdf);
		for (const id of ids_to_update) formData.append("criteria", getCriterion(id).text);

		const resp = await fetch("/api/grade_paper", { method: "POST", body: formData });		
		const reader = resp.body.pipeThrough(new TextDecoderStream()).getReader();
		let buffer = '';
		let looking_for = 0;
		while (looking_for < ids_to_update.length) {
			const { value, done } = await reader.read();
			if (done) break;
			buffer += value;
			const lines = buffer.split("\n");
			buffer = lines.pop()!;
			for (const line of lines) {
				if (!line.trim()) continue;
				const res = JSON.parse(line);
				const c = getCriterion(ids_to_update[looking_for++]);
				c.verdict = res.verdict;
				c.explanation = res.explanation;
				c.status = "loaded"
			}
		}
	}

</script>


<h1>Criteria: </h1>
{#each criteria as criterion, i}
<div class="criterion">

    <!--  minus button https://allsvgicons.com/search/?q=minus -->
    <button onclick={()=>{
        criteria.splice(i, 1);
    }}> 
        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><title>baseline-minus</title><path fill="currentColor" d="M19 12.998H5v-2h14z"/></svg>
    </button>   
 
    <!-- redo button-->
    <button onclick={async ()=>{
		await send([criterion.id])
    }}> 
        <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><title>redo</title><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><path d="M18.364 18.364A9 9 0 1 1 12 3c4.058 0 6.518 2.705 9 5.5"/><path d="M21 4.5v4h-4"/></g></svg>
    </button>
    <div>
		<div class="criterion_header">
			<input type="text" bind:value="{criterion.text}" />
			<p>{`status=${criterion.status}`}</p>
		</div>
        
        <h3> {
            `[${criteria[i]["verdict"]}] ${criteria[i]["explanation"]}`
            } 
        </h3>
    </div>
    
</div>
{/each}

<!-- plus button-->
<button onclick={()=>criteria = [...criteria, newCriterion("...") ]}>
    <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24"><title>baseline-plus</title><path fill="currentColor" d="M19 12.998h-6v6h-2v-6H5v-2h6v-6h2v6h6z"/></svg>
</button>    
<button id="send" onclick={async ()=> {await send(criteria.map(criterion => criterion.id))
}}>Get All New Feedback</button>


<style>

    .criterion {
        display: flex;
        flex-direction: row;
    }
	.criterion_header{

		display: flex;
		gap: 1rem;
        flex-direction: row;
	}
	input {
		padding: 0;
		margin: 0;
	}
</style>