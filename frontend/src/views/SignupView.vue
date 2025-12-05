<template>
  <div class="view-fullscreen">
    <div class="auth-card">
      <div class="auth-header">
        <h1>Create account</h1>
        <p>Get started with your free account</p>
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
            minlength="8"
            :disabled="isLoading"
          />
          <span class="form-hint">At least 8 characters</span>
        </div>

        <div class="form-group">
          <label for="confirmPassword" class="form-label">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            class="input"
            placeholder="••••••••"
            required
            :disabled="isLoading"
          />
        </div>

        <div v-if="validationError" class="error-message">
          {{ validationError }}
        </div>

        <button 
          type="submit" 
          class="btn btn-primary btn-block" 
          :class="{ 'btn-loading': isLoading }"
          :disabled="isLoading"
        >
          <span v-if="!isLoading">Create Account</span>
        </button>
      </form>

      <div class="auth-footer">
        <p>Already have an account? <router-link to="/login">Sign in</router-link></p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'SignupView',
  setup() {
    const store = useStore()
    const router = useRouter()

    const email = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const validationError = ref<string | null>(null)

    const isLoading = computed(() => store.state.isLoading)

    const handleSubmit = async () => {
      validationError.value = null
      store.commit('SET_ERROR', null)

      if (password.value !== confirmPassword.value) {
        validationError.value = 'Passwords do not match'
        return
      }

      try {
        await store.dispatch('signup', {
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
      confirmPassword,
      validationError,
      isLoading,
      handleSubmit
    }
  }
})
</script>
