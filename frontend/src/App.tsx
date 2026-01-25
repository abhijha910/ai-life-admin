import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useAuthStore } from './store/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'
import EmailInbox from './pages/EmailInbox'
import EmailDetail from './pages/EmailDetail'
import DocumentScanner from './pages/DocumentScanner'
import TaskList from './pages/TaskList'
import Settings from './pages/Settings'
import OAuthCallback from './pages/OAuthCallback'

const queryClient = new QueryClient()

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/emails"
            element={
              <PrivateRoute>
                <EmailInbox />
              </PrivateRoute>
            }
          />
          <Route
            path="/emails/:emailId"
            element={
              <PrivateRoute>
                <EmailDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/documents"
            element={
              <PrivateRoute>
                <DocumentScanner />
              </PrivateRoute>
            }
          />
          <Route
            path="/tasks"
            element={
              <PrivateRoute>
                <TaskList />
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <Settings />
              </PrivateRoute>
            }
          />
          <Route
            path="/emails/oauth/callback"
            element={
              <PrivateRoute>
                <OAuthCallback />
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  )
}

export default App
