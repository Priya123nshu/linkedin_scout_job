'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import axios from 'axios'
import { Search, Loader2, Briefcase, MapPin, Building2, Calendar, ExternalLink } from 'lucide-react'

export default function JobDetails() {
  const { getToken } = useAuth()
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const token = await getToken()
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/job-details`,
        { url },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.data.success) {
        setData(response.data.data)
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch job details')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Get Job Details</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn Job URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.linkedin.com/jobs/view/123456"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Loading...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Get Job Details
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

      {data && (
        <div className="bg-white rounded-lg shadow p-6 space-y-6">
          <div className="border-b pb-4">
            <h3 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
              <Briefcase className="w-6 h-6 text-blue-600" />
              {data.title || 'N/A'}
            </h3>
            <div className="flex items-center gap-4 text-gray-600 mt-2">
              {data.company && (
                <span className="flex items-center gap-1">
                  <Building2 className="w-4 h-4" />
                  {data.company}
                </span>
              )}
              {data.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {data.location}
                </span>
              )}
              {data.posted_date && (
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {data.posted_date}
                </span>
              )}
            </div>
            {data.url && (
              <a
                href={data.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 mt-4 inline-flex items-center gap-1"
              >
                <ExternalLink className="w-4 h-4" />
                View on LinkedIn
              </a>
            )}
          </div>

          {data.description && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Description</h4>
              <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
                {data.description}
              </div>
            </div>
          )}

          {data.requirements && data.requirements.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Requirements</h4>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                {data.requirements.map((req: string, idx: number) => (
                  <li key={idx}>{req}</li>
                ))}
              </ul>
            </div>
          )}

          {data.salary && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-1">Salary</h4>
              <p className="text-gray-700">{data.salary}</p>
            </div>
          )}

          {data.employment_type && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-1">Employment Type</h4>
              <p className="text-gray-700">{data.employment_type}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
