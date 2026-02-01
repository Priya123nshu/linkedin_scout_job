'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import axios from 'axios'
import { Search, Loader2, FileText, Calendar } from 'lucide-react'

export default function CompanyPosts() {
  const { getToken } = useAuth()
  const [url, setUrl] = useState('')
  const [limit, setLimit] = useState(10)
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
        `${process.env.NEXT_PUBLIC_API_URL}/api/company-posts`,
        { url, limit },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.data.success) {
        setData(response.data.data)
      } else {
        setError(response.data.error || 'Failed to fetch company posts')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch company posts')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Get Company Posts</h2>
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
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Limit (number of posts)
            </label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 10)}
              min="1"
              max="50"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
                Get Posts
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

      {data && data.posts && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Found {data.posts.length} post{data.posts.length !== 1 ? 's' : ''}
          </h3>
          {data.posts.map((post: any, idx: number) => (
            <div key={idx} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center gap-2 text-gray-500 mb-3">
                <Calendar className="w-4 h-4" />
                <span className="text-sm">{post.date || 'N/A'}</span>
              </div>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{post.content || 'No content'}</p>
              </div>
              {post.url && (
                <a
                  href={post.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 mt-4 inline-block text-sm"
                >
                  View on LinkedIn →
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
