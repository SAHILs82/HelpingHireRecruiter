import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getLeaderboard, scoreApplication } from '../components/api/scoringAPI';
import { getJobDescription } from '../components/api/jobDescriptionAPI';
import { getApplicationsByJob } from '../components/api/applicationAPI';
import { triggerSkillGapAnalysis, getSkillGapReport } from '../components/api/skillGapAPI';
import { Card, CardContent } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Loader2, ArrowLeft, Trophy, Star, RefreshCw, ChevronRight, Microscope } from 'lucide-react';

export default function ScoringLeaderboardPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [unscoredApps, setUnscoredApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scoringAppId, setScoringAppId] = useState(null);
  const [analyzingAppId, setAnalyzingAppId] = useState(null);
  const [gapScores, setGapScores] = useState({});

  const fetchData = async () => {
    setLoading(true);
    try {
      const [jobData, appsData, leaderData] = await Promise.all([
        getJobDescription(jobId),
        getApplicationsByJob(jobId),
        getLeaderboard(jobId)
      ]);
      setJob(jobData);
      setLeaderboard(leaderData);
      
      const scoredAppIds = leaderData.map(l => l.application_id);
      setUnscoredApps(appsData.filter(a => !scoredAppIds.includes(a.id)));

      // Fetch existing skill gap scores for each leaderboard entry
      const scores = {};
      for (const entry of leaderData) {
        try {
          const report = await getSkillGapReport(entry.application_id);
          scores[entry.application_id] = report.impact_score;
        } catch {
          // No report yet
        }
      }
      setGapScores(scores);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (jobId) {
      fetchData();
    }
  }, [jobId]);

  const handleScore = async (appId) => {
    setScoringAppId(appId);
    try {
      await scoreApplication(appId);
      await fetchData(); // Refresh data
    } catch (err) {
      alert(`Scoring failed: ${err.message}`);
    } finally {
      setScoringAppId(null);
    }
  };

  const handleRunGapAnalysis = async (appId) => {
    setAnalyzingAppId(appId);
    try {
      const result = await triggerSkillGapAnalysis(appId);
      setGapScores(prev => ({ ...prev, [appId]: result.impact_score }));
    } catch (err) {
      alert(`Skill gap analysis failed: ${err.message}`);
    } finally {
      setAnalyzingAppId(null);
    }
  };

  if (loading && !job) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  const getGapBadge = (appId) => {
    if (analyzingAppId === appId) {
      return <Loader2 size={14} className="animate-spin text-primary" />;
    }
    if (gapScores[appId] !== undefined) {
      const score = gapScores[appId];
      const readiness = Math.round((1 - score) * 100);
      const color = readiness >= 80 ? 'bg-green-100 text-green-700 border-green-200' 
                   : readiness >= 50 ? 'bg-yellow-100 text-yellow-700 border-yellow-200' 
                   : 'bg-red-100 text-red-700 border-red-200';
      return (
        <Badge className={`text-[10px] px-2 py-0.5 border ${color} font-bold`}>
          {readiness}%
        </Badge>
      );
    }
    return (
      <Button
        variant="ghost"
        size="sm"
        className="h-7 text-xs text-muted-foreground hover:text-primary gap-1"
        onClick={(e) => { e.stopPropagation(); handleRunGapAnalysis(appId); }}
      >
        <Microscope size={12} /> Analyze
      </Button>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/jobs')}>
          <ArrowLeft size={20} />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Scoring Leaderboard</h1>
          <p className="text-muted-foreground">AI-ranked candidates for {job?.role_title || 'this role'}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <div className="p-6 border-b flex justify-between items-center bg-muted/20">
            <h2 className="text-xl font-semibold flex items-center gap-2"><Trophy className="text-yellow-500" /> Top Candidates</h2>
            <Button variant="outline" size="sm" onClick={fetchData}><RefreshCw size={14} className="mr-2" /> Refresh</Button>
          </div>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16 text-center">Rank</TableHead>
                  <TableHead>Candidate</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Recommendation</TableHead>
                  <TableHead className="text-center">Gap</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leaderboard.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-12 text-muted-foreground">
                      No candidates have been scored yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  leaderboard.map((entry, index) => (
                    <TableRow key={entry.id} className={index === 0 ? "bg-yellow-500/5 hover:bg-yellow-500/10" : ""}>
                      <TableCell className="text-center font-bold">
                        {index === 0 ? <Trophy size={18} className="mx-auto text-yellow-500" /> : `#${index + 1}`}
                      </TableCell>
                      <TableCell>
                        <div className="font-semibold">{entry.candidate_name || 'Unknown Candidate'}</div>
                        <div className="text-xs text-muted-foreground font-mono">{entry.candidate_id.substring(0, 8)}...</div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-lg">{entry.score}</span>
                          <span className="text-muted-foreground text-sm">/ 100</span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-1.5 mt-1 max-w-[100px]">
                          <div className={`h-1.5 rounded-full ${entry.score >= 80 ? 'bg-green-500' : entry.score >= 60 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${entry.score}%` }}></div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={entry.recommendation === 'Strong Hire' ? 'success' : entry.recommendation === 'Hire' ? 'default' : 'secondary'}>
                          {entry.recommendation || 'Pending'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        {getGapBadge(entry.application_id)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" onClick={() => navigate(`/scoring/${entry.application_id}/detail`)}>
                          Details <ChevronRight size={14} />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card className="md:col-span-1 border-dashed bg-muted/10 h-fit">
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold flex items-center gap-2"><Star className="text-primary" /> Unscored Applications</h2>
            <p className="text-sm text-muted-foreground mt-1">Run AI evaluation on these profiles</p>
          </div>
          <CardContent className="p-0">
            {unscoredApps.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground text-sm">
                All candidates have been scored.
              </div>
            ) : (
              <ul className="divide-y">
                {unscoredApps.map(app => (
                  <li key={app.id} className="p-4 flex items-center justify-between hover:bg-muted/30 transition-colors">
                    <div>
                      <div className="font-medium text-sm">{app.candidate_name || 'New Candidate'}</div>
                      <div className="text-[10px] text-muted-foreground font-mono">{app.candidate_email || app.candidate_id.substring(0, 8)}</div>
                    </div>
                    <Button 
                      size="sm" 
                      onClick={() => handleScore(app.id)}
                      disabled={scoringAppId === app.id}
                    >
                      {scoringAppId === app.id ? <Loader2 size={14} className="animate-spin" /> : 'Run AI Score'}
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
