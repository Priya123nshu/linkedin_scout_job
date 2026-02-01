'use client'

import { useState } from 'react'
import { useAuth } from '@clerk/nextjs'
import axios from 'axios'
import { Key, Loader2, Save } from 'lucide-react'

interface SessionConfigProps {
    onSessionSet: () => void
}

export default function SessionConfig({ onSessionSet }: SessionConfigProps) {
    const { getToken } = useAuth()
    const [liAt, setLiAt] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)

        try {
            const token = await getToken()
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

            await axios.post(
                `${apiUrl}/api/session`,
                { li_at: liAt },
                {
                    headers: {
                        Authorization: token ? `Bearer ${token}` : undefined,
                        'Content-Type': 'application/json',
                    },
                }
            )

            onSessionSet()
        } catch (err: any) {
            console.error('Session setup error:', err)
            setError(err.response?.data?.detail || 'Failed to save session')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                <div className="flex items-center gap-3 mb-6">
                    <div className="p-3 bg-blue-100 rounded-full">
                        <Key className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-gray-900">LinkedIn Authentication</h2>
                        <p className="text-sm text-gray-500">Session cookie required</p>
                    </div>
                </div>

                <p className="text-gray-600 mb-6 text-sm">
                    To use this app, you need to provide your LinkedIn <code>li_at</code> cookie.
                    This is used securely to fetch data and is not stored permanently.
                </p>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            li_at Cookie Value
                        </label>
                        <input
                            type="password"
                            value={liAt}
                            onChange={(e) => setLiAt(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="Enter your li_at cookie..."
                            required
                        />
                    </div>

                    {error && (
                        <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg">
                            {error}
                        </div>
                    )}

                    <div className="flex justify-end gap-3 mt-6">
                        <button
                            type="submit"
                            disabled={loading || !liAt}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Saving...
                                </>
                            ) : (
                                <>
                                    <Save className="w-4 h-4" />
                                    Save Session
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
