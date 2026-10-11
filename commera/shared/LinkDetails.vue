<script setup>
import { computed, ref, watch } from 'vue'
import { Alert, Badge, Button, FormControl, Switch } from 'frappe-ui'
import { useMethodRead } from '@commera/admin'
import CartLines from './CartLines.vue'
import { PREFILL_FIELDS, UTM_FIELDS } from './links'

// `form` is the page's reactive draft; the sections edit it in place and the page saves it.
const props = defineProps({
  form: { type: Object, required: true },
  link: { type: Object, default: null },
})

const couponsRequest = useMethodRead('commera_buy_links.api.search_coupon_codes')
const couponOptions = computed(() => [
  { label: 'No discount', value: '' },
  ...(couponsRequest.data ?? []).map((coupon) => ({ label: coupon.coupon_code, value: coupon.name })),
])

const isActive = computed({
  get: () => props.form.status === 'Active',
  set: (value) => (props.form.status = value ? 'Active' : 'Draft'),
})

const usage = computed(() => {
  const limit = Number(props.form.usage_limit) || 0
  if (!limit || !props.link) return null
  const used = props.link.used_count
  return `${used} of ${limit} used · ${Math.max(limit - used, 0)} left`
})

const showPrefill = ref(false)
watch(
  () => props.link,
  (value) => (showPrefill.value ||= Boolean(value && PREFILL_FIELDS.some(({ field }) => value[field]))),
  { immediate: true },
)
</script>

<template>
  <div class="flex flex-col gap-6">
    <section class="rounded-5 border border-outline-gray-1 p-4">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg-semibold text-ink-gray-8">Link</h2>
        <Switch v-model="isActive" label="Active" />
      </div>
      <div class="mt-4 grid gap-4 sm:grid-cols-2">
        <FormControl v-model="form.title" label="Name" description="Only staff see this name." required />
        <FormControl
          v-model="form.slug"
          label="Custom slug"
          placeholder="spring-sale"
          description="Optional. Lowercase letters, digits and hyphens."
        />
      </div>
      <Alert
        v-if="link?.unavailable_reason"
        class="mt-4"
        theme="amber"
        :title="`Shoppers who open this link see: “${link.unavailable_reason}”`"
      />
    </section>

    <section class="rounded-5 border border-outline-gray-1 p-4">
      <h2 class="text-lg-semibold text-ink-gray-8">Cart</h2>
      <p class="mt-1 text-sm text-ink-gray-5">Opening the link replaces the shopper's cart with these items.</p>
      <CartLines v-model="form.items" class="mt-4" />
    </section>

    <section class="rounded-5 border border-outline-gray-1 p-4">
      <h2 class="text-lg-semibold text-ink-gray-8">Discount</h2>
      <FormControl
        v-model="form.coupon_code"
        class="mt-4 sm:max-w-xs"
        type="select"
        label="Coupon code"
        :options="couponOptions"
        description="Applied at checkout. Create codes in Desk under Coupon Code."
      />
    </section>

    <section class="rounded-5 border border-outline-gray-1 p-4">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg-semibold text-ink-gray-8">Customer prefill</h2>
        <Button
          variant="ghost"
          :label="showPrefill ? 'Hide fields' : 'Show fields'"
          :icon-right="showPrefill ? 'lucide-chevron-up' : 'lucide-chevron-down'"
          :aria-expanded="showPrefill"
          @click="showPrefill = !showPrefill"
        />
      </div>
      <p class="mt-1 text-sm text-ink-gray-5">
        Fills empty checkout fields. Add <code>?checkout[email]=…</code> to the link to prefill per shopper.
      </p>
      <div v-if="showPrefill" class="mt-4 grid gap-4 sm:grid-cols-2">
        <FormControl
          v-for="{ field, label, type } in PREFILL_FIELDS"
          :key="field"
          v-model="form[field]"
          :type="type || 'text'"
          :label="label"
        />
      </div>
    </section>

    <section class="rounded-5 border border-outline-gray-1 p-4">
      <h2 class="text-lg-semibold text-ink-gray-8">Attribution</h2>
      <p class="mt-1 text-sm text-ink-gray-5">Sent to the store's analytics with every click.</p>
      <div class="mt-4 grid gap-4 sm:grid-cols-2">
        <FormControl v-for="{ field, label } in UTM_FIELDS" :key="field" v-model="form[field]" :label="label" />
        <FormControl
          v-model="form.order_tags"
          class="sm:col-span-2"
          label="Order tags"
          placeholder="influencer, spring-sale"
          description="Comma-separated. Added to every order placed through this link."
        />
      </div>
    </section>

    <section class="rounded-5 border border-outline-gray-1 p-4">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-lg-semibold text-ink-gray-8">Limits</h2>
        <Badge v-if="usage" :label="usage" theme="gray" variant="subtle" />
      </div>
      <div class="mt-4 grid gap-4 sm:grid-cols-2">
        <FormControl
          v-model="form.usage_limit"
          type="number"
          label="Usage limit"
          placeholder="No limit"
          description="Orders allowed. At the limit the link moves to Draft."
        />
        <FormControl v-model="form.once_per_customer" class="sm:pt-6" type="checkbox" label="Once per customer" />
        <FormControl v-model="form.starts_on" type="datetime" label="Starts on" />
        <FormControl v-model="form.ends_on" type="datetime" label="Ends on" />
      </div>
      <p class="mt-3 text-sm text-ink-gray-5">
        With a coupon, checkout removes the coupon when a limit is hit and tells the shopper why. Without one, limits only stop new clicks.
      </p>
    </section>
  </div>
</template>
