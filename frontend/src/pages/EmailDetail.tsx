import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { ArrowLeft, Star, Mail, Calendar, User, Tag, CheckCircle2, Reply, Forward, Loader2, Sparkles } from 'lucide-react'

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
      await api.post(`/emails/${emailId}/mark-read`)
      return { success: true }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['emails'] })
      queryClient.invalidateQueries({ queryKey: ['email', emailId] })
    },
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 animate-fade-in">
        <Navigation />
        <main className="max-w-4xl mx-auto py-8 px-4">
          <div className="text-center py-20 animate-fade-in">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600"></div>
            <p className="mt-6 text-gray-500 text-lg font-medium animate-pulse">Loading email...</p>
          </div>
        </main>
      </div>
    )
  }

  if (error || !email) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 animate-fade-in">
        <Navigation />
        <main className="max-w-4xl mx-auto py-8 px-4">
          <div className="text-center py-20 animate-bounce-in">
            <div className="inline-block p-6 bg-gradient-to-br from-red-100 to-orange-100 rounded-full mb-6">
              <Mail className="w-16 h-16 text-red-600" />
            </div>
            <p className="text-gray-600 text-xl font-bold mb-4">Email not found</p>
            <button
              onClick={() => navigate('/emails')}
              className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-lg"
            >
              Back to Inbox
            </button>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 animate-fade-in">
      <Navigation />

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/emails')}
          className="mb-6 flex items-center space-x-2 text-indigo-600 hover:text-indigo-700 transition-all duration-300 hover:scale-105 group animate-slide-down"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span className="font-semibold">Back to Inbox</span>
        </button>

        {/* Email Card */}
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden animate-slide-up hover-glow">
          {/* Header */}
          <div className="px-6 py-6 border-b border-gray-200/50 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-3">
                  {email.is_important && (
                    <Star className="w-6 h-6 text-yellow-300 fill-yellow-300 animate-pulse" />
                  )}
                  <h1 className="text-3xl font-bold text-white drop-shadow-lg">
                    {email.subject || '(No subject)'}
                  </h1>
                </div>
                
                {/* Sender Info */}
                <div className="flex items-center space-x-4 text-sm text-white/90 mb-3">
                  <div className="flex items-center space-x-2 px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-xl">
                    <User className="w-4 h-4" />
                    <span className="font-semibold">{email.sender_name || email.sender_email}</span>
                    {email.sender_email && (
                      <span className="text-white/70">&lt;{email.sender_email}&gt;</span>
                    )}
                  </div>
                </div>

                {/* Metadata */}
                <div className="flex flex-wrap items-center gap-3 text-xs">
                  <div className="flex items-center space-x-1 px-3 py-1.5 bg-white/20 backdrop-blur-sm rounded-xl text-white">
                    <Calendar className="w-3 h-3" />
                    <span>{format(new Date(email.received_at), 'EEEE, MMMM d, yyyy')}</span>
                    <span className="mx-1">•</span>
                    <span>{format(new Date(email.received_at), 'h:mm a')}</span>
                  </div>
                  {email.ai_priority_score && email.ai_priority_score > 70 && (
                    <div className="flex items-center space-x-1 px-3 py-1.5 bg-red-500/30 backdrop-blur-sm rounded-xl text-white">
                      <Tag className="w-3 h-3" />
                      <span className="font-semibold">
                        High Priority ({email.ai_priority_score}/100)
                      </span>
                    </div>
                  )}
                  {!email.is_read && (
                    <span className="px-3 py-1.5 bg-indigo-500/30 backdrop-blur-sm rounded-xl text-white font-semibold animate-pulse">
                      Unread
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* AI Summary */}
          {email.ai_summary && (
            <div className="px-6 py-5 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-b border-blue-200 animate-slide-up">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl">
                  <Sparkles className="w-5 h-5 text-white animate-pulse" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-blue-900 mb-2">AI Summary</h3>
                  <p className="text-sm text-blue-800 leading-relaxed">{email.ai_summary}</p>
                </div>
              </div>
            </div>
          )}

          {/* Extracted Tasks */}
          {email.ai_extracted_tasks?.tasks && email.ai_extracted_tasks.tasks.length > 0 && (
            <div className="px-6 py-5 bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-200 animate-slide-up">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl">
                  <CheckCircle2 className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-green-900 mb-3">
                    Extracted Tasks ({email.ai_extracted_tasks.tasks.length})
                  </h3>
                  <ul className="space-y-2">
                    {email.ai_extracted_tasks.tasks.map((task: any, idx: number) => (
                      <li key={idx} className="flex items-start space-x-2 text-sm text-green-800">
                        <span className="mt-1 w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></span>
                        <span>{task.title || task}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Extracted Dates */}
          {email.ai_extracted_dates?.dates && email.ai_extracted_dates.dates.length > 0 && (
            <div className="px-6 py-5 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-purple-200 animate-slide-up">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl">
                  <Calendar className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-bold text-purple-900 mb-3">
                    Important Dates
                  </h3>
                  <ul className="space-y-2">
                    {email.ai_extracted_dates.dates.map((date: string, idx: number) => (
                      <li key={idx} className="flex items-start space-x-2 text-sm text-purple-800">
                        <span className="mt-1 w-2 h-2 bg-purple-500 rounded-full flex-shrink-0"></span>
                        <span>{date}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Email Body */}
          <div className="px-6 py-8 animate-fade-in">
            <div className="prose max-w-none">
              {email.body_html ? (
                <div 
                  dangerouslySetInnerHTML={{ __html: email.body_html }}
                  className="email-body text-gray-700 leading-relaxed"
                />
              ) : (
                <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                  {email.body_text || 'No content available'}
                </div>
              )}
            </div>
          </div>

          {/* Footer Actions */}
          <div className="px-6 py-5 border-t-2 border-gray-200 bg-gradient-to-r from-gray-50 to-indigo-50/30">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => {
                  alert('Reply functionality coming soon!')
                }}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-lg font-semibold group"
              >
                <Reply className="w-5 h-5 group-hover:animate-pulse" />
                <span>Reply</span>
              </button>
              <button
                onClick={() => {
                  alert('Forward functionality coming soon!')
                }}
                className="flex items-center space-x-2 px-6 py-3 bg-white text-indigo-600 border-2 border-indigo-600 rounded-xl hover:bg-indigo-50 transition-all duration-300 hover:scale-105 hover:shadow-lg font-semibold group"
              >
                <Forward className="w-5 h-5 group-hover:animate-pulse" />
                <span>Forward</span>
              </button>
              {!email.is_read && (
                <button
                  onClick={() => markAsReadMutation.mutate()}
                  disabled={markAsReadMutation.isPending}
                  className="flex items-center space-x-2 px-6 py-3 bg-white text-gray-600 border-2 border-gray-300 rounded-xl hover:bg-gray-50 transition-all duration-300 hover:scale-105 hover:shadow-lg font-semibold disabled:opacity-50"
                >
                  {markAsReadMutation.isPending ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Marking...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle2 className="w-5 h-5" />
                      <span>Mark as Read</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
