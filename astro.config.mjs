import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://www.fotograf-spalder.com',
  output: 'static',
  compressHTML: false,
  trailingSlash: 'never',
  build: {
    format: 'file',
  },
});
