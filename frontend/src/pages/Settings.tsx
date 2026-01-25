import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { Settings as SettingsIcon, User, Bell, Clock, Sparkles, Save, Shield } from 'lucide-react'

export default function Settings() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'profile' | 'notifications' | 'ai' | 'account'>('profile')

  const { data: userData } = useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const response = await api.get('/auth/me')
      return response.data
    },
  })

  const { data: settingsData } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await api.get('/settings')
      return response.data
    },
  })

  const updateSettingsMutation = useMutation({
    mutationFn: async (data: any) => {
      // Convert daily_plan_time from "HH:mm" to time object format
      const settingsData: any = {
        timezone: data.timezone,
        notification_preferences: data.notification_preferences,
        ai_preferences: data.ai_preferences,
      }
      
      // Convert time string to proper format
      if (data.daily_plan_time) {
        const [hours, minutes] = data.daily_plan_time.split(':')
        settingsData.daily_plan_time = `${hours}:${minutes}:00`
      }
      
      const response = await api.put('/settings', settingsData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      queryClient.invalidateQueries({ queryKey: ['user'] })
    },
  })

  const [formData, setFormData] = useState({
    full_name: '',
    timezone: 'UTC',
    daily_plan_time: '08:00',
    notification_preferences: {} as Record<string, any>,
    ai_preferences: {} as Record<string, any>,
  })

  // Update form data when settings load
  useEffect(() => {
    if (userData) {
      setFormData(prev => ({ ...prev, full_name: userData.full_name || '' }))
    }
    if (settingsData) {
      setFormData(prev => ({
        ...prev,
        timezone: settingsData.timezone || 'UTC',
        daily_plan_time: settingsData.daily_plan_time 
          ? settingsData.daily_plan_time.substring(0, 5) // Convert "08:00:00" to "08:00"
          : '08:00',
        notification_preferences: settingsData.notification_preferences || {},
        ai_preferences: settingsData.ai_preferences || {},
      }))
    }
  }, [userData, settingsData])

  const handleSave = () => {
    updateSettingsMutation.mutate(formData)
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'ai', label: 'AI Preferences', icon: Sparkles },
    { id: 'account', label: 'Account', icon: Shield },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navigation />

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-indigo-50 to-purple-50">
            <div className="flex items-center space-x-3">
              <SettingsIcon className="w-6 h-6 text-indigo-600" />
              <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
            </div>
          </div>

          <div className="flex">
            {/* Sidebar */}
            <div className="w-64 border-r border-gray-200 bg-gray-50">
              <nav className="p-4 space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                        activeTab === tab.id
                          ? 'bg-indigo-600 text-white'
                          : 'text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{tab.label}</span>
                    </button>
                  )
                })}
              </nav>
            </div>

            {/* Content */}
            <div className="flex-1 p-6">
              {activeTab === 'profile' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Profile Information</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                        <input
                          type="text"
                          value={formData.full_name}
                          onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input
                          type="email"
                          value={userData?.email || ''}
                          disabled
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                        />
                        <p className="mt-1 text-xs text-gray-500">Email cannot be changed</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
                        <select
                          value={formData.timezone}
                          onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        >
                          <option value="UTC">UTC</option>
                          <option value="America/New_York">Eastern Time (US)</option>
                          <option value="America/Chicago">Central Time (US)</option>
                          <option value="America/Denver">Mountain Time (US)</option>
                          <option value="America/Los_Angeles">Pacific Time (US)</option>
                          <option value="Europe/London">London</option>
                          <option value="Europe/Paris">Paris</option>
                          <option value="Asia/Kolkata">India (IST)</option>
                          <option value="Asia/Tokyo">Tokyo</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'notifications' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Notification Preferences</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium">Email Notifications</p>
                          <p className="text-sm text-gray-500">Receive notifications via email</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={formData.notification_preferences?.email || false}
                            onChange={(e) =>
                              setFormData({
                                ...formData,
                                notification_preferences: {
                                  ...formData.notification_preferences,
                                  email: e.target.checked,
                                },
                              })
                            }
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                        </label>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium">Task Reminders</p>
                          <p className="text-sm text-gray-500">Get reminded about upcoming tasks</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={formData.notification_preferences?.task_reminders || false}
                            onChange={(e) =>
                              setFormData({
                                ...formData,
                                notification_preferences: {
                                  ...formData.notification_preferences,
                                  task_reminders: e.target.checked,
                                },
                              })
                            }
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'ai' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-4">AI Preferences</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Daily Plan Time
                        </label>
                        <div className="flex items-center space-x-2">
                          <Clock className="w-5 h-5 text-gray-400" />
                          <input
                            type="time"
                            value={formData.daily_plan_time}
                            onChange={(e) => setFormData({ ...formData, daily_plan_time: e.target.value })}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                          />
                        </div>
                        <p className="mt-1 text-xs text-gray-500">
                          When should your daily plan be generated?
                        </p>
                      </div>
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium">Auto-generate Tasks from Emails</p>
                          <p className="text-sm text-gray-500">Automatically create tasks from email content</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={formData.ai_preferences?.auto_generate_tasks || false}
                            onChange={(e) =>
                              setFormData({
                                ...formData,
                                ai_preferences: {
                                  ...formData.ai_preferences,
                                  auto_generate_tasks: e.target.checked,
                                },
                              })
                            }
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'account' && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Account Settings</h3>
                    <div className="space-y-4">
                      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <p className="text-sm text-yellow-800">
                          <strong>Account deletion:</strong> To delete your account, please contact support.
                        </p>
                      </div>
                      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-sm text-blue-800">
                          <strong>Data export:</strong> You can export all your data at any time.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-8 pt-6 border-t border-gray-200">
                <button
                  onClick={handleSave}
                  disabled={updateSettingsMutation.isPending}
                  className="flex items-center space-x-2 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  <Save className="w-4 h-4" />
                  <span>{updateSettingsMutation.isPending ? 'Saving...' : 'Save Changes'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
