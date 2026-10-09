<script setup>
import { computed, ref } from 'vue'
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from 'frappe-ui/list'
import { EmptyState, ListPagination, ListSkeleton, StatusBadge, money, shortDate, useMethodRead } from '@commera/admin'

const props = defineProps({ name: { type: String, required: true } })

const page = ref(1)
const pageSize = ref(20)
const ordersRequest = useMethodRead('commera_buy_links.api.get_link_orders', {
  params: () => ({ name: props.name, start: (page.value - 1) * pageSize.value, page_length: pageSize.value }),
  refetch: true,
})
const rows = computed(() => ordersRequest.data?.rows ?? [])
const total = computed(() => ordersRequest.data?.total ?? 0)
</script>

<template>
  <div>
    <List :row-height="56" :columns="['minmax(0,1fr)', '7rem', '11rem', '8rem']">
      <ListHeader>
        <ListHeaderCell>Order</ListHeaderCell>
        <ListHeaderCell>Placed</ListHeaderCell>
        <ListHeaderCell>Stage</ListHeaderCell>
        <ListHeaderCell class="justify-end">Total</ListHeaderCell>
      </ListHeader>
      <ListSkeleton v-if="ordersRequest.loading && !rows.length" :columns="4" />
      <ListRows v-else :items="rows" row-key="name" v-slot="{ item }">
        <ListRow :to="`/orders/${item.name}`" :value="item.name">
          <ListCell>
            <div class="min-w-0">
              <p class="truncate text-base text-ink-gray-8">{{ item.customer_name }}</p>
              <p class="mt-0.5 truncate text-sm text-ink-gray-5 tabular-nums">{{ item.name }}</p>
            </div>
          </ListCell>
          <ListCell><span class="text-base text-ink-gray-7">{{ shortDate(item.transaction_date) }}</span></ListCell>
          <ListCell><StatusBadge v-if="item.stage" :status="item.stage.key" :label="item.stage.label" /></ListCell>
          <ListCell class="justify-end"><span class="text-base text-ink-gray-8 tabular-nums">{{ money(item.total) }}</span></ListCell>
        </ListRow>
      </ListRows>
    </List>
    <ListPagination v-if="total" v-model:page="page" v-model:page-size="pageSize" :total="total" />
    <EmptyState
      v-if="!ordersRequest.loading && !rows.length"
      icon="lucide-shopping-bag"
      title="No orders yet"
      description="Orders placed through this link show here."
    />
  </div>
</template>
