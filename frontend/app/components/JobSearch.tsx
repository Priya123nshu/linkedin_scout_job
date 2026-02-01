'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import axios from 'axios'
import { Search, Loader2, Briefcase, MapPin, Clock, ExternalLink } from 'lucide-react'

export default function JobSearch() {
  const { getToken } = useAuth()
  const [keywords, setKeywords] = useState('')
  const [location, setLocation] = useState('')
  const [limit, setLimit] = useState(10)
  const [timePosted, setTimePosted] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const timeOptions = [
    { value: '', label: 'Any time' },
    { value: '1h', label: 'Past hour' },
    { value: '24h', label: 'Past 24 hours' },
    { value: '7d', label: 'Past week' },
    { value: '30d', label: 'Past month' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const token = await getToken()

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await axios.post(
        `${apiUrl}/search`,
        {
          keywords: keywords ? keywords.split(',').map(k => k.trim()).filter(k => k.length > 0) : [],
          location: location || undefined,
          limit: limit || undefined,
          time_posted: timePosted || undefined,
        },
        {
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined,
            'Content-Type': 'application/json',
          },
        }
      )

      if (response.data.status === 'success') {
        setData(response.data)
      }
    } catch (err: any) {
      console.error('Job search error:', err)
      const errorMessage = err.response?.data?.detail ||
        err.response?.data?.message ||
        err.message ||
        'Failed to search jobs'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Search Jobs</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Keywords
            </label>
            <input
              type="text"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="e.g. Python Developer, React (comma separated)"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., San Francisco, CA"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Limit
              </label>
              <input
                type="number"
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value) || 10)}
                min="1"
                max="50"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Posted
              </label>
              <select
                value={timePosted}
                onChange={(e) => setTimePosted(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
              >
                {timeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Search Jobs
              </>
            )}
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {data && data.jobs && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Found {data.jobs.length} job{data.jobs.length !== 1 ? 's' : ''}
          </h3>
          {data.jobs.map((job: any, idx: number) => (
            <div key={idx} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <Briefcase className="w-5 h-5 text-blue-600" />
                    {job.title || 'N/A'}
                  </h4>
                  <p className="text-gray-600 mb-2">{job.company || 'N/A'}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    {job.location && (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {job.location}
                      </span>
                    )}
                    {job.time_posted && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {job.time_posted}
                      </span>
                    )}
                  </div>
                  {job.description && (
                    <p className="text-gray-700 mt-3 line-clamp-2">{job.description}</p>
                  )}
                </div>
                {job.url && (
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-4 text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    <ExternalLink className="w-4 h-4" />
                    View
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
