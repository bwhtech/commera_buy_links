export const QR_STYLES = ['Square', 'Rounded', 'Dots']
export const CODE_PRESETS = ['#000000', '#1F2937', '#1E3A8A', '#6D28D9', '#7F1D1D', '#14532D']
export const BACKGROUND_PRESETS = ['#FFFFFF', '#F8FAFC', '#FEF3C7', '#ECFDF5']

export function isHexColour(value) {
  return /^#[0-9a-f]{6}$/i.test(value ?? '')
}

function luminance(hex) {
  const channels = [1, 3, 5].map((start) => parseInt(hex.slice(start, start + 2), 16) / 255)
  const [red, green, blue] = channels.map((value) => (value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4))
  return 0.2126 * red + 0.7152 * green + 0.0722 * blue
}

// Phone cameras need a dark code on a light background; inverted or faint codes fail on many scanners.
export function getScanWarning(color, background) {
  if (!isHexColour(color) || !isHexColour(background)) return ''
  const code = luminance(color)
  const paper = luminance(background)
  if (code > paper) return 'The code is lighter than its background. Many phones cannot read an inverted code.'
  if ((paper + 0.05) / (code + 0.05) < 4) return 'The colours are close. Make the code darker so phones read it in dim light.'
  return ''
}
