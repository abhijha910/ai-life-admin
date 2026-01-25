import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle token refresh on 401 and connection errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Handle connection errors (backend not running)
    if (!error.response) {
      // Network error or backend not available
      if (error.code === 'ECONNREFUSED' || error.code === 'ECONNRESET' || error.message?.includes('Network Error')) {
        console.error('Backend connection error. Is the backend server running on http://localhost:8000?')
        // Don't redirect to login for connection errors - just show error
        return Promise.reject(new Error('Backend server is not available. Please ensure the backend is running on http://localhost:8000'))
      }
    }
    
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          })
          localStorage.setItem('access_token', response.data.access_token)
          localStorage.setItem('refresh_token', response.data.refresh_token)
          return api.request(error.config)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
