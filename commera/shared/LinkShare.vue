<script setup>
import { computed } from 'vue'
import { Button, Dropdown, TextInput } from 'frappe-ui'
import { useLinkActions } from './useLinkActions'

const props = defineProps({
  url: { type: String, required: true },
  qrSvg: { type: String, required: true },
  code: { type: String, required: true },
})

const { copy } = useLinkActions()
const path = computed(() => new URL(props.url).pathname)
// Files come from the server so PNG and PDF match the SVG here, in the style set under Settings > Buy links.
const downloadOptions = ['svg', 'png', 'pdf'].map((fileFormat) => ({
  label: fileFormat.toUpperCase(),
  icon: 'lucide-download',
  onClick: () =>
    window.open(
      `/api/method/commera_buy_links.api.download_qr?name=${encodeURIComponent(props.code)}&file_format=${fileFormat}`,
      '_blank',
    ),
}))
const qrSource = computed(() => `data:image/svg+xml;charset=utf-8,${encodeURIComponent(props.qrSvg)}`)
</script>

<template>
  <section class="rounded-5 border border-outline-gray-1 p-4">
    <h2 class="text-lg-semibold text-ink-gray-8">Share</h2>
    <div class="mt-3 flex gap-2">
      <TextInput class="min-w-0 flex-1 font-mono" :model-value="path" readonly aria-label="Link path" />
      <Button icon="lucide-copy" tooltip="Copy link" @click="copy(url)" />
      <Button icon="lucide-external-link" tooltip="Open link" :link="url" />
    </div>
    <img :src="qrSource" alt="QR code for this link" class="mx-auto mt-4 w-36 rounded-4 bg-white p-1" />
    <div class="mt-2 flex justify-center">
      <Dropdown
        :options="downloadOptions"
        align="center"
        :button="{ label: 'Download QR code', iconLeft: 'lucide-download', iconRight: 'lucide-chevron-down', variant: 'ghost' }"
      />
    </div>
  </section>
</template>
