<script setup>
import { computed, ref, watch } from 'vue'
import { Button, Combobox, TextInput, debounce } from 'frappe-ui'
import { EmptyState, money, useMethodRead } from '@commera/admin'

const lines = defineModel({ type: Array, required: true })

const query = ref('')
// One request per pause in typing: each refetch aborts the one before it.
const search = ref('')
watch(query, debounce((value) => (search.value = value.trim()), 250))
const picked = ref(null)
const resultsRequest = useMethodRead('commera_buy_links.api.search_items', {
  params: () => ({ search: search.value }),
  immediate: false,
  refetch: true,
})

const inCart = computed(() => new Set(lines.value.map((line) => line.item_code)))
const results = computed(() => (resultsRequest.data ?? []).filter((item) => !inCart.value.has(item.item_code)))
const options = computed(() =>
  results.value.map((item) => ({
    label: item.title,
    value: item.item_code,
    description: `${item.item_code} · ${money(item.price)}`,
  })),
)
const total = computed(() => lines.value.reduce((sum, line) => sum + (line.price ?? 0) * line.qty, 0))

// Binding `query` hands its reset to us, so each open starts from a blank search.
function onOpen(isOpen) {
  if (!isOpen) return
  query.value = ''
  search.value = ''
  if (!resultsRequest.data) resultsRequest.reload()
}

function add(itemCode) {
  const item = results.value.find((result) => result.item_code === itemCode)
  if (item) lines.value = [...lines.value, { ...item, qty: 1 }]
  picked.value = null
}

function setQty(line, value) {
  line.qty = Math.max(1, Math.floor(Number(value) || 1))
}

function remove(line) {
  lines.value = lines.value.filter((other) => other !== line)
}
</script>

<template>
  <div>
    <Combobox
      v-model="picked"
      v-model:query="query"
      trigger="button"
      placeholder="Add a product"
      empty-text="No sellable products match"
      :options="options"
      :filterable="false"
      :loading="resultsRequest.loading"
      @update:model-value="add"
      @update:open="onOpen"
    >
      <template #prefix>
        <span class="lucide-plus size-4 text-ink-gray-6" aria-hidden="true" />
      </template>
    </Combobox>

    <ul v-if="lines.length" class="mt-3 divide-y divide-outline-gray-1 rounded-5 border border-outline-gray-1">
      <li v-for="line in lines" :key="line.item_code" class="flex items-center gap-3 px-3 py-2">
        <div class="min-w-0 flex-1">
          <p class="truncate text-base text-ink-gray-8">{{ line.title }}</p>
          <p class="mt-0.5 truncate text-sm" :class="line.is_listed === false ? 'text-ink-red-7' : 'text-ink-gray-5'">
            {{ line.is_listed === false ? 'Not on the storefront: Commera skips this line' : line.item_code }}
          </p>
        </div>
        <span class="hidden w-20 shrink-0 text-right text-base text-ink-gray-7 tabular-nums sm:block">
          {{ money(line.price) }}
        </span>
        <TextInput
          class="w-20 shrink-0"
          type="number"
          min="1"
          :model-value="line.qty"
          :aria-label="`Quantity of ${line.title}`"
          @update:model-value="(value) => setQty(line, value)"
        />
        <Button variant="ghost" icon="lucide-x" :tooltip="`Remove ${line.title}`" @click="remove(line)" />
      </li>
      <li class="flex items-center justify-between px-3 py-2">
        <span class="text-sm text-ink-gray-5">Before discount</span>
        <span class="text-base text-ink-gray-8 tabular-nums">{{ money(total) }}</span>
      </li>
    </ul>
    <EmptyState
      v-else
      compact
      icon="lucide-shopping-cart"
      title="No products yet"
      description="Add the products this link puts in the cart."
    />
  </div>
</template>
