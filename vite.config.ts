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
        // Order matters in the list below.
        additionalData: `
          @import "./src/styles/colors.scss";
          @import "./src/styles/_bootstrap_variables.scss";
          @import "./src/styles/_canvas_colors.scss";
          @import "./src/styles/_alerts.scss";
          @import "./src/styles/_base.scss";
          @import "./src/styles/_buttons.scss";
          @import "./src/styles/_canvas_base.scss";
          @import "./src/styles/_canvas_buttons.scss";
          @import "./src/styles/_canvas_embedded.scss";
          @import "./src/styles/_containers.scss";
          @import "./src/styles/_disabled_links.scss";
          @import "./src/styles/_flexbox.scss";
          @import "./src/styles/_footer.scss";
          @import "./src/styles/_google_reminder.scss";
          @import "./src/styles/_header.scss";
          @import "./src/styles/_icons.scss";
          @import "./src/styles/_junction.scss";
          @import "./src/styles/_lists.scss";
          @import "./src/styles/_logo.scss";
          @import "./src/styles/_navigation.scss";
          @import "./src/styles/_offcanvas.scss";
          @import "./src/styles/_print.scss";
          @import "./src/styles/_profile_bconnected.scss";
          @import "./src/styles/_scrollbars.scss";
          @import "./src/styles/_selects.scss";
          @import "./src/styles/_status.scss";
          @import "./src/styles/_tables.scss";
          @import "./src/styles/_text.scss";
          @import "./src/styles/_toolbox.scss";
          @import "./src/styles/_useful.scss";
          @import "./src/styles/_user_search.scss";
          @import "./src/styles/_widgets.scss";
          @import "./src/styles/_youtube_videos.scss";
          @import './src/styles/junction-global.scss';
        `
      }
    }
  },
  define: {'process.env': {}},
  plugins: [
    vue({
      template: {transformAssetUrls}
    }),
    // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vite-plugin
    vuetify({
      autoImport: true,
      styles: {
        configFile: 'src/styles/settings.scss'
      }
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
