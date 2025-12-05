import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios'
import { parseAPIError, APIErrorResponse } from '../utils/errors'

const API_BASE = '/api'

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(
    message: string,
    public readonly internalCode: number,
    public readonly statusCode: number,
    public readonly response?: APIErrorResponse
  ) {
    super(message)
    this.name = 'APIError'
  }
}

/**
 * Create axios instance with default config
 */
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Response interceptor to handle errors
 */
axiosInstance.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    const axiosError = error as AxiosError<APIErrorResponse>
    
    if (axiosError.response) {
      // Server responded with error status
      const apiError = axiosError.response.data
      if (apiError && apiError.internal_code !== undefined) {
        const errorMessage = parseAPIError(apiError)
        throw new APIError(
          errorMessage,
          apiError.internal_code,
          apiError.status_code ?? axiosError.response.status,
          apiError
        )
      }
      // Fallback for non-standard error responses
      const errorMessage = 'Unexpected error occurred, please try again later.'
      throw new APIError(
        errorMessage,
        50000,
        axiosError.response.status
      )
    } else if (axiosError.request) {
      // Request was made but no response received (network error)
      throw new APIError(
        'Network error. Please check your connection and try again.',
        50000,
        500
      )
    } else {
      // Something else happened
      throw new APIError(
        parseAPIError(error),
        50000,
        500
      )
    }
  }
)

/**
 * Base API request wrapper
 */
async function apiRequest<T>(config: AxiosRequestConfig): Promise<T> {
  const response = await axiosInstance.request<T>(config)
  return response.data
}

/**
 * Auth API endpoints
 */
export const authAPI = {
  /**
   * Sign up a new user
   */
  async signup(email: string, password: string): Promise<{ message: string }> {
    return apiRequest<{ message: string }>({
      url: '/auth/signup',
      method: 'POST',
      data: { email, password },
    })
  },

  /**
   * Sign in an existing user
   */
  async signin(email: string, password: string): Promise<{ message: string }> {
    return apiRequest<{ message: string }>({
      url: '/auth/signin',
      method: 'POST',
      data: { email, password },
    })
  },

  /**
   * Sign out the current user
   */
  async signout(): Promise<{ message: string }> {
    return apiRequest<{ message: string }>({
      url: '/auth/signout',
      method: 'POST',
    })
  },
}

/**
 * User API endpoints
 */
export const userAPI = {
  /**
   * Get current user information
   */
  async getMe(): Promise<{ id: string; email: string; created_at: string }> {
    return apiRequest<{ id: string; email: string; created_at: string }>({
      url: '/user/me',
      method: 'GET',
    })
  },
}

