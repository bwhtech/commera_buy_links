export const PREFILL_FIELDS = [
  { field: 'email', label: 'Email', type: 'email' },
  { field: 'first_name', label: 'First name' },
  { field: 'last_name', label: 'Last name' },
  { field: 'address1', label: 'Address line 1' },
  { field: 'address2', label: 'Address line 2' },
  { field: 'city', label: 'City' },
  { field: 'province', label: 'State' },
  { field: 'zip', label: 'Postal code' },
  { field: 'country', label: 'Country' },
]

export const UTM_FIELDS = [
  { field: 'utm_source', label: 'UTM source' },
  { field: 'utm_medium', label: 'UTM medium' },
  { field: 'utm_campaign', label: 'UTM campaign' },
  { field: 'utm_term', label: 'UTM term' },
  { field: 'utm_content', label: 'UTM content' },
]

export function emptyLink() {
  return {
    title: '',
    status: 'Draft',
    slug: '',
    coupon_code: '',
    items: [],
    usage_limit: '',
    once_per_customer: 0,
    starts_on: null,
    ends_on: null,
    order_tags: '',
    ...Object.fromEntries([...PREFILL_FIELDS, ...UTM_FIELDS].map(({ field }) => [field, ''])),
  }
}

// Buttons stay enabled; pressing one with a gap says what to fill in instead of greying out without a reason.
export function getLinkProblem({ title, items }) {
  if (!title?.trim()) return 'Give the link a name.'
  if (!items?.length) return 'Add at least one product to the cart.'
  return null
}
