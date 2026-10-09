<script>
export const plugin = { label: 'Links', icon: 'link', requires: 'Buy Link', order: 1 }
</script>

<script setup>
import { computed, ref, watch } from 'vue'
import { Badge, Dropdown, TabButtons, TextInput } from 'frappe-ui'
import { List, ListCell, ListHeader, ListHeaderCell, ListRow, ListRows } from 'frappe-ui/list'
import { EmptyState, ListPagination, ListSkeleton, money, useMethodRead, usePage, usePlugin } from '@commera/admin'
import CreateLinkDialog from '../../shared/CreateLinkDialog.vue'
import { useLinkActions } from '../../shared/useLinkActions'

const STATUS_FILTERS = [
  { label: 'All', value: '' },
  { label: 'Active', value: 'Active' },
  { label: 'Draft', value: 'Draft' },
]

const { navigate } = usePlugin()

const status = ref('')
const search = ref('')
const page = ref(1)
const pageSize = ref(20)
watch([status, search], () => (page.value = 1))

const linksRequest = useMethodRead('commera_buy_links.api.get_links', {
  params: () => ({
    status: status.value,
    search: search.value.trim(),
    start: (page.value - 1) * pageSize.value,
    page_length: pageSize.value,
  }),
  refetch: true,
})

const rows = computed(() => linksRequest.data?.rows ?? [])
const total = computed(() => linksRequest.data?.total ?? 0)
const isFiltered = computed(() => Boolean(status.value || search.value.trim()))

const isCreating = ref(false)
const { getMenuOptions } = useLinkActions({ onDeleted: () => linksRequest.reload() })

usePage().setActions([
  { label: 'Create link', icon: 'plus', variant: 'solid', onClick: () => (isCreating.value = true) },
])

// Below `sm` the List drops to two tracks, so a wider skeleton row would wrap to double height.
const skeletonColumns = window.matchMedia('(max-width: 639.98px)').matches ? 2 : 7
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <TabButtons v-model="status" :options="STATUS_FILTERS" />
    <TextInput
      v-model="search"
      class="w-full sm:ml-auto sm:w-64"
      type="search"
      placeholder="Search name, code or slug"
      :debounce="300"
    >
      <template #prefix>
        <span class="lucide-search size-4 text-ink-gray-5" aria-hidden="true" />
      </template>
    </TextInput>
  </div>

  <p class="mt-3 text-sm text-ink-gray-5">Clicks, orders and sales for the last 30 days.</p>
  <div class="mt-2 overflow-x-auto">
    <!-- frappe-ui 1.0.0-beta.55 takes columns as one array; --list-columns narrows it below sm. -->
    <List
      class="max-sm:[--list-columns:minmax(0,1fr)_6rem_2rem] sm:min-w-[54rem]"
      :row-height="60"
      :columns="['minmax(0,1fr)', '6rem', '5rem', '5rem', '6rem', '7rem', '2rem']"
    >
      <ListHeader>
        <ListHeaderCell>Link</ListHeaderCell>
        <ListHeaderCell class="max-sm:hidden">Status</ListHeaderCell>
        <ListHeaderCell class="justify-end max-sm:hidden">Clicks</ListHeaderCell>
        <ListHeaderCell class="justify-end max-sm:hidden">Orders</ListHeaderCell>
        <ListHeaderCell class="justify-end max-sm:hidden">Conversion</ListHeaderCell>
        <ListHeaderCell class="justify-end">Sales</ListHeaderCell>
        <ListHeaderCell />
      </ListHeader>

      <ListSkeleton v-if="linksRequest.loading && !rows.length" :columns="skeletonColumns" />

      <ListRows v-else :items="rows" row-key="name" v-slot="{ item }">
        <ListRow :value="item.name" @click="navigate(`links/${item.name}`)">
          <ListCell>
            <div class="min-w-0">
              <p class="truncate text-base text-ink-gray-8">{{ item.title }}</p>
              <p class="mt-0.5 truncate font-mono text-sm text-ink-gray-5">/buy/{{ item.slug || item.name }}</p>
            </div>
          </ListCell>
          <ListCell class="max-sm:hidden">
            <Badge :label="item.status" :theme="item.status === 'Active' ? 'green' : 'gray'" variant="subtle" />
          </ListCell>
          <ListCell class="justify-end max-sm:hidden">
            <span class="text-base text-ink-gray-7 tabular-nums">{{ item.clicks }}</span>
          </ListCell>
          <ListCell class="justify-end max-sm:hidden">
            <span class="text-base text-ink-gray-7 tabular-nums">{{ item.orders }}</span>
          </ListCell>
          <ListCell class="justify-end max-sm:hidden">
            <span class="text-base text-ink-gray-7 tabular-nums">{{ item.conversion }}%</span>
          </ListCell>
          <ListCell class="justify-end">
            <span class="text-base text-ink-gray-8 tabular-nums">{{ money(item.sales) }}</span>
          </ListCell>
          <ListCell class="justify-end" @click.stop>
            <Dropdown
              :options="getMenuOptions(item)"
              align="end"
              :button="{ icon: 'lucide-ellipsis', variant: 'ghost', 'aria-label': `Actions for ${item.title}` }"
            />
          </ListCell>
        </ListRow>
      </ListRows>
    </List>
  </div>

  <ListPagination v-if="total" v-model:page="page" v-model:page-size="pageSize" :total="total" />

  <EmptyState
    v-if="!linksRequest.loading && !rows.length"
    icon="lucide-link"
    :title="isFiltered ? 'No links match' : 'No buy links yet'"
    :description="
      isFiltered
        ? 'Try another search or filter.'
        : 'A buy link fills the cart with products and a discount, then opens checkout. Share it in ads, email, SMS or chat.'
    "
  />

  <CreateLinkDialog v-model:open="isCreating" />
</template>
