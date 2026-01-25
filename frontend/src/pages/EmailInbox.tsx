import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useLocation, useNavigate } from 'react-router-dom'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { Mail, RefreshCw, Plus, Search, Star } from 'lucide-react'

function ConnectEmailButton({ provider, label, className }: { 
  provider: 'gmail' | 'outlook'
  label: string
  className: string
  onSuccess: () => void
}) {
  const [loading, setLoading] = useState(false)

  const handleConnect = async () => {
    setLoading(true)
    try {
      const response = await api.get(`/emails/oauth/${provider}/authorize`)
      // Redirect to OAuth URL
      window.location.href = response.data.auth_url
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || `Failed to initiate ${provider} OAuth. Please check backend configuration.`
      // Show a more user-friendly error message
      alert(`⚠️ OAuth Configuration Required\n\n${errorMsg}\n\nTo enable ${provider === 'gmail' ? 'Gmail' : 'Outlook'} OAuth:\n1. Create OAuth credentials in ${provider === 'gmail' ? 'Google Cloud Console' : 'Azure Portal'}\n2. Add credentials to backend .env file:\n   ${provider === 'gmail' ? 'GMAIL_CLIENT_ID=your_client_id\n   GMAIL_CLIENT_SECRET=your_client_secret' : 'OUTLOOK_CLIENT_ID=your_client_id\n   OUTLOOK_CLIENT_SECRET=your_client_secret'}\n3. Restart the backend server`)
      setLoading(false)
    }
  }

  return (
    <button
      onClick={handleConnect}
      disabled={loading}
      className={className}
    >
      {loading ? 'Connecting...' : label}
    </button>
  )
}

export default function EmailInbox() {
  const [searchQuery, setSearchQuery] = useState('')
  const [showConnectModal, setShowConnectModal] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [filters, setFilters] = useState({
    unreadOnly: false,
    importantOnly: false,
    dateFrom: '',
    dateTo: ''
  })
  const [showFilters, setShowFilters] = useState(false)
  const queryClient = useQueryClient()
  const location = useLocation()
  const navigate = useNavigate()

  // Show success message from OAuth callback
  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message)
      // Clear the message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000)
      // Clear location state
      window.history.replaceState({}, document.title)
    }
  }, [location])

  // Fetch connected email accounts
  const { data: accountsData } = useQuery({
    queryKey: ['email-accounts'],
    queryFn: async () => {
      try {
        const response = await api.get('/emails/accounts')
        // Deduplicate on frontend as well (in case backend hasn't cleaned up yet)
        const seen = new Map()
        const unique = response.data.filter((account: any) => {
          const key = `${account.email_address.toLowerCase()}_${account.provider}`
          if (seen.has(key)) return false
          seen.set(key, true)
          return true
        })
        return unique
      } catch (error: any) {
        // Silently fail - backend might be down
        console.warn('Failed to fetch email accounts:', error)
        return []
      }
    },
    retry: 2,
    retryDelay: 1000,
  })

  const { data, isLoading, error } = useQuery({
    queryKey: ['emails', searchQuery, filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: '1',
        page_size: '50'
      })
      if (searchQuery) {
        params.append('search', searchQuery)
      }
      if (filters.unreadOnly) {
        params.append('unread_only', 'true')
      }
      if (filters.importantOnly) {
        params.append('important_only', 'true')
      }
      if (filters.dateFrom) {
        params.append('date_from', filters.dateFrom)
      }
      if (filters.dateTo) {
        params.append('date_to', filters.dateTo)
      }
      const response = await api.get(`/emails?${params.toString()}`)
      return response.data
    },
    retry: 2,
    retryDelay: 1000,
  })

  const connectedAccounts = accountsData || []

  const syncMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/emails/sync', {})
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] })
    },
  })

  const emails = data?.emails || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Mail className="w-6 h-6 text-indigo-600" />
                <h2 className="text-2xl font-bold text-gray-900">Email Inbox</h2>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setShowConnectModal(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>Connect Account</span>
                </button>
                <button
                  onClick={() => syncMutation.mutate()}
                  disabled={syncMutation.isPending}
                  className="flex items-center space-x-2 px-4 py-2 bg-white text-indigo-600 border border-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${syncMutation.isPending ? 'animate-spin' : ''}`} />
                  <span>Sync</span>
                </button>
              </div>
            </div>

            {/* Success Message */}
            {successMessage && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm font-semibold text-green-800">
                  ✓ {successMessage}
                </p>
              </div>
            )}

            {/* Connected Accounts */}
            {connectedAccounts.length > 0 && (
              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-green-800 mb-2">
                      ✓ Connected Accounts ({connectedAccounts.length})
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {connectedAccounts.map((account: any) => (
                        <span
                          key={account.id}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 capitalize"
                        >
                          {account.provider === 'gmail' ? '📧' : account.provider === 'outlook' ? '📬' : '📨'} {account.email_address}
                        </span>
                      ))}
                    </div>
                  </div>
                  {connectedAccounts.length > 1 && (
                    <button
                      onClick={async () => {
                        try {
                          await api.post('/emails/accounts/cleanup')
                          queryClient.invalidateQueries({ queryKey: ['email-accounts'] })
                          alert('Duplicate accounts cleaned up!')
                        } catch (err: any) {
                          alert(`Failed to cleanup: ${err.response?.data?.detail || err.message}`)
                        }
                      }}
                      className="ml-4 px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors whitespace-nowrap"
                    >
                      Cleanup Duplicates
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Search and Filters */}
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search emails..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  />
                </div>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`px-4 py-2 rounded-lg border transition-colors ${
                    showFilters || filters.unreadOnly || filters.importantOnly || filters.dateFrom || filters.dateTo
                      ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  Filters
                </button>
              </div>
              
              {/* Filter Panel */}
              {showFilters && (
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.unreadOnly}
                        onChange={(e) => setFilters({ ...filters, unreadOnly: e.target.checked })}
                        className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                      />
                      <span className="text-sm font-medium text-gray-700">Unread Only</span>
                    </label>
                    <label className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filters.importantOnly}
                        onChange={(e) => setFilters({ ...filters, importantOnly: e.target.checked })}
                        className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                      />
                      <span className="text-sm font-medium text-gray-700">Important Only</span>
                    </label>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setFilters({ unreadOnly: false, importantOnly: false, dateFrom: '', dateTo: '' })}
                        className="text-xs text-gray-600 hover:text-gray-800 underline"
                      >
                        Clear Filters
                      </button>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">From Date</label>
                      <input
                        type="date"
                        value={filters.dateFrom}
                        onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">To Date</label>
                      <input
                        type="date"
                        value={filters.dateTo}
                        onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Email List */}
          <div className="divide-y divide-gray-200">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <p className="mt-4 text-gray-500">Loading emails...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Failed to load emails</p>
                <button
                  onClick={() => queryClient.invalidateQueries({ queryKey: ['emails'] })}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Retry
                </button>
              </div>
            ) : emails.length > 0 ? (
              emails.map((email: any) => {
                // Extract preview text from body_text (first 100 chars, clean HTML)
                const getPreviewText = () => {
                  if (email.ai_summary) return email.ai_summary;
                  if (email.body_text) {
                    const text = email.body_text.replace(/\s+/g, ' ').trim();
                    return text.length > 100 ? text.substring(0, 100) + '...' : text;
                  }
                  return '';
                };
                
                const previewText = getPreviewText();
                const senderDisplay = email.sender_name || email.sender_email || 'Unknown';
                const senderEmailOnly = email.sender_email ? email.sender_email.split('<')[0].trim() : '';
                
                return (
                  <div
                    key={email.id}
                    onClick={() => {
                      // Navigate to email detail page
                      navigate(`/emails/${email.id}`)
                    }}
                    className={`p-4 hover:bg-gray-50 transition-colors cursor-pointer border-l-4 ${
                      !email.is_read ? 'border-indigo-500 bg-indigo-50/30' : 'border-transparent'
                    } hover:border-indigo-500`}
                  >
                    <div className="flex items-start gap-4">
                      {/* Checkbox/Star area */}
                      <div className="flex items-center gap-2 pt-1">
                        {email.is_important && (
                          <Star className="w-4 h-4 text-yellow-400 fill-yellow-400 flex-shrink-0" />
                        )}
                        {!email.is_read && (
                          <span className="w-2 h-2 bg-indigo-600 rounded-full flex-shrink-0"></span>
                        )}
                      </div>
                      
                      {/* Main content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-1">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <p className={`font-semibold truncate ${!email.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                                {senderDisplay}
                              </p>
                              {senderEmailOnly && senderEmailOnly !== senderDisplay && (
                                <span className="text-xs text-gray-500 truncate hidden sm:inline">
                                  {senderEmailOnly}
                                </span>
                              )}
                            </div>
                            <p className={`text-sm mb-1 truncate ${!email.is_read ? 'font-semibold text-gray-900' : 'font-normal text-gray-700'}`}>
                              {email.subject || '(No subject)'}
                            </p>
                            {previewText && (
                              <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                                {previewText}
                              </p>
                            )}
                          </div>
                          
                          {/* Right side: Date and badges */}
                          <div className="flex items-start gap-3 flex-shrink-0">
                            <div className="flex flex-col items-end gap-1">
                              <span className="text-xs text-gray-500 whitespace-nowrap">
                                {format(new Date(email.received_at), 'MMM d')}
                              </span>
                              <span className="text-xs text-gray-400 whitespace-nowrap">
                                {format(new Date(email.received_at), 'h:mm a')}
                              </span>
                            </div>
                            {email.ai_extracted_tasks?.tasks && email.ai_extracted_tasks.tasks.length > 0 && (
                              <span className="px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded whitespace-nowrap">
                                {email.ai_extracted_tasks.tasks.length} task{email.ai_extracted_tasks.tasks.length !== 1 ? 's' : ''}
                              </span>
                            )}
                          </div>
                        </div>
                        
                        {/* Bottom metadata */}
                        <div className="flex items-center gap-4 text-xs text-gray-500">
                          {email.ai_priority_score && email.ai_priority_score > 70 && (
                            <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded font-medium">
                              High Priority
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12">
                <Mail className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 text-lg font-medium">No emails found</p>
                <p className="text-gray-400 text-sm mt-2">
                  {searchQuery ? 'Try a different search term' : 'Connect your email account to get started'}
                </p>
                {!searchQuery && (
                  <button
                    onClick={() => setShowConnectModal(true)}
                    className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Connect Email Account
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Connect Modal */}
        {showConnectModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
              <h3 className="text-xl font-bold mb-4">Connect Email Account</h3>
              <p className="text-gray-600 mb-6">
                Connect your Gmail, Outlook, or IMAP account to sync emails automatically.
              </p>
              <div className="space-y-3">
                <p className="text-sm text-gray-600 mb-4">
                  Email account connection requires OAuth authentication. You will be redirected to the provider's login page.
                </p>
                <ConnectEmailButton
                  provider="gmail"
                  label="Connect Gmail"
                  className="w-full px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  onSuccess={() => {
                    setShowConnectModal(false)
                    queryClient.invalidateQueries({ queryKey: ['emails'] })
                    queryClient.invalidateQueries({ queryKey: ['email-accounts'] })
                  }}
                />
                <ConnectEmailButton
                  provider="outlook"
                  label="Connect Outlook"
                  className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  onSuccess={() => {
                    setShowConnectModal(false)
                    queryClient.invalidateQueries({ queryKey: ['emails'] })
                    queryClient.invalidateQueries({ queryKey: ['email-accounts'] })
                  }}
                />
                <button 
                  onClick={() => {
                    alert('IMAP connection requires manual configuration. Please use the API directly or configure IMAP settings in backend.')
                    setShowConnectModal(false)
                  }}
                  className="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Connect IMAP
                </button>
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-xs text-yellow-800 font-semibold mb-1">📝 Setup Instructions:</p>
                  <p className="text-xs text-yellow-700">
                    To enable OAuth, add credentials to <code className="bg-yellow-100 px-1 rounded">backend/.env</code> or <code className="bg-yellow-100 px-1 rounded">backend/app/config.py</code>
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowConnectModal(false)}
                className="mt-4 w-full px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
