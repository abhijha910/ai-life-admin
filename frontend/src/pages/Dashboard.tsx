import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import { format } from 'date-fns'

export default function Dashboard() {
  const { logout } = useAuthStore()

  const { data: plan, isLoading } = useQuery({
    queryKey: ['daily-plan'],
    queryFn: async () => {
      const response = await api.get('/plans/today')
      return response.data
    },
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold">AI Life Admin</h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link to="/dashboard" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                  Dashboard
                </Link>
                <Link to="/emails" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
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
          <h2 className="text-2xl font-bold mb-6">Today's Plan</h2>
          
          {isLoading ? (
            <div className="text-center py-12">Loading...</div>
          ) : plan ? (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="mb-4">
                <p className="text-sm text-gray-500">
                  {format(new Date(plan.date), 'EEEE, MMMM d, yyyy')}
                </p>
                <p className="text-lg font-semibold mt-2">
                  Total Duration: {Math.round(plan.total_duration / 60)} hours
                </p>
              </div>
              
              {plan.ai_recommendations && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-blue-900 mb-2">AI Recommendations</h3>
                  <p className="text-blue-800">{plan.ai_recommendations}</p>
                </div>
              )}

              <div className="space-y-4">
                {plan.tasks && plan.tasks.length > 0 ? (
                  plan.tasks.map((task: any, index: number) => (
                    <div key={index} className="border-l-4 border-indigo-500 pl-4 py-2">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-semibold">{task.title}</h4>
                          <p className="text-sm text-gray-500">
                            Priority: {task.priority} | Duration: {task.estimated_duration} min
                          </p>
                          {task.scheduled_time && (
                            <p className="text-xs text-gray-400 mt-1">
                              {format(new Date(task.scheduled_time), 'h:mm a')}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500">No tasks scheduled for today.</p>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">No plan available</div>
          )}
        </div>
      </main>
    </div>
  )
}
