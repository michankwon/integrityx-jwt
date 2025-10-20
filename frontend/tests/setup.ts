/**
 * Test setup for frontend components
 */

// Mock fetch for testing
global.fetch = jest.fn()

// Mock window.URL for blob downloads
global.URL = {
  createObjectURL: jest.fn(() => 'mock-url'),
  revokeObjectURL: jest.fn(),
} as any

// Mock document methods
Object.defineProperty(document, 'createElement', {
  value: jest.fn(() => ({
    href: '',
    download: '',
    style: { display: '' },
    click: jest.fn(),
  })),
})

Object.defineProperty(document.body, 'appendChild', {
  value: jest.fn(),
})

Object.defineProperty(document.body, 'removeChild', {
  value: jest.fn(),
})

// Mock navigator.clipboard
Object.defineProperty(navigator, 'clipboard', {
  value: {
    writeText: jest.fn(() => Promise.resolve()),
  },
})

// Mock window.dispatchEvent
global.dispatchEvent = jest.fn()

// Mock toast
jest.mock('react-hot-toast', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams(),
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
  }),
}))

// Mock window.location
delete (window as any).location
window.location = {
  href: 'http://localhost:3000',
  search: '',
  pathname: '/',
  origin: 'http://localhost:3000',
} as any

// Mock window.history
window.history = {
  replaceState: jest.fn(),
} as any

