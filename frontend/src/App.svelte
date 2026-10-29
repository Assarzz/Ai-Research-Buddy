<script>
	let user = $state('')
	let mode = $state('core_eval_standard')
	let text = $state('')
	let result = $state('')

	fetch("/api/get_user")
		.then(r => r.json())
		.then(data => user = data.user);

	async function send() {
		const resp = await fetch("/grade_paper", {
			method: "POST",
			headers: {
				"Content-Type": "text/plain",
				"Review-mode": mode,
			},
			body: text
		});

		result = await resp.text();
	}
</script>

<h1 class="title">AI research buddy</h1>
<h1 class="title">Hello: {user}</h1>

<div class="center">
	<div class="move-good">

		<select id="grading_type" bind:value={mode}>
			<option value="core_eval_standard">Core eval standard</option>
			<option value="just_wing_it">Normal AI review</option>
		</select>
		<br>
		<textarea id="paper" placeholder="insert paper here" bind:value={text}></textarea>
		<br>
		<button id="send" onclick={send}>FEEDBACK</button>
		<div id="resp">{result}</div>
	</div>
</div>

<style>
	:global(body) {
		background-color: #243119;
		color: #C9F2C7;
		padding: 8vw;
	}

	.title {
		text-align: center;
	}
	.center {
		display: flex;
		justify-content: center;
		align-items: center;
		border: 3px solid #629460;
		border-radius: 3px;

		background-color: #96BE8C;
		color: #243119;
	}

	:global(.wrong) {
		color: red;
	}

	.move-good {
		text-align: center;
		padding: 2vw
	}
</style>
