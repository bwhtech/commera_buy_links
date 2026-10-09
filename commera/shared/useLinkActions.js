import { dialog } from 'frappe-ui'
import { useMethodAction, usePlugin } from '@commera/admin'

export function useLinkActions({ onDeleted } = {}) {
  const { navigate, toast } = usePlugin()
  const duplicateRequest = useMethodAction('commera_buy_links.api.duplicate_link')
  // Quiet: the confirm dialog shows the error inline, so a toast would say it twice.
  const deleteRequest = useMethodAction('commera_buy_links.api.delete_link', { quiet: true })

  async function copy(url) {
    await navigator.clipboard.writeText(url)
    toast.success('Link copied', { id: 'buy-link-copied' })
  }

  async function duplicate(name) {
    const newName = await duplicateRequest.submit({ name })
    if (duplicateRequest.error) return
    toast.success('Link duplicated as a draft')
    navigate(`links/${newName}`)
  }

  function remove(link) {
    dialog.danger({
      title: `Delete ${link.title}?`,
      message: 'The link stops working at once.',
      confirmLabel: 'Delete link',
      onConfirm: async () => {
        await deleteRequest.submit({ name: link.name })
        // Frappe prefixes the exception class ("ValidationError: …"); the shopper-facing text is the rest.
        if (deleteRequest.error) throw new Error(String(deleteRequest.error.message).replace(/^\w+Error: /, ''))
        toast.success('Link deleted')
        onDeleted?.()
      },
    })
  }

  function getMenuOptions(link) {
    return [
      { label: 'Copy link', icon: 'lucide-copy', onClick: () => copy(link.url) },
      { label: 'Open link', icon: 'lucide-external-link', onClick: () => window.open(link.url, '_blank', 'noopener') },
      { label: 'Duplicate', icon: 'lucide-files', onClick: () => duplicate(link.name) },
      { label: 'Delete', icon: 'lucide-trash-2', theme: 'red', onClick: () => remove(link) },
    ]
  }

  return { copy, duplicate, remove, getMenuOptions, duplicateRequest }
}
