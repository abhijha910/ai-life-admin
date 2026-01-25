import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { CheckCircle2, Circle, Plus, Edit, Trash2, Clock, Calendar, Flag, Filter, AlertCircle } from 'lucide-react'

export default function TaskList() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingTask, setEditingTask] = useState<any>(null)
  const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks', filter],
    queryFn: async () => {
      const params = new URLSearchParams({ page: '1', page_size: '100' })
      if (filter !== 'all') {
        params.append('status', filter)
      }
      const response = await api.get(`/tasks?${params}`)
      return response.data
    },
    retry: 2,
    retryDelay: 1000,
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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Backend Connection Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
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
        
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-gray-900">Tasks</h2>
              <button
                onClick={() => setShowCreateModal(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>New Task</span>
              </button>
            </div>

            {/* Filters */}
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              {(['all', 'pending', 'in_progress', 'completed'] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    filter === f
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1).replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Task List */}
          <div className="divide-y divide-gray-200">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <p className="mt-4 text-gray-500">Loading tasks...</p>
              </div>
            ) : tasks.length > 0 ? (
              tasks.map((task: any) => (
                <div
                  key={task.id}
                  className={`p-4 hover:bg-gray-50 transition-colors ${
                    task.status === 'completed' ? 'opacity-75' : ''
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <button
                        onClick={() => handleComplete(task.id)}
                        className="mt-0.5"
                      >
                        {getStatusIcon(task.status)}
                      </button>
                      <div className="flex-1 min-w-0">
                        <h3
                          className={`font-semibold mb-1 ${
                            task.status === 'completed'
                              ? 'line-through text-gray-400'
                              : 'text-gray-900'
                          }`}
                        >
                          {task.title}
                        </h3>
                        {task.description && (
                          <p className="text-sm text-gray-600 mb-2">{task.description}</p>
                        )}
                        <div className="flex items-center flex-wrap gap-3 text-xs text-gray-500">
                          <span className={`px-2 py-1 rounded border ${getPriorityColor(task.priority)}`}>
                            <Flag className="w-3 h-3 inline mr-1" />
                            Priority: {task.priority}
                          </span>
                          {task.due_date && (
                            <span className="flex items-center space-x-1">
                              <Calendar className="w-3 h-3" />
                              <span>Due: {format(new Date(task.due_date), 'MMM d, yyyy')}</span>
                            </span>
                          )}
                          {task.estimated_duration && (
                            <span className="flex items-center space-x-1">
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
                          className="p-2 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                        >
                          <Edit className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(task.id)}
                        className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <CheckCircle2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 text-lg font-medium">No tasks found</p>
                <p className="text-gray-400 text-sm mt-2">
                  {filter !== 'all' ? `No ${filter} tasks` : 'Create your first task to get started'}
                </p>
                {filter === 'all' && (
                  <button
                    onClick={() => setShowCreateModal(true)}
                    className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
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
          />
        )}
      </main>
    </div>
  )
}

function TaskModal({ task, onClose, onSave }: { task?: any; onClose: () => void; onSave: (data: any) => void }) {
  const [title, setTitle] = useState(task?.title || '')
  const [description, setDescription] = useState(task?.description || '')
  const [priority, setPriority] = useState(task?.priority || 50)
  const [dueDate, setDueDate] = useState(task?.due_date ? format(new Date(task.due_date), 'yyyy-MM-dd') : '')
  const [duration, setDuration] = useState(task?.estimated_duration || 60)

  // Update form when task changes
  useEffect(() => {
    if (task) {
      setTitle(task.title || '')
      setDescription(task.description || '')
      setPriority(task.priority || 50)
      setDueDate(task.due_date ? format(new Date(task.due_date), 'yyyy-MM-dd') : '')
      setDuration(task.estimated_duration || 60)
    } else {
      // Reset form for new task
      setTitle('')
      setDescription('')
      setPriority(50)
      setDueDate('')
      setDuration(60)
    }
  }, [task])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const taskData: any = {
      title,
      description: description || null,
      priority: parseInt(priority.toString()),
      estimated_duration: parseInt(duration.toString()),
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-lg w-full mx-4 p-6">
        <h3 className="text-xl font-bold mb-4">{task ? 'Edit Task' : 'Create New Task'}</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
              <input
                type="number"
                min="1"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              {task ? 'Update' : 'Create'} Task
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
