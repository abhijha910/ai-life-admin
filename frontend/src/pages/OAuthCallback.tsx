import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import api from '../services/api'

export default function OAuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const queryClient = useQueryClient()

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      const error = searchParams.get('error')

      if (error) {
        alert(`OAuth error: ${error}`)
        navigate('/emails')
        return
      }

      if (!code || !state) {
        alert('Missing OAuth parameters')
        navigate('/emails')
        return
      }

      try {
        // Extract provider from state (format: state_token:provider:user_id)
        // If state doesn't contain provider, try to detect from URL or use 'gmail' as default
        let provider = 'gmail' // default
        if (state && state.includes(':')) {
          const parts = state.split(':')
          if (parts.length >= 2) {
            provider = parts[1] // provider is second part
          }
        }
        
        // Call backend to handle OAuth callback (GET request with query params)
        // Provider is optional since backend can extract it from state
        const response = await api.get('/emails/oauth/callback', {
          params: { code, state, provider }
        })
        
        // Refresh accounts and emails lists
        queryClient.invalidateQueries({ queryKey: ['email-accounts'] })
        queryClient.invalidateQueries({ queryKey: ['emails'] })
        
        // Auto-sync emails after connection
        try {
          await api.post('/emails/sync', {})
          queryClient.invalidateQueries({ queryKey: ['emails'] })
        } catch (syncError: any) {
          // Sync might fail, but connection is successful
          console.warn('Auto-sync failed:', syncError)
        }
        
        // Success - redirect to emails page with success message
        navigate('/emails', { 
          state: { 
            message: `Successfully connected ${response.data?.email_address || 'email account'}! Emails are being synced...` 
          } 
        })
      } catch (error: any) {
        alert(error.response?.data?.detail || 'Failed to connect email account')
        navigate('/emails')
      }
    }

    handleCallback()
  }, [searchParams, navigate, queryClient])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">Connecting your email account...</p>
      </div>
    </div>
  )
}
