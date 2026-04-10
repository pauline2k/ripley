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
        <v-btn
          v-if="functionCancel && cancelButtonFirst"
          id="are-you-sure-cancel"
          class="mr-2"
          :color="cancelButtonColor"
          :disabled="isProcessing"
          :text="buttonLabelCancel"
          :variant="cancelButtonVariant"
          @click="functionCancel"
        />
        <ProgressButton
          id="are-you-sure-confirm"
          :action="confirm"
          class="mr-2"
          :color="confirmButtonColor"
          :disabled="isProcessing"
          :in-progress="isProcessing"
          :text="buttonLabelConfirm"
          :variant="confirmButtonVariant"
        />
        <v-btn
          v-if="functionCancel && !cancelButtonFirst"
          id="are-you-sure-cancel"
          :color="cancelButtonColor"
          :disabled="isProcessing"
          :text="buttonLabelCancel"
          :variant="cancelButtonVariant"
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
  cancelButtonColor: {
    type: String,
    required: false,
    default: undefined
  },
  cancelButtonFirst: {
    type: Boolean,
    required: false
  },
  cancelButtonVariant: {
    type: String,
    required: false,
    default: 'text'
  },
  confirmButtonColor: {
    type: String,
    required: false,
    default: 'primary'
  },
  confirmButtonVariant: {
    type: String,
    required: false,
    default: 'flat'
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
  initialFocusTarget: {
    type: String,
    required: false,
    default: 'confirm'
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
    putFocusNextTick(props.initialFocusTarget === 'cancel' ? 'are-you-sure-cancel' : 'are-you-sure-confirm')
  } else {
    isProcessing.value = false
  }
})

const confirm = () => {
  isProcessing.value = true
  props.functionConfirm()
}
</script>
