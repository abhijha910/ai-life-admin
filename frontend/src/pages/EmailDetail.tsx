import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { ArrowLeft, Star, Mail, Calendar, User, Tag } from 'lucide-react'

export default function EmailDetail() {
  const { emailId } = useParams<{ emailId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: email, isLoading, error } = useQuery({
    queryKey: ['email', emailId],
    queryFn: async () => {
      const response = await api.get(`/emails/${emailId}`)
      return response.data
    },
    enabled: !!emailId,
  })

  const markAsReadMutation = useMutation({
    mutationFn: async () => {
      // TODO: Add mark as read endpoint
      return { success: true }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] })
      queryClient.invalidateQueries({ queryKey: ['email', emailId] })
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <Navigation />
        <main className="max-w-4xl mx-auto py-8 px-4">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            <p className="mt-4 text-gray-500">Loading email...</p>
          </div>
        </main>
      </div>
    )
  }

  if (error || !email) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <Navigation />
        <main className="max-w-4xl mx-auto py-8 px-4">
          <div className="text-center py-12">
            <Mail className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 text-lg font-medium">Email not found</p>
            <button
              onClick={() => navigate('/emails')}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Back to Inbox
            </button>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation />

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/emails')}
          className="mb-4 flex items-center space-x-2 text-indigo-600 hover:text-indigo-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Inbox</span>
        </button>

        {/* Email Card */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-2">
                  {email.is_important && (
                    <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
                  )}
                  <h1 className="text-2xl font-bold text-gray-900">
                    {email.subject || '(No subject)'}
                  </h1>
                </div>
                
                {/* Sender Info */}
                <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                  <div className="flex items-center space-x-2">
                    <User className="w-4 h-4" />
                    <span className="font-semibold">{email.sender_name || email.sender_email}</span>
                    {email.sender_email && (
                      <span className="text-gray-500">&lt;{email.sender_email}&gt;</span>
                    )}
                  </div>
                </div>

                {/* Metadata */}
                <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{format(new Date(email.received_at), 'EEEE, MMMM d, yyyy')}</span>
                    <span className="mx-1">•</span>
                    <span>{format(new Date(email.received_at), 'h:mm a')}</span>
                  </div>
                  {email.ai_priority_score && email.ai_priority_score > 70 && (
                    <div className="flex items-center space-x-1">
                      <Tag className="w-3 h-3" />
                      <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded font-medium">
                        High Priority ({email.ai_priority_score}/100)
                      </span>
                    </div>
                  )}
                  {!email.is_read && (
                    <span className="px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded font-medium">
                      Unread
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* AI Summary */}
          {email.ai_summary && (
            <div className="px-6 py-4 bg-blue-50 border-b border-blue-100">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">AI Summary</h3>
              <p className="text-sm text-blue-800">{email.ai_summary}</p>
            </div>
          )}

          {/* Extracted Tasks */}
          {email.ai_extracted_tasks?.tasks && email.ai_extracted_tasks.tasks.length > 0 && (
            <div className="px-6 py-4 bg-green-50 border-b border-green-100">
              <h3 className="text-sm font-semibold text-green-900 mb-2">
                Extracted Tasks ({email.ai_extracted_tasks.tasks.length})
              </h3>
              <ul className="list-disc list-inside space-y-1">
                {email.ai_extracted_tasks.tasks.map((task: any, idx: number) => (
                  <li key={idx} className="text-sm text-green-800">{task}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Extracted Dates */}
          {email.ai_extracted_dates?.dates && email.ai_extracted_dates.dates.length > 0 && (
            <div className="px-6 py-4 bg-purple-50 border-b border-purple-100">
              <h3 className="text-sm font-semibold text-purple-900 mb-2">
                Important Dates
              </h3>
              <ul className="list-disc list-inside space-y-1">
                {email.ai_extracted_dates.dates.map((date: string, idx: number) => (
                  <li key={idx} className="text-sm text-purple-800">{date}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Email Body */}
          <div className="px-6 py-6">
            <div className="prose max-w-none">
              {email.body_html ? (
                <div 
                  dangerouslySetInnerHTML={{ __html: email.body_html }}
                  className="email-body"
                />
              ) : (
                <div className="whitespace-pre-wrap text-gray-700">
                  {email.body_text || 'No content available'}
                </div>
              )}
            </div>
          </div>

          {/* Footer Actions */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => {
                  // TODO: Implement reply
                  alert('Reply functionality coming soon!')
                }}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Reply
              </button>
              <button
                onClick={() => {
                  // TODO: Implement forward
                  alert('Forward functionality coming soon!')
                }}
                className="px-4 py-2 bg-white text-indigo-600 border border-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors"
              >
                Forward
              </button>
              {!email.is_read && (
                <button
                  onClick={() => markAsReadMutation.mutate()}
                  className="px-4 py-2 bg-white text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Mark as Read
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
