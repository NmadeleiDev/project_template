/**
 * Error code mappings for human-readable error messages
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
 * API Error Response structure
 */
export interface APIErrorResponse {
  internal_code: number
  detail: string
  status_code: number
}

/**
 * Get human-readable error message from error code
 */
export function getErrorMessage(errorCode: number, fallback?: string): string {
  return ERROR_MESSAGES[errorCode] || fallback || 'An unexpected error occurred. Please try again.'
}

/**
 * Parse API error response and return human-readable message
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
 * Extract API error from fetch response
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

