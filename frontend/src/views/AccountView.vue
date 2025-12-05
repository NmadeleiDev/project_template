<template>
  <div class="view-fullscreen">
    <div class="account-card">
      <div class="account-header flex flex-col items-center gap-6 mb-10">
        <div class="avatar avatar-lg">
          <span>{{ userInitial }}</span>
        </div>
        <h1 class="heading-3">Your Account</h1>
      </div>

      <div class="detail-list mb-10">
        <div class="detail-item">
          <span class="detail-label">Email</span>
          <span class="detail-value">{{ user?.email }}</span>
        </div>

        <div class="detail-item">
          <span class="detail-label">User ID</span>
          <span class="detail-value mono">{{ user?.id }}</span>
        </div>

        <div class="detail-item">
          <span class="detail-label">Member since</span>
          <span class="detail-value">{{ formattedDate }}</span>
        </div>
      </div>

      <button @click="handleSignout" class="btn btn-danger btn-block">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
          <polyline points="16 17 21 12 16 7"></polyline>
          <line x1="21" y1="12" x2="9" y2="12"></line>
        </svg>
        Sign Out
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'AccountView',
  setup() {
    const store = useStore()
    const router = useRouter()

    const user = computed(() => store.getters.currentUser)

    const userInitial = computed(() => {
      const email = user.value?.email
      return email ? email.charAt(0).toUpperCase() : '?'
    })

    const formattedDate = computed(() => {
      if (!user.value?.created_at) return ''
      const date = new Date(user.value.created_at)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    })

    const handleSignout = async () => {
      await store.dispatch('signout')
      router.push('/login')
    }

    return {
      user,
      userInitial,
      formattedDate,
      handleSignout
    }
  }
})
</script>
