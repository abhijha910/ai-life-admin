import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Sparkles, LogOut, User } from 'lucide-react'

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
    <nav className="bg-white/80 backdrop-blur-lg shadow-lg border-b border-gray-200/50 sticky top-0 z-40 animate-slide-down">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20 items-center">
          <div className="flex items-center space-x-8">
            <Link to="/dashboard" className="flex-shrink-0 flex items-center space-x-2 group">
              <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-lg">
                <Sparkles className="w-6 h-6 text-white group-hover:animate-pulse" />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent group-hover:from-indigo-700 group-hover:via-purple-700 group-hover:to-pink-700 transition-all duration-300">
                AI Life Admin
              </h1>
            </Link>
            <div className="hidden sm:flex sm:space-x-1">
              {navLinks.map((link, index) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`stagger-item inline-flex items-center px-4 py-2 text-sm font-semibold rounded-xl transition-all duration-300 relative group ${
                    isActive(link.path)
                      ? 'text-indigo-600 bg-gradient-to-r from-indigo-50 to-purple-50 shadow-md scale-105'
                      : 'text-gray-600 hover:text-indigo-600 hover:bg-gray-50 hover:scale-105'
                  }`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  {link.label}
                  {isActive(link.path) && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-scale-in"></span>
                  )}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <div className="hidden sm:flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl">
                <div className="p-1.5 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg">
                  <User className="w-4 h-4 text-white" />
                </div>
                <span className="text-sm font-semibold text-gray-700">
                  {user.full_name || user.email}
                </span>
              </div>
            )}
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-red-600 bg-gray-50 hover:bg-red-50 rounded-xl text-sm font-semibold transition-all duration-300 hover:scale-105 hover:shadow-md group"
            >
              <LogOut className="w-4 h-4 group-hover:animate-pulse" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
