import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import Navigation from '../components/Navigation'
import api from '../services/api'
import { Settings as SettingsIcon, User, Bell, Clock, Sparkles, Save, Shield, Loader2, CheckCircle2 } from 'lucide-react'

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
      const settingsData: any = {
        timezone: data.timezone,
        notification_preferences: data.notification_preferences,
        ai_preferences: data.ai_preferences,
      }
      
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

  useEffect(() => {
    if (userData) {
      setFormData(prev => ({ ...prev, full_name: userData.full_name || '' }))
    }
    if (settingsData) {
      setFormData(prev => ({
        ...prev,
        timezone: settingsData.timezone || 'UTC',
        daily_plan_time: settingsData.daily_plan_time 
          ? settingsData.daily_plan_time.substring(0, 5)
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
    { id: 'profile', label: 'Profile', icon: User, color: 'from-indigo-500 to-blue-500' },
    { id: 'notifications', label: 'Notifications', icon: Bell, color: 'from-purple-500 to-pink-500' },
    { id: 'ai', label: 'AI Preferences', icon: Sparkles, color: 'from-pink-500 to-red-500' },
    { id: 'account', label: 'Account', icon: Shield, color: 'from-gray-500 to-gray-600' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 animate-fade-in">
      <Navigation />

      <main className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-white/80 backdrop-blur-lg rounded-2xl shadow-xl border border-gray-200/50 overflow-hidden animate-slide-up hover-glow">
          {/* Header */}
          <div className="px-6 py-6 border-b border-gray-200/50 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500">
            <div className="flex items-center space-x-3 animate-slide-down">
              <div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
                <SettingsIcon className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-white drop-shadow-lg">Settings</h2>
            </div>
          </div>

          <div className="flex flex-col md:flex-row">
            {/* Sidebar */}
            <div className="w-full md:w-64 border-b md:border-b-0 md:border-r border-gray-200/50 bg-gradient-to-b md:bg-gradient-to-r from-gray-50 to-indigo-50/30">
              <nav className="p-4 space-y-2">
                {tabs.map((tab, index) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`stagger-item w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 font-semibold group ${
                        activeTab === tab.id
                          ? `bg-gradient-to-r ${tab.color} text-white shadow-lg scale-105`
                          : 'text-gray-700 hover:bg-white/50 hover:scale-105'
                      }`}
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <Icon className={`w-5 h-5 ${activeTab === tab.id ? 'animate-pulse' : ''}`} />
                      <span>{tab.label}</span>
                    </button>
                  )
                })}
              </nav>
            </div>

            {/* Content */}
            <div className="flex-1 p-8 animate-slide-up">
              {activeTab === 'profile' && (
                <div className="space-y-6 animate-fade-in">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                      <User className="w-6 h-6 text-indigo-600" />
                      <span>Profile Information</span>
                    </h3>
                    <div className="space-y-5">
                      <div className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Full Name</label>
                        <input
                          type="text"
                          value={formData.full_name}
                          onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
                        />
                      </div>
                      <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                        <input
                          type="email"
                          value={userData?.email || ''}
                          disabled
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl bg-gray-50 text-gray-500 cursor-not-allowed"
                        />
                        <p className="mt-2 text-xs text-gray-500">Email cannot be changed</p>
                      </div>
                      <div className="animate-slide-up" style={{ animationDelay: '0.3s' }}>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Timezone</label>
                        <select
                          value={formData.timezone}
                          onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-300 hover:border-indigo-300"
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
                <div className="space-y-6 animate-fade-in">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                      <Bell className="w-6 h-6 text-purple-600" />
                      <span>Notification Preferences</span>
                    </h3>
                    <div className="space-y-4">
                      <div className="stagger-item flex items-center justify-between p-5 bg-gradient-to-r from-gray-50 to-purple-50 rounded-xl border-2 border-gray-200 hover:border-purple-300 transition-all duration-300 hover-lift" style={{ animationDelay: '0.1s' }}>
                        <div>
                          <p className="font-bold text-gray-900">Email Notifications</p>
                          <p className="text-sm text-gray-600 mt-1">Receive notifications via email</p>
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
                          <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-purple-500 peer-checked:to-pink-500"></div>
                        </label>
                      </div>
                      <div className="stagger-item flex items-center justify-between p-5 bg-gradient-to-r from-gray-50 to-purple-50 rounded-xl border-2 border-gray-200 hover:border-purple-300 transition-all duration-300 hover-lift" style={{ animationDelay: '0.2s' }}>
                        <div>
                          <p className="font-bold text-gray-900">Task Reminders</p>
                          <p className="text-sm text-gray-600 mt-1">Get reminded about upcoming tasks</p>
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
                          <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-purple-500 peer-checked:to-pink-500"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'ai' && (
                <div className="space-y-6 animate-fade-in">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                      <Sparkles className="w-6 h-6 text-pink-600 animate-pulse" />
                      <span>AI Preferences</span>
                    </h3>
                    <div className="space-y-5">
                      <div className="stagger-item animate-slide-up" style={{ animationDelay: '0.1s' }}>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Daily Plan Time
                        </label>
                        <div className="flex items-center space-x-3 p-4 bg-gradient-to-r from-pink-50 to-red-50 rounded-xl border-2 border-pink-200">
                          <Clock className="w-6 h-6 text-pink-600" />
                          <input
                            type="time"
                            value={formData.daily_plan_time}
                            onChange={(e) => setFormData({ ...formData, daily_plan_time: e.target.value })}
                            className="px-4 py-2 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-all duration-300 hover:border-pink-300"
                          />
                        </div>
                        <p className="mt-2 text-xs text-gray-500">
                          When should your daily plan be generated?
                        </p>
                      </div>
                      <div className="stagger-item flex items-center justify-between p-5 bg-gradient-to-r from-gray-50 to-pink-50 rounded-xl border-2 border-gray-200 hover:border-pink-300 transition-all duration-300 hover-lift" style={{ animationDelay: '0.2s' }}>
                        <div>
                          <p className="font-bold text-gray-900">Auto-generate Tasks from Emails</p>
                          <p className="text-sm text-gray-600 mt-1">Automatically create tasks from email content</p>
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
                          <div className="w-14 h-7 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-gradient-to-r peer-checked:from-pink-500 peer-checked:to-red-500"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'account' && (
                <div className="space-y-6 animate-fade-in">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center space-x-2">
                      <Shield className="w-6 h-6 text-gray-600" />
                      <span>Account Settings</span>
                    </h3>
                    <div className="space-y-4">
                      <div className="stagger-item p-5 bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-200 rounded-xl animate-scale-in hover-glow" style={{ animationDelay: '0.1s' }}>
                        <div className="flex items-start space-x-3">
                          <Shield className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-sm font-bold text-yellow-900 mb-1">Account Deletion</p>
                            <p className="text-sm text-yellow-800 leading-relaxed">
                              To delete your account, please contact support.
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="stagger-item p-5 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl animate-scale-in hover-glow" style={{ animationDelay: '0.2s' }}>
                        <div className="flex items-start space-x-3">
                          <CheckCircle2 className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                          <div>
                            <p className="text-sm font-bold text-blue-900 mb-1">Data Export</p>
                            <p className="text-sm text-blue-800 leading-relaxed">
                              You can export all your data at any time.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-10 pt-6 border-t-2 border-gray-200 animate-slide-up">
                <button
                  onClick={handleSave}
                  disabled={updateSettingsMutation.isPending}
                  className="flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed font-semibold hover:scale-105 hover:shadow-lg group"
                >
                  {updateSettingsMutation.isPending ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Saving...</span>
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5 group-hover:animate-pulse" />
                      <span>Save Changes</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
