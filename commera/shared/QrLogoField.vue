<script setup>
import { Button, FileUploader, TabButtons } from 'frappe-ui'

defineProps({ storeLogo: { type: String, default: null } })
const mode = defineModel('mode', { type: String, default: 'None' })
const image = defineModel('image', { type: String, default: null })

const MODES = ['None', 'Store logo', 'Upload'].map((value) => ({ label: value, value }))
const FILE_TYPES = ['image/png', 'image/jpeg', 'image/webp']

function validateFile(file) {
  if (!FILE_TYPES.includes(file.type)) return 'Upload a PNG, JPG or WebP. The PNG and PDF downloads cannot draw SVG.'
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div class="flex flex-col gap-2">
      <span class="text-sm text-ink-gray-5">Logo in the middle</span>
      <TabButtons v-model="mode" :options="MODES" class="self-start" />
    </div>

    <div v-if="mode === 'Store logo'" class="flex items-center gap-3 rounded-4 bg-surface-gray-1 p-3">
      <template v-if="storeLogo">
        <img :src="storeLogo" alt="" class="size-10 rounded-3 bg-white object-contain p-1" />
        <p class="text-p-sm text-ink-gray-6">Your storefront logo. It changes here when you change it for the store.</p>
      </template>
      <p v-else class="text-p-sm text-ink-gray-6">
        Your store has no PNG, JPG or WebP logo yet. Pick <b>Upload</b> to add one for the QR code only.
      </p>
    </div>

    <FileUploader
      v-else-if="mode === 'Upload'"
      :file-types="FILE_TYPES"
      :validate-file="validateFile"
      :private="false"
      doctype="Buy Links Settings"
      docname="Buy Links Settings"
      fieldname="qr_logo_image"
      @success="(file) => (image = file.file_url)"
    >
      <template #default="{ uploading, progress, error, openFileSelector }">
        <div class="flex items-center gap-3 rounded-4 bg-surface-gray-1 p-3">
          <button
            type="button"
            class="flex size-14 shrink-0 items-center justify-center overflow-hidden rounded-3 border border-dashed border-outline-gray-3 bg-white"
            aria-label="Upload a logo"
            @click="openFileSelector"
          >
            <img v-if="image" :src="image" alt="" class="size-full object-contain p-1" />
            <span v-else class="lucide-image-plus size-5 text-ink-gray-5" />
          </button>
          <div class="flex min-w-0 flex-1 flex-col gap-1">
            <p class="text-p-sm text-ink-gray-6">
              {{ uploading ? `Uploading ${progress}%` : 'A square PNG, JPG or WebP with some empty space around it.' }}
            </p>
            <p v-if="error" class="text-sm text-ink-red-6">{{ error }}</p>
            <div class="flex gap-2">
              <Button size="sm" :label="image ? 'Replace' : 'Upload'" :loading="uploading" @click="openFileSelector" />
              <Button v-if="image" size="sm" variant="ghost" label="Remove" @click="image = null" />
            </div>
          </div>
        </div>
      </template>
    </FileUploader>
  </div>
</template>
