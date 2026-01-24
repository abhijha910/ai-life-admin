import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  user: any | null
  login: (token: string, refreshToken: string, user: any) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: !!localStorage.getItem('access_token'),
  user: null,
  login: (token: string, refreshToken: string, user: any) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('refresh_token', refreshToken)
    set({ isAuthenticated: true, user })
  },
  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ isAuthenticated: false, user: null })
  },
}))
