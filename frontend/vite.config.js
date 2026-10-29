import { svelte } from '@sveltejs/vite-plugin-svelte'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: '../webhost/webpages/build',
    emptyOutDir: true,
  },
  
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000',
      '/grade_paper': 'http://127.0.0.1:5000',
    },
  },
})
