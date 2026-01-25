import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { Calendar, Clock, TrendingUp, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react'

export default function Dashboard() {
  const queryClient = useQueryClient()

  const { data: plan, isLoading: planLoading, error: planError } = useQuery({
    queryKey: ['daily-plan'],
    queryFn: async () => {
      const response = await api.get('/plans/today')
      return response.data
    },
    retry: 2,
    retryDelay: 1000,
  })

  const { data: tasksData, error: tasksError } = useQuery({
    queryKey: ['tasks-stats'],
    queryFn: async () => {
      const response = await api.get('/tasks?page=1&page_size=100')
      return response.data
    },
    retry: 2,
    retryDelay: 1000,
  })

  const regenerateMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/plans/regenerate')
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['daily-plan'] })
    },
  })

  const tasks = tasksData?.tasks || []
  const completedTasks = tasks.filter((t: any) => t.status === 'completed').length
  const pendingTasks = tasks.filter((t: any) => t.status === 'pending').length
  const inProgressTasks = tasks.filter((t: any) => t.status === 'in_progress').length
  const totalDuration = plan?.total_duration || 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Backend Connection Error Banner */}
        {(planError || tasksError) && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <div>
                <p className="text-sm font-semibold text-red-800">Backend Connection Error</p>
                <p className="text-xs text-red-600 mt-1">
                  Unable to connect to backend server. Please ensure the backend is running on http://localhost:8000
                </p>
              </div>
            </div>
          </div>
        )}
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Tasks</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{tasks.length}</p>
              </div>
              <div className="p-3 bg-indigo-100 rounded-lg">
                <CheckCircle2 className="w-6 h-6 text-indigo-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{completedTasks}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">In Progress</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">{inProgressTasks}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <Clock className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pending</p>
                <p className="text-3xl font-bold text-orange-600 mt-2">{pendingTasks}</p>
              </div>
              <div className="p-3 bg-orange-100 rounded-lg">
                <AlertCircle className="w-6 h-6 text-orange-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Today's Plan */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Calendar className="w-6 h-6 text-indigo-600" />
                <h2 className="text-2xl font-bold text-gray-900">Today's Plan</h2>
              </div>
              <button
                onClick={() => regenerateMutation.mutate()}
                disabled={regenerateMutation.isPending}
                className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Sparkles className="w-4 h-4" />
                <span>{regenerateMutation.isPending ? 'Regenerating...' : 'Regenerate Plan'}</span>
              </button>
            </div>
          </div>

          <div className="p-6">
            {planLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <p className="mt-4 text-gray-500">Loading your plan...</p>
              </div>
            ) : plan ? (
              <>
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-lg font-semibold text-gray-700">
                      {format(new Date(plan.date), 'EEEE, MMMM d, yyyy')}
                    </p>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span>Total Duration: {Math.round(totalDuration / 60)} hours</span>
                    </div>
                  </div>
                </div>

                {plan.ai_recommendations && (
                  <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-5">
                    <div className="flex items-start space-x-3">
                      <Sparkles className="w-5 h-5 text-indigo-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <h3 className="font-semibold text-indigo-900 mb-2">AI Recommendations</h3>
                        <p className="text-indigo-800 leading-relaxed">{plan.ai_recommendations}</p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="space-y-3">
                  {plan.tasks && plan.tasks.length > 0 ? (
                    plan.tasks.map((task: any, index: number) => (
                      <div
                        key={task.id || index}
                        className="border-l-4 border-indigo-500 bg-gray-50 rounded-r-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 mb-1">{task.title}</h4>
                            {task.description && (
                              <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                            )}
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span className="flex items-center space-x-1">
                                <span className="font-medium">Priority:</span>
                                <span className={`px-2 py-0.5 rounded ${
                                  task.priority >= 80 ? 'bg-red-100 text-red-700' :
                                  task.priority >= 50 ? 'bg-orange-100 text-orange-700' :
                                  'bg-green-100 text-green-700'
                                }`}>
                                  {task.priority}
                                </span>
                              </span>
                              {task.estimated_duration && (
                                <span className="flex items-center space-x-1">
                                  <Clock className="w-3 h-3" />
                                  <span>{task.estimated_duration} min</span>
                                </span>
                              )}
                              {task.scheduled_time && (
                                <span className="flex items-center space-x-1">
                                  <Calendar className="w-3 h-3" />
                                  <span>{format(new Date(task.scheduled_time), 'h:mm a')}</span>
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                      <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500 text-lg font-medium">No tasks scheduled for today</p>
                      <p className="text-gray-400 text-sm mt-2">Enjoy your free day! 🎉</p>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No plan available for today</p>
                <button
                  onClick={() => regenerateMutation.mutate()}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Generate Plan
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
