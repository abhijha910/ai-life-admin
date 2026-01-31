import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { Calendar, Clock, TrendingUp, CheckCircle2, AlertCircle, Sparkles, Loader2, ShieldAlert, Zap, Brain, X } from 'lucide-react'

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

  const { data: suggestions } = useQuery({
    queryKey: ['action-suggestions'],
    queryFn: async () => {
      const response = await api.get('/ai-los/suggestions')
      return response.data
    },
  })

  const dismissSuggestionMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.post(`/ai-los/suggestions/${id}/dismiss`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['action-suggestions'] })
    },
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
  const unapprovedTasks = tasks.filter((t: any) => !t.is_approved).length
  const totalDuration = plan?.total_duration || 0

  const stats = [
    { label: 'Total Tasks', value: tasks.length, icon: CheckCircle2, color: 'indigo', bg: 'from-indigo-500 to-blue-500' },
    { label: 'Needs Approval', value: unapprovedTasks, icon: Brain, color: 'purple', bg: 'from-purple-500 to-indigo-500' },
    { label: 'Completed', value: completedTasks, icon: TrendingUp, color: 'green', bg: 'from-green-500 to-emerald-500' },
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

        {/* Level 3 & 6: Cognitive Load & Burnout Radar */}
        {plan?.overload_info && (
          <div className={`mb-8 p-6 rounded-2xl border-2 animate-scale-in hover-glow ${
            plan.overload_info.is_overloaded 
              ? 'bg-red-50 border-red-200' 
              : 'bg-emerald-50 border-emerald-200'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-xl ${
                  plan.overload_info.is_overloaded ? 'bg-red-500' : 'bg-emerald-500'
                }`}>
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className={`text-lg font-bold ${
                    plan.overload_info.is_overloaded ? 'text-red-900' : 'text-emerald-900'
                  }`}>
                    Cognitive Load: {plan.overload_info.load_percentage}%
                  </h3>
                  <p className={plan.overload_info.is_overloaded ? 'text-red-700' : 'text-emerald-700'}>
                    {plan.overload_info.recommendation}
                  </p>
                </div>
              </div>
              <div className="text-right hidden sm:block">
                <span className={`px-4 py-2 rounded-full text-sm font-bold uppercase tracking-wider ${
                  plan.overload_info.burnout_risk === 'high' 
                    ? 'bg-red-100 text-red-700' 
                    : plan.overload_info.burnout_risk === 'medium'
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-emerald-100 text-emerald-700'
                }`}>
                  {plan.overload_info.burnout_risk} Burnout Risk
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Level 4: Action Suggestions (Action Cards) */}
        {suggestions && suggestions.length > 0 && (
          <div className="mb-8 animate-slide-up">
            <div className="flex items-center space-x-2 mb-4">
              <Zap className="w-5 h-5 text-amber-500" />
              <h3 className="text-xl font-bold text-gray-800">AI Insights & Actions</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {suggestions.map((suggestion: any, index: number) => (
                <div 
                  key={suggestion.id}
                  className="bg-white rounded-2xl shadow-md border border-amber-100 p-5 hover-lift hover-glow relative group overflow-hidden"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <button 
                    onClick={() => dismissSuggestionMutation.mutate(suggestion.id)}
                    className="absolute top-3 right-3 p-1 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="p-2 bg-amber-100 rounded-lg">
                      <Sparkles className="w-4 h-4 text-amber-600" />
                    </div>
                    <span className="text-xs font-bold text-amber-600 uppercase tracking-wider">{suggestion.type.replace('_', ' ')}</span>
                  </div>
                  <h4 className="font-bold text-gray-900 mb-2">{suggestion.title}</h4>
                  <p className="text-sm text-gray-600 mb-4">{suggestion.description}</p>
                  <button className="w-full py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold text-sm hover:from-amber-600 hover:to-orange-600 transition-all shadow-md">
                    {suggestion.action_label}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

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
                        {plan.overload_info?.regret_warnings?.length > 0 && (
                          <div className="mt-4 space-y-2">
                            {plan.overload_info.regret_warnings.map((warning: string, i: number) => (
                              <div key={i} className="flex items-center space-x-2 text-amber-700 text-sm font-medium bg-amber-50 p-2 rounded-lg border border-amber-100">
                                <ShieldAlert className="w-4 h-4" />
                                <span>{warning}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div className="space-y-4">
                  {plan.tasks && plan.tasks.length > 0 ? (
                    plan.tasks.map((task: any, index: number) => (
                      <div
                        key={task.id || index}
                        className={`stagger-item border-l-4 ${
                          task.risk_level >= 70 ? 'border-red-500' : 
                          task.risk_level >= 40 ? 'border-amber-500' : 'border-indigo-500'
                        } bg-gradient-to-r from-gray-50 to-indigo-50/30 rounded-r-2xl p-5 hover:shadow-xl transition-all duration-300 hover-lift group`}
                        style={{ animationDelay: `${index * 0.1}s` }}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="font-bold text-gray-900 text-lg group-hover:text-indigo-600 transition-colors">{task.title}</h4>
                              {task.risk_level > 0 && (
                                <div className="flex items-center space-x-1 px-2 py-1 bg-white shadow-sm border rounded-lg text-xs font-bold">
                                  <ShieldAlert className={`w-3 h-3 ${task.risk_level >= 70 ? 'text-red-500' : 'text-amber-500'}`} />
                                  <span className={task.risk_level >= 70 ? 'text-red-700' : 'text-amber-700'}>
                                    {task.risk_level}% Risk
                                  </span>
                                </div>
                              )}
                            </div>
                            {task.description && (
                              <p className="text-sm text-gray-600 mb-2 leading-relaxed">{task.description}</p>
                            )}
                            {task.consequences && (
                              <p className="text-xs font-medium text-red-600 bg-red-50 p-2 rounded-lg border border-red-100 mb-3 italic">
                                ⚠ {task.consequences}
                              </p>
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
