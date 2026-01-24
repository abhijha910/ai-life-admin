import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import { format } from 'date-fns'

export default function TaskList() {
  const { logout } = useAuthStore()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await api.get('/tasks?page=1&page_size=50')
      return response.data
    },
  })

  const completeMutation = useMutation({
    mutationFn: async (taskId: string) => {
      const response = await api.post(`/tasks/${taskId}/complete`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  const handleComplete = (taskId: string) => {
    completeMutation.mutate(taskId)
  }

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
                <Link to="/emails" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                  Emails
                </Link>
                <Link to="/documents" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                  Documents
                </Link>
                <Link to="/tasks" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
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
          <h2 className="text-2xl font-bold mb-6">Tasks</h2>
          
          {isLoading ? (
            <div className="text-center py-12">Loading...</div>
          ) : data && data.tasks ? (
            <div className="bg-white shadow rounded-lg">
              <div className="divide-y divide-gray-200">
                {data.tasks.map((task: any) => (
                  <div key={task.id} className="p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center">
                          <h3 className={`font-semibold ${task.status === 'completed' ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                            {task.title}
                          </h3>
                          <span className={`ml-2 px-2 py-1 text-xs font-semibold rounded ${
                            task.status === 'completed' ? 'bg-green-100 text-green-800' :
                            task.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {task.status}
                          </span>
                        </div>
                        {task.description && (
                          <p className="mt-1 text-sm text-gray-600">{task.description}</p>
                        )}
                        <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                          <span>Priority: {task.priority}</span>
                          {task.due_date && (
                            <span>Due: {format(new Date(task.due_date), 'MMM d, yyyy')}</span>
                          )}
                          {task.estimated_duration && (
                            <span>Duration: {task.estimated_duration} min</span>
                          )}
                        </div>
                      </div>
                      {task.status !== 'completed' && (
                        <button
                          onClick={() => handleComplete(task.id)}
                          className="ml-4 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Complete
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">No tasks found</div>
          )}
        </div>
      </main>
    </div>
  )
}
