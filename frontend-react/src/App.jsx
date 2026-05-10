import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import { authAPI } from './api/authAPI'

// Pages
import JDIntakePage from './pages/JDIntakePage'
import JobListingPage from './pages/JobListingPage'
import JobDescriptionPage from './pages/JobDescriptionPage'
import CandidatesPage from './pages/CandidatesPage'
import CandidateProfilePage from './pages/CandidateProfilePage'
import ScoringLeaderboardPage from './pages/ScoringLeaderboardPage'
import ScoreDetailPage from './pages/ScoreDetailPage'
import JobSeekerDashboard from './pages/JobSeekerDashboard'
import LoginPage from './pages/auth/LoginPage'
import SignupPage from './pages/auth/SignupPage'
import { Button } from './components/ui/button'
import { ToastProvider } from './components/ui/CustomToast'

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('project8User')
    return saved ? JSON.parse(saved) : null
  })
  const [isInitializing, setIsInitializing] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('project8Token')
      if (token && !user) {
        try {
          const userData = await authAPI.getCurrentUser(token)
          setUser(userData)
          localStorage.setItem('project8User', JSON.stringify(userData))
        } catch (err) {
          console.error("Session restoration failed", err)
          localStorage.removeItem('project8Token')
          localStorage.removeItem('project8User')
        }
      }
      setIsInitializing(false)
    }
    initAuth()
  }, [])

  const logout = () => {
    localStorage.removeItem('project8User');
    localStorage.removeItem('project8Token');
    setUser(null);
  };

  if (isInitializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-12 h-12 border-4 border-indigo-600/20 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <ToastProvider>
      <BrowserRouter>
        {!user ? (
          <Routes>
            <Route path="/login" element={<LoginPage onLogin={setUser} />} />
            <Route path="/signup" element={<SignupPage onLogin={setUser} />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        ) : user.role === 'job_seeker' ? (
          <div className="min-h-screen bg-slate-50 flex flex-col">
            <div className="bg-white border-b sticky top-0 z-20 shadow-sm">
              <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-black shadow-lg shadow-indigo-200">HH</div>
                  <span className="font-extrabold text-xl tracking-tight text-slate-900">HelpingHire <span className="text-indigo-600">Seeker</span></span>
                </div>
                <div className="flex items-center gap-6">
                  <div className="hidden sm:flex flex-col items-end">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Logged in as</span>
                    <span className="text-sm text-slate-700 font-bold leading-none">{user.email}</span>
                  </div>
                  <Button 
                    variant="ghost" 
                    className="text-sm font-bold text-slate-600 hover:bg-slate-100 hover:text-red-600 rounded-xl px-5 py-2 transition-all" 
                    onClick={logout}
                  >
                    Logout
                  </Button>
                </div>
              </div>
            </div>
            <main className="flex-1 overflow-auto">
              <JobSeekerDashboard />
            </main>
          </div>
        ) : (
          <Routes>
            <Route element={<AppLayout onLogout={logout} user={user} />}>
              <Route path="/" element={<Navigate to="/jd-intake" replace />} />
              <Route path="/jd-intake" element={<JDIntakePage />} />
              <Route path="/jobs" element={<JobListingPage />} />
              <Route path="/jobs/:id" element={<JobDescriptionPage />} />
              <Route path="/candidates" element={<CandidatesPage />} />
              <Route path="/candidates/:id" element={<CandidateProfilePage />} />
              <Route path="/scoring/:jobId" element={<ScoringLeaderboardPage />} />
              <Route path="/scoring/:applicationId/detail" element={<ScoreDetailPage />} />
              <Route path="*" element={<Navigate to="/jd-intake" replace />} />
            </Route>
          </Routes>
        )}
      </BrowserRouter>
    </ToastProvider>
  )
}

export default App
