import vue from '@vitejs/plugin-vue'
import vuetify, {transformAssetUrls} from 'vite-plugin-vuetify'
import {defineConfig} from 'vite'
import {fileURLToPath, URL} from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
  base: process.env.NODE_ENV === 'development' ? '/' : '/static',
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @use "./src/assets/styles/colors.scss" as *;
          @use "./src/assets/styles/variables.scss" as *;
        `
      }
    }
  },
  define: {'process.env': {}},
  plugins: [
    vue({
      template: {transformAssetUrls}
    }),
    vuetify({
      autoImport: true,
      styles: {configFile: 'src/main.scss'}
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
    extensions: [
      '.js',
      '.json',
      '.jsx',
      '.mjs',
      '.ts',
      '.tsx',
      '.vue'
    ]
  },
  server: {
    port: 8080
  }
})
