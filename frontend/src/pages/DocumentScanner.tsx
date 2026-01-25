import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { Upload, FileText, Search, Download, Eye, Trash2, File, Image, FileType } from 'lucide-react'

export default function DocumentScanner() {
  const [uploading, setUploading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['documents', searchQuery],
    queryFn: async () => {
      const params = new URLSearchParams({ page: '1', page_size: '50' })
      if (searchQuery) {
        params.append('search', searchQuery)
      }
      const response = await api.get(`/documents?${params}`)
      return response.data
    },
    retry: 2,
    retryDelay: 1000,
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
    onError: () => {
      setUploading(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (docId: string) => {
      await api.delete(`/documents/${docId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    },
  })

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setUploading(true)
      uploadMutation.mutate(file)
    }
  }

  const handleDelete = (docId: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
      deleteMutation.mutate(docId)
    }
  }

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(ext || '')) {
      return <Image className="w-5 h-5 text-blue-500" />
    }
    if (['pdf'].includes(ext || '')) {
      return <FileText className="w-5 h-5 text-red-500" />
    }
    if (['doc', 'docx'].includes(ext || '')) {
      return <FileType className="w-5 h-5 text-blue-600" />
    }
    return <File className="w-5 h-5 text-gray-500" />
  }

  const documents = data?.documents || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <FileText className="w-6 h-6 text-indigo-600" />
                <h2 className="text-2xl font-bold text-gray-900">Documents</h2>
              </div>
              <label className="cursor-pointer flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
                <Upload className="w-4 h-4" />
                <span>{uploading ? 'Uploading...' : 'Upload Document'}</span>
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                />
              </label>
            </div>

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Document List */}
          <div className="divide-y divide-gray-200">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <p className="mt-4 text-gray-500">Loading documents...</p>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 mb-2">Failed to load documents</p>
                <p className="text-sm text-gray-400 mb-4">
                  {(error as any)?.message?.includes('Backend server') 
                    ? 'Backend server is not available. Please ensure the backend is running on http://localhost:8000'
                    : 'Please check your connection and try again'}
                </p>
                <button
                  onClick={() => queryClient.invalidateQueries({ queryKey: ['documents'] })}
                  className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                >
                  Retry
                </button>
              </div>
            ) : documents.length > 0 ? (
              documents.map((doc: any) => (
                <div
                  key={doc.id}
                  className="p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1 min-w-0">
                      <div className="mt-1">
                        {getFileIcon(doc.file_name)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 truncate">{doc.file_name}</p>
                        {doc.ai_classification && (
                          <span className="mt-1 inline-block px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 rounded">
                            {doc.ai_classification}
                          </span>
                        )}
                        {doc.ai_summary && (
                          <p className="mt-2 text-sm text-gray-600 line-clamp-2">{doc.ai_summary}</p>
                        )}
                        <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                          <span>{format(new Date(doc.uploaded_at), 'MMM d, yyyy h:mm a')}</span>
                          {doc.file_size && (
                            <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      {doc.presigned_url && (
                        <button
                          onClick={async () => {
                            try {
                              // Fetch file through authenticated API
                              const token = localStorage.getItem('access_token')
                              const response = await fetch(doc.presigned_url, {
                                headers: {
                                  'Authorization': `Bearer ${token}`
                                }
                              })
                              
                              if (!response.ok) {
                                throw new Error('Failed to fetch file')
                              }
                              
                              const blob = await response.blob()
                              const url = window.URL.createObjectURL(blob)
                              const a = document.createElement('a')
                              a.href = url
                              a.target = '_blank'
                              a.rel = 'noopener noreferrer'
                              document.body.appendChild(a)
                              a.click()
                              window.URL.revokeObjectURL(url)
                              document.body.removeChild(a)
                            } catch (error: any) {
                              alert(`Failed to view document: ${error.message}`)
                            }
                          }}
                          className="p-2 text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                          title="View"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      )}
                      {doc.presigned_url && (
                        <button
                          onClick={async () => {
                            try {
                              // Fetch file through authenticated API
                              const token = localStorage.getItem('access_token')
                              const response = await fetch(doc.presigned_url, {
                                headers: {
                                  'Authorization': `Bearer ${token}`
                                }
                              })
                              
                              if (!response.ok) {
                                throw new Error('Failed to fetch file')
                              }
                              
                              const blob = await response.blob()
                              const url = window.URL.createObjectURL(blob)
                              const a = document.createElement('a')
                              a.href = url
                              a.download = doc.file_name
                              document.body.appendChild(a)
                              a.click()
                              window.URL.revokeObjectURL(url)
                              document.body.removeChild(a)
                            } catch (error: any) {
                              alert(`Failed to download document: ${error.message}`)
                            }
                          }}
                          className="p-2 text-gray-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 text-lg font-medium">No documents found</p>
                <p className="text-gray-400 text-sm mt-2">
                  {searchQuery ? 'Try a different search term' : 'Upload your first document to get started'}
                </p>
                {!searchQuery && (
                  <label className="mt-4 inline-block px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors cursor-pointer">
                    <Upload className="w-4 h-4 inline mr-2" />
                    Upload Document
                    <input
                      type="file"
                      className="hidden"
                      onChange={handleFileUpload}
                      accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                    />
                  </label>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
