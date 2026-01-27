/**
 * Error code mappings for human-readable error messages.
 *
 * Maps backend error codes (internal_code) to user-friendly messages.
 * Error code ranges:
 * - 40000-40099: Bad Request (validation, malformed input)
 * - 40100-40199: Unauthorized (authentication errors)
 * - 40200-40299: Forbidden (permission errors)
 * - 40400-40499: Not Found
 * - 50000-59999: Server errors
 *
 * @see backend/api/exceptions.py for error code definitions
 */
const ERROR_MESSAGES: Record<number, string> = {
  // 40000 - 40099: Bad Request
  40000: 'Bad request',
  40001: 'An account with this email already exists. Please sign in instead.',

  // 40100 - 40199: Unauthorized
  40100: 'You are not authorized to perform this action.',
  40101: 'Invalid email or password. Please check your credentials and try again.',
  40102: 'Please sign in to continue.',
  40103: 'Your session token is invalid. Please sign in again.',
  40104: 'Your session has expired. Please sign in again.',
  40105: 'User account not found.',

  // 50000 - 59999: Server Error
  50000: 'An unexpected server error occurred. Please try again later.',
}

/**
 * API Error Response structure from backend.
 *
 * All API errors from the backend follow this format.
 * The response is automatically parsed by the Axios interceptor.
 *
 * @property internal_code - Unique error code for specific error type
 * @property detail - Human-readable error message from backend
 * @property status_code - HTTP status code (400, 401, 404, 500, etc.)
 *
 * @example
 * {
 *   internal_code: 40001,
 *   detail: "User with this email already exists",
 *   status_code: 400
 * }
 */
export interface APIErrorResponse {
  internal_code: number
  detail: string
  status_code: number
}

/**
 * Get human-readable error message from error code.
 *
 * Looks up the error code in ERROR_MESSAGES mapping and returns
 * a user-friendly message. Falls back to provided fallback or
 * a generic error message.
 *
 * @param errorCode - Backend error code (e.g., 40001, 40101)
 * @param fallback - Optional fallback message if code not found
 * @returns User-friendly error message
 *
 * @example
 * getErrorMessage(40001) // "An account with this email already exists..."
 * getErrorMessage(99999, "Custom fallback") // "Custom fallback"
 */
export function getErrorMessage(errorCode: number, fallback?: string): string {
  return ERROR_MESSAGES[errorCode] || fallback || 'An unexpected error occurred. Please try again.'
}

/**
 * Parse API error response and return human-readable message.
 *
 * Handles various error formats:
 * - TypeError (network errors)
 * - Error objects
 * - API error responses with internal_code
 * - Generic objects with detail property
 *
 * Always returns a user-friendly string, never throws.
 *
 * @param error - Error from API call (can be any type)
 * @returns User-friendly error message
 *
 * @example
 * try {
 *   await authAPI.signin(email, password)
 * } catch (error) {
 *   const message = parseAPIError(error)
 *   console.error(message) // "Invalid email or password..."
 * }
 */
export function parseAPIError(error: unknown): string {
  // Handle fetch errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return 'Network error. Please check your connection and try again.'
  }

  // Handle Error objects
  if (error instanceof Error) {
    return error.message
  }

  // Handle API error response
  if (typeof error === 'object' && error !== null) {
    const apiError = error as Partial<APIErrorResponse>
    if (apiError.internal_code !== undefined) {
      return getErrorMessage(apiError.internal_code, apiError.detail)
    }
    if (apiError.detail) {
      return apiError.detail
    }
  }

  return 'An unexpected error occurred. Please try again.'
}

/**
 * Extract API error from fetch Response object.
 *
 * Attempts to parse the response body as JSON to extract
 * the API error structure. If parsing fails, returns a
 * default error with HTTP status information.
 *
 * @param response - Fetch API Response object
 * @returns Parsed API error response
 *
 * @example
 * const response = await fetch('/api/auth/signin', { ... })
 * if (!response.ok) {
 *   const error = await extractAPIError(response)
 *   console.error(error.detail)
 * }
 */
export async function extractAPIError(response: Response): Promise<APIErrorResponse> {
  try {
    const data = await response.json()
    return {
      internal_code: data.internal_code ?? 50000,
      detail: data.detail ?? 'An unexpected error occurred',
      status_code: data.status_code ?? response.status,
    }
  } catch {
    // If response is not JSON, return a default error
    return {
      internal_code: 50000,
      detail: `HTTP ${response.status}: ${response.statusText}`,
      status_code: response.status,
    }
  }
}

