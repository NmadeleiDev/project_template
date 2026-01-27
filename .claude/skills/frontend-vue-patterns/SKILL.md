---
name: frontend-vue-patterns
description: Defines Vue 3 Composition API patterns with TypeScript. Use when creating components, managing reactivity, handling props/events, or integrating with store/router.
---

# Frontend Vue 3 Patterns

This skill defines Vue 3 component development patterns using Composition API with TypeScript.

## When to Use

- When creating any Vue component
- When managing reactive state
- When defining props or emitting events
- When using Vuex store in components
- When implementing forms
- When reviewing component code

## Instructions

### Core Principle

**This project uses Vue 3 Composition API with TypeScript for all components. Options API is not used.**

### Standard Component Template

```vue
<template>
  <div class="component-name">
    <!-- Template content -->
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'ComponentName', // PascalCase, matches file name

  props: {
    // Props definition
  },

  emits: ['event-name'], // Declare all emitted events

  setup(props, { emit }) {
    const store = useStore()
    const router = useRouter()

    // State
    const someValue = ref('')

    // Computed
    const computedValue = computed(() => someValue.value.toUpperCase())

    // Methods
    const handleAction = () => {
      emit('event-name', someValue.value)
    }

    // Return everything used in template
    return {
      someValue,
      computedValue,
      handleAction,
    }
  },
})
</script>

<style scoped>
/* Component-specific styles */
</style>
```

### Reactivity Patterns

**ref() for Primitive Values:**
```typescript
import { ref } from 'vue'

const email = ref('')
const count = ref(0)
const isActive = ref(false)

// Access value with .value
email.value = 'new@example.com'

// In template, no .value needed
// <input v-model="email" />
```

**reactive() for Objects:**
```typescript
import { reactive } from 'vue'

const form = reactive({
  email: '',
  password: '',
  rememberMe: false,
})

// Access directly (no .value)
form.email = 'new@example.com'
```

**computed() for Derived State:**
```typescript
import { computed } from 'vue'

const fullName = computed(() => {
  return `${firstName.value} ${lastName.value}`
})
```

### Props Definition

```typescript
import { defineComponent, PropType } from 'vue'

interface User {
  id: string
  email: string
}

export default defineComponent({
  props: {
    // Required prop
    user: {
      type: Object as PropType<User>,
      required: true,
    },

    // Optional with default
    size: {
      type: String as PropType<'small' | 'medium' | 'large'>,
      default: 'medium',
    },

    // Boolean prop
    isActive: {
      type: Boolean,
      default: false,
    },
  },

  setup(props) {
    // Access props (reactive)
    console.log(props.user.email)
    return {}
  },
})
```

### Events (emit)

```typescript
export default defineComponent({
  props: {
    modelValue: String, // v-model support
  },

  emits: ['update:modelValue', 'submit'],

  setup(props, { emit }) {
    const handleInput = (event: Event) => {
      const target = event.target as HTMLInputElement
      emit('update:modelValue', target.value)
    }

    const handleSubmit = () => {
      emit('submit', props.modelValue)
    }

    return { handleInput, handleSubmit }
  },
})
```

### Lifecycle Hooks

```typescript
import { onMounted, onUnmounted } from 'vue'

export default defineComponent({
  setup() {
    onMounted(() => {
      // Fetch data, set up listeners
    })

    onUnmounted(() => {
      // Clean up listeners, timers
    })

    return {}
  },
})
```

### Watchers

```typescript
import { watch, ref } from 'vue'

const email = ref('')

// Watch single ref
watch(email, (newValue, oldValue) => {
  console.log('Email changed:', oldValue, '->', newValue)
})

// Watch with options
watch(
  searchQuery,
  async (newQuery) => {
    await performSearch(newQuery)
  },
  { immediate: true }
)
```

### Store Integration (Vuex)

```typescript
import { computed } from 'vue'
import { useStore } from 'vuex'

export default defineComponent({
  setup() {
    const store = useStore()

    // State
    const user = computed(() => store.state.user)

    // Getters
    const isAuthenticated = computed(() => store.getters.isAuthenticated)

    // Actions
    const login = async (email: string, password: string) => {
      await store.dispatch('signin', { email, password })
    }

    return { user, isAuthenticated, login }
  },
})
```

### Router Integration

```typescript
import { useRouter, useRoute } from 'vue-router'

export default defineComponent({
  setup() {
    const router = useRouter()
    const route = useRoute()

    // Current route info
    const currentPath = computed(() => route.path)

    // Navigate programmatically
    const goToAccount = () => {
      router.push('/account')
    }

    return { currentPath, goToAccount }
  },
})
```

### Form Handling

```vue
<template>
  <form @submit.prevent="handleSubmit" class="form-stack">
    <div class="form-group">
      <label for="email">Email</label>
      <input
        id="email"
        v-model="form.email"
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
import { reactive, ref } from 'vue'

export default defineComponent({
  setup() {
    const form = reactive({
      email: '',
      password: '',
    })

    const isLoading = ref(false)

    const handleSubmit = async () => {
      isLoading.value = true
      try {
        await submitForm(form)
      } finally {
        isLoading.value = false
      }
    }

    return { form, isLoading, handleSubmit }
  },
})
</script>
```

### Conditional and List Rendering

```vue
<template>
  <!-- Conditional -->
  <div v-if="isAuthenticated">Welcome!</div>
  <div v-else>Please log in</div>

  <!-- List -->
  <div v-for="item in items" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

### Dynamic Classes

```vue
<template>
  <div
    :class="{
      'is-active': isActive,
      'has-error': hasError,
    }"
  >
    Content
  </div>
</template>
```

### Common Mistakes to Avoid

**❌ WRONG: Options API**
```vue
<script>
export default {
  data() {
    return { count: 0 }
  },
}
</script>
```

**✅ CORRECT: Composition API**
```vue
<script lang="ts">
import { defineComponent, ref } from 'vue'

export default defineComponent({
  setup() {
    const count = ref(0)
    return { count }
  }
})
</script>
```

**❌ WRONG: Missing .value**
```typescript
const count = ref(0)
count++ // ❌ Wrong!
```

**✅ CORRECT: Use .value**
```typescript
const count = ref(0)
count.value++ // ✅ Correct
```

### File Naming Conventions

- **Components**: PascalCase - `UserCard.vue`, `LoginView.vue`
- **Composables**: camelCase with `use` prefix - `useAuth.ts`
- **Utils**: camelCase - `formatDate.ts`
- **Types**: PascalCase - `User.ts`

### Checklist

- [ ] Uses Composition API (`defineComponent` + `setup`)
- [ ] TypeScript enabled (`<script lang="ts">`)
- [ ] Component has `name` property (PascalCase)
- [ ] All emits declared in `emits` array
- [ ] Props use TypeScript `PropType` for complex types
- [ ] Uses `ref()` for primitives, `reactive()` for objects
- [ ] All computed values use `computed()`
- [ ] Cleanup in `onUnmounted` for side effects
- [ ] Returns everything used in template from `setup()`
