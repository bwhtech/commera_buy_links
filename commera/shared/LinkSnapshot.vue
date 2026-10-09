<script setup>
import { computed } from 'vue'
import { money, useMethodRead } from '@commera/admin'
import CheckoutFunnel from './CheckoutFunnel.vue'

// A fixed 30-day glance beside every tab; the Analytics tab is where the period changes.
const props = defineProps({ name: { type: String, required: true } })

const statsRequest = useMethodRead('commera_buy_links.api.get_link_stats', {
  params: () => ({ name: props.name, period: '30d' }),
  refetch: true,
})
const totals = computed(() => statsRequest.data?.totals ?? {})
const figures = computed(() => [
  { label: 'Clicks', value: totals.value.clicks ?? 0 },
  { label: 'Orders', value: totals.value.orders ?? 0 },
  { label: 'Conversion', value: `${totals.value.conversion ?? 0}%` },
  { label: 'Sales', value: money(totals.value.sales ?? 0) },
])
</script>

<template>
  <section class="rounded-5 border border-outline-gray-1 p-4">
    <h2 class="text-lg-semibold text-ink-gray-8">Last 30 days</h2>
    <dl class="mt-3 grid grid-cols-2 gap-x-4 gap-y-3">
      <div v-for="figure in figures" :key="figure.label">
        <dt class="text-sm text-ink-gray-5">{{ figure.label }}</dt>
        <dd class="mt-0.5 text-lg-semibold text-ink-gray-9 tabular-nums">{{ figure.value }}</dd>
      </div>
    </dl>
    <CheckoutFunnel class="mt-4 border-t border-outline-gray-1 pt-4" :totals="totals" compact />
  </section>
</template>
