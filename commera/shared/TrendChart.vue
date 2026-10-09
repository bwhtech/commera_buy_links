<script setup>
import { computed } from 'vue'
import { AreaChart } from 'frappe-ui/charts'
import { EmptyState } from '@commera/admin'

const props = defineProps({ series: { type: Array, default: () => [] } })

const hasActivity = computed(() => props.series.some((day) => day.clicks || day.orders))
// Orders are a small share of clicks, so they get their own axis or they lie flat along the bottom.
const SERIES = {
  clicks: { label: 'Clicks' },
  orders: { label: 'Orders', axis: 'y2', type: 'line' },
}
</script>

<template>
  <p v-if="series.length < 2" class="px-3 py-10 text-center text-p-sm text-ink-gray-5">
    A trend needs more than one day. Pick 7 days or more.
  </p>
  <EmptyState
    v-else-if="!hasActivity"
    compact
    icon="lucide-chart-line"
    title="No clicks in this period"
    description="The chart fills in once shoppers open the link."
  />
  <div v-else class="h-64">
    <AreaChart :data="series" x="date" :y="['clicks', 'orders']" :series-config="SERIES" :x-axis="{ timeGrain: 'day' }" />
  </div>
</template>
