import { useMemo, useState } from 'react'
import './App.css'
import JDGeneratorForm from './components/JDGeneratorForm'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const sampleCandidates = [
  {
    candidate_id: 'c1',
    name: 'Aman Verma',
    email: 'aman@example.com',
    declared_skills: ['Python', 'FastAPI', 'LangChain'],
    cv_text:
      'Experience\nBuilt FastAPI and LangChain RAG systems for hiring workflows.\nSkills\nPython FastAPI LangChain RAG',
  },
  {
    candidate_id: 'c2',
    name: 'Sana Patel',
    email: 'sana@example.com',
    declared_skills: ['Python', 'Django', 'Postgres'],
    cv_text:
      'Experience\nBuilt backend systems and data APIs.\nSkills\nPython Django SQL',
  },
]

function App() {
  const [authMode, setAuthMode] = useState('login')
  const [role, setRole] = useState('recruiter')
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('project8User')
    return saved ? JSON.parse(saved) : null
  })
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [jobId, setJobId] = useState('job-ai-001')
  const [jdText, setJdText] = useState(
    'Junior AI Engineer role with Python, FastAPI, LangChain, RAG, testing, and deployment skills.'
  )
  const [candidateJson, setCandidateJson] = useState(JSON.stringify(sampleCandidates, null, 2))
  const [screeningResult, setScreeningResult] = useState(null)
  const [seekerName, setSeekerName] = useState('Your Name')
  const [seekerCvText, setSeekerCvText] = useState('')
  const [fitResult, setFitResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const topCards = useMemo(() => {
    const results = screeningResult?.results || []
    const shortlisted = results.filter((r) =>
      ['fast_track', 'strong_fit', 'borderline'].includes(r?.decision?.label)
    ).length
    return [
      { label: 'Candidates Processed', value: results.length || 0 },
      { label: 'Shortlisted', value: shortlisted },
      { label: 'Need Human Review', value: results.filter((r) => r?.decision?.label === 'needs_human_review').length },
    ]
  }, [screeningResult])

  const submitAuth = (event) => {
    event.preventDefault()
    if (!email || !password) return
    const newUser = { email, role }
    localStorage.setItem('project8User', JSON.stringify(newUser))
    setUser(newUser)
    setError('')
  }

  const logout = () => {
    localStorage.removeItem('project8User')
    setUser(null)
    setScreeningResult(null)
    setFitResult(null)
  }

  const runRecruiterScreen = async () => {
    try {
      setLoading(true)
      setError('')
      const candidates = JSON.parse(candidateJson)
      const response = await fetch(`${API_BASE_URL}/screen`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId, jd_text: jdText, candidates }),
      })
      if (!response.ok) throw new Error(`Screening failed (${response.status})`)
      setScreeningResult(await response.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const runSeekerFitCheck = async () => {
    try {
      if (seekerCvText.trim().length < 30) {
        setError('Please add more CV details (at least 30 characters).')
        return
      }
      setLoading(true)
      setError('')
      const response = await fetch(`${API_BASE_URL}/screen`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          jd_text: jdText,
          candidates: [{ candidate_id: 'self-check', name: seekerName, cv_text: seekerCvText, declared_skills: [] }],
        }),
      })
      if (!response.ok) throw new Error(`Fit check failed (${response.status})`)
      const data = await response.json()
      setFitResult(data.results?.[0] || null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>Project 08: AI Hiring Screener</h1>
          <p>Deep-agent hiring with recruiter and job seeker workflows.</p>
        </div>
        {user && (
          <div className="topbar-actions">
            <span className="badge">{user.role}</span>
            <button onClick={logout}>Logout</button>
          </div>
        )}
      </header>

      {!user ? (
        <section className="auth-card">
          <div className="auth-switch">
            <button className={authMode === 'login' ? 'active' : ''} onClick={() => setAuthMode('login')}>
              Login
            </button>
            <button className={authMode === 'signup' ? 'active' : ''} onClick={() => setAuthMode('signup')}>
              Signup
            </button>
          </div>
          <form onSubmit={submitAuth}>
            <label>
              Role
              <select value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="recruiter">Recruiter</option>
                <option value="job_seeker">Job Seeker</option>
              </select>
            </label>
            <label>
              Email
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </label>
            <label>
              Password
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="********" />
            </label>
            <button type="submit">{authMode === 'login' ? 'Sign In' : 'Create Account'}</button>
          </form>
          <p className="hint">This demo auth keeps flow simple and low-click while we focus on core hiring logic.</p>
        </section>
      ) : (
        <main className="dashboard">
          <section className="quickbar">
            <div className="quick-item">
              <label>Job ID</label>
              <input value={jobId} onChange={(e) => setJobId(e.target.value)} />
            </div>
            <div className="quick-item expand">
              <label>JD Snapshot</label>
              <input value={jdText} onChange={(e) => setJdText(e.target.value)} />
            </div>
          </section>

          {user.role === 'recruiter' ? (
            <>
              <section className="cards">
                {topCards.map((card) => (
                  <article key={card.label} className="card">
                    <h3>{card.value}</h3>
                    <p>{card.label}</p>
                  </article>
                ))}
              </section>

              <JDGeneratorForm onSubmit={(data) => console.log("Intake saved:", data)} />

              <section className="panel-grid">
                <article className="panel">
                  <h2>One-Click Batch Screening</h2>
                  <p>Paste candidate JSON and run the deep-agent workflow.</p>
                  <textarea value={candidateJson} onChange={(e) => setCandidateJson(e.target.value)} rows={14} />
                  <button onClick={runRecruiterScreen} disabled={loading}>{loading ? 'Running...' : 'Run Screening'}</button>
                </article>

                <article className="panel">
                  <h2>Results</h2>
                  {!screeningResult ? (
                    <p>No results yet.</p>
                  ) : (
                    <div className="result-list">
                      {screeningResult.results.map((item) => (
                        <div key={item.candidate_id} className="result-row">
                          <div>
                            <strong>{item.candidate_id}</strong>
                            <p>{item.decision?.label}</p>
                          </div>
                          <span>Score: {item.decision?.final_score}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </article>
              </section>
            </>
          ) : (
            <section className="panel-grid single">
              <article className="panel">
                <h2>Fit Probability Check</h2>
                <label>
                  Name
                  <input value={seekerName} onChange={(e) => setSeekerName(e.target.value)} />
                </label>
                <label>
                  CV Text
                  <textarea value={seekerCvText} onChange={(e) => setSeekerCvText(e.target.value)} rows={14} />
                </label>
                <button onClick={runSeekerFitCheck} disabled={loading}>{loading ? 'Analyzing...' : 'Check My Fit'}</button>
              </article>

              <article className="panel">
                <h2>Your Report</h2>
                {!fitResult ? (
                  <p>Run fit check to view score, mismatch reasons, and improvement path.</p>
                ) : (
                  <div className="fit-output">
                    <p><strong>Decision:</strong> {fitResult.decision?.label}</p>
                    <p><strong>Score:</strong> {fitResult.decision?.final_score}</p>
                    <h4>Skill Gaps</h4>
                    <pre>{JSON.stringify(fitResult.skill_gap, null, 2)}</pre>
                  </div>
                )}
              </article>
            </section>
          )}

          {error && <p className="error">{error}</p>}
        </main>
      )}

      <footer>
        <small>API: <code>{API_BASE_URL}</code></small>
      </footer>
    </div>
  )
}

export default App
