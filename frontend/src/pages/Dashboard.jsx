import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getStats, getDocuments, getAuditLogs } from '../api'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [documents, setDocuments] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getStats(), getDocuments(), getAuditLogs()])
      .then(([s, d, l]) => {
        setStats(s)
        setDocuments(d.documents?.slice(0, 8) || [])
        setLogs(l.logs?.slice(0, 8) || [])
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading"><div className="spinner" /> Loading dashboard...</div>

  return (
    <>
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h2>Dashboard</h2>
            <div className="page-header-sub">Insurance policy document management overview</div>
          </div>
          <div className="page-header-actions">
            <span className={`badge badge-${stats?.rag_status === 'online' ? 'online' : 'offline'}`}>
              <span className="badge-dot" />
              RAG Service {stats?.rag_status || 'unknown'}
            </span>
          </div>
        </div>
      </div>

      <div className="page-body">
        <div className="quick-actions">
          <Link to="/upload" className="btn btn-primary">⬆ Upload Document</Link>
          <Link to="/query" className="btn btn-secondary">⚡ Ask Question</Link>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon blue">📄</div>
            <div>
              <div className="stat-value">{stats?.total_documents ?? 0}</div>
              <div className="stat-label">Total Documents</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon green">✓</div>
            <div>
              <div className="stat-value">{stats?.indexed ?? 0}</div>
              <div className="stat-label">Indexed</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon amber">⟳</div>
            <div>
              <div className="stat-value">{stats?.pending ?? 0}</div>
              <div className="stat-label">Processing</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon red">✕</div>
            <div>
              <div className="stat-value">{stats?.failed ?? 0}</div>
              <div className="stat-label">Failed</div>
            </div>
          </div>
        </div>

        <div className="dashboard-grid">
          <div className="card">
            <div className="card-header">
              <h3>Recent Documents</h3>
              <Link to="/documents" className="btn btn-ghost btn-sm">View All →</Link>
            </div>
            <div className="card-body-flush table-wrap">
              {documents.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Status</th>
                      <th>Pages</th>
                      <th>Uploaded</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.id} className="clickable" onClick={() => window.location.href = `/documents/${doc.id}`}>
                        <td><span className="table-link">{doc.title}</span></td>
                        <td><span className={`badge badge-${doc.status}`}><span className="badge-dot" />{doc.status}</span></td>
                        <td>{doc.page_count ?? '—'}</td>
                        <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="table-empty">No documents yet. <Link to="/upload">Upload your first policy.</Link></div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>Recent Activity</h3>
              <Link to="/audit" className="btn btn-ghost btn-sm">View All →</Link>
            </div>
            <div className="card-body-flush">
              {logs.length > 0 ? logs.map((log, i) => (
                <div className="activity-item" key={i}>
                  <div className="activity-time">{new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                  <div className="activity-content">
                    <span className={`action-badge action-${log.action}`}>{log.action_display}</span>
                    <div className="activity-detail">{log.detail?.slice(0, 60)}</div>
                  </div>
                </div>
              )) : (
                <div className="table-empty">No activity yet.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
