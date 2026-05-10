import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getApplicationScoreDetail } from '../components/api/scoringAPI';
import { getSkillGapReport, triggerSkillGapAnalysis } from '../components/api/skillGapAPI';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Loader2, ArrowLeft, CheckCircle2, XCircle, AlertCircle, TrendingUp, Microscope, Sparkles } from 'lucide-react';
import SkillGapPanel from '../components/SkillGapPanel';

export default function ScoreDetailPage() {
  const { applicationId } = useParams();
  const navigate = useNavigate();
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Skill gap state
  const [skillGapReport, setSkillGapReport] = useState(null);
  const [skillGapLoading, setSkillGapLoading] = useState(false);
  const [skillGapError, setSkillGapError] = useState(null);
  const [runningAnalysis, setRunningAnalysis] = useState(false);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const data = await getApplicationScoreDetail(applicationId);
        setDetail(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [applicationId]);

  // Try to load existing skill gap report
  useEffect(() => {
    const fetchReport = async () => {
      try {
        const report = await getSkillGapReport(applicationId);
        setSkillGapReport(report);
      } catch {
        // 404 = no report yet, that's fine
      }
    };
    fetchReport();
  }, [applicationId]);

  const handleRunAnalysis = async () => {
    setRunningAnalysis(true);
    setSkillGapError(null);
    try {
      await triggerSkillGapAnalysis(applicationId);
      // After triggering, fetch the report
      const report = await getSkillGapReport(applicationId);
      setSkillGapReport(report);
    } catch (err) {
      setSkillGapError(err.message);
    } finally {
      setRunningAnalysis(false);
    }
  };

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  if (error || !detail) {
    return (
      <div className="space-y-4 text-center py-12">
        <h2 className="text-2xl font-bold text-destructive">Score Detail Not Found</h2>
        <p className="text-muted-foreground">{error}</p>
        <Button onClick={() => navigate(-1)} variant="outline">Go Back</Button>
      </div>
    );
  }

  // Determine color based on score
  const scoreColor = detail.score >= 80 ? 'text-green-500' : detail.score >= 60 ? 'text-yellow-500' : 'text-red-500';
  const ScoreBadgeVariant = detail.recommendation === 'Strong Hire' ? 'success' : detail.recommendation === 'Hire' ? 'default' : 'destructive';

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4 mb-8">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft size={20} />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">Evaluation Report</h1>
          <p className="text-muted-foreground">Detailed breakdown of candidate's fit for the role</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1 h-fit text-center overflow-hidden">
          <div className="bg-muted py-8 px-4 flex flex-col items-center justify-center">
            <div className="text-sm font-medium text-muted-foreground mb-2 uppercase tracking-wider">Overall Match</div>
            <div className={`text-7xl font-black ${scoreColor} tracking-tighter mb-4`}>
              {detail.score}
            </div>
            <Badge variant={ScoreBadgeVariant} className="text-lg px-4 py-1.5">{detail.recommendation}</Badge>
          </div>
          <CardContent className="p-6">
             <div className="space-y-4">
               <h4 className="font-semibold text-left border-b pb-2">Score Breakdown</h4>
               {detail.breakdown && Object.entries(detail.breakdown).map(([category, score]) => (
                 <div key={category} className="flex flex-col gap-1 text-sm text-left">
                   <div className="flex justify-between items-center">
                     <span className="capitalize text-muted-foreground">{category.replace('_', ' ')}</span>
                     <span className="font-semibold">{score}/100</span>
                   </div>
                   <div className="w-full bg-secondary rounded-full h-1.5">
                     <div className="bg-primary h-1.5 rounded-full" style={{ width: `${score}%` }}></div>
                   </div>
                 </div>
               ))}
             </div>
          </CardContent>
        </Card>

        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><TrendingUp size={20} className="text-primary"/> AI Assessment Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-foreground leading-relaxed">
                {detail.agent_summary}
              </p>
            </CardContent>
          </Card>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <Card className="border-green-500/20 bg-green-500/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2 text-green-700 dark:text-green-400">
                  <CheckCircle2 size={18} /> Strengths
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {detail.strengths?.map((str, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <span className="text-green-500 mt-0.5">•</span>
                      <span>{str}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card className="border-red-500/20 bg-red-500/5">
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2 text-red-700 dark:text-red-400">
                  <AlertCircle size={18} /> Weaknesses
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {detail.weaknesses?.map((wk, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <span className="text-red-500 mt-0.5">•</span>
                      <span>{wk}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>

          {detail.missing_requirements && detail.missing_requirements.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2">
                  <XCircle size={18} className="text-destructive" /> Missing Core Requirements
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {detail.missing_requirements.map((req, i) => (
                    <Badge key={i} variant="outline" className="border-destructive/50 text-destructive bg-destructive/10">
                      {req}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* ── Skill Gap Analysis Section ── */}
      <div className="border-t pt-8 mt-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <Microscope size={24} className="text-primary" />
              Deep Skill Gap Analysis
            </h2>
            <p className="text-muted-foreground text-sm mt-1">
              AI-powered forensic audit using market research & repository scanning
            </p>
          </div>
          {!skillGapReport && (
            <Button
              onClick={handleRunAnalysis}
              disabled={runningAnalysis}
              className="gap-2 shadow-lg hover:shadow-xl transition-all"
              size="lg"
            >
              {runningAnalysis ? (
                <><Loader2 size={16} className="animate-spin" /> Analyzing...</>
              ) : (
                <><Sparkles size={16} /> Run Analysis</>
              )}
            </Button>
          )}
          {skillGapReport && (
            <Button
              onClick={handleRunAnalysis}
              disabled={runningAnalysis}
              variant="outline"
              className="gap-2"
              size="sm"
            >
              {runningAnalysis ? (
                <><Loader2 size={14} className="animate-spin" /> Re-analyzing...</>
              ) : (
                'Re-run Analysis'
              )}
            </Button>
          )}
        </div>

        {skillGapError && (
          <Card className="border-destructive/30 bg-destructive/5 mb-4">
            <CardContent className="p-4 text-sm text-destructive">
              Analysis failed: {skillGapError}
            </CardContent>
          </Card>
        )}

        {runningAnalysis && !skillGapReport && (
          <Card className="border-primary/20 bg-primary/[0.03]">
            <CardContent className="p-12 text-center space-y-4">
              <div className="relative mx-auto w-16 h-16">
                <Loader2 className="w-16 h-16 animate-spin text-primary/30" />
                <Microscope className="w-6 h-6 text-primary absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Deep analysis in progress...</p>
                <p className="text-sm text-muted-foreground mt-1">Searching market trends, scanning repos, and auditing skills. This may take 15-30 seconds.</p>
              </div>
            </CardContent>
          </Card>
        )}

        {skillGapReport && (
          <SkillGapPanel report={skillGapReport} variant="recruiter" />
        )}
      </div>
    </div>
  );
}
