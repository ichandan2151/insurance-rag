import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../App'
import { logout } from '../api'

export default function Layout({ children }) {
  const { user, setUser } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await logout()
    } catch (e) { /* ignore */ }
    setUser(null)
    navigate('/login')
  }

  const initial = user?.username?.charAt(0).toUpperCase() || '?'

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>Insurance<span>RAG</span></h1>
          <p>Policy Analysis Platform</p>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section">
            <div className="nav-section-label">Main</div>
            <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <span className="nav-icon">⊞</span> Dashboard
            </NavLink>
            <NavLink to="/query" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <span className="nav-icon">⚡</span> Ask Question
            </NavLink>
          </div>

          <div className="nav-section">
            <div className="nav-section-label">Management</div>
            <NavLink to="/upload" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <span className="nav-icon">⬆</span> Upload
            </NavLink>
            <NavLink to="/documents" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <span className="nav-icon">◧</span> Documents
            </NavLink>
          </div>

          <div className="nav-section">
            <div className="nav-section-label">Governance</div>
            <NavLink to="/audit" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <span className="nav-icon">☰</span> Audit Log
            </NavLink>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="user-avatar">{initial}</div>
            <div className="user-info">
              <div className="user-name">{user?.username}</div>
              <div className="user-role">Administrator</div>
            </div>
            <button className="sidebar-logout" onClick={handleLogout} title="Logout">
              ⏻
            </button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        {children}
      </main>
    </div>
  )
}
