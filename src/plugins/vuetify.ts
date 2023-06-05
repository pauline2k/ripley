import '@mdi/font/css/materialdesignicons.css'
import {createVuetify} from 'vuetify'

// Temporary workaround to enable data tables under Vue 3 + Vuetify. https://vuetifyjs.com/en/labs/introduction/
import {VDataTable, VDataTableVirtual} from 'vuetify/labs/VDataTable'

// @ts-ignore
import colors from 'vuetify/lib/util/colors'

export default createVuetify({
  components: {
    VDataTable,
    VDataTableVirtual,
  },
  theme: {
    themes: {
      light: {
        colors: {
          error: '#b94a48',
          info: '#3a87ad',
          primary: '#3b7ea1',
          red: colors.red.darken1,
          secondary: '#eee',
          success: '#468847'
        },
      },
    },
  },
})
