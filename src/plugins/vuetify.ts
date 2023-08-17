import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import {aliases, mdi} from 'vuetify/iconsets/mdi'
import {createVuetify} from 'vuetify'
import {VAlert} from 'vuetify/components/VAlert'
import {VAppBar, VAppBarTitle} from 'vuetify/components/VAppBar'
import {VApp} from 'vuetify/components/VApp'
import {VBtn} from 'vuetify/components/VBtn'
import {VCard, VCardActions, VCardText, VCardTitle} from 'vuetify/components/VCard'
import {VCheckbox} from 'vuetify/components/VCheckbox'
import {VCol, VContainer, VSpacer, VRow} from 'vuetify/components/VGrid'
import {VDataTable, VDataTableVirtual} from 'vuetify/labs/VDataTable'
import {VDialog} from 'vuetify/components/VDialog'
import {VIcon} from 'vuetify/components/VIcon'
import {VImg} from 'vuetify/components/VImg'
import {VList, VListItem, VListItemAction, VListItemTitle} from 'vuetify/components/VList'
import {VMain} from 'vuetify/components/VMain'
import {VMenu} from 'vuetify/components/VMenu'
import {VProgressCircular} from 'vuetify/components/VProgressCircular'
import {VSnackbar} from 'vuetify/components/VSnackbar'
import {VSwitch} from 'vuetify/components/VSwitch'
import {VTextField} from 'vuetify/components/VTextField'

// @ts-ignore
import colors from 'vuetify/lib/util/colors'

export default createVuetify({
  components: {
    VAlert,
    VApp,
    VAppBar,
    VAppBarTitle,
    VBtn,
    VCard,
    VCardActions,
    VCardText,
    VCardTitle,
    VCheckbox,
    VCol,
    VContainer,
    VDataTable,
    VDataTableVirtual,
    VDialog,
    VIcon,
    VImg,
    VList,
    VListItem,
    VListItemAction,
    VListItemTitle,
    VMain,
    VMenu,
    VProgressCircular,
    VRow,
    VSnackbar,
    VSpacer,
    VSwitch,
    VTextField
  },
  display: {
    thresholds: {
      xs: 0,
      sm: 576,
      md: 768,
      lg: 992,
      xl: 1200
    }
  },
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
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
