// Buy Links popup: draws a link's offer over the storefront when the URL carries ?buy=<code>.
// Commera loads this file on every storefront page, so it does nothing without that parameter.
;(function () {
  const params = new URLSearchParams(window.location.search)
  const code = params.get('buy')
  if (!code) return

  const isPreview = params.get('preview') === '1'
  let popup = null
  let root = null
  let countdownTimer = null

  function element(tag, className, text) {
    const node = document.createElement(tag)
    if (className) node.className = className
    // textContent, never innerHTML: link fields are merchant-written and the query string is the shopper's.
    if (text != null) node.textContent = text
    return node
  }

  function money(amount) {
    try {
      return new Intl.NumberFormat(document.documentElement.lang || undefined, {
        style: 'currency',
        currency: popup.currency || 'USD',
      }).format(amount)
    } catch (error) {
      return String(amount)
    }
  }

  function cartUrl() {
    const codes = popup.lines.map((line) => `${encodeURIComponent(line.item_code)}:${line.qty}`).join(',')
    return `/cart/${codes}${popup.query ? `?${popup.query}` : ''}`
  }

  function close() {
    clearInterval(countdownTimer)
    root?.remove()
    root = null
    document.documentElement.classList.remove('cbl-open')
    if (isPreview) return
    const url = new URL(window.location.href)
    url.searchParams.delete('buy')
    window.history.replaceState(null, '', url)
  }

  function startedAt() {
    const key = `commera-buy-links:${popup.code}:started`
    const stored = Number(window.sessionStorage.getItem(key))
    if (stored) return stored
    window.sessionStorage.setItem(key, String(Date.now()))
    return Date.now()
  }

  function renderCountdown(card) {
    if (!popup.popup_countdown || !(popup.popup_countdown_minutes > 0)) return
    const box = element('div', 'cbl-callout cbl-countdown')
    card.append(box)
    const endsAt = (isPreview ? Date.now() : startedAt()) + popup.popup_countdown_minutes * 60000
    const tick = () => {
      const left = Math.max(0, endsAt - Date.now())
      const minutes = Math.floor(left / 60000)
      const seconds = String(Math.floor((left % 60000) / 1000)).padStart(2, '0')
      box.textContent = (popup.popup_countdown_text || '{timer}').replace('{timer}', `${minutes}:${seconds}`)
      // At zero the offer is gone; the shopper stays in the store, as with Skip.
      if (!left && !isPreview) close()
    }
    tick()
    countdownTimer = setInterval(tick, 1000)
  }

  function renderLines(card) {
    const list = element('ul', 'cbl-lines')
    for (const line of popup.lines) {
      const row = element('li', 'cbl-line')
      if (line.image) {
        const image = element('img', 'cbl-image')
        image.src = line.image
        image.alt = ''
        row.append(image)
      }
      const details = element('div', 'cbl-line-details')
      details.append(element('p', 'cbl-line-title', line.title))
      if (line.size) details.append(element('p', 'cbl-line-meta', line.size))
      const stepper = element('div', 'cbl-stepper')
      const minus = element('button', 'cbl-step', '−')
      const count = element('span', 'cbl-count', String(line.qty))
      const plus = element('button', 'cbl-step', '+')
      minus.type = plus.type = 'button'
      minus.setAttribute('aria-label', `Fewer ${line.title}`)
      plus.setAttribute('aria-label', `More ${line.title}`)
      minus.onclick = () => setQty(line, line.qty - 1)
      plus.onclick = () => setQty(line, line.qty + 1)
      stepper.append(minus, count, plus)
      details.append(stepper)
      row.append(details)
      const price = element('div', 'cbl-line-price')
      if (line.default_price && line.default_price > line.price) {
        price.append(element('s', 'cbl-was', money(line.default_price * line.qty)))
      }
      price.append(element('span', null, money(line.price * line.qty)))
      row.append(price)
      list.append(row)
    }
    card.append(list)
  }

  function setQty(line, qty) {
    if (qty < 1) return showMessage('A line needs at least 1. Skip the offer to leave without it.')
    if (line.max_qty && qty > line.max_qty) return showMessage(`Only ${line.max_qty} of ${line.title} are in stock.`)
    line.qty = qty
    render()
  }

  function renderSummary(card) {
    const summary = element('dl', 'cbl-summary')
    const subtotal = popup.lines.reduce((sum, line) => sum + line.price * line.qty, 0)
    const row = (label, value, className) => {
      const wrapper = element('div', `cbl-summary-row ${className || ''}`)
      wrapper.append(element('dt', null, label), element('dd', null, value))
      summary.append(wrapper)
    }
    row('Subtotal', money(subtotal))
    // Commera prices the coupon at checkout, so the popup names it rather than guessing its amount.
    if (popup.coupon) row('Discount', `${popup.coupon} at checkout`, 'cbl-discount')
    card.append(summary)
  }

  function renderConsent(card) {
    if (!popup.popup_consent) return
    const wrapper = element('div', 'cbl-consent')
    const label = element('label', 'cbl-consent-label')
    const box = element('input')
    box.type = 'checkbox'
    box.className = 'cbl-consent-box'
    label.append(box, element('span', null, popup.popup_consent_label || 'I agree to the terms'))
    wrapper.append(label)
    if (popup.popup_consent_terms) {
      const terms = element('details', 'cbl-terms')
      terms.append(element('summary', null, 'Read the terms'), element('p', 'cbl-terms-body', popup.popup_consent_terms))
      wrapper.append(terms)
    }
    box.onchange = () => showMessage('')
    card.append(wrapper)
  }

  function showMessage(text) {
    const message = root?.querySelector('.cbl-message')
    if (message) message.textContent = text
  }

  function checkout() {
    const consent = root.querySelector('.cbl-consent-box')
    // The button stays enabled and says what is missing, rather than greying out without a reason.
    if (consent && !consent.checked) return showMessage('Tick the box above to continue.')
    if (!popup.lines.length) return showMessage('This offer has no products left in stock.')
    if (isPreview) return showMessage('Preview: shoppers go to checkout from here.')
    window.location.href = cartUrl()
  }

  function render() {
    clearInterval(countdownTimer)
    root?.remove()
    root = element('div', 'cbl-backdrop')
    root.setAttribute('role', 'dialog')
    root.setAttribute('aria-modal', 'true')
    const card = element('div', 'cbl-card')
    root.append(card)

    if (popup.logo) {
      const logo = element('img', 'cbl-logo')
      logo.src = popup.logo
      logo.alt = popup.store_name || ''
      card.append(logo)
    } else {
      card.append(element('p', 'cbl-store', popup.store_name))
    }
    if (popup.popup_callout) card.append(element('div', 'cbl-callout', popup.popup_callout))
    renderLines(card)
    for (const notice of popup.notices || []) card.append(element('p', 'cbl-notice', notice))
    renderSummary(card)
    renderCountdown(card)
    renderConsent(card)
    card.append(element('p', 'cbl-message'))
    const button = element('button', 'cbl-checkout', popup.popup_button_label || 'Go to checkout')
    button.type = 'button'
    button.onclick = checkout
    card.append(button)
    if (popup.popup_skip_label) {
      const skip = element('button', 'cbl-skip', popup.popup_skip_label)
      skip.type = 'button'
      skip.onclick = close
      card.append(skip)
    }

    document.body.append(root)
    document.documentElement.classList.add('cbl-open')
  }

  async function load() {
    const query = new URLSearchParams(params)
    query.delete('buy')
    query.set('code', code)
    const response = await fetch(`/api/v2/method/commera_buy_links.api.get_popup?${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) return
    const data = (await response.json()).data
    if (!data || data.unavailable) return
    popup = data
    render()
    if (isPreview) window.parent.postMessage({ type: 'commera-buy-links:ready' }, window.location.origin)
  }

  // The dashboard preview sends unsaved settings; only a page on this same origin may do so.
  window.addEventListener('message', (event) => {
    if (!isPreview || event.origin !== window.location.origin || event.data?.type !== 'commera-buy-links:preview') return
    if (!popup) return
    for (const [key, value] of Object.entries(event.data.settings || {})) {
      if (key.startsWith('popup_')) popup[key] = value
    }
    render()
  })

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && root && !isPreview) close()
  })

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', load)
  else load()
})()
