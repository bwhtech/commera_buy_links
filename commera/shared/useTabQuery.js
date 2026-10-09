import { computed } from 'vue'
import { usePlugin } from '@commera/admin'

// The open tab lives in ?tab=, so a reload or a shared URL lands on it. The first tab keeps the URL bare.
export function useTabQuery(basePath, values) {
  const { query, navigate } = usePlugin()
  return computed({
    get: () => (values.includes(query.value.tab) ? query.value.tab : values[0]),
    set: (tab) => navigate(tab === values[0] ? basePath() : `${basePath()}?tab=${tab}`),
  })
}
