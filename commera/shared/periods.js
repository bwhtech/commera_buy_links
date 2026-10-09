// The reference app reports today, 7 and 30 days; 90 adds a quarter for slower links.
export const PERIODS = [
  { label: 'Today', value: 'today', caption: 'vs yesterday' },
  { label: '7 days', value: '7d', caption: 'vs previous 7 days' },
  { label: '30 days', value: '30d', caption: 'vs previous 30 days' },
  { label: '90 days', value: '90d', caption: 'vs previous 90 days' },
]

export function periodCaption(period) {
  return PERIODS.find((option) => option.value === period)?.caption
}

// Percent change against the previous period; null when there is nothing to compare with.
export function percentChange(current, previous) {
  if (!previous) return null
  return Math.round(((current - previous) / previous) * 1000) / 10
}
