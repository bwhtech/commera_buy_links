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

export const CART_MODES = [
  { label: "Replace the shopper's cart", value: 'Replace the cart' },
  { label: "Add to the shopper's cart", value: 'Add to the cart' },
]

export const DESTINATIONS = [
  { label: 'Checkout', value: 'Checkout' },
  { label: 'Cart', value: 'Cart' },
  { label: 'A page on the store', value: 'Page' },
]

export function emptyLink() {
  return {
    title: '',
    status: 'Draft',
    slug: '',
    coupon_code: '',
    items: [],
    cart_mode: 'Replace the cart',
    destination: 'Checkout',
    destination_path: '',
    usage_limit: '',
    once_per_customer: 0,
    starts_on: null,
    ends_on: null,
    order_tags: '',
    popup_enabled: 0,
    popup_callout: '',
    popup_button_label: 'Go to checkout',
    popup_skip_label: 'Skip offer and continue shopping',
    popup_consent: 0,
    popup_consent_label: 'I agree to the terms',
    popup_consent_terms: '',
    popup_countdown: 0,
    popup_countdown_minutes: 10,
    popup_countdown_text: 'This offer ends in {timer}',
    ...Object.fromEntries([...PREFILL_FIELDS, ...UTM_FIELDS].map(({ field }) => [field, ''])),
  }
}

// Buttons stay enabled; pressing one with a gap says what to fill in instead of greying out without a reason.
export function getLinkProblem({ title, items, destination, destination_path }) {
  if (!title?.trim()) return 'Give the link a name.'
  if (!items?.length) return 'Add at least one product to the cart.'
  if (destination === 'Page' && !destination_path?.trim()) return 'Enter the path of the page to open.'
  return null
}
