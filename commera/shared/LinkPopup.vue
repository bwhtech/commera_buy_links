<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { Alert, Button, FormControl, Switch } from 'frappe-ui'

// `form` is the page's draft: the switches edit it in place and the page's Save stores it.
const props = defineProps({
  form: { type: Object, required: true },
  link: { type: Object, required: true },
})

const frame = ref(null)
const previewUrl = computed(() => `/en?buy=${encodeURIComponent(props.link.name)}&preview=1`)
const settings = computed(() =>
  Object.fromEntries(Object.entries(props.form).filter(([field]) => field.startsWith('popup_'))),
)

// The preview is the real storefront script; unsaved edits reach it by message, on this same origin only.
function sendDraft() {
  frame.value?.contentWindow?.postMessage(
    { type: 'commera-buy-links:preview', settings: JSON.parse(JSON.stringify(settings.value)) },
    window.location.origin,
  )
}
watch(settings, sendDraft, { deep: true })

// The storefront script says when its popup is drawn, so the draft never arrives before there is a popup to apply it to.
function onMessage(event) {
  if (event.origin === window.location.origin && event.data?.type === 'commera-buy-links:ready') sendDraft()
}
window.addEventListener('message', onMessage)
onBeforeUnmount(() => window.removeEventListener('message', onMessage))

const toggle = (field) =>
  computed({
    get: () => Boolean(props.form[field]),
    set: (value) => (props.form[field] = value ? 1 : 0),
  })
const isEnabled = toggle('popup_enabled')
const hasConsent = toggle('popup_consent')
const hasCountdown = toggle('popup_countdown')
</script>

<template>
  <div class="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_24rem]">
    <div class="flex flex-col gap-6">
      <Alert
        v-if="!link.storefront_enabled"
        theme="amber"
        title="The storefront can't show popups yet"
        description="Turn on Run on the storefront for Buy Links under Settings > Plugins. Until then, links go straight to checkout and the preview stays empty."
        :primary-action="{ label: 'Open Settings > Plugins', route: '/settings/plugins' }"
      />

      <section class="rounded-5 border border-outline-gray-1 p-4">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg-semibold text-ink-gray-8">Popup</h2>
            <p class="mt-1 text-sm text-ink-gray-5">Shows the offer over your storefront before checkout.</p>
          </div>
          <Switch v-model="isEnabled" label="On" />
        </div>
        <div class="mt-4 flex flex-col gap-4">
          <FormControl
            v-model="form.popup_callout"
            type="textarea"
            label="Message"
            placeholder="Your second mat is 10% off. Pick how many you need."
          />
          <div class="grid gap-4 sm:grid-cols-2">
            <FormControl v-model="form.popup_button_label" label="Checkout button" />
            <FormControl
              v-model="form.popup_skip_label"
              label="Skip link"
              description="Leave empty to hide it."
            />
          </div>
        </div>
      </section>

      <section class="rounded-5 border border-outline-gray-1 p-4">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-lg-semibold text-ink-gray-8">Consent</h2>
          <Switch v-model="hasConsent" label="Ask" />
        </div>
        <div v-if="hasConsent" class="mt-4 flex flex-col gap-4">
          <FormControl v-model="form.popup_consent_label" label="Checkbox label" />
          <FormControl
            v-model="form.popup_consent_terms"
            type="textarea"
            label="Terms"
            description="Shoppers open these under the checkbox."
          />
        </div>
      </section>

      <section class="rounded-5 border border-outline-gray-1 p-4">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-lg-semibold text-ink-gray-8">Countdown</h2>
          <Switch v-model="hasCountdown" label="Show" />
        </div>
        <div v-if="hasCountdown" class="mt-4 grid gap-4 sm:grid-cols-[8rem_minmax(0,1fr)]">
          <FormControl v-model="form.popup_countdown_minutes" type="number" label="Minutes" />
          <FormControl
            v-model="form.popup_countdown_text"
            label="Text"
            description="{timer} shows the time left. At zero the popup closes and the shopper stays in the store."
          />
        </div>
      </section>
    </div>

    <section class="rounded-5 border border-outline-gray-1 p-3 xl:sticky xl:top-4">
      <div class="flex items-center justify-between gap-2 px-1">
        <h2 class="text-base-medium text-ink-gray-8">Preview</h2>
        <Button variant="ghost" icon="lucide-rotate-cw" tooltip="Reload preview" @click="frame?.contentWindow?.location.reload()" />
      </div>
      <p class="px-1 text-sm text-ink-gray-5">
        Your storefront on a phone. Edits show here at once; cart changes show after Save.
      </p>
      <iframe
        ref="frame"
        :src="previewUrl"
        title="Popup preview"
        class="mt-2 h-[42rem] w-full rounded-4 border border-outline-gray-1 bg-surface-gray-1"
      />
    </section>
  </div>
</template>
