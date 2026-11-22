import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  // Dev server: proxy as chamadas /api/ para o Django (porta 8000)
  // Assim não há CORS durante o desenvolvimento com Vite separado.
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    // Saída no dist/ padrão — Django vai servir de lá via WhiteNoise
    outDir: 'dist',
    emptyOutDir: true,
    // Assets com hash para cache-busting
    assetsDir: 'assets',
    // Mantém o sourcemap apenas em dev (não mandar para prod)
    sourcemap: false,
    rollupOptions: {
      output: {
        // Divide chunks maiores para carregamento lazy eficiente
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'tiptap-vendor': [
            '@tiptap/vue-3',
            '@tiptap/starter-kit',
            '@tiptap/extension-image',
            '@tiptap/extension-table',
            '@tiptap/extension-table-cell',
            '@tiptap/extension-table-header',
            '@tiptap/extension-table-row',
          ],
        },
      },
    },
  },
});
