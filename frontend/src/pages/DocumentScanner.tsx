import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import { format } from 'date-fns'

export default function DocumentScanner() {
  const { logout } = useAuthStore()
  const [uploading, setUploading] = useState(false)
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: async () => {
      const response = await api.get('/documents?page=1&page_size=20')
      return response.data
    },
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      setUploading(false)
    },
  })

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploading(true)
      uploadMutation.mutate(file)
    }
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
                <Link to="/documents" className="border-indigo-500 text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
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
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Documents</h2>
            <label className="cursor-pointer bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">
              {uploading ? 'Uploading...' : 'Upload Document'}
              <input
                type="file"
                className="hidden"
                onChange={handleFileUpload}
                disabled={uploading}
              />
            </label>
          </div>
          
          {isLoading ? (
            <div className="text-center py-12">Loading...</div>
          ) : data && data.documents ? (
            <div className="bg-white shadow rounded-lg">
              <div className="divide-y divide-gray-200">
                {data.documents.map((doc: any) => (
                  <div key={doc.id} className="p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900">{doc.file_name}</p>
                        {doc.ai_classification && (
                          <span className="mt-1 inline-block px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded">
                            {doc.ai_classification}
                          </span>
                        )}
                        <p className="mt-2 text-sm text-gray-500">
                          {format(new Date(doc.uploaded_at), 'MMM d, yyyy h:mm a')}
                        </p>
                        {doc.ai_summary && (
                          <p className="mt-2 text-sm text-gray-600">{doc.ai_summary}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">No documents found</div>
          )}
        </div>
      </main>
    </div>
  )
}
