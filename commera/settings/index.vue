<script>
export const plugin = { label: 'Buy links', icon: 'link' }
</script>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { Button, LoadingText, SettingsRow, TextInput } from 'frappe-ui'
import { useMethodAction, useMethodRead } from '@commera/admin'
import QrColourField from '../shared/QrColourField.vue'
import QrLogoField from '../shared/QrLogoField.vue'
import { BACKGROUND_PRESETS, CODE_PRESETS, QR_STYLES, getScanWarning, isHexColour } from '../shared/qrSettings'

const settingsRequest = useMethodRead('commera_buy_links.api.get_settings')
const previewRequest = useMethodAction('commera_buy_links.api.get_qr_preview', { quiet: true })
const saveRequest = useMethodAction('commera_buy_links.api.save_settings', { quiet: true })

const form = ref(null)
const saved = ref(null)
const storeLogo = ref(null)
const previewSvg = ref('')
const problem = ref('')
const status = ref('')

watch(
  () => settingsRequest.data,
  (data) => {
    if (!data || form.value) return
    const { qr_preview, store_logo, ...values } = data
    form.value = { ...values }
    saved.value = { ...values }
    storeLogo.value = store_logo
    previewSvg.value = qr_preview
  },
  { immediate: true },
)

const previewSource = computed(() => `data:image/svg+xml;charset=utf-8,${encodeURIComponent(previewSvg.value)}`)
const scanWarning = computed(() => form.value && getScanWarning(form.value.qr_color, form.value.qr_background))

// The server draws the preview with the same code as the downloads, then the same values are saved.
// Edits queue behind each other, so a slow answer never overwrites a newer one.
let timer = null
let queue = Promise.resolve()

watch(
  form,
  () => {
    clearTimeout(timer)
    timer = setTimeout(flush, 300)
  },
  { deep: true },
)
onBeforeUnmount(() => timer && flush())

function flush() {
  timer = null
  queue = queue.then(refresh)
}

const errorText = (error) => error?.message?.replace(/^\s*\w*Error:\s*/, '').replace(/<[^>]+>/g, '') || 'Something went wrong'

async function refresh() {
  const values = { ...form.value }
  // The fields already say what is missing; the server would only repeat it.
  if (!isHexColour(values.qr_color) || !isHexColour(values.qr_background)) return
  if (values.qr_logo === 'Upload' && !values.qr_logo_image) return
  if (values.qr_logo === 'Store logo' && !storeLogo.value) return
  await previewRequest.submit({ values })
  if (previewRequest.error) {
    problem.value = errorText(previewRequest.error)
    return
  }
  problem.value = ''
  previewSvg.value = previewRequest.data
  if (JSON.stringify(values) === JSON.stringify(saved.value)) return

  status.value = 'Saving…'
  await saveRequest.submit({ values })
  if (saveRequest.error) {
    problem.value = errorText(saveRequest.error)
    status.value = ''
    return
  }
  saved.value = values
  status.value = 'Saved'
}

function swapColours() {
  const { qr_color, qr_background } = form.value
  Object.assign(form.value, { qr_color: qr_background, qr_background: qr_color })
}
</script>

<template>
  <LoadingText v-if="!form" class="py-6" />
  <div v-else class="flex flex-col">
    <p class="pt-5 text-sm text-ink-gray-5">General</p>
    <SettingsRow
      class="!border-t-0"
      title="Attribution window"
      description="How long after a click an order still counts for the link."
    >
      <div class="flex items-center gap-2">
        <TextInput v-model.number="form.attribution_days" type="number" min="0" class="w-24" aria-label="Attribution window in days" />
        <span class="text-base text-ink-gray-6">days</span>
      </div>
    </SettingsRow>

    <div class="flex items-center justify-between pt-5">
      <p class="text-sm text-ink-gray-5">QR code</p>
      <span v-if="status" class="flex items-center gap-1 text-sm text-ink-gray-5">
        <span v-if="status === 'Saved'" class="lucide-check size-3.5 text-ink-green-6" aria-hidden="true" />
        {{ status }}
      </span>
    </div>

    <div class="mt-3 grid items-start gap-6 md:grid-cols-[minmax(0,1fr)_14rem]">
      <div class="flex flex-col gap-6">
        <div class="flex flex-col gap-2">
          <span class="text-sm text-ink-gray-5">Style</span>
          <div class="grid grid-cols-3 gap-2" role="radiogroup" aria-label="QR style">
            <button
              v-for="style in QR_STYLES"
              :key="style"
              type="button"
              role="radio"
              :aria-checked="form.qr_style === style"
              class="flex flex-col items-center gap-2 rounded-4 border p-3 text-sm transition-colors"
              :class="
                form.qr_style === style
                  ? 'border-outline-gray-4 bg-surface-gray-2 text-ink-gray-9'
                  : 'border-outline-gray-1 text-ink-gray-6 hover:bg-surface-gray-1'
              "
              @click="form.qr_style = style"
            >
              <svg viewBox="0 0 9 9" class="size-9" aria-hidden="true">
                <g :fill="isHexColour(form.qr_color) ? form.qr_color : 'currentColor'">
                  <template v-for="[x, y] in [[0, 0], [3, 0], [6, 0], [0, 3], [6, 3], [3, 6], [6, 6], [0, 6]]" :key="`${x}${y}`">
                    <circle v-if="style === 'Dots'" :cx="x + 1.25" :cy="y + 1.25" r="1.2" />
                    <rect v-else :x="x" :y="y" width="2.5" height="2.5" :rx="style === 'Rounded' ? 0.8 : 0" />
                  </template>
                </g>
              </svg>
              {{ style }}
            </button>
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-ink-gray-5">Colours</span>
            <Button size="sm" variant="ghost" icon-left="lucide-arrow-up-down" label="Swap" @click="swapColours" />
          </div>
          <QrColourField v-model="form.qr_color" label="Code" :presets="CODE_PRESETS" />
          <QrColourField v-model="form.qr_background" label="Background" :presets="BACKGROUND_PRESETS" />
          <p v-if="scanWarning" class="flex gap-1.5 text-p-sm text-ink-amber-7">
            <span class="lucide-triangle-alert mt-0.5 size-3.5 shrink-0" aria-hidden="true" />
            {{ scanWarning }}
          </p>
        </div>

        <QrLogoField v-model:mode="form.qr_logo" v-model:image="form.qr_logo_image" :store-logo="storeLogo" />
      </div>

      <div class="flex flex-col gap-2 md:sticky md:top-0">
        <div
          class="rounded-5 border border-outline-gray-1 p-4 transition-opacity"
          :class="previewRequest.loading && 'opacity-70'"
          :style="{ backgroundColor: isHexColour(form.qr_background) ? form.qr_background : undefined }"
        >
          <img :src="previewSource" alt="Preview of the QR code" class="w-full" />
        </div>
        <p v-if="problem" class="text-p-sm text-ink-red-6">{{ problem }}</p>
        <p v-else class="text-p-sm text-ink-gray-5">
          Every link's QR code and download uses this style. Scan this sample with your phone to check it.
        </p>
      </div>
    </div>
  </div>
</template>
