<script>
  import Router from 'svelte-spa-router';

  import Home from './routes/home/page.svelte';
  import Login from './routes/login/page.svelte';

  const routes = {
    '/': Home,
    '/login': Login,
  };
</script>

<Router {routes} />
