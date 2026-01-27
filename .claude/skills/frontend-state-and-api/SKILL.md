---
name: frontend-state-and-api
description: Defines Vuex store patterns and centralized API client with typed errors. Use when managing global state, making API calls, or handling authentication.
---

# Frontend State Management and API Integration

This skill defines how to manage state with Vuex and make API calls through a centralized client with type-safe error handling.

## When to Use

- When adding global state
- When making any API call
- When handling authentication
- When managing user data
- When deciding between component state vs store
- When handling API errors

## Instructions

### Core Principles

1. **Vuex for Global State**: Authentication, user data, global UI state
2. **Component State for Local**: Form inputs, UI toggles, component-specific data
3. **Centralized API Client**: All HTTP requests go through `api/index.ts`
4. **Type-Safe Errors**: Use `APIError` class for consistent error handling

### Vuex Store Structure

**State:**
```typescript
interface State {
  user: User | null        // Current authenticated user
  isLoading: boolean       // Global loading state
  error: string | null     // Global error message
}
```

**Getters:**
```typescript
getters: {
  isAuthenticated: (state) => !!state.user,
  currentUser: (state) => state.user,
}
```

**Mutations (Synchronous):**
```typescript
mutations: {
  SET_USER(state, user: User | null) {
    state.user = user
  },
  SET_LOADING(state, isLoading: boolean) {
    state.isLoading = isLoading
  },
}
```

**Actions (Asynchronous):**
```typescript
actions: {
  async signin({ commit }, { email, password }) {
    commit('SET_LOADING', true)
    try {
      await authAPI.signin(email, password)
      await this.dispatch('fetchUser')
    } catch (error) {
      commit('SET_ERROR', error.message)
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },
}
```

### Using Store in Components

```typescript
import { computed } from 'vue'
import { useStore } from 'vuex'

export default defineComponent({
  setup() {
    const store = useStore()

    // Access state with computed
    const user = computed(() => store.state.user)
    const isAuthenticated = computed(() => store.getters.isAuthenticated)

    // Call actions
    const login = async () => {
      await store.dispatch('signin', { email, password })
    }

    return { user, isAuthenticated, login }
  },
})
```

### API Client Structure

**Centralized Axios Instance:**
```typescript
const axiosInstance = axios.create({
  baseURL: '/api',
  withCredentials: true, // Send cookies with requests
})
```

**APIError Class:**
```typescript
export class APIError extends Error {
  constructor(
    message: string,
    public readonly internalCode: number,
    public readonly statusCode: number
  ) {
    super(message)
  }
}
```

**API Module Pattern:**
```typescript
export const authAPI = {
  async signup(email: string, password: string): Promise<{ message: string }> {
    return apiRequest<{ message: string }>({
      url: '/auth/signup',
      method: 'POST',
      data: { email, password },
    })
  },

  async signin(email: string, password: string): Promise<{ message: string }> {
    return apiRequest<{ message: string }>({
      url: '/auth/signin',
      method: 'POST',
      data: { email, password },
    })
  },
}
```

### Adding New API Endpoints

```typescript
// 1. Define response type
interface Post {
  id: string
  title: string
  content: string
}

// 2. Create API module
export const postAPI = {
  async getPosts(): Promise<Post[]> {
    return apiRequest<Post[]>({
      url: '/posts',
      method: 'GET',
    })
  },

  async createPost(data: { title: string; content: string }): Promise<Post> {
    return apiRequest<Post>({
      url: '/posts',
      method: 'POST',
      data,
    })
  },
}
```

### Error Handling Patterns

**Global Error Display:**
```typescript
try {
  await store.dispatch('signin', { email, password })
} catch (error) {
  // Error already set in store and displayed globally
}
```

**Component-Level Error Handling:**
```typescript
const error = ref<string | null>(null)
const isLoading = ref(false)

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

**Handling Specific Error Codes:**
```typescript
try {
  await store.dispatch('signin', { email, password })
} catch (error) {
  if (error instanceof APIError) {
    switch (error.internalCode) {
      case 40101: // Invalid credentials
        // Show password reset option
        break
      case 40001: // User already exists
        // Redirect to login
        break
    }
  }
}
```

### When to Use Store vs Component State

**Use Vuex Store When:**
- Data is needed across multiple components
- Data should persist during navigation
- Data is authentication-related
- Data is global application state

**Use Component State When:**
- Data is local to component
- Data is temporary (form inputs, UI toggles)
- Data doesn't need to outlive component
- Data is not shared with other components

### Common Patterns

**Authenticated API Call:**
```typescript
try {
  const data = await userAPI.getMe()
} catch (error) {
  if (error instanceof APIError && error.statusCode === 401) {
    router.push('/login')
  }
}
```

**Loading State Pattern:**
```typescript
const isLoading = ref(false)
const data = ref<Post[]>([])

const loadData = async () => {
  isLoading.value = true
  try {
    data.value = await postAPI.getPosts()
  } finally {
    isLoading.value = false
  }
}
```

### Checklist

- [ ] Global state only in Vuex store
- [ ] Local state uses `ref()` or `reactive()`
- [ ] All API calls go through centralized client
- [ ] Errors handled with try/catch
- [ ] Loading states shown to user
- [ ] APIError instances checked for specific codes
- [ ] Network errors handled gracefully
- [ ] Cleanup in `onUnmounted` for timers/listeners
- [ ] Type definitions for all API responses
