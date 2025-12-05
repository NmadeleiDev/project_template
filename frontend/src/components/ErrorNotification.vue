<template>
  <Transition name="slide-down">
    <div v-if="message" class="notification-container">
      <div class="notification notification-error">
        <svg
          class="notification-icon"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span class="notification-text">{{ message }}</span>
        <button class="notification-close" @click="close" aria-label="Close">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script lang="ts">
import { defineComponent, watch } from 'vue'

export default defineComponent({
  name: 'ErrorNotification',
  props: {
    message: {
      type: String,
      default: null,
    },
    duration: {
      type: Number,
      default: 5000, // 5 seconds
    },
  },
  emits: ['close'],
  setup(props, { emit }) {
    let timeoutId: ReturnType<typeof setTimeout> | null = null

    const close = () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
        timeoutId = null
      }
      emit('close')
    }

    watch(
      () => props.message,
      (newMessage) => {
        if (timeoutId) {
          clearTimeout(timeoutId)
        }
        if (newMessage && props.duration > 0) {
          timeoutId = setTimeout(() => {
            close()
          }, props.duration)
        }
      },
      { immediate: true }
    )

    return {
      close,
    }
  },
})
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: var(--space-8);
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-toast);
  pointer-events: none;
  padding: 0 var(--space-4);
  width: 100%;
  max-width: 540px;
}

.notification {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  backdrop-filter: var(--backdrop-blur);
  border-radius: var(--radius-lg);
  pointer-events: auto;
  width: 100%;
}

.notification-error {
  background: var(--color-error-100);
  border: 1px solid var(--color-error-300);
  box-shadow: var(--shadow-error);
}

.notification-icon {
  width: 20px;
  height: 20px;
  color: var(--color-error-400);
  flex-shrink: 0;
}

.notification-text {
  color: var(--color-error-400);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  line-height: var(--leading-normal);
  flex: 1;
}

.notification-close {
  background: none;
  border: none;
  padding: var(--space-1);
  cursor: pointer;
  color: var(--color-error-400);
  opacity: 0.7;
  transition: opacity var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-close:hover {
  opacity: 1;
}

.notification-close svg {
  width: 18px;
  height: 18px;
}

/* Override slide-down for centered positioning */
.slide-down-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-100%);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-100%);
}
</style>
