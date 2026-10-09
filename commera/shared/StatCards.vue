<script setup>
import { computed } from 'vue'
import { NumberCard } from 'frappe-ui/charts'
import { money } from '@commera/admin'
import { percentChange, periodCaption } from './periods'

const props = defineProps({
  stats: { type: Object, default: null },
  period: { type: String, required: true },
  loading: { type: Boolean, default: false },
  // Four across needs the full page width; beside the side panel the captions would truncate.
  narrow: { type: Boolean, default: false },
})

const cards = computed(() => {
  const totals = props.stats?.totals ?? {}
  const previous = props.stats?.previous ?? {}
  const series = props.stats?.series ?? []
  const trend = (key) => (series.length > 1 ? { data: series.map((day) => day[key]) } : undefined)
  return [
    { title: 'Clicks', value: totals.clicks ?? 0, delta: percentChange(totals.clicks, previous.clicks), sparkline: trend('clicks') },
    { title: 'Orders', value: totals.orders ?? 0, delta: percentChange(totals.orders, previous.orders), sparkline: trend('orders') },
    {
      title: 'Conversion',
      value: totals.conversion ?? 0,
      suffix: '%',
      precision: 1,
      delta: percentChange(totals.conversion, previous.conversion),
    },
    { title: 'Sales', value: money(totals.sales ?? 0), delta: percentChange(totals.sales, previous.sales), sparkline: trend('sales') },
  ]
})
</script>

<template>
  <div class="grid grid-cols-2 gap-3" :class="{ 'lg:grid-cols-4': !narrow }">
    <NumberCard
      v-for="card in cards"
      :key="card.title"
      v-bind="card"
      :loading="loading && !stats"
      delta-suffix="%"
      :delta-caption="periodCaption(period)"
    />
  </div>
</template>
