import { useState } from 'react'

interface Source {
  id: string
  article_num: string
  text: string
  score: number
}

interface ChatResponse {
  query: string
  answer: string
  sources: Source[]
}

// In production, API is served from the same origin
// In development, Vite proxy handles /api -> backend
const API_URL = import.meta.env.DEV ? '/api' : ''

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<ChatResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    setLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), top_k: 3 }),
      })

      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`)
      }

      const data: ChatResponse = await res.json()
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const getScoreClass = (score: number): string => {
    if (score >= 0.8) return 'high'
    if (score >= 0.5) return 'medium'
    return ''
  }

  return (
    <div className="app">
      <header className="header">
        <h1>AI Research Assistant</h1>
        <p>Ask questions about GDPR regulations</p>
      </header>

      <form className="search-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="search-input"
          placeholder="What are the GDPR principles?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="search-btn" disabled={loading || !query.trim()}>
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading">
          <div className="spinner" />
          <span>Searching documents...</span>
        </div>
      )}

      <div className="results">
        {response && !loading && (
          <>
            <div className="answer-card">
              <h2>Answer</h2>
              <p className="answer-text">{response.answer}</p>
            </div>

            {response.sources.length > 0 && (
              <div className="sources-section">
                <h2>Sources ({response.sources.length})</h2>
                <div className="sources-list">
                  {response.sources.map((source) => (
                    <div key={source.id} className="source-card">
                      <div className="source-header">
                        <span className="source-article">{source.article_num}</span>
                        <span className={`source-score ${getScoreClass(source.score)}`}>
                          {(source.score * 100).toFixed(0)}% match
                        </span>
                      </div>
                      <p className="source-text">{source.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {!response && !loading && !error && (
          <div className="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
            </svg>
            <p>Enter a question to search the knowledge base</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
