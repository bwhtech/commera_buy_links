<script setup>
import { ref, watch } from 'vue'
import { Button, Dialog, ErrorMessage, FormControl } from 'frappe-ui'
import { useMethodAction, usePlugin } from '@commera/admin'
import CartLines from './CartLines.vue'
import { getLinkProblem } from './links'

const open = defineModel('open', { type: Boolean, default: false })

const { navigate } = usePlugin()
const title = ref('')
const lines = ref([])
// Quiet: the dialog shows the error above its buttons, so a toast would say it twice.
const createRequest = useMethodAction('commera_buy_links.api.save_link', { quiet: true })
const problem = ref('')

watch(open, (isOpen) => {
  if (!isOpen) return
  title.value = ''
  lines.value = []
  problem.value = ''
})

// The message answers the last press; once the shopper edits, it no longer applies.
watch([title, () => lines.value.length], () => (problem.value = ''))

async function create() {
  problem.value = getLinkProblem({ title: title.value, items: lines.value }) ?? ''
  if (problem.value) return
  const name = await createRequest.submit({ link: { title: title.value, status: 'Draft', items: lines.value } })
  if (createRequest.error) return
  open.value = false
  navigate(`links/${name}`)
}
</script>

<template>
  <Dialog v-model:open="open" title="Create buy link" size="xl">
    <div class="space-y-4">
      <FormControl v-model="title" label="Name" placeholder="Spring sale bundle" description="Only staff see this name." required />
      <div class="space-y-1.5">
        <p class="text-sm text-ink-gray-6">Products</p>
        <CartLines v-model="lines" />
      </div>
      <p class="text-p-sm text-ink-gray-5">
        The link starts as a draft. Add a discount, prefill and limits on the next screen.
      </p>
      <ErrorMessage v-if="problem || createRequest.error" :message="problem || createRequest.error" />
    </div>
    <template #actions="{ close }">
      <div class="flex justify-end gap-2">
        <Button label="Cancel" @click="close" />
        <Button
          variant="solid"
          label="Create draft link"
          :loading="createRequest.loading"
          @click="create"
        />
      </div>
    </template>
  </Dialog>
</template>
