import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getCandidate } from '../components/api/candidateAPI';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Loader2, ArrowLeft, Mail, Phone, ExternalLink, GraduationCap, Briefcase, Award } from 'lucide-react';

export default function CandidateProfilePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCandidate = async () => {
      try {
        const data = await getCandidate(id);
        setCandidate(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchCandidate();
  }, [id]);

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  if (error || !candidate) {
    return (
      <div className="space-y-4 text-center py-12">
        <h2 className="text-2xl font-bold text-destructive">Candidate Not Found</h2>
        <p className="text-muted-foreground">{error}</p>
        <Button onClick={() => navigate('/candidates')} variant="outline">Back to Candidates</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/candidates')}>
          <ArrowLeft size={20} />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{candidate.full_name || 'Unknown Candidate'}</h1>
            {candidate.seniority_level && <Badge variant="secondary" className="capitalize">{candidate.seniority_level}</Badge>}
          </div>
          <p className="text-muted-foreground">{candidate.primary_domain || 'General Profiling'}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-1 h-fit">
          <CardHeader>
            <CardTitle className="text-lg">Contact & Links</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            {candidate.email && (
              <div className="flex items-center gap-2"><Mail size={16} className="text-muted-foreground"/> {candidate.email}</div>
            )}
            {candidate.phone && (
              <div className="flex items-center gap-2"><Phone size={16} className="text-muted-foreground"/> {candidate.phone}</div>
            )}
            {candidate.linkedin_url && (
              <div className="flex items-center gap-2"><ExternalLink size={16} className="text-muted-foreground"/> <a href={candidate.linkedin_url} target="_blank" rel="noreferrer" className="text-primary hover:underline">LinkedIn</a></div>
            )}
            {candidate.github_url && (
              <div className="flex items-center gap-2"><ExternalLink size={16} className="text-muted-foreground"/> <a href={candidate.github_url} target="_blank" rel="noreferrer" className="text-primary hover:underline">GitHub</a></div>
            )}
            {candidate.portfolio_url && (
              <div className="flex items-center gap-2"><ExternalLink size={16} className="text-muted-foreground"/> <a href={candidate.portfolio_url} target="_blank" rel="noreferrer" className="text-primary hover:underline">Portfolio</a></div>
            )}

            <div className="pt-4 border-t mt-4">
              <span className="text-xs text-muted-foreground block mb-1">Total Experience</span>
              <div className="font-semibold text-lg">{candidate.total_experience || 0} Years</div>
            </div>

            {candidate.confidence_score != null && (
              <div className="pt-4 border-t mt-4">
                <span className="text-xs text-muted-foreground block mb-1">Extraction Confidence</span>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full" style={{ width: `${candidate.confidence_score * 100}%` }}></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="md:col-span-2 space-y-6">
          {candidate.highlights && candidate.highlights.length > 0 && (
            <Card className="border-primary/50 bg-primary/5">
              <CardContent className="p-4">
                <h4 className="font-semibold mb-2 flex items-center gap-2"><Award size={16} className="text-primary" /> Key Highlights</h4>
                <ul className="list-disc pl-5 space-y-1 text-sm">
                  {candidate.highlights.map((h, i) => <li key={i}>{h}</li>)}
                </ul>
              </CardContent>
            </Card>
          )}

          {candidate.skills && Object.keys(candidate.skills).length > 0 && (
            <Card>
              <CardHeader><CardTitle>Skills</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {Object.entries(candidate.skills).map(([category, skills]) => (
                  <div key={category}>
                    <h5 className="text-sm font-medium text-muted-foreground capitalize mb-2">{category.replace('_', ' ')}</h5>
                    <div className="flex flex-wrap gap-2">
                      {skills.map((s, i) => <Badge key={i} variant="secondary">{s}</Badge>)}
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {candidate.work_experience && candidate.work_experience.length > 0 && (
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><Briefcase size={20}/> Experience</CardTitle></CardHeader>
              <CardContent className="space-y-6">
                {candidate.work_experience.map((exp, i) => (
                  <div key={i} className="relative pl-4 border-l-2 border-muted">
                    <div className="absolute w-2 h-2 bg-primary rounded-full -left-[5px] top-2"></div>
                    <h4 className="font-semibold">{exp.role || exp.title}</h4>
                    <p className="text-sm text-muted-foreground">{exp.company} {exp.duration ? `| ${exp.duration}` : ''}</p>
                    {exp.description && <p className="text-sm mt-2 whitespace-pre-wrap">{exp.description}</p>}
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {candidate.education && candidate.education.length > 0 && (
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2"><GraduationCap size={20}/> Education</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {candidate.education.map((edu, i) => (
                  <div key={i}>
                    <h4 className="font-semibold">{edu.degree} {edu.field ? `in ${edu.field}` : ''}</h4>
                    <p className="text-sm text-muted-foreground">{edu.institution} {edu.end_year ? `| ${edu.start_year || ''} - ${edu.end_year}` : ''}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
          
          <Card>
             <CardHeader><CardTitle>Raw Extracted Text</CardTitle></CardHeader>
             <CardContent>
                <div className="max-h-96 overflow-y-auto bg-muted p-4 rounded-md">
                   <pre className="text-xs whitespace-pre-wrap font-sans">{candidate.cv_text}</pre>
                </div>
             </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
