import { defineConfig } from 'astro/config';
import { mkdir, rename } from 'node:fs/promises';

const restorationDirectoryRoute = {
  name: 'restoration-directory-route',
  hooks: {
    'astro:build:done': async ({ dir }) => {
      const targetDirectory = new URL('restaurering-gamle-bilder/', dir);
      await mkdir(targetDirectory, { recursive: true });
      await rename(
        new URL('restaurering-gamle-bilder.html', dir),
        new URL('restaurering-gamle-bilder/index.html', dir),
      );
    },
  },
};

export default defineConfig({
  site: 'https://www.fotograf-spalder.com',
  output: 'static',
  compressHTML: false,
  trailingSlash: 'never',
  build: {
    format: 'file',
  },
  integrations: [restorationDirectoryRoute],
});
