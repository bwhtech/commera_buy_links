<script>
export const plugin = {
  label: 'Buy link',
  requires: 'Buy Link',
  condition: 'commera_buy_links.conditions.order_has_link',
}
</script>

<script setup>
import { Button } from 'frappe-ui'
import { useMethodRead, usePlugin } from '@commera/admin'

const { record } = usePlugin()
const linkRequest = useMethodRead('commera_buy_links.api.get_order_link', {
  params: () => ({ sales_order: record.value.name }),
})
</script>

<template>
  <div v-if="linkRequest.data" class="flex flex-col gap-2">
    <div class="flex items-center justify-between gap-2">
      <div class="min-w-0">
        <p class="truncate text-base text-ink-gray-8">{{ linkRequest.data.title }}</p>
        <p class="mt-0.5 truncate font-mono text-sm text-ink-gray-5">{{ linkRequest.data.path }}</p>
      </div>
      <Button
        variant="ghost"
        icon="lucide-arrow-up-right"
        tooltip="Open the link"
        :route="`/plugins/commera_buy_links/links/${linkRequest.data.name}`"
      />
    </div>
    <p v-if="linkRequest.data.coupon" class="text-sm text-ink-gray-6">Coupon {{ linkRequest.data.coupon }}</p>
    <p v-for="(value, key) in linkRequest.data.utm" :key="key" class="text-sm text-ink-gray-6">
      {{ key.replace('utm_', 'UTM ') }}: {{ value }}
    </p>
  </div>
</template>
