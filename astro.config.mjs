// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://inmoia-eosin.vercel.app',
  vite: {
    plugins: [tailwindcss()]
  },
  integrations: [
    sitemap({
      serialize(item) {
        const path = new URL(item.url).pathname;
        if (path === '/') {
          item.priority = 1.0;
        } else if (path === '/herramientas' || path === '/herramientas/') {
          item.priority = 0.9;
        } else {
          // Artículos del blog (servidos en la raíz, no bajo /blog/)
          item.priority = 0.7;
        }
        return item;
      },
    }),
  ],
});
