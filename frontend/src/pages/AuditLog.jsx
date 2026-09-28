import { useState, useEffect } from 'react'
import { getAuditLogs } from '../api'

export default function AuditLog() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAuditLogs()
      .then((data) => setLogs(data.logs || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading"><div className="spinner" /> Loading audit log...</div>

  return (
    <>
      <div className="page-header">
        <h2>Audit Log</h2>
        <div className="page-header-sub">AI governance trail — all document uploads, queries, and system events</div>
      </div>

      <div className="page-body">
        <div className="card">
          <div className="card-body-flush table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Detail</th>
                  <th>IP Address</th>
                </tr>
              </thead>
              <tbody>
                {logs.length > 0 ? logs.map((log, i) => (
                  <tr key={i}>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td>{log.user || '—'}</td>
                    <td>
                      <span className={`action-badge action-${log.action}`}>
                        {log.action_display}
                      </span>
                    </td>
                    <td style={{ maxWidth: '500px' }}>
                      <div>{log.detail?.slice(0, 100)}</div>
                      {log.query_text && (
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                          <strong>Q:</strong> {log.query_text?.slice(0, 120)}
                        </div>
                      )}
                      {log.answer_text && (
                        <div style={{
                          fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.35rem',
                          background: 'var(--bg-light)', padding: '0.5rem 0.75rem', borderRadius: '6px',
                          borderLeft: '3px solid var(--primary)', lineHeight: '1.5'
                        }}>
                          <strong>A:</strong> {log.answer_text?.slice(0, 300)}{log.answer_text?.length > 300 ? '...' : ''}
                        </div>
                      )}
                      {log.source_count > 0 && (
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                          {log.source_count} source{log.source_count !== 1 ? 's' : ''} · {log.response_model}
                        </div>
                      )}
                    </td>
                    <td className="table-mono">{log.ip_address || '—'}</td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={5}>
                      <div className="table-empty">No audit entries yet.</div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}
