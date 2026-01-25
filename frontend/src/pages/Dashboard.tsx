import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { Calendar, Clock, TrendingUp, CheckCircle2, AlertCircle, Sparkles, Loader2 } from 'lucide-react'

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

  const stats = [
    { label: 'Total Tasks', value: tasks.length, icon: CheckCircle2, color: 'indigo', bg: 'from-indigo-500 to-blue-500' },
    { label: 'Completed', value: completedTasks, icon: TrendingUp, color: 'green', bg: 'from-green-500 to-emerald-500' },
    { label: 'In Progress', value: inProgressTasks, icon: Clock, color: 'blue', bg: 'from-blue-500 to-cyan-500' },
    { label: 'Pending', value: pendingTasks, icon: AlertCircle, color: 'orange', bg: 'from-orange-500 to-amber-500' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 animate-fade-in">
      <Navigation />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Backend Connection Error Banner */}
        {(planError || tasksError) && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl animate-slide-down hover-glow">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600 animate-pulse" />
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <div
                key={stat.label}
                className="stagger-item bg-white/80 backdrop-blur-lg rounded-2xl shadow-lg border border-gray-200/50 p-6 hover-lift hover-glow group overflow-hidden relative"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-5 transition-opacity duration-300" style={{ background: `linear-gradient(to bottom right, var(--tw-gradient-stops))` }}></div>
                <div className="relative flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.label}</p>
                    <p className={`text-4xl font-bold bg-gradient-to-r ${stat.bg} bg-clip-text text-transparent`}>
                      {stat.value}
                    </p>
                  </div>
                  <div className={`p-4 bg-gradient-to-br ${stat.bg} rounded-2xl shadow-lg group-hover:scale-110 group-hover:rotate-6 transition-all duration-300`}>
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Today's Plan */}
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden animate-slide-up hover-glow">
          <div className="px-6 py-6 border-b border-gray-200/50 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3 animate-slide-down">
                <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                  <Calendar className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white drop-shadow-lg">Today's Plan</h2>
              </div>
              <button
                onClick={() => regenerateMutation.mutate()}
                disabled={regenerateMutation.isPending}
                className="flex items-center space-x-2 px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-xl hover:bg-white/30 transition-all duration-300 hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                {regenerateMutation.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Regenerating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5 group-hover:animate-pulse" />
                    <span>Regenerate Plan</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="p-6">
            {planLoading ? (
              <div className="text-center py-20 animate-fade-in">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600"></div>
                <p className="mt-6 text-gray-500 text-lg font-medium animate-pulse">Loading your plan...</p>
              </div>
            ) : plan ? (
              <>
                <div className="mb-6 animate-slide-up">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xl font-bold text-gray-800">
                      {format(new Date(plan.date), 'EEEE, MMMM d, yyyy')}
                    </p>
                    <div className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 rounded-xl text-sm font-semibold text-indigo-700">
                      <Clock className="w-4 h-4" />
                      <span>Total Duration: {Math.round(totalDuration / 60)} hours</span>
                    </div>
                  </div>
                </div>

                {plan.ai_recommendations && (
                  <div className="mb-6 bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-2 border-blue-200 rounded-2xl p-6 animate-scale-in hover-glow">
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl">
                        <Sparkles className="w-5 h-5 text-white animate-pulse" />
                      </div>
                      <div>
                        <h3 className="font-bold text-indigo-900 mb-2 text-lg">AI Recommendations</h3>
                        <p className="text-indigo-800 leading-relaxed">{plan.ai_recommendations}</p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  {plan.tasks && plan.tasks.length > 0 ? (
                    plan.tasks.map((task: any, index: number) => (
                      <div
                        key={task.id || index}
                        className="stagger-item border-l-4 border-indigo-500 bg-gradient-to-r from-gray-50 to-indigo-50/30 rounded-r-2xl p-5 hover:shadow-xl transition-all duration-300 hover-lift group"
                        style={{ animationDelay: `${index * 0.1}s` }}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <h4 className="font-bold text-gray-900 mb-2 text-lg group-hover:text-indigo-600 transition-colors">{task.title}</h4>
                            {task.description && (
                              <p className="text-sm text-gray-600 mb-3 leading-relaxed">{task.description}</p>
                            )}
                            <div className="flex items-center space-x-4 text-xs flex-wrap gap-2">
                              <span className="flex items-center space-x-2 px-3 py-1.5 rounded-full font-semibold bg-white shadow-sm">
                                <span className="font-medium text-gray-600">Priority:</span>
                                <span className={`px-2 py-0.5 rounded-full ${
                                  task.priority >= 80 ? 'bg-red-100 text-red-700' :
                                  task.priority >= 50 ? 'bg-orange-100 text-orange-700' :
                                  'bg-green-100 text-green-700'
                                }`}>
                                  {task.priority}
                                </span>
                              </span>
                              {task.estimated_duration && (
                                <span className="flex items-center space-x-1 px-3 py-1.5 rounded-full bg-white shadow-sm font-semibold text-gray-700">
                                  <Clock className="w-3 h-3" />
                                  <span>{task.estimated_duration} min</span>
                                </span>
                              )}
                              {task.scheduled_time && (
                                <span className="flex items-center space-x-1 px-3 py-1.5 rounded-full bg-white shadow-sm font-semibold text-gray-700">
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
                    <div className="text-center py-16 bg-gradient-to-br from-gray-50 to-indigo-50/30 rounded-2xl border-2 border-dashed border-gray-300 animate-bounce-in">
                      <div className="inline-block p-4 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full mb-4">
                        <Calendar className="w-12 h-12 text-indigo-600" />
                      </div>
                      <p className="text-gray-600 text-xl font-bold mb-2">No tasks scheduled for today</p>
                      <p className="text-gray-400 text-sm">Enjoy your free day! 🎉</p>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="text-center py-16 animate-bounce-in">
                <div className="inline-block p-4 bg-gradient-to-br from-red-100 to-orange-100 rounded-full mb-4">
                  <AlertCircle className="w-12 h-12 text-red-600" />
                </div>
                <p className="text-gray-600 text-lg font-semibold mb-4">No plan available for today</p>
                <button
                  onClick={() => regenerateMutation.mutate()}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-lg"
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
