<template>
  <div class="view-fullscreen">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Welcome back</h1>
        <p>Sign in to your account</p>
      </div>

      <form @submit.prevent="handleSubmit" class="form-stack">
        <div class="form-group">
          <label for="email" class="form-label">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="input"
            placeholder="you@example.com"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="input"
            placeholder="••••••••"
            required
            :disabled="isLoading"
          />
        </div>

        <button 
          type="submit" 
          class="btn btn-primary btn-block" 
          :class="{ 'btn-loading': isLoading }"
          :disabled="isLoading"
        >
          <span v-if="!isLoading">Sign In</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>Don't have an account? <router-link to="/signup">Sign up</router-link></p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'LoginView',
  setup() {
    const store = useStore()
    const router = useRouter()

    const email = ref('')
    const password = ref('')

    const isLoading = computed(() => store.state.isLoading)

    const handleSubmit = async () => {
      store.commit('SET_ERROR', null)
      try {
        await store.dispatch('signin', {
          email: email.value,
          password: password.value
        })
        router.push('/account')
      } catch {
        // Error is already handled by the store and displayed globally
      }
    }

    return {
      email,
      password,
      isLoading,
      handleSubmit
    }
  }
})
</script>
