<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { Skeleton, Tabs } from 'frappe-ui'
import { useMethodAction, useMethodRead, usePage, usePlugin } from '@commera/admin'
import LinkAnalytics from '../../shared/LinkAnalytics.vue'
import LinkDetails from '../../shared/LinkDetails.vue'
import LinkOrders from '../../shared/LinkOrders.vue'
import LinkShare from '../../shared/LinkShare.vue'
import LinkSnapshot from '../../shared/LinkSnapshot.vue'
import { emptyLink, getLinkProblem } from '../../shared/links'
import { useLinkActions } from '../../shared/useLinkActions'
import { useTabQuery } from '../../shared/useTabQuery'

const props = defineProps({ id: String })

const { navigate, toast } = usePlugin()
const isNew = computed(() => props.id === 'new')

const form = reactive(emptyLink())
const linkRequest = useMethodRead('commera_buy_links.api.get_link', {
  params: () => ({ name: props.id }),
  immediate: !isNew.value,
  refetch: true,
})
const link = computed(() => (isNew.value ? null : linkRequest.data))
const savedForm = ref(JSON.stringify(form))
const isDirty = computed(() => JSON.stringify(form) !== savedForm.value)
watch(
  link,
  (value) => {
    if (!value) return
    // A usage limit of 0 means none, so it shows as the empty field's "No limit" placeholder.
    Object.assign(form, emptyLink(), value, { usage_limit: value.usage_limit || '' })
    savedForm.value = JSON.stringify(form)
  },
  { immediate: true },
)

const saveRequest = useMethodAction('commera_buy_links.api.save_link')
const { duplicate, remove, duplicateRequest } = useLinkActions({ onDeleted: () => navigate('links') })

async function save() {
  if (!isNew.value && !isDirty.value) return toast.info('No changes to save', { id: 'buy-link-saved' })
  const problem = getLinkProblem(form)
  if (problem) return toast.warning(problem)
  const name = await saveRequest.submit({ link: { ...form, name: isNew.value ? null : props.id } })
  if (saveRequest.error) return
  toast.success('Link saved', { id: 'buy-link-saved' })
  savedForm.value = JSON.stringify(form)
  if (isNew.value) navigate(`links/${name}`)
  else linkRequest.reload()
}

const page = usePage()
page.setBreadcrumbs(() => [
  { label: 'Links', to: 'links' },
  { label: isNew.value ? 'New link' : form.title || props.id },
])
page.setActions(() => [
  {
    label: 'Save',
    icon: 'check',
    variant: 'solid',
    loading: saveRequest.loading,
    onClick: save,
  },
  ...(isNew.value
    ? []
    : [
        { label: 'Duplicate', icon: 'files', loading: duplicateRequest.loading, onClick: () => duplicate(props.id) },
        { label: 'Delete', icon: 'trash-2', onClick: () => remove({ name: props.id, title: form.title }) },
      ]),
])

const tab = useTabQuery(() => `links/${props.id}`, ['details', 'analytics', 'orders'])
const tabs = computed(() => [
  { label: 'Details', value: 'details' },
  { label: 'Analytics', value: 'analytics' },
  { label: link.value?.used_count ? `Orders (${link.value.used_count})` : 'Orders', value: 'orders' },
])
</script>

<template>
  <div v-if="!isNew && linkRequest.loading && !link" class="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
    <Skeleton class="h-96 rounded-5" />
    <Skeleton class="h-96 rounded-5" />
  </div>

  <LinkDetails v-else-if="isNew" :form="form" />

  <div v-else-if="link" class="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
    <Tabs v-model="tab" class="min-w-0" :tabs="tabs">
      <template #tab-panel="{ tab: current }">
        <div class="pt-5">
          <LinkDetails v-if="current.value === 'details'" :form="form" :link="link" />
          <LinkAnalytics v-else-if="current.value === 'analytics'" :name="link.name" />
          <LinkOrders v-else :name="link.name" />
        </div>
      </template>
    </Tabs>

    <aside class="flex min-w-0 flex-col gap-6 lg:sticky lg:top-4">
      <LinkShare :url="link.url" :qr-svg="link.qr_svg" :code="link.name" />
      <LinkSnapshot :name="link.name" />
    </aside>
  </div>
</template>
