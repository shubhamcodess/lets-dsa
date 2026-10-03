import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';

// Relative base + hash routing: the build works at any path (GitHub Pages project site,
// a custom domain, or a subfolder) without knowing it in advance.
export default defineConfig({
  base: process.env.SITE_BASE ?? './',
  plugins: [preact()],
  build: { target: 'es2022', cssCodeSplit: false, reportCompressedSize: true },
});
