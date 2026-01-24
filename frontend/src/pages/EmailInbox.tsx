import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import { format } from 'date-fns'

export default function EmailInbox() {
  const { logout } = useAuthStore()

  const { data, isLoading } = useQuery({
    queryKey: ['emails'],
    queryFn: async () => {
      const response = await api.get('/emails?page=1&page_size=20')
      return response.data
    },
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <Link to="/dashboard" className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold">AI Life Admin</h1>
              </Link>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link to="/dashboard" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                  Dashboard
                </Link>
                <Link to="/emails" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                  Emails
                </Link>
                <Link to="/documents" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                  Documents
                </Link>
                <Link to="/tasks" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                  Tasks
                </Link>
                <Link to="/settings" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                  Settings
                </Link>
              </div>
            </div>
            <button
              onClick={logout}
              className="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h2 className="text-2xl font-bold mb-6">Email Inbox</h2>
          
          {isLoading ? (
            <div className="text-center py-12">Loading...</div>
          ) : data && data.emails ? (
            <div className="bg-white shadow rounded-lg">
              <div className="divide-y divide-gray-200">
                {data.emails.map((email: any) => (
                  <div key={email.id} className="p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <p className="font-semibold text-gray-900">{email.sender_name || email.sender_email}</p>
                          {email.is_important && (
                            <span className="ml-2 px-2 py-1 text-xs font-semibold bg-yellow-100 text-yellow-800 rounded">
                              Important
                            </span>
                          )}
                        </div>
                        <p className="mt-1 text-sm text-gray-900">{email.subject || '(No subject)'}</p>
                        {email.ai_summary && (
                          <p className="mt-2 text-sm text-gray-500">{email.ai_summary}</p>
                        )}
                        <p className="mt-1 text-xs text-gray-400">
                          {format(new Date(email.received_at), 'MMM d, yyyy h:mm a')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">No emails found</div>
          )}
        </div>
      </main>
    </div>
  )
}
