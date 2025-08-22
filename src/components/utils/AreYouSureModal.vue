<template>
  <v-dialog
    v-model="model"
    aria-describedby="are-you-sure-text"
    aria-labelledby="are-you-sure-header"
    persistent
    role="alertdialog"
    :width="width"
  >
    <v-card class="modal-content">
      <v-card-title>
        <h3
          id="are-you-sure-header"
          :class="modalHeaderClass"
          class="font-weight-medium mx-2"
        >
          {{ modalHeader }}
        </h3>
      </v-card-title>
      <v-card-text id="are-you-sure-text" class="modal-body">
        <span v-html="text" />
        <slot />
      </v-card-text>
      <v-card-actions class="modal-footer">
        <ProgressButton
          id="are-you-sure-confirm"
          :action="confirm"
          :disabled="isProcessing"
          :in-progress="isProcessing"
          :text="buttonLabelConfirm"
        />
        <v-btn
          v-if="functionCancel"
          id="are-you-sure-cancel"
          :disabled="isProcessing"
          :text="buttonLabelCancel"
          variant="text"
          @click="functionCancel"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import {ref, watch} from 'vue'
import ProgressButton from '@/components/utils/ProgressButton.vue'
import {putFocusNextTick} from '@/utils'

const props = defineProps({
  buttonLabelCancel: {
    type: String,
    required: false,
    default: 'Cancel'
  },
  buttonLabelConfirm: {
    type: String,
    required: false,
    default: 'Confirm'
  },
  functionCancel: {
    default: undefined,
    required: false,
    type: Function
  },
  functionConfirm: {
    type: Function,
    required: true
  },
  modalHeader: {
    type: String,
    required: false,
    default: 'Are you sure?'
  },
  modalHeaderClass: {
    type: String,
    required: false,
    default: 'modal-header'
  },
  text: {
    type: String,
    required: false,
    default: ''
  },
  width: {
    default: 600,
    required: false,
    type: Number
  }
})

const focusLocked = ref(false)
const isProcessing = ref(false)
const model = defineModel({type: Boolean})

watch(model, isOpen => {
  if (isOpen) {
    setTimeout(() => focusLocked.value = isOpen, 500)
    putFocusNextTick('are-you-sure-confirm')
  } else {
    isProcessing.value = false
  }
})

const confirm = () => {
  isProcessing.value = true
  props.functionConfirm()
}
</script>
