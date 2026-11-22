/**
 * Lightweight toast notifications and confirmation dialogs
 * Provides equivalents for Element Plus ElMessage and ElMessageBox
 */

// ==================== Toast notifications ====================

const TYPE_ICONS = {
  success: `<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
  error: `<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
  warning: `<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  info: `<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`
}

const TYPE_COLORS = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800'
}

const TYPE_ICON_COLORS = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500'
}

let toastContainer = null

function getToastContainer() {
  if (!toastContainer) {
    toastContainer = document.createElement('div')
    toastContainer.className = 'fixed top-4 left-1/2 -translate-x-1/2 z-[9999] flex flex-col items-center gap-2 pointer-events-none'
    document.body.appendChild(toastContainer)
  }
  return toastContainer
}

/**
 * Show a toast
 * @param {'success'|'error'|'warning'|'info'} type
 * @param {string} msg
 * @param {number} duration Display duration in milliseconds, defaulting to 3000
 */
export function showMessage(type, msg, duration = 3000) {
  const container = getToastContainer()

  const el = document.createElement('div')
  el.className = `
    pointer-events-auto flex items-center gap-2 px-4 py-3 rounded-lg border shadow-lg
    ${TYPE_COLORS[type] || TYPE_COLORS.info}
    animate-[toast-in_0.3s_ease-out]
  `
  el.innerHTML = `
    <span class="flex-shrink-0 ${TYPE_ICON_COLORS[type] || TYPE_ICON_COLORS.info}">${TYPE_ICONS[type] || TYPE_ICONS.info}</span>
    <span class="text-sm font-medium">${escapeHtml(msg)}</span>
  `

  container.appendChild(el)

  // Remove automatically
  setTimeout(() => {
    el.classList.add('animate-[toast-out_0.3s_ease-in]')
    el.addEventListener('animationend', () => {
      el.remove()
      if (container.children.length === 0 && toastContainer) {
        toastContainer.remove()
        toastContainer = null
      }
    })
  }, duration)
}

// Convenience methods
export const ElMessage = {
  success: (msg, duration) => showMessage('success', msg, duration),
  error: (msg, duration) => showMessage('error', msg, duration),
  warning: (msg, duration) => showMessage('warning', msg, duration),
  info: (msg, duration) => showMessage('info', msg, duration)
}

// ==================== Confirmation dialogs ====================

/**
 * Show a confirmation dialog
 * @param {string} message Message text
 * @param {string} title Dialog title
 * @param {object} options - { confirmButtonText, cancelButtonText, type }
 * @returns {Promise}
 */
export function showConfirm(message, title = 'System Notice', options = {}) {
  const {
    confirmButtonText = 'Confirm',
    cancelButtonText = 'Cancel',
    type = 'warning'
  } = options

  return new Promise((resolve, reject) => {
    // Backdrop
    const overlay = document.createElement('div')
    overlay.className = 'fixed inset-0 z-[10000] bg-black/40 flex items-center justify-center animate-[fade-in_0.2s_ease-out]'

    // Dialog
    const modal = document.createElement('div')
    modal.className = 'bg-white rounded-xl shadow-2xl w-[420px] max-w-[90vw] overflow-hidden animate-[modal-in_0.25s_ease-out]'

    const iconMap = {
      warning: `<svg class="w-8 h-8 text-yellow-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
      error: `<svg class="w-8 h-8 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
      info: `<svg class="w-8 h-8 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`
    }

    modal.innerHTML = `
      <div class="p-6">
        <div class="flex items-start gap-4">
          <div class="flex-shrink-0">${iconMap[type] || iconMap.warning}</div>
          <div class="flex-1 min-w-0">
            <h3 class="text-base font-semibold text-gray-900 mb-2">${escapeHtml(title)}</h3>
            <p class="text-sm text-gray-600 leading-relaxed">${escapeHtml(message)}</p>
          </div>
        </div>
      </div>
      <div class="flex justify-end gap-3 px-6 pb-6 pt-2">
        <button class="cancel-btn px-5 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
          ${escapeHtml(cancelButtonText)}
        </button>
        <button class="confirm-btn px-5 py-2 text-sm font-medium text-white bg-[var(--color-primary)] rounded-lg hover:bg-[var(--color-primary-dark)] transition-colors">
          ${escapeHtml(confirmButtonText)}
        </button>
      </div>
    `

    overlay.appendChild(modal)
    document.body.appendChild(overlay)

    const cleanup = () => {
      overlay.classList.add('animate-[fade-out_0.2s_ease-in]')
      overlay.addEventListener('animationend', () => overlay.remove())
    }

    // Confirm button
    modal.querySelector('.confirm-btn').addEventListener('click', () => {
      cleanup()
      resolve()
    })

    // Cancel button
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
      cleanup()
      reject(new Error('cancel'))
    })

    // Dismiss when the backdrop is clicked
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        cleanup()
        reject(new Error('cancel'))
      }
    })
  })
}

// Compatible with the ElMessageBox API
export const ElMessageBox = {
  confirm: (message, title, options) => showConfirm(message, title, options)
}

// ==================== Utilities ====================

function escapeHtml(str) {
  if (!str) return ''
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}
