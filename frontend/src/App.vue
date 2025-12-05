<template>
  <div class="bg-pattern"></div>
  <ErrorNotification
    :message="errorMessage"
    @close="clearError"
  />
  <main class="app-main">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import ErrorNotification from './components/ErrorNotification.vue'

export default defineComponent({
  name: 'App',
  components: {
    ErrorNotification,
  },
  setup() {
    const store = useStore()
    const errorMessage = computed(() => store.state.error as string | null)

    const clearError = () => {
      store.commit('SET_ERROR', null)
    }

    return {
      errorMessage,
      clearError,
    }
  },
})
</script>
