import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'

export default function Navigation() {
  const { logout, user } = useAuthStore()
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path
  }

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard' },
    { path: '/emails', label: 'Emails' },
    { path: '/documents', label: 'Documents' },
    { path: '/tasks', label: 'Tasks' },
    { path: '/settings', label: 'Settings' },
  ]

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link to="/dashboard" className="flex-shrink-0 flex items-center">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                AI Life Admin
              </h1>
            </Link>
            <div className="hidden sm:ml-8 sm:flex sm:space-x-1">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`inline-flex items-center px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                    isActive(link.path)
                      ? 'text-indigo-600 border-b-2 border-indigo-600'
                      : 'text-gray-600 hover:text-gray-900 hover:border-b-2 hover:border-gray-300'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <span className="hidden sm:block text-sm text-gray-600">
                {user.full_name || user.email}
              </span>
            )}
            <button
              onClick={logout}
              className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-gray-100"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
