<script setup>
import { computed, ref } from 'vue'
import { TabButtons } from 'frappe-ui'
import { BarChart } from 'frappe-ui/charts'
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from 'frappe-ui/list'
import { EmptyState, money, shortDate, useMethodRead } from '@commera/admin'
import CheckoutFunnel from './CheckoutFunnel.vue'
import StatCards from './StatCards.vue'
import TrendChart from './TrendChart.vue'
import { PERIODS } from './periods'

// With `name`, one link's numbers; without it, every link together plus the links that sold most.
const props = defineProps({ name: { type: String, default: null } })

const period = ref('30d')
const statsRequest = useMethodRead(
  props.name ? 'commera_buy_links.api.get_link_stats' : 'commera_buy_links.api.get_overview',
  { params: () => ({ ...(props.name ? { name: props.name } : {}), period: period.value }), refetch: true },
)
const stats = computed(() => statsRequest.data)
const activeDays = computed(() =>
  [...(stats.value?.series ?? [])]
    .filter((day) => day.clicks || day.orders)
    .reverse()
    .map((day) => ({ ...day, conversion: day.clicks ? Math.round((day.orders / day.clicks) * 1000) / 10 : 0 })),
)
const topLinks = computed(() => stats.value?.top_links ?? [])
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-end">
      <TabButtons v-model="period" :options="PERIODS" />
    </div>

    <StatCards :stats="stats" :period="period" :loading="statsRequest.loading" :narrow="Boolean(name)" />

    <section class="rounded-5 border border-outline-gray-1 p-4">
      <h2 class="text-lg-semibold text-ink-gray-8">Clicks and orders per day</h2>
      <TrendChart class="mt-3" :series="stats?.series" />
    </section>

    <section v-if="name" class="rounded-5 border border-outline-gray-1 p-4">
      <h2 class="text-lg-semibold text-ink-gray-8">Where shoppers drop off</h2>
      <CheckoutFunnel class="mt-3" :totals="stats?.totals" />
    </section>

    <section v-else class="rounded-5 border border-outline-gray-1 p-4">
      <h2 class="text-lg-semibold text-ink-gray-8">Top links by sales</h2>
      <EmptyState
        v-if="!topLinks.length"
        compact
        icon="lucide-chart-column"
        title="No sales in this period"
        description="Links that bring orders show here."
      />
      <div v-else class="mt-3 h-56">
        <BarChart :data="topLinks" x="title" :y="['sales']" :series-config="{ sales: { label: 'Sales' } }" horizontal />
      </div>
    </section>

    <section v-if="activeDays.length">
      <h2 class="text-lg-semibold text-ink-gray-8">By day</h2>
      <List class="mt-2" :row-height="44" :columns="['minmax(0,1fr)', '6rem', '6rem', '7rem', '8rem']">
        <ListHeader>
          <ListHeaderCell>Date</ListHeaderCell>
          <ListHeaderCell class="justify-end">Clicks</ListHeaderCell>
          <ListHeaderCell class="justify-end">Orders</ListHeaderCell>
          <ListHeaderCell class="justify-end">Conversion</ListHeaderCell>
          <ListHeaderCell class="justify-end">Sales</ListHeaderCell>
        </ListHeader>
        <ListRows :items="activeDays" row-key="date" v-slot="{ item }">
          <ListRow>
            <ListCell><span class="text-base text-ink-gray-8">{{ shortDate(item.date) }}</span></ListCell>
            <ListCell class="justify-end"><span class="text-base text-ink-gray-7 tabular-nums">{{ item.clicks }}</span></ListCell>
            <ListCell class="justify-end"><span class="text-base text-ink-gray-7 tabular-nums">{{ item.orders }}</span></ListCell>
            <ListCell class="justify-end"><span class="text-base text-ink-gray-7 tabular-nums">{{ item.conversion }}%</span></ListCell>
            <ListCell class="justify-end"><span class="text-base text-ink-gray-8 tabular-nums">{{ money(item.sales) }}</span></ListCell>
          </ListRow>
        </ListRows>
      </List>
    </section>
  </div>
</template>
