import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useLocation, useNavigate } from 'react-router-dom'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { Mail, RefreshCw, Plus, Search, Star, Filter, CheckCircle2, Loader2 } from 'lucide-react'

function ConnectEmailButton({ provider, label, className }: { 
  provider: 'gmail' | 'outlook'
  label: string
  className: string
}) {
  const [loading, setLoading] = useState(false)

  const handleConnect = async () => {
    setLoading(true)
    try {
      const response = await api.get(`/emails/oauth/${provider}/authorize`)
      window.location.href = response.data.auth_url
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || `Failed to initiate ${provider} OAuth. Please check backend configuration.`
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
      {loading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin mr-2" />
          Connecting...
        </>
      ) : (
        label
      )}
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

  useEffect(() => {
    if (location.state?.message) {
      setSuccessMessage(location.state.message)
      setTimeout(() => setSuccessMessage(null), 5000)
      window.history.replaceState({}, document.title)
    }
  }, [location])

  const { data: accountsData } = useQuery({
    queryKey: ['email-accounts'],
    queryFn: async () => {
      try {
        const response = await api.get('/emails/accounts')
        const seen = new Map()
        const unique = response.data.filter((account: any) => {
          const key = `${account.email_address.toLowerCase()}_${account.provider}`
          if (seen.has(key)) return false
          seen.set(key, true)
          return true
        })
        return unique
      } catch (error: any) {
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
      if (searchQuery) params.append('search', searchQuery)
      if (filters.unreadOnly) params.append('unread_only', 'true')
      if (filters.importantOnly) params.append('important_only', 'true')
      if (filters.dateFrom) params.append('date_from', filters.dateFrom)
      if (filters.dateTo) params.append('date_to', filters.dateTo)
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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 animate-fade-in">
      <Navigation />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden animate-slide-up hover-glow">
          {/* Header */}
          <div className="px-6 py-6 border-b border-gray-200/50 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3 animate-slide-down">
                <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                  <Mail className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white drop-shadow-lg">Email Inbox</h2>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setShowConnectModal(true)}
                  className="flex items-center space-x-2 px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-xl hover:bg-white/30 transition-all duration-300 hover:scale-105 hover:shadow-lg group"
                >
                  <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
                  <span>Connect Account</span>
                </button>
                <button
                  onClick={() => syncMutation.mutate()}
                  disabled={syncMutation.isPending}
                  className="flex items-center space-x-2 px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-xl hover:bg-white/30 transition-all duration-300 hover:scale-105 hover:shadow-lg disabled:opacity-50 group"
                >
                  <RefreshCw className={`w-5 h-5 ${syncMutation.isPending ? 'animate-spin' : 'group-hover:rotate-180'} transition-transform duration-500`} />
                  <span>Sync</span>
                </button>
              </div>
            </div>

            {/* Success Message */}
            {successMessage && (
              <div className="mt-4 p-4 bg-green-500/20 backdrop-blur-sm border border-green-300/50 rounded-xl animate-scale-in">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-green-100 animate-pulse" />
                  <p className="text-sm font-semibold text-white">
                    {successMessage}
                  </p>
                </div>
              </div>
            )}

            {/* Connected Accounts */}
            {connectedAccounts.length > 0 && (
              <div className="mt-4 p-4 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl animate-slide-up">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-3">
                      <CheckCircle2 className="w-5 h-5 text-green-200" />
                      <p className="text-sm font-semibold text-white">
                        Connected Accounts ({connectedAccounts.length})
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {connectedAccounts.map((account: any, index: number) => (
                        <span
                          key={account.id}
                          className="stagger-item inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-white/30 backdrop-blur-sm text-white border border-white/40 shadow-sm hover:bg-white/40 transition-all duration-300 hover:scale-105"
                          style={{ animationDelay: `${index * 0.05}s` }}
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
                      className="ml-4 px-4 py-2 text-xs bg-white/30 backdrop-blur-sm text-white rounded-xl hover:bg-white/40 transition-all duration-300 hover:scale-105 whitespace-nowrap font-semibold"
                    >
                      Cleanup Duplicates
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Search and Filters */}
            <div className="space-y-3 mt-4 animate-slide-up">
              <div className="flex items-center gap-3">
                <div className="relative flex-1">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/70" />
                  <input
                    type="text"
                    placeholder="Search emails..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50 focus:bg-white/30 transition-all duration-300"
                  />
                </div>
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`px-5 py-3 rounded-xl border transition-all duration-300 hover:scale-105 font-semibold ${
                    showFilters || filters.unreadOnly || filters.importantOnly || filters.dateFrom || filters.dateTo
                      ? 'bg-white text-indigo-600 shadow-lg'
                      : 'bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30'
                  }`}
                >
                  <Filter className="w-4 h-4 inline mr-2" />
                  Filters
                </button>
              </div>
              
              {/* Filter Panel */}
              {showFilters && (
                <div className="p-5 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl space-y-4 animate-scale-in">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <label className="flex items-center space-x-3 cursor-pointer p-3 bg-white/10 rounded-xl hover:bg-white/20 transition-all duration-300">
                      <input
                        type="checkbox"
                        checked={filters.unreadOnly}
                        onChange={(e) => setFilters({ ...filters, unreadOnly: e.target.checked })}
                        className="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500"
                      />
                      <span className="text-sm font-semibold text-white">Unread Only</span>
                    </label>
                    <label className="flex items-center space-x-3 cursor-pointer p-3 bg-white/10 rounded-xl hover:bg-white/20 transition-all duration-300">
                      <input
                        type="checkbox"
                        checked={filters.importantOnly}
                        onChange={(e) => setFilters({ ...filters, importantOnly: e.target.checked })}
                        className="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500"
                      />
                      <span className="text-sm font-semibold text-white">Important Only</span>
                    </label>
                    <button
                      onClick={() => setFilters({ unreadOnly: false, importantOnly: false, dateFrom: '', dateTo: '' })}
                      className="px-4 py-2 text-xs text-white hover:text-indigo-200 hover:bg-white/20 rounded-xl transition-all duration-300 font-semibold"
                    >
                      Clear Filters
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-white mb-2">From Date</label>
                      <input
                        type="date"
                        value={filters.dateFrom}
                        onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                        className="w-full px-4 py-2 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-white text-sm focus:ring-2 focus:ring-white/50 focus:bg-white/30 transition-all duration-300"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-white mb-2">To Date</label>
                      <input
                        type="date"
                        value={filters.dateTo}
                        onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                        className="w-full px-4 py-2 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-white text-sm focus:ring-2 focus:ring-white/50 focus:bg-white/30 transition-all duration-300"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Email List */}
          <div className="divide-y divide-gray-200/50">
            {isLoading ? (
              <div className="text-center py-20 animate-fade-in">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600"></div>
                <p className="mt-6 text-gray-500 text-lg font-medium animate-pulse">Loading emails...</p>
              </div>
            ) : error ? (
              <div className="text-center py-20 animate-bounce-in">
                <Mail className="w-16 h-16 text-gray-400 mx-auto mb-4 animate-pulse" />
                <p className="text-gray-600 text-lg font-bold mb-2">Failed to load emails</p>
                <p className="text-gray-400 text-sm mb-6">
                  {(error as any)?.message?.includes('Backend server') 
                    ? 'Backend server is not available. Please ensure the backend is running on http://localhost:8000'
                    : 'Please check your connection and try again'}
                </p>
                <button
                  onClick={() => queryClient.invalidateQueries({ queryKey: ['emails'] })}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-lg"
                >
                  Retry
                </button>
              </div>
            ) : emails.length > 0 ? (
              emails.map((email: any, index: number) => {
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
                    onClick={() => navigate(`/emails/${email.id}`)}
                    className={`stagger-item p-5 hover:bg-gradient-to-r hover:from-indigo-50/50 hover:to-purple-50/50 transition-all duration-300 hover-lift cursor-pointer group ${
                      !email.is_read ? 'bg-indigo-50/30 border-l-4 border-indigo-500' : 'border-l-4 border-transparent'
                    }`}
                    style={{ animationDelay: `${index * 0.03}s` }}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex items-center gap-2 pt-1">
                        {email.is_important && (
                          <Star className="w-5 h-5 text-yellow-400 fill-yellow-400 flex-shrink-0 group-hover:animate-pulse" />
                        )}
                        {!email.is_read && (
                          <span className="w-3 h-3 bg-indigo-600 rounded-full flex-shrink-0 animate-pulse"></span>
                        )}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <p className={`font-bold truncate text-lg group-hover:text-indigo-600 transition-colors ${
                                !email.is_read ? 'text-gray-900' : 'text-gray-700'
                              }`}>
                                {senderDisplay}
                              </p>
                              {senderEmailOnly && senderEmailOnly !== senderDisplay && (
                                <span className="text-xs text-gray-500 truncate hidden sm:inline">
                                  {senderEmailOnly}
                                </span>
                              )}
                            </div>
                            <p className={`text-base mb-2 truncate group-hover:text-indigo-600 transition-colors ${
                              !email.is_read ? 'font-bold text-gray-900' : 'font-semibold text-gray-700'
                            }`}>
                              {email.subject || '(No subject)'}
                            </p>
                            {previewText && (
                              <p className="text-sm text-gray-600 line-clamp-2 mb-3 leading-relaxed">
                                {previewText}
                              </p>
                            )}
                          </div>
                          
                          <div className="flex items-start gap-3 flex-shrink-0">
                            <div className="flex flex-col items-end gap-1">
                              <span className="text-xs font-semibold text-gray-500 whitespace-nowrap">
                                {format(new Date(email.received_at), 'MMM d')}
                              </span>
                              <span className="text-xs text-gray-400 whitespace-nowrap">
                                {format(new Date(email.received_at), 'h:mm a')}
                              </span>
                            </div>
                            {email.ai_extracted_tasks?.tasks && email.ai_extracted_tasks.tasks.length > 0 && (
                              <span className="px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-800 rounded-full whitespace-nowrap shadow-sm animate-scale-in">
                                {email.ai_extracted_tasks.tasks.length} task{email.ai_extracted_tasks.tasks.length !== 1 ? 's' : ''}
                              </span>
                            )}
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-3 flex-wrap">
                          {email.ai_priority_score && email.ai_priority_score > 70 && (
                            <span className="px-3 py-1 text-xs font-semibold bg-gradient-to-r from-red-100 to-pink-100 text-red-700 rounded-full shadow-sm">
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
              <div className="text-center py-20 animate-bounce-in">
                <div className="inline-block p-6 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full mb-6 animate-pulse">
                  <Mail className="w-16 h-16 text-indigo-600" />
                </div>
                <p className="text-gray-600 text-xl font-bold mb-2">No emails found</p>
                <p className="text-gray-400 text-sm mb-6">
                  {searchQuery ? 'Try a different search term' : 'Connect your email account to get started'}
                </p>
                {!searchQuery && (
                  <button
                    onClick={() => setShowConnectModal(true)}
                    className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-lg"
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
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in p-4">
            <div className="bg-white/95 backdrop-blur-lg rounded-2xl shadow-2xl max-w-md w-full p-8 animate-scale-in border border-gray-200/50">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Connect Email Account
                </h3>
                <button
                  onClick={() => setShowConnectModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-300 hover:rotate-90"
                >
                  ✕
                </button>
              </div>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Connect your Gmail, Outlook, or IMAP account to sync emails automatically.
              </p>
              <div className="space-y-3">
                <p className="text-sm text-gray-600 mb-4 p-3 bg-blue-50 rounded-xl border border-blue-200">
                  Email account connection requires OAuth authentication. You will be redirected to the provider's login page.
                </p>
                <ConnectEmailButton
                  provider="gmail"
                  label="📧 Connect Gmail"
                  className="w-full px-6 py-4 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl hover:from-red-700 hover:to-red-800 transition-all duration-300 hover:scale-105 hover:shadow-lg font-semibold"
                />
                <ConnectEmailButton
                  provider="outlook"
                  label="📬 Connect Outlook"
                  className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all duration-300 hover:scale-105 hover:shadow-lg font-semibold"
                />
                <button 
                  onClick={() => {
                    alert('IMAP connection requires manual configuration. Please use the API directly or configure IMAP settings in backend.')
                    setShowConnectModal(false)
                  }}
                  className="w-full px-6 py-4 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all duration-300 hover:scale-105 hover:shadow-lg font-semibold"
                >
                  📨 Connect IMAP
                </button>
                <div className="mt-4 p-4 bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-200 rounded-xl">
                  <p className="text-xs text-yellow-800 font-bold mb-1">📝 Setup Instructions:</p>
                  <p className="text-xs text-yellow-700 leading-relaxed">
                    To enable OAuth, add credentials to <code className="bg-yellow-100 px-1.5 py-0.5 rounded font-mono">backend/.env</code> or <code className="bg-yellow-100 px-1.5 py-0.5 rounded font-mono">backend/app/config.py</code>
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
