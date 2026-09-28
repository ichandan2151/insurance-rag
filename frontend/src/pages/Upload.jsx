import { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { uploadDocument } from '../api'

export default function Upload() {
  const [file, setFile] = useState(null)
  const [title, setTitle] = useState('')
  const [dragover, setDragover] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const inputRef = useRef()

  const handleDrop = (e) => {
    e.preventDefault()
    setDragover(false)
    const f = e.dataTransfer.files[0]
    if (f && f.name.toLowerCase().endsWith('.pdf')) {
      setFile(f)
      if (!title) setTitle(f.name.replace('.pdf', '').replace(/_/g, ' '))
    }
  }

  const handleFileChange = (e) => {
    const f = e.target.files[0]
    if (f) {
      setFile(f)
      if (!title) setTitle(f.name.replace('.pdf', '').replace(/_/g, ' '))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file || !title) return
    setUploading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', title)
      const data = await uploadDocument(formData)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const reset = () => {
    setFile(null)
    setTitle('')
    setResult(null)
    setError('')
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  return (
    <>
      <div className="page-header">
        <h2>Upload Policy Document</h2>
        <div className="page-header-sub">Upload insurance policy PDFs for indexing and analysis</div>
      </div>

      <div className="page-body">
        {result ? (
          <div className="upload-success">
            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>✓</div>
            <h3>Document Indexed Successfully</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              <strong>{result.title || result.filename}</strong> — {result.pages} pages, {result.chunks} chunks
            </p>
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <button className="btn btn-primary" onClick={reset}>Upload Another</button>
              <Link to="/query" className="btn btn-secondary">Ask a Question</Link>
            </div>
          </div>
        ) : (
          <div className="upload-grid">
            <div>
              <form onSubmit={handleSubmit}>
                {error && <div className="alert alert-error">{error}</div>}

                <div
                  className={`dropzone ${dragover ? 'dragover' : ''}`}
                  onDragOver={(e) => { e.preventDefault(); setDragover(true) }}
                  onDragLeave={() => setDragover(false)}
                  onDrop={handleDrop}
                  onClick={() => inputRef.current?.click()}
                >
                  <input
                    ref={inputRef}
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                  />
                  <div className="dropzone-icon">📄</div>
                  <div className="dropzone-text">
                    {dragover ? 'Drop your PDF here' : 'Drag & drop a PDF here, or click to browse'}
                  </div>
                  <div className="dropzone-hint">Supports PDF files up to 50 MB</div>
                </div>

                {file && (
                  <div className="file-selected">
                    <span style={{ fontSize: '1.25rem' }}>📎</span>
                    <span className="file-selected-name">{file.name}</span>
                    <span className="file-selected-size">{formatSize(file.size)}</span>
                    <button type="button" className="btn btn-ghost btn-sm" onClick={() => setFile(null)}>✕</button>
                  </div>
                )}

                <div className="form-group" style={{ marginTop: '1.25rem' }}>
                  <label>Document Title</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Homeowners Policy HO-3"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!file || !title || uploading}
                >
                  {uploading ? '⟳ Uploading & Indexing...' : '⬆ Upload & Index'}
                </button>
              </form>
            </div>

            <div>
              <div className="card">
                <div className="card-header">
                  <h3>How it works</h3>
                </div>
                <div className="card-body">
                  <ol className="upload-steps">
                    <li>Upload a PDF insurance policy document</li>
                    <li>Text is extracted from every page using PyMuPDF</li>
                    <li>Content is split into overlapping chunks for context</li>
                    <li>Chunks are embedded and stored in pgvector</li>
                    <li>Ask questions on the <Link to="/query">Query</Link> page with cited answers</li>
                  </ol>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
