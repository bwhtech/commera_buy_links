<script setup>
import { computed } from 'vue'
import { FunnelChart } from 'frappe-ui/charts'
import { EmptyState } from '@commera/admin'

const props = defineProps({
  totals: { type: Object, default: () => ({}) },
  // In the side panel each stage gets a third of 20rem, so the labels shorten and the plot is lower.
  compact: { type: Boolean, default: false },
})

// "Reached checkout" counts carts tagged with the link: Commera saves the cart when the shopper reaches checkout.
const stages = computed(() => [
  { stage: 'Clicks', count: props.totals.clicks ?? 0 },
  { stage: props.compact ? 'Checkout' : 'Reached checkout', count: props.totals.checkouts ?? 0 },
  { stage: 'Orders', count: props.totals.orders ?? 0 },
])
</script>

<template>
  <EmptyState
    v-if="!totals.clicks"
    compact
    icon="lucide-filter"
    title="No funnel yet"
    description="It shows where shoppers drop off once the link gets clicks."
  />
  <div v-else :class="compact ? 'h-48' : 'h-64'">
    <FunnelChart :data="stages" category="stage" value="count" />
  </div>
</template>
