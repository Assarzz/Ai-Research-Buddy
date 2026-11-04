<script>
  import Router from 'svelte-spa-router';

  import Home from './routes/home/page.svelte';
  import Login from './routes/login/page.svelte';
  import Signup from './routes/signin/page.svelte'

  const routes = {
    '/': Home,
    '/login': Login,
    '/signup': Signup
  };
</script>

<Router {routes} />
