'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import axios from 'axios'
import { Search, Loader2, Building2, Users, Globe } from 'lucide-react'

export default function CompanyProfile() {
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
        `${process.env.NEXT_PUBLIC_API_URL}/api/company-profile`,
        { url },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.data.success) {
        setData(response.data.data)
      } else {
        setError(response.data.error || 'Failed to fetch company profile')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch company profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 text-gray-900">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Get Company Profile</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn Company URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.linkedin.com/company/companyname/"
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
                Get Company Profile
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
            <h3 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Building2 className="w-6 h-6" />
              {data.name || 'N/A'}
            </h3>
            {data.website && (
              <a
                href={data.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 mt-2 flex items-center gap-1"
              >
                <Globe className="w-4 h-4" />
                {data.website}
              </a>
            )}
          </div>

          {data.description && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">About</h4>
              <p className="text-gray-700">{data.description}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.employees && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-gray-600 mb-1">
                  <Users className="w-5 h-5" />
                  <span className="font-semibold">Employees</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">{data.employees}</p>
              </div>
            )}

            {data.industry && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 text-gray-600 mb-1">
                  <span className="font-semibold">Industry</span>
                </div>
                <p className="text-xl font-bold text-gray-900">{data.industry}</p>
              </div>
            )}
          </div>

          {data.locations && data.locations.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Locations</h4>
              <div className="space-y-2">
                {data.locations.map((loc: string, idx: number) => (
                  <p key={idx} className="text-gray-700">{loc}</p>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
