import { createStore } from 'vuex'
import { authAPI, userAPI, APIError } from '../api'

interface User {
  id: string
  email: string
  created_at: string
}

interface State {
  user: User | null
  isLoading: boolean
  error: string | null
}

export default createStore<State>({
  state: {
    user: null,
    isLoading: false,
    error: null
  },
  getters: {
    isAuthenticated: (state) => !!state.user,
    currentUser: (state) => state.user
  },
  mutations: {
    SET_USER(state, user: User | null) {
      state.user = user
    },
    SET_LOADING(state, isLoading: boolean) {
      state.isLoading = isLoading
    },
    SET_ERROR(state, error: string | null) {
      state.error = error
    }
  },
  actions: {
    async signup({ commit }, { email, password }: { email: string; password: string }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        await authAPI.signup(email, password)
        await this.dispatch('fetchUser')
      } catch (error) {
        const errorMessage = error instanceof APIError ? error.message : 'An unexpected error occurred'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async signin({ commit }, { email, password }: { email: string; password: string }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        await authAPI.signin(email, password)
        await this.dispatch('fetchUser')
      } catch (error) {
        const errorMessage = error instanceof APIError ? error.message : 'An unexpected error occurred'
        commit('SET_ERROR', errorMessage)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async signout({ commit }) {
      try {
        await authAPI.signout()
      } finally {
        commit('SET_USER', null)
      }
    },

    async fetchUser({ commit }) {
      try {
        const user = await userAPI.getMe()
        commit('SET_USER', user)
      } catch (error) {
        // Don't show error for 401 when fetching user (user just not logged in)
        if (error instanceof APIError && error.statusCode === 401) {
          commit('SET_USER', null)
          return
        }
        // Don't show error for network errors when fetching user
        if (error instanceof APIError && error.statusCode !== 401) {
          commit('SET_ERROR', error.message)
        }
        commit('SET_USER', null)
      }
    }
  }
})
