import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getDocuments } from '../api'

export default function Documents() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getDocuments()
      .then((data) => setDocuments(data.documents || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading"><div className="spinner" /> Loading documents...</div>

  return (
    <>
      <div className="page-header">
        <div className="page-header-row">
          <div>
            <h2>Policy Documents</h2>
            <div className="page-header-sub">{documents.length} document{documents.length !== 1 ? 's' : ''} uploaded</div>
          </div>
          <Link to="/upload" className="btn btn-primary btn-sm">⬆ Upload New</Link>
        </div>
      </div>

      <div className="page-body">
        <div className="card">
          <div className="card-body-flush table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Filename</th>
                  <th>Status</th>
                  <th>Pages</th>
                  <th>Chunks</th>
                  <th>Uploaded By</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {documents.length > 0 ? documents.map((doc) => (
                  <tr key={doc.id} className="clickable" onClick={() => navigate(`/documents/${doc.id}`)}>
                    <td><span className="table-link">{doc.title}</span></td>
                    <td className="table-mono">{doc.filename}</td>
                    <td>
                      <span className={`badge badge-${doc.status}`}>
                        <span className="badge-dot" />{doc.status}
                      </span>
                    </td>
                    <td>{doc.page_count ?? '—'}</td>
                    <td>{doc.chunk_count ?? '—'}</td>
                    <td>{doc.uploaded_by || '—'}</td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {new Date(doc.uploaded_at).toLocaleDateString('en-US', {
                        month: 'short', day: 'numeric', year: 'numeric'
                      })}
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={7}>
                      <div className="table-empty">
                        No documents uploaded yet. <Link to="/upload">Upload your first policy.</Link>
                      </div>
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
