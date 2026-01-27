# Frontend Documentation

This is the frontend application for the project template, built with Vue 3, TypeScript, and a modern CSS design system.

## Table of Contents

- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Architecture](#architecture)
- [Development Conventions](#development-conventions)
- [Common Patterns](#common-patterns)
- [Styling Guide](#styling-guide)
- [Testing](#testing)

## Technology Stack

- **Framework**: Vue 3 (Composition API)
- **Language**: TypeScript
- **State Management**: Vuex
- **Routing**: Vue Router
- **HTTP Client**: Axios
- **Build Tool**: Vue CLI 5
- **CSS**: Pure CSS with design tokens (no preprocessors)

## Project Structure

```
frontend/src/
├── api/                      # API client and HTTP utilities
│   └── index.ts             # Axios instance, API modules (authAPI, userAPI)
├── components/              # Reusable Vue components
│   └── ErrorNotification.vue
├── router/                  # Vue Router configuration
│   └── index.ts            # Routes and navigation guards
├── store/                   # Vuex state management
│   └── index.ts            # Global state (user, loading, error)
├── styles/                  # CSS design system
│   ├── index.css           # Main stylesheet (imports all)
│   ├── variables.css       # Design tokens (colors, spacing, etc.)
│   ├── reset.css           # CSS reset
│   ├── layout.css          # Layout system (flex, grid, containers)
│   ├── typography.css      # Text styles
│   ├── animations.css      # Transitions and animations
│   ├── scrollbar.css       # Custom scrollbar styling
│   ├── utilities.css       # Utility classes
│   ├── background.css      # Background patterns
│   └── components/         # Pre-built component styles
│       ├── buttons.css     # Button styles (.btn, .btn-primary, etc.)
│       ├── inputs.css      # Input/textarea styles
│       └── cards.css       # Card styles
├── utils/                   # Utility functions
│   └── errors.ts           # Error parsing utilities
├── views/                   # Page components
│   ├── LoginView.vue       # Login page
│   ├── SignupView.vue      # Signup page
│   └── AccountView.vue     # Protected account page
├── App.vue                  # Root component
└── main.ts                  # Application entry point
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

```bash
cd frontend
npm install
```

### Development Server

```bash
npm run serve
# Visit http://localhost:8080
```

### Build for Production

```bash
npm run build
# Output in dist/
```

### Lint Code

```bash
npm run lint
```

## Architecture

### Vue 3 Composition API

All components use the **Composition API** with TypeScript for better type inference and code organization.

```vue
<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useStore } from 'vuex'

export default defineComponent({
  name: 'MyComponent',
  setup() {
    const store = useStore()
    const count = ref(0)

    const doubleCount = computed(() => count.value * 2)

    const increment = () => {
      count.value++
    }

    return { count, doubleCount, increment }
  }
})
</script>
```

### State Management (Vuex)

Global state is managed with Vuex:

```typescript
// State
interface State {
  user: User | null          // Current authenticated user
  isLoading: boolean         // Global loading state
  error: string | null       // Global error message
}

// Getters
isAuthenticated: (state) => !!state.user

// Mutations (synchronous)
SET_USER(state, user: User | null)

// Actions (asynchronous)
async signin({ commit }, { email, password })
```

### Routing

Vue Router with navigation guards for authentication:

```typescript
// Route meta
meta: {
  requiresAuth: true,   // Requires authentication
  requiresGuest: true   // Requires NOT authenticated
}

// Navigation guard
router.beforeEach(async (to, from, next) => {
  // Check authentication and redirect accordingly
})
```

### API Client

Centralized Axios instance with interceptors:

```typescript
// All requests go through /api
const axiosInstance = axios.create({
  baseURL: '/api',
  withCredentials: true, // Send JWT cookie
})

// Response interceptor parses errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Convert to APIError with user-friendly messages
  }
)
```

## Development Conventions

### 1. Scrolling Convention (CRITICAL)

**The global container is ALWAYS non-scrollable.**

- `html`, `body`, `#app`, `.app-main` have `overflow: hidden`
- Views that need scrolling MUST use `.view-scrollable` container
- Views that fit on screen use `.view-fullscreen` container

```vue
<!-- For content that may exceed screen height -->
<template>
  <div class="view-scrollable">
    <div class="view-content">
      <!-- Long content here -->
    </div>
  </div>
</template>

<!-- For content that always fits on screen -->
<template>
  <div class="view-fullscreen">
    <div class="auth-card">
      <!-- Login form -->
    </div>
  </div>
</template>
```

**Why**: Locked viewport provides consistent layout, predictable positioning, and better mobile experience.

### 2. Vue Component Structure

```vue
<template>
  <div class="component-name">
    <!-- Template -->
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'ComponentName', // PascalCase
  props: {},
  emits: [],
  setup() {
    // Composition API logic
    return {}
  }
})
</script>

<style scoped>
/* Component-specific styles */
.component-name {
  /* Use CSS variables */
  padding: var(--space-4);
  color: var(--text-primary);
}
</style>
```

### 3. Styling Convention (CRITICAL)

**Always use CSS variables (design tokens) instead of hard-coded values.**

```css
/* ✅ CORRECT */
.component {
  padding: var(--space-4);
  color: var(--text-primary);
  background: var(--surface-elevated);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

/* ❌ WRONG */
.component {
  padding: 16px;        /* Use var(--space-4) */
  color: #333333;       /* Use var(--text-primary) */
  border-radius: 8px;   /* Use var(--radius-lg) */
}
```

### 4. File Naming

- **Components**: PascalCase - `UserCard.vue`, `LoginView.vue`
- **Utilities**: camelCase - `errors.ts`, `formatDate.ts`
- **Views**: PascalCase with `View` suffix - `LoginView.vue`, `AccountView.vue`

### 5. TypeScript Usage

All components use TypeScript with proper type definitions:

```typescript
interface User {
  id: string
  email: string
  created_at: string
}

// API response types
const fetchUser = async (): Promise<User> => {
  return userAPI.getMe()
}
```

## Common Patterns

### Form Handling

```vue
<template>
  <form @submit.prevent="handleSubmit" class="form-stack">
    <div class="form-group">
      <label for="email" class="form-label">Email</label>
      <input
        id="email"
        v-model="email"
        type="email"
        class="input"
        required
        :disabled="isLoading"
      />
    </div>

    <button
      type="submit"
      class="btn btn-primary"
      :disabled="isLoading"
    >
      Submit
    </button>
  </form>
</template>

<script lang="ts">
export default defineComponent({
  setup() {
    const email = ref('')
    const isLoading = ref(false)

    const handleSubmit = async () => {
      isLoading.value = true
      try {
        await submitForm(email.value)
      } finally {
        isLoading.value = false
      }
    }

    return { email, isLoading, handleSubmit }
  }
})
</script>
```

### API Calls with Error Handling

```typescript
const loadData = async () => {
  isLoading.value = true
  error.value = null

  try {
    const data = await postAPI.getPosts()
    // Handle success
  } catch (e) {
    error.value = e instanceof APIError
      ? e.message
      : 'Failed to load data'
  } finally {
    isLoading.value = false
  }
}
```

### Navigation

```typescript
import { useRouter } from 'vue-router'

const router = useRouter()

// Navigate programmatically
router.push('/account')
router.push({ name: 'post', params: { id: '123' } })
router.back()
```

### Store Access

```typescript
import { useStore } from 'vuex'
import { computed } from 'vue'

const store = useStore()

// State
const user = computed(() => store.state.user)

// Getters
const isAuthenticated = computed(() => store.getters.isAuthenticated)

// Mutations
store.commit('SET_ERROR', 'Error message')

// Actions
await store.dispatch('signin', { email, password })
```

## Styling Guide

### Design Tokens (CSS Variables)

All design tokens are in `styles/variables.css`:

**Colors**:
- `--surface-base`, `--surface-elevated` - Backgrounds
- `--text-primary`, `--text-secondary`, `--text-muted` - Text colors
- `--border-default`, `--border-subtle` - Borders
- `--color-primary-*` - Brand colors
- `--color-error-*`, `--color-success-*` - Status colors

**Spacing** (4px/8px scale):
- `--space-1` through `--space-12`

**Typography**:
- `--text-xs` through `--text-4xl` - Font sizes
- `--font-normal`, `--font-medium`, `--font-semibold`, `--font-bold` - Weights
- `--leading-tight`, `--leading-normal`, `--leading-relaxed` - Line heights

**Border Radius**:
- `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`, `--radius-full`

**Shadows**:
- `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-xl`

**Transitions**:
- `--transition-fast`, `--transition-base`, `--transition-slow`

### Pre-Built Component Classes

```html
<!-- Buttons -->
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-danger">Delete</button>

<!-- Inputs -->
<input class="input" type="text" />
<textarea class="textarea"></textarea>

<!-- Cards -->
<div class="card">
  <div class="card-header">Header</div>
  <div class="card-body">Content</div>
</div>

<!-- Auth card (centered card for login/signup) -->
<div class="auth-card">
  <div class="auth-header">
    <h1>Welcome</h1>
  </div>
  <!-- Form -->
</div>
```

### Utility Classes

```html
<!-- Layout -->
<div class="flex flex-col items-center gap-4">...</div>
<div class="grid grid-cols-3 gap-4">...</div>

<!-- Spacing -->
<div class="p-4 m-2">Padded</div>

<!-- Typography -->
<h1 class="h1">Heading 1</h1>
<p class="text-lg font-semibold">Text</p>

<!-- Overflow -->
<div class="overflow-y-auto">Scrollable</div>
```

### Responsive Design

Mobile-first approach with utility classes:

```html
<!-- Stack on mobile, row on tablet+ -->
<div class="stack-to-row">
  <div>Left</div>
  <div>Right</div>
</div>

<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- Items -->
</div>
```

## Testing

### Running Tests

```bash
# Unit tests (when implemented)
npm run test:unit

# E2E tests (when implemented)
npm run test:e2e
```

### Testing Strategy

- **Unit Tests**: Component logic, utilities
- **Integration Tests**: API calls, store actions
- **E2E Tests**: User workflows (login, signup, etc.)

## Error Handling

### Global Error Display

Errors from Vuex actions are automatically displayed via `ErrorNotification` component:

```typescript
// Errors are shown globally
try {
  await store.dispatch('signin', { email, password })
} catch {
  // Error already displayed by ErrorNotification
}
```

### Component-Level Errors

```typescript
const error = ref<string | null>(null)

try {
  const data = await postAPI.getPosts()
} catch (e) {
  error.value = e instanceof APIError ? e.message : 'An error occurred'
}
```

### Error Code Handling

```typescript
catch (error) {
  if (error instanceof APIError) {
    switch (error.internalCode) {
      case 40101: // Invalid credentials
        // Show forgot password link
        break
      case 40001: // User already exists
        // Redirect to login
        break
    }
  }
}
```

## Adding New Features

### Adding a New View

1. Create view component in `src/views/`:
```vue
<!-- NewView.vue -->
<template>
  <div class="view-scrollable">
    <div class="view-content">
      <h1>New View</h1>
    </div>
  </div>
</template>
```

2. Add route in `router/index.ts`:
```typescript
{
  path: '/new',
  name: 'new',
  component: () => import('../views/NewView.vue'),
  meta: { requiresAuth: true } // Optional
}
```

### Adding API Endpoints

Add to `api/index.ts`:

```typescript
export const myAPI = {
  async getData(): Promise<DataType[]> {
    return apiRequest<DataType[]>({
      url: '/my-endpoint',
      method: 'GET',
    })
  },
}
```

### Adding Global State

Add to `store/index.ts`:

```typescript
// State
interface State {
  // ... existing state
  newState: SomeType | null
}

// Mutation
SET_NEW_STATE(state, value: SomeType | null) {
  state.newState = value
}

// Action
async fetchNewData({ commit }) {
  const data = await myAPI.getData()
  commit('SET_NEW_STATE', data)
}
```

## Build and Deploy

### Production Build

```bash
npm run build
```

Output in `dist/` directory contains:
- Minified JavaScript bundles
- Optimized CSS
- Static assets

### Environment Variables

Create `.env.production`:

```env
VUE_APP_API_URL=https://api.example.com
```

Access in code:

```typescript
const apiUrl = process.env.VUE_APP_API_URL
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Considerations

- **Lazy Loading**: Routes are lazy-loaded with dynamic imports
- **Code Splitting**: Automatic with Vue CLI
- **Tree Shaking**: Unused code removed in production build
- **Asset Optimization**: Images and fonts optimized

## Best Practices

1. **Always use Composition API** (not Options API)
2. **Always use TypeScript** with proper types
3. **Always use CSS variables** for styling
4. **Keep components focused** and reusable
5. **Handle loading and error states** in UI
6. **Use navigation guards** for route protection
7. **Global state in Vuex**, local state in components
8. **Mobile-first responsive design**

## Related Documentation

- Backend API: See `../backend/README.md`
- Architecture: See `../docs/ARCHITECTURE.md`
- Claude Code Skills: See `../.claude/skills/`

## Troubleshooting

### Common Issues

**Hot reload not working**:
```bash
# Restart dev server
npm run serve
```

**Type errors in IDE**:
```bash
# Restart TypeScript server in VS Code
Cmd+Shift+P → "TypeScript: Restart TS Server"
```

**Build errors**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Contributing

When contributing to the frontend:

1. Follow Vue 3 Composition API patterns
2. Use TypeScript for all new code
3. Follow scrolling conventions (view containers)
4. Use CSS variables instead of hard-coded values
5. Add proper error handling
6. Test on mobile viewport
7. Follow existing code style

## License

MIT License - see LICENSE file for details
