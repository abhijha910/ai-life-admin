import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { format } from 'date-fns'
import { Upload, FileText, Search, Download, Eye, Trash2, File, Image, FileType, Sparkles, Loader2, Calendar } from 'lucide-react'

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

  const processMutation = useMutation({
    mutationFn: async (docId: string) => {
      const response = await api.post(`/documents/${docId}/process`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
    onError: (error: any) => {
      alert(`Processing failed: ${error?.response?.data?.detail || error.message}`)
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
      return <Image className="w-6 h-6 text-blue-500 animate-pulse" />
    }
    if (['pdf'].includes(ext || '')) {
      return <FileText className="w-6 h-6 text-red-500" />
    }
    if (['doc', 'docx'].includes(ext || '')) {
      return <FileType className="w-6 h-6 text-blue-600" />
    }
    return <File className="w-6 h-6 text-gray-500" />
  }

  const documents = data?.documents || []

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 animate-fade-in">
      <Navigation />

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden animate-slide-up hover-glow">
          {/* Header */}
          <div className="px-6 py-6 border-b border-gray-200/50 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3 animate-slide-down">
                <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-white drop-shadow-lg">Documents</h2>
              </div>
              <label className="group cursor-pointer flex items-center space-x-2 px-6 py-3 bg-white/20 backdrop-blur-sm text-white rounded-xl hover:bg-white/30 transition-all duration-300 hover:scale-105 hover:shadow-lg animate-bounce-in">
                {uploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Uploading...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5 group-hover:animate-bounce" />
                    <span>Upload Document</span>
                  </>
                )}
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
            <div className="relative animate-slide-up">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/70" />
              <input
                type="text"
                placeholder="Search documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-white/20 backdrop-blur-sm border border-white/30 rounded-xl text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/50 focus:bg-white/30 transition-all duration-300"
              />
            </div>
          </div>

          {/* Document List */}
          <div className="divide-y divide-gray-200/50">
            {isLoading ? (
              <div className="text-center py-20 animate-fade-in">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-200 border-t-indigo-600"></div>
                <p className="mt-6 text-gray-500 text-lg font-medium animate-pulse">Loading documents...</p>
              </div>
            ) : error ? (
              <div className="text-center py-20 animate-bounce-in">
                <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4 animate-pulse" />
                <p className="text-gray-500 mb-2 text-lg font-semibold">Failed to load documents</p>
                <p className="text-sm text-gray-400 mb-6">
                  {(error as any)?.message?.includes('Backend server') 
                    ? 'Backend server is not available. Please ensure the backend is running on http://localhost:8000'
                    : 'Please check your connection and try again'}
                </p>
                <button
                  onClick={() => queryClient.invalidateQueries({ queryKey: ['documents'] })}
                  className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-lg"
                >
                  Retry
                </button>
              </div>
            ) : documents.length > 0 ? (
              documents.map((doc: any, index: number) => (
                <div
                  key={doc.id}
                  className="stagger-item p-5 hover:bg-gradient-to-r hover:from-indigo-50/50 hover:to-purple-50/50 transition-all duration-300 hover-lift group"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1 min-w-0">
                      <div className="mt-1 p-2 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-xl group-hover:scale-110 transition-transform duration-300">
                        {getFileIcon(doc.file_name)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-bold text-gray-900 truncate text-lg group-hover:text-indigo-600 transition-colors">{doc.file_name}</p>
                        <div className="flex items-center gap-2 mt-2 flex-wrap">
                          {doc.ai_classification && (
                            <span className="inline-block px-3 py-1 text-xs font-semibold bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 rounded-full shadow-sm animate-scale-in">
                              {doc.ai_classification}
                            </span>
                          )}
                          {doc.processed_at ? (
                            <span className="inline-flex items-center px-3 py-1 text-xs font-semibold bg-gradient-to-r from-green-100 to-emerald-200 text-green-800 rounded-full shadow-sm animate-scale-in">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
                              Processed
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-3 py-1 text-xs font-semibold bg-gradient-to-r from-yellow-100 to-amber-200 text-yellow-800 rounded-full shadow-sm animate-scale-in">
                              <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2 animate-pulse"></span>
                              Not Processed
                            </span>
                          )}
                        </div>
                        {doc.ai_summary && (
                          <p className="mt-3 text-sm text-gray-600 line-clamp-2 leading-relaxed">{doc.ai_summary}</p>
                        )}
                        {doc.ocr_text && (
                          <p className="mt-2 text-xs text-gray-500 font-medium">
                            <span className="inline-flex items-center">
                              <FileText className="w-3 h-3 mr-1" />
                              Text extracted: {doc.ocr_text.length.toLocaleString()} characters
                            </span>
                          </p>
                        )}
                        <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            {format(new Date(doc.uploaded_at), 'MMM d, yyyy h:mm a')}
                          </span>
                          {doc.file_size && (
                            <span className="flex items-center">
                              <File className="w-3 h-3 mr-1" />
                              {(doc.file_size / 1024).toFixed(1)} KB
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      {!doc.processed_at && (
                        <button
                          onClick={() => processMutation.mutate(doc.id)}
                          disabled={processMutation.isPending}
                          className="p-3 text-purple-600 bg-purple-50 rounded-xl hover:bg-purple-100 hover:scale-110 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group relative"
                          title="Process document with AI and extract tasks"
                        >
                          {processMutation.isPending ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                          ) : (
                            <Sparkles className="w-5 h-5 group-hover:animate-pulse" />
                          )}
                        </button>
                      )}
                      {doc.presigned_url && (
                        <>
                          <button
                            onClick={async () => {
                              try {
                                const token = localStorage.getItem('access_token')
                                const response = await fetch(doc.presigned_url, {
                                  headers: { 'Authorization': `Bearer ${token}` }
                                })
                                if (!response.ok) throw new Error('Failed to fetch file')
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
                            className="p-3 text-indigo-600 bg-indigo-50 rounded-xl hover:bg-indigo-100 hover:scale-110 transition-all duration-300 group"
                            title="View"
                          >
                            <Eye className="w-5 h-5 group-hover:animate-pulse" />
                          </button>
                          <button
                            onClick={async () => {
                              try {
                                const token = localStorage.getItem('access_token')
                                const response = await fetch(doc.presigned_url, {
                                  headers: { 'Authorization': `Bearer ${token}` }
                                })
                                if (!response.ok) throw new Error('Failed to fetch file')
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
                            className="p-3 text-green-600 bg-green-50 rounded-xl hover:bg-green-100 hover:scale-110 transition-all duration-300 group"
                            title="Download"
                          >
                            <Download className="w-5 h-5 group-hover:animate-bounce" />
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="p-3 text-red-600 bg-red-50 rounded-xl hover:bg-red-100 hover:scale-110 transition-all duration-300 group"
                        title="Delete"
                      >
                        <Trash2 className="w-5 h-5 group-hover:animate-pulse" />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-20 animate-bounce-in">
                <div className="inline-block p-6 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full mb-6 animate-pulse">
                  <FileText className="w-16 h-16 text-indigo-600" />
                </div>
                <p className="text-gray-500 text-xl font-bold mb-2">No documents found</p>
                <p className="text-gray-400 text-sm mb-6">
                  {searchQuery ? 'Try a different search term' : 'Upload your first document to get started'}
                </p>
                {!searchQuery && (
                  <label className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 hover:scale-105 hover:shadow-lg cursor-pointer animate-scale-in">
                    <Upload className="w-5 h-5 mr-2" />
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
