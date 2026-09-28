import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getDocument } from '../api'

export default function DocumentDetail() {
  const { id } = useParams()
  const [doc, setDoc] = useState(null)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getDocument(id)
      .then((data) => {
        setDoc(data.document)
        setLogs(data.logs || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="loading"><div className="spinner" /> Loading document...</div>
  if (!doc) return <div className="loading">Document not found.</div>

  return (
    <>
      <div className="page-header">
        <h2>{doc.title}</h2>
      </div>

      <div className="page-body">
        <div className="breadcrumb">
          <Link to="/documents">Documents</Link>
          <span className="breadcrumb-sep">›</span>
          <span className="breadcrumb-current">{doc.title}</span>
        </div>

        <div className="detail-grid">
          <div className="card">
            <div className="card-header">
              <h3>Document Details</h3>
            </div>
            <div className="card-body-flush">
              <table className="detail-table">
                <tbody>
                  <tr><th>Title</th><td>{doc.title}</td></tr>
                  <tr><th>Filename</th><td className="table-mono">{doc.filename}</td></tr>
                  <tr>
                    <th>Status</th>
                    <td>
                      <span className={`badge badge-${doc.status}`}>
                        <span className="badge-dot" />{doc.status}
                      </span>
                    </td>
                  </tr>
                  <tr><th>Pages</th><td>{doc.page_count ?? 'N/A'}</td></tr>
                  <tr><th>Chunks</th><td>{doc.chunk_count ?? 'N/A'}</td></tr>
                  <tr><th>Uploaded By</th><td>{doc.uploaded_by || '—'}</td></tr>
                  <tr>
                    <th>Uploaded At</th>
                    <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                  </tr>
                  <tr><th>RAG Doc ID</th><td>{doc.rag_document_id ?? '—'}</td></tr>
                  {doc.error_message && (
                    <tr>
                      <th>Error</th>
                      <td style={{ color: 'var(--danger)' }}>{doc.error_message}</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Related Activity</h3>
            </div>
            <div className="card-body-flush">
              {logs.length > 0 ? logs.map((log, i) => (
                <div className="activity-item" key={i}>
                  <div className="activity-time">
                    {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <div className="activity-content">
                    <span className={`action-badge action-${log.action}`}>{log.action_display}</span>
                    <div className="activity-detail">{log.detail?.slice(0, 80)}</div>
                  </div>
                </div>
              )) : (
                <div className="table-empty">No activity recorded.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
