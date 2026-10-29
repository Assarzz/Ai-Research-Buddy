
<script>
    let username = $state('');
    let password = $state('');
    let result = $state('');

    async function login(event) {
        event.preventDefault();
        result = '';

        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            window.location.href = `/`;
        } else {
            result = 'failed';
        }
    }
</script>

<svelte:head>
    <title>AI research buddy login</title>
</svelte:head>

<h1 class="title">Login to use the AI research buddy</h1>

<div class="center">
    <div class="move-good">
        <form onsubmit={login}>
            <input
                type="text"
                name="username"
                placeholder="example@emailservice.com"
                bind:value={username}
                autocomplete="username"
                required
            />

            <input
                type="password"
                name="password"
                placeholder="Password"
                bind:value={password}
                autocomplete="current-password"
                required
            />

            <br />
            <button type="submit">LOGIN</button>
        </form>

        <br />

        {#if result === 'failed'}
            <h2 class="wrong">INCORRECT LOGIN!</h2>
        {/if}
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

    .wrong {
        color: red;
    }

    .move-good {
        text-align: center;
        padding: 2vw;
    }

    input {
        display: block;
        margin: 10px auto;
        padding: 10px;
    }

    button {
        padding: 8px 20px;
        cursor: pointer;
    }
</style>

