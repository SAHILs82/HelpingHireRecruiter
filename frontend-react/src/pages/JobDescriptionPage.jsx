import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getJobDescription } from '../components/api/jobDescriptionAPI';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Loader2, ArrowLeft, Building, MapPin, Briefcase, IndianRupee, Clock, Users } from 'lucide-react';

export default function JobDescriptionPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const data = await getJobDescription(id);
        setJob(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchJob();
  }, [id]);

  if (loading) {
    return <div className="flex h-[50vh] items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  if (error || !job) {
    return (
      <div className="space-y-4 text-center py-12">
        <h2 className="text-2xl font-bold text-destructive">Job Description Not Found</h2>
        <p className="text-muted-foreground">{error}</p>
        <Button onClick={() => navigate('/jobs')} variant="outline">Back to Jobs</Button>
      </div>
    );
  }

  const rubric = job.structured_output;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/jobs')}>
          <ArrowLeft size={20} />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">{job.role_title || 'Untitled Role'}</h1>
            <Badge variant="secondary" className="capitalize">{job.status}</Badge>
          </div>
          <p className="text-muted-foreground">AI-Generated Job Description</p>
        </div>
        <Button onClick={() => navigate(`/scoring/${job.id}`)}>
          <Users size={16} className="mr-2" /> View Candidates
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="md:col-span-1 h-fit">
          <CardHeader>
            <CardTitle className="text-lg">Role Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            {job.company_name && (
              <div className="flex items-center gap-2"><Building size={16} className="text-muted-foreground"/> {job.company_name}</div>
            )}
            {job.location && (
              <div className="flex items-center gap-2"><MapPin size={16} className="text-muted-foreground"/> {job.location}</div>
            )}
            {job.employment_type && (
              <div className="flex items-center gap-2"><Briefcase size={16} className="text-muted-foreground"/> <span className="capitalize">{job.employment_type}</span></div>
            )}
            {job.experience_level != null && (
              <div className="flex items-center gap-2"><Clock size={16} className="text-muted-foreground"/> {job.experience_level}+ years exp</div>
            )}
            {job.salary_range && (
              <div className="flex items-center gap-2"><IndianRupee size={16} className="text-muted-foreground"/> ₹{job.salary_range} LPA</div>
            )}
            {job.confidence_score != null && (
              <div className="pt-4 border-t mt-4">
                <span className="text-xs text-muted-foreground block mb-1">AI Confidence Score</span>
                <div className="w-full bg-secondary rounded-full h-2">
                  <div className="bg-primary h-2 rounded-full" style={{ width: `${job.confidence_score * 100}%` }}></div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="md:col-span-3 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Job Description</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none dark:prose-invert">
                {/* The JD text is usually markdown, but we'll render it as text preserving newlines for now */}
                <pre className="whitespace-pre-wrap font-sans text-sm text-foreground/90">{job.jd_text}</pre>
              </div>
            </CardContent>
          </Card>

          {rubric && (
            <Card>
              <CardHeader>
                <CardTitle>Evaluation Rubric</CardTitle>
                <CardDescription>AI uses this structured data to automatically score CVs.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-semibold mb-2">Must-Have Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {rubric.must_have_skills?.map((skill, i) => (
                      <Badge key={i} variant="default">{skill}</Badge>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Nice-to-Have Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {rubric.nice_to_have_skills?.map((skill, i) => (
                      <Badge key={i} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">Weighting Breakdown</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(rubric.weighting || {}).map(([key, value]) => (
                      <div key={key} className="bg-muted p-3 rounded-lg text-center">
                        <div className="text-2xl font-bold text-primary">{value}%</div>
                        <div className="text-xs text-muted-foreground uppercase tracking-wider">{key}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
