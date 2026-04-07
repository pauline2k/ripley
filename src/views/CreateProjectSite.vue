<template>
  <div v-if="!contextStore.isLoading" class="mx-10 my-5">
    <Header1 text="Create a Project Site" />
    <div>
      <v-alert
        v-if="error"
        density="compact"
        role="alert"
        :text="error"
        type="warning"
      />
      <div class="align-center d-flex justify-center pb-8 pt-4">
        <div class="pr-3">
          <label
            for="page-create-project-site-name"
            class="text-subtitle-1 font-weight-medium"
          >
            Project Site Name
          </label>
        </div>
        <div class="mr-16 w-50">
          <v-text-field
            id="page-create-project-site-name"
            v-model="name"
            class="w-100"
            density="comfortable"
            :disabled="isCreating"
            hide-details
            maxlength="255"
            variant="outlined"
            @keydown.enter="create"
          />
        </div>
      </div>
      <div class="d-flex justify-end">
        <v-btn
          id="create-project-site-button"
          class="mr-2"
          color="primary"
          type="submit"
          :disabled="isCreating || !trim(name)"
          @click="create"
        >
          <span v-if="!isCreating">Create a Project Site</span>
          <span v-if="isCreating">
            <v-progress-circular
              class="mr-1"
              indeterminate
              size="18"
            />
            Creating<span aria-hidden="true">...</span><span class="sr-only"> Project Site</span>
          </span>
        </v-btn>
        <v-btn
          id="cancel-and-return-to-site-creation"
          aria-label="Cancel and return to Site Creation Overview"
          :disabled="isCreating"
          type="button"
          variant="tonal"
          @click="cancel"
        >
          Cancel
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref} from 'vue'
import {trim} from 'lodash'
import Header1 from '@/components/utils/Header1.vue'
import {createProjectSite} from '@/api/canvas-site'
import {iframeParentLocation, isInIframe} from '@/utils'
import {useContextStore} from '@/stores/context'
import {useRouter} from 'vue-router'

const contextStore = useContextStore()
const error = ref()
const isCreating = ref<boolean>()
const name = ref()
const router = useRouter()

onMounted(() => {
  contextStore.loadingComplete()
})

const cancel = () => {
  router.push({path: '/manage_sites'})
}

const create = () => {
  if (!isCreating.value && trim(name.value)) {
    error.value = null
    isCreating.value = true
    contextStore.alertScreenReader('Creating project site.')
    createProjectSite(name.value).then(
      data => {
        contextStore.alertScreenReader('Done. Loading new project site.')
        if (isInIframe) {
          iframeParentLocation(data.url)
        } else {
          window.location.href = data.url
        }
      },
      error => {
        error.value = error
      }
    ).finally(() => {
      isCreating.value = false
    })
  }
}
</script>
