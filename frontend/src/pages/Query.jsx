import { useState } from 'react'
import { queryRAG } from '../api'

export default function Query() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const data = await queryRAG(question.trim())
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <>
      <div className="page-header">
        <h2>Ask a Question</h2>
        <div className="page-header-sub">Query your indexed insurance policies with AI-powered analysis</div>
      </div>

      <div className="page-body">
        <div className="query-container">
          <div className="query-input-card">
            <form onSubmit={handleSubmit}>
              <div className="query-input-wrap">
                <textarea
                  className="query-textarea"
                  placeholder="Ask about coverage limits, exclusions, deductibles, or any policy detail..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={handleKeyDown}
                  rows={3}
                />
                <button
                  type="submit"
                  className="query-submit"
                  disabled={loading || !question.trim()}
                  title="Send query"
                >
                  {loading ? '⟳' : '→'}
                </button>
              </div>
            </form>
          </div>

          {error && <div className="alert alert-error">{error}</div>}

          {loading && (
            <div className="loading">
              <div className="spinner" />
              <span>Searching policies and generating answer<span className="loading-dots"></span></span>
            </div>
          )}

          {result && !loading && (
            <>
              <div className="answer-card">
                <div className="answer-header">
                  <h3>Answer</h3>
                  {result.model && <span className="model-badge">{result.model}</span>}
                </div>
                <div className="answer-body">{result.answer}</div>
              </div>

              {result.sources?.length > 0 && (
                <div className="card">
                  <div className="card-header">
                    <h3>Sources ({result.sources.length})</h3>
                  </div>
                  <div className="card-body">
                    <div className="sources-grid">
                      {result.sources.map((src, i) => (
                        <div className="source-card" key={i}>
                          <div className="source-header">
                            <span className="source-doc">{src.title || src.filename}</span>
                            <span className="source-page">Page {src.page_number}</span>
                          </div>
                          <div className="source-similarity">
                            <span>{(src.similarity * 100).toFixed(0)}% match</span>
                            <div className="similarity-bar">
                              <div className="similarity-fill" style={{ width: `${src.similarity * 100}%` }} />
                            </div>
                          </div>
                          {src.excerpt && (
                            <div className="source-excerpt">{src.excerpt}</div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {!result && !loading && !error && (
            <div className="query-empty">
              <div className="query-empty-icon">🔍</div>
              <h3>Ask anything about your insurance policies</h3>
              <p>
                Try questions like "What is the deductible for collision coverage?" or
                "Is flood damage covered under the homeowners policy?"
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  )
}
