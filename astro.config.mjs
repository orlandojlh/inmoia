// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://inmoia-eosin.vercel.app',
  vite: {
    plugins: [tailwindcss()]
  },
  integrations: [sitemap()],
});
