<script>
export const plugin = { label: 'Create buy link', icon: 'link', requires: 'Buy Link' }
</script>

<script setup>
import { ref, watch } from 'vue'
import { FormControl } from 'frappe-ui'
import { useAction, useMethodAction, useMethodRead, usePlugin } from '@commera/admin'
import CartLines from '../../../shared/CartLines.vue'
import { getLinkProblem } from '../../../shared/links'

const { record, navigate } = usePlugin()
const action = useAction()

const variantsRequest = useMethodRead('commera_buy_links.api.search_items', {
  params: () => ({ product: record.value.name }),
})
const title = ref('')
const lines = ref([])
watch(
  () => variantsRequest.data,
  (variants) => {
    if (!variants?.length || lines.value.length) return
    title.value = variants[0].title.split(' - ')[0]
    lines.value = [{ ...variants[0], qty: 1 }]
  },
)

const saveRequest = useMethodAction('commera_buy_links.api.save_link')
action.setPrimary({ label: 'Create draft link' })

action.onSubmit(async () => {
  const problem = getLinkProblem({ title: title.value, items: lines.value })
  if (problem) throw new Error(problem)
  const name = await saveRequest.submit({ link: { title: title.value, status: 'Draft', items: lines.value } })
  if (saveRequest.error) throw saveRequest.error
  navigate(`/plugins/commera_buy_links/links/${name}`)
})
</script>

<template>
  <div class="flex flex-col gap-4">
    <FormControl v-model="title" label="Name" />
    <p v-if="variantsRequest.data && !variantsRequest.data.length" class="text-base text-ink-gray-6">
      This product has no option on the storefront yet. Publish one, then create the link.
    </p>
    <CartLines v-else v-model="lines" />
    <p class="text-sm text-ink-gray-5">The link opens as a draft so you can add a discount and limits before sharing it.</p>
  </div>
</template>
