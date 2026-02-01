'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import axios from 'axios'
import { Search, Loader2, User, Briefcase, GraduationCap, MapPin } from 'lucide-react'

export default function PersonProfile() {
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
        `${process.env.NEXT_PUBLIC_API_URL}/api/person-profile`,
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
        setError(response.data.error || 'Failed to fetch profile')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch profile')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 text-gray-900">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Get Person Profile</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn Profile URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.linkedin.com/in/username/"
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
                Get Profile
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
            <h3 className="text-2xl font-bold text-gray-900">{data.name || 'N/A'}</h3>
            <p className="text-gray-600 mt-1">{data.headline || ''}</p>
            {data.location && (
              <p className="text-gray-500 mt-2 flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                {data.location}
              </p>
            )}
          </div>

          {data.about && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">About</h4>
              <p className="text-gray-700">{data.about}</p>
            </div>
          )}

          {data.experiences && data.experiences.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Briefcase className="w-5 h-5" />
                Experience
              </h4>
              <div className="space-y-4">
                {data.experiences.map((exp: any, idx: number) => (
                  <div key={idx} className="border-l-2 border-blue-500 pl-4">
                    <h5 className="font-semibold text-gray-900">{exp.title || 'N/A'}</h5>
                    <p className="text-gray-600">{exp.company || 'N/A'}</p>
                    {exp.duration && <p className="text-sm text-gray-500">{exp.duration}</p>}
                    {exp.description && <p className="text-gray-700 mt-2">{exp.description}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.educations && data.educations.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <GraduationCap className="w-5 h-5" />
                Education
              </h4>
              <div className="space-y-3">
                {data.educations.map((edu: any, idx: number) => (
                  <div key={idx} className="border-l-2 border-green-500 pl-4">
                    <h5 className="font-semibold text-gray-900">{edu.degree || 'N/A'}</h5>
                    <p className="text-gray-600">{edu.school || 'N/A'}</p>
                    {edu.duration && <p className="text-sm text-gray-500">{edu.duration}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {data.skills && data.skills.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Skills</h4>
              <div className="flex flex-wrap gap-2">
                {data.skills.map((skill: string, idx: number) => (
                  <span
                    key={idx}
                    className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
