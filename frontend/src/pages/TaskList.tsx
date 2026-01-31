import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { CheckCircle2, Circle, Plus, Edit, Trash2, Clock, Calendar, Flag, Filter, AlertCircle, ShieldCheck, ShieldAlert, Zap, Brain } from 'lucide-react'

export default function TaskList() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingTask, setEditingTask] = useState<any>(null)
  const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed' | 'needs_approval'>('all')
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks', filter],
    queryFn: async () => {
      const params = new URLSearchParams({ page: '1', page_size: '100' })
      if (filter === 'needs_approval') {
        params.append('is_approved', 'false')
      } else if (filter !== 'all') {
        params.append('status', filter)
        params.append('is_approved', 'true')
      }
      // If filter is 'all', we don't append is_approved to show everything
      const response = await api.get(`/tasks?${params}`)
      return response.data
    },
    retry: 2,
    retryDelay: 1000,
  })

  const approveMutation = useMutation({
    mutationFn: async (taskId: string) => {
      const response = await api.post(`/tasks/${taskId}/approve`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['daily-plan'] })
    },
  })

  const completeMutation = useMutation({
    mutationFn: async (taskId: string) => {
      const response = await api.post(`/tasks/${taskId}/complete`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['daily-plan'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (taskId: string) => {
      await api.delete(`/tasks/${taskId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['daily-plan'] })
    },
  })

  const createMutation = useMutation({
    mutationFn: async (taskData: any) => {
      const response = await api.post('/tasks', taskData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['daily-plan'] })
      setShowCreateModal(false)
      setEditingTask(null)
    },
    onError: (error: any) => {
      console.error('Task creation error:', error)
      alert(error.response?.data?.detail || 'Failed to create task. Please try again.')
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ taskId, taskData }: { taskId: string; taskData: any }) => {
      const response = await api.put(`/tasks/${taskId}`, taskData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
      queryClient.invalidateQueries({ queryKey: ['daily-plan'] })
      setEditingTask(null)
    },
  })

  const handleComplete = (taskId: string) => {
    completeMutation.mutate(taskId)
  }

  const handleDelete = (taskId: string) => {
    if (confirm('Are you sure you want to delete this task?')) {
      deleteMutation.mutate(taskId)
    }
  }

  const tasks = data?.tasks || []
  const unapprovedCount = tasks.filter((t: any) => !t.is_approved).length

  const getPriorityColor = (priority: number) => {
    if (priority >= 80) return 'bg-red-100 text-red-700 border-red-200'
    if (priority >= 50) return 'bg-orange-100 text-orange-700 border-orange-200'
    return 'bg-green-100 text-green-700 border-green-200'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />
      case 'in_progress':
        return <Circle className="w-5 h-5 text-blue-600 fill-blue-600" />
      default:
        return <Circle className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 animate-fade-in">
      <Navigation />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Backend Connection Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl animate-slide-down hover-glow">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600 animate-pulse" />
              <div>
                <p className="text-sm font-semibold text-red-800">Backend Connection Error</p>
                <p className="text-xs text-red-600 mt-1">
                  {error.message?.includes('Backend server') 
                    ? 'Backend server is not available. Please ensure the backend is running on http://localhost:8000'
                    : 'Unable to load tasks. Please check your connection and try again.'}
                </p>
              </div>
            </div>
          </div>
        )}
        
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden animate-slide-up hover-glow">
          {/* Header */}
          <div className="px-6 py-6 border-b border-gray-200/50 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3 animate-slide-down">
                <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                  <CheckCircle2 className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white drop-shadow-lg">Tasks</h2>
              </div>
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center space-x-2 px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-xl hover:bg-white/30 transition-all duration-300 hover:scale-105 hover:shadow-lg group"
              >
                <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
                <span>New Task</span>
              </button>
            </div>

            {/* Filters */}
            <div className="flex items-center space-x-2 animate-slide-up overflow-x-auto pb-2 scrollbar-hide">
              <Filter className="w-4 h-4 text-white/80 flex-shrink-0" />
              {(['all', 'pending', 'in_progress', 'completed', 'needs_approval'] as const).map((f, index) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-300 hover:scale-105 whitespace-nowrap ${
                    filter === f
                      ? 'bg-white text-indigo-600 shadow-lg'
                      : 'bg-white/20 backdrop-blur-sm text-white hover:bg-white/30'
                  }`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  {f === 'needs_approval' ? (
                    <span className="flex items-center space-x-1">
                      <Zap className="w-3 h-3" />
                      <span>AI Pending</span>
                      {unapprovedCount > 0 && (
                        <span className="ml-1 px-1.5 py-0.5 bg-white text-indigo-600 rounded-full text-[10px] font-bold">
                          {unapprovedCount}
                        </span>
                      )}
                    </span>
                  ) : (
                    f.charAt(0).toUpperCase() + f.slice(1).replace('_', ' ')
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Task List */}
          <div className="divide-y divide-gray-200/50">
            {isLoading ? (
              <div className="text-center py-20 animate-fade-in">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600"></div>
                <p className="mt-6 text-gray-500 text-lg font-medium animate-pulse">Loading tasks...</p>
              </div>
            ) : tasks.length > 0 ? (
              tasks.map((task: any, index: number) => (
                <div
                  key={task.id}
                  className={`stagger-item p-5 hover:bg-gradient-to-r hover:from-indigo-50/50 hover:to-purple-50/50 transition-all duration-300 hover-lift group ${
                    task.status === 'completed' ? 'opacity-60' : ''
                  } ${!task.is_approved ? 'border-l-4 border-amber-400 bg-amber-50/30' : ''}`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      {task.is_approved ? (
                        <button
                          onClick={() => handleComplete(task.id)}
                          className="mt-0.5 p-2 hover:scale-110 transition-transform duration-300 group/check"
                        >
                          <div className="group-hover/check:animate-pulse">
                            {getStatusIcon(task.status)}
                          </div>
                        </button>
                      ) : (
                        <div className="mt-1 p-2 bg-amber-100 rounded-lg">
                          <Brain className="w-5 h-5 text-amber-600 animate-pulse" />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3
                            className={`font-bold text-lg group-hover:text-indigo-600 transition-colors ${
                              task.status === 'completed'
                                ? 'line-through text-gray-400'
                                : 'text-gray-900'
                            }`}
                          >
                            {task.title}
                          </h3>
                          {!task.is_approved && (
                            <span className="text-[10px] font-bold uppercase tracking-tighter bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-md">
                              AI Generated
                            </span>
                          )}
                          {task.risk_level > 60 && (
                            <span className="flex items-center space-x-1 text-[10px] font-bold uppercase tracking-tighter bg-red-100 text-red-700 px-1.5 py-0.5 rounded-md">
                              <ShieldAlert className="w-2.5 h-2.5" />
                              <span>High Risk</span>
                            </span>
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
                        {!task.is_approved && (
                          <div className="flex items-center space-x-2 mb-3">
                            <button
                              onClick={() => approveMutation.mutate(task.id)}
                              className="px-4 py-1.5 bg-emerald-500 text-white text-xs font-bold rounded-lg hover:bg-emerald-600 transition-colors flex items-center space-x-1"
                            >
                              <ShieldCheck className="w-3 h-3" />
                              <span>Approve Task</span>
                            </button>
                            <button
                              onClick={() => handleDelete(task.id)}
                              className="px-4 py-1.5 bg-gray-200 text-gray-700 text-xs font-bold rounded-lg hover:bg-gray-300 transition-colors"
                            >
                              Dismiss
                            </button>
                          </div>
                        )}
                        <div className="flex items-center flex-wrap gap-2 text-xs">
                          <span className={`px-3 py-1.5 rounded-full font-semibold border shadow-sm ${getPriorityColor(task.priority)}`}>
                            <Flag className="w-3 h-3 inline mr-1" />
                            Priority: {task.priority}
                          </span>
                          {task.due_date && (
                            <span className="flex items-center space-x-1 px-3 py-1.5 rounded-full bg-white shadow-sm font-semibold text-gray-700">
                              <Calendar className="w-3 h-3" />
                              <span>Due: {format(new Date(task.due_date), 'MMM d, yyyy')}</span>
                            </span>
                          )}
                          {task.estimated_duration && (
                            <span className="flex items-center space-x-1 px-3 py-1.5 rounded-full bg-white shadow-sm font-semibold text-gray-700">
                              <Clock className="w-3 h-3" />
                              <span>{task.estimated_duration} min</span>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      {task.status !== 'completed' && (
                        <button
                          onClick={() => setEditingTask(task)}
                          className="p-3 text-indigo-600 bg-indigo-50 rounded-xl hover:bg-indigo-100 hover:scale-110 transition-all duration-300 group/edit"
                          title="Edit"
                        >
                          <Edit className="w-5 h-5 group-hover/edit:animate-pulse" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(task.id)}
                        className="p-3 text-red-600 bg-red-50 rounded-xl hover:bg-red-100 hover:scale-110 transition-all duration-300 group/delete"
                        title="Delete"
                      >
                        <Trash2 className="w-5 h-5 group-hover/delete:animate-pulse" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-20 animate-bounce-in">
                <div className="inline-block p-6 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full mb-6 animate-pulse">
                  <CheckCircle2 className="w-16 h-16 text-indigo-600" />
                </div>
                <p className="text-gray-600 text-xl font-bold mb-2">No tasks found</p>
                <p className="text-gray-400 text-sm mb-6">
                  {filter !== 'all' ? `No ${filter} tasks` : 'Create your first task to get started'}
                </p>
                {filter === 'all' && (
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-lg"
                  >
                    Create Task
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Create/Edit Modal */}
        {(showCreateModal || editingTask) && (
          <TaskModal
            task={editingTask}
            onClose={() => {
              setShowCreateModal(false)
              setEditingTask(null)
            }}
            onSave={(taskData) => {
              if (editingTask) {
                updateMutation.mutate({ taskId: editingTask.id, taskData })
              } else {
                createMutation.mutate(taskData)
              }
            }}
            isSubmitting={createMutation.isPending || updateMutation.isPending}
          />
        )}
      </main>
    </div>
  )
}

function TaskModal({ task, onClose, onSave, isSubmitting = false }: { 
  task?: any
  onClose: () => void
  onSave: (data: any) => void
  isSubmitting?: boolean
}) {
  const [title, setTitle] = useState(task?.title || '')
  const [description, setDescription] = useState(task?.description || '')
  const [consequences, setConsequences] = useState(task?.consequences || '')
  const [priority, setPriority] = useState(task?.priority || 50)
  const [dueDate, setDueDate] = useState(task?.due_date ? format(new Date(task.due_date), 'yyyy-MM-dd') : '')
  const [duration, setDuration] = useState(task?.estimated_duration || 60)
  const [goalId, setGoalId] = useState(task?.goal_id || '')

  const { data: goals } = useQuery({
    queryKey: ['goals'],
    queryFn: async () => {
      const response = await api.get('/ai-los/goals')
      return response.data
    }
  })

  // Update form when task changes
  useEffect(() => {
    if (task) {
      setTitle(task.title || '')
      setDescription(task.description || '')
      setConsequences(task.consequences || '')
      setPriority(task.priority || 50)
      setDueDate(task.due_date ? format(new Date(task.due_date), 'yyyy-MM-dd') : '')
      setDuration(task.estimated_duration || 60)
      setGoalId(task.goal_id || '')
    } else {
      // Reset form for new task
      setTitle('')
      setDescription('')
      setConsequences('')
      setPriority(50)
      setDueDate('')
      setDuration(60)
      setGoalId('')
    }
  }, [task])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Prevent duplicate submissions
    if (isSubmitting) {
      return
    }
    
    const taskData: any = {
      title,
      description: description || null,
      consequences: consequences || null,
      priority: parseInt(priority.toString()),
      estimated_duration: parseInt(duration.toString()),
      goal_id: goalId || null,
    }
    
    // Only include due_date if provided
    if (dueDate) {
      // Convert date to ISO string with time
      const dueDateTime = new Date(dueDate + 'T00:00:00')
      taskData.due_date = dueDateTime.toISOString()
    }
    
    onSave(taskData)
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in p-4">
      <div className="bg-white/95 backdrop-blur-lg rounded-2xl shadow-2xl max-w-lg w-full p-8 animate-scale-in border border-gray-200/50 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            {task ? 'Edit Task' : 'Create New Task'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-300 hover:rotate-90"
          >
            ✕
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Consequences (What happens if missed?)</label>
            <input
              type="text"
              value={consequences}
              onChange={(e) => setConsequences(e.target.value)}
              placeholder="e.g. ₹500 penalty, missed deadline"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Goal Alignment</label>
            <select
              value={goalId}
              onChange={(e) => setGoalId(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
            >
              <option value="">General (No specific goal)</option>
              {goals?.map((goal: any) => (
                <option key={goal.id} value={goal.id}>{goal.title} ({goal.category})</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <input
                type="number"
                min="0"
                max="100"
                value={priority}
                onChange={(e) => setPriority(parseInt(e.target.value))}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
              <input
                type="number"
                min="1"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
            />
          </div>
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-3 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 font-semibold hover:scale-105 hover:shadow-lg"
            >
              {isSubmitting ? (
                <>
                  <div className="inline-block animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  <span>{task ? 'Updating...' : 'Creating...'}</span>
                </>
              ) : (
                <span>{task ? 'Update' : 'Create'} Task</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
