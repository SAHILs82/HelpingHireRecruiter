import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'

// Pages
// import DashboardPage from './pages/DashboardPage'
import JDIntakePage from './pages/JDIntakePage'
// import JDIntakeDetailPage from './pages/JDIntakeDetailPage'
import JobListingPage from './pages/JobListingPage'
import JobDescriptionPage from './pages/JobDescriptionPage'
import CandidatesPage from './pages/CandidatesPage'
import CandidateProfilePage from './pages/CandidateProfilePage'
import ScoringLeaderboardPage from './pages/ScoringLeaderboardPage'
import ScoreDetailPage from './pages/ScoreDetailPage'

// Auth Components
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './components/ui/card'
import { Input } from './components/ui/input'
import { Label } from './components/ui/label'
import { Button } from './components/ui/button'

function LoginPage({ onLogin }) {
// ... existing Login component
  const [authMode, setAuthMode] = useState('login')
  const [role, setRole] = useState('recruiter')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const submitAuth = (e) => {
    e.preventDefault()
    if (!email || !password) return
    const newUser = { email, role }
    localStorage.setItem('project8User', JSON.stringify(newUser))
    onLogin(newUser)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center space-y-2">
          <div className="mx-auto w-12 h-12 rounded-lg bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold mb-2">
            HH
          </div>
          <CardTitle className="text-2xl font-bold">HelpingHire AI</CardTitle>
          <CardDescription>
            Deep-agent hiring with recruiter and job seeker workflows
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-2 mb-6 p-1 bg-muted rounded-lg">
            <button
              type="button"
              className={`py-1.5 px-3 text-sm font-medium rounded-md transition-all ${authMode === 'login' ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
              onClick={() => setAuthMode('login')}
            >
              Login
            </button>
            <button
              type="button"
              className={`py-1.5 px-3 text-sm font-medium rounded-md transition-all ${authMode === 'signup' ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
              onClick={() => setAuthMode('signup')}
            >
              Signup
            </button>
          </div>
          <form onSubmit={submitAuth} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <select 
                id="role"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={role} 
                onChange={(e) => setRole(e.target.value)}
              >
                <option value="recruiter">Recruiter</option>
                <option value="job_seeker">Job Seeker</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input 
                id="email"
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="you@example.com" 
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input 
                id="password"
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••••" 
              />
            </div>
            <Button type="submit" className="w-full">
              {authMode === 'login' ? 'Sign In' : 'Create Account'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center text-xs text-muted-foreground">
          This demo auth keeps flow simple while focusing on core logic.
        </CardFooter>
      </Card>
    </div>
  )
}

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('project8User')
    return saved ? JSON.parse(saved) : null
  })

  // Simple placeholder components while we build the pages
  const Placeholder = ({ name }) => (
    <div className="flex h-[60vh] items-center justify-center rounded-xl border border-dashed p-8 text-center animate-in fade-in duration-500">
      <div className="space-y-3">
        <h2 className="text-xl font-semibold text-muted-foreground">{name} Component Coming Soon</h2>
        <p className="text-sm text-muted-foreground/60 max-w-sm mx-auto">
          We are currently building this view with Shadcn UI components and full backend integration.
        </p>
      </div>
    </div>
  )

  if (!user) {
    return <LoginPage onLogin={setUser} />
  }

  // Job Seeker flow (simple for now)
  if (user.role === 'job_seeker') {
    return (
      <div className="min-h-screen bg-slate-50 p-8 flex flex-col items-center">
        <div className="w-full max-w-4xl flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Job Seeker Portal</h1>
          <Button variant="outline" onClick={() => {
            localStorage.removeItem('project8User');
            setUser(null);
          }}>Logout</Button>
        </div>
        <Card className="w-full max-w-4xl p-12">
          <Placeholder name="Job Seeker Fit Check" />
        </Card>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/jd-intake" replace />} />
          
          <Route path="/jd-intake" element={<JDIntakePage />} />
          <Route path="/jd-intake/new" element={<JDIntakePage />} />
          
          <Route path="/jobs" element={<JobListingPage />} />
          <Route path="/jobs/:id" element={<JobDescriptionPage />} />
          
          <Route path="/candidates" element={<CandidatesPage />} />
          <Route path="/candidates/:id" element={<CandidateProfilePage />} />
          
          <Route path="/scoring/:jobId" element={<ScoringLeaderboardPage />} />
          <Route path="/scoring/:applicationId/detail" element={<ScoreDetailPage />} />
          
          <Route path="*" element={<Navigate to="/jd-intake" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
