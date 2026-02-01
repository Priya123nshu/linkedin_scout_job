'use client'

import { useUser, useAuth } from '@clerk/nextjs'
import { SignInButton, SignOutButton, UserButton } from '@clerk/nextjs'
import { useState, useEffect } from 'react'
import axios from 'axios'
import PersonProfile from './components/PersonProfile'
import CompanyProfile from './components/CompanyProfile'
import CompanyPosts from './components/CompanyPosts'
import JobSearch from './components/JobSearch'
import JobDetails from './components/JobDetails'
import SessionConfig from './components/SessionConfig'

export default function Home() {
  const { isSignedIn, user } = useUser()
  const { getToken } = useAuth()
  const [activeTab, setActiveTab] = useState<'person' | 'company' | 'posts' | 'search' | 'job'>('person')

  // Session management state
  const [needsSession, setNeedsSession] = useState(false)
  const [checkingSession, setCheckingSession] = useState(true)

  const checkSession = async () => {
    try {
      const token = await getToken()
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

      const res = await axios.get(`${apiUrl}/api/health`, {
        headers: { Authorization: token ? `Bearer ${token}` : undefined }
      })

      // If backend says no session, we need one
      if (res.data.has_session === false) {
        setNeedsSession(true)
      } else {
        setNeedsSession(false)
      }
    } catch (e) {
      console.error("Health check failed", e)
      // If health check fails (e.g. backend down), maybe don't block?
      // Or assume no session?
    } finally {
      setCheckingSession(false)
    }
  }

  useEffect(() => {
    if (isSignedIn) {
      checkSession()
    }
  }, [isSignedIn])

  if (!isSignedIn) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
          <h1 className="text-3xl font-bold text-gray-800 mb-4 text-center">
            LinkedIn MCP Client
          </h1>
          <p className="text-gray-600 mb-6 text-center">
            Sign in to access LinkedIn profiles, companies, and job listings
          </p>
          <div className="flex justify-center">
            <SignInButton mode="modal">
              <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors">
                Sign In
              </button>
            </SignInButton>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Session Configuration Modal */}
      {needsSession && (
        <SessionConfig onSessionSet={() => {
          setNeedsSession(false)
          // Optional: Refresh simple browser check
        }} />
      )}

      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">LinkedIn MCP Client</h1>
            <div className="flex items-center gap-4">
              <div className="flex flex-col items-end">
                <span className="text-sm font-medium text-gray-900">{user?.fullName || user?.firstName}</span>
                <span className="text-xs text-gray-500">{user?.primaryEmailAddress?.emailAddress}</span>
              </div>
              <UserButton />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'person', label: 'Person Profile' },
              { id: 'company', label: 'Company Profile' },
              { id: 'posts', label: 'Company Posts' },
              { id: 'search', label: 'Job Search' },
              { id: 'job', label: 'Job Details' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'person' && <PersonProfile />}
        {activeTab === 'company' && <CompanyProfile />}
        {activeTab === 'posts' && <CompanyPosts />}
        {activeTab === 'search' && <JobSearch />}
        {activeTab === 'job' && <JobDetails />}
      </main>
    </div>
  )
}
