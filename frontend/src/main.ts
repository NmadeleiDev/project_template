/**
 * Application entry point.
 *
 * Initializes the Vue 3 application with:
 * - Vuex store for global state management
 * - Vue Router for client-side routing
 * - Global CSS design system
 *
 * The app is mounted to the #app element in index.html.
 */

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// Import global styles (design tokens, layout, components)
import './styles/index.css'

// Create and mount Vue application
createApp(App)
  .use(store)   // Enable Vuex state management
  .use(router)  // Enable Vue Router
  .mount('#app')
