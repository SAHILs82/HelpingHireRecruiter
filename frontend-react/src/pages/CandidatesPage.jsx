import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Loader2, Upload, FileText, X } from 'lucide-react';
import { listJobDescriptions } from '../components/api/jobDescriptionAPI';
import { uploadCV } from '../components/api/cvParsingAPI';
import { getApplicationsByJob } from '../components/api/applicationAPI';

export default function CandidatesPage() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState('');
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Upload state
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const jobsData = await listJobDescriptions();
        setJobs(jobsData);
        if (jobsData.length > 0) {
          setSelectedJob(jobsData[0].id);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchInitialData();
  }, []);

  useEffect(() => {
    const fetchApps = async () => {
      if (!selectedJob) return;
      setLoading(true);
      try {
        const apps = await getApplicationsByJob(selectedJob);
        setApplications(apps);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchApps();
  }, [selectedJob]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !selectedJob) return;
    setUploading(true);
    try {
      await uploadCV(selectedJob, file);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      // Refresh list
      const apps = await getApplicationsByJob(selectedJob);
      setApplications(apps);
    } catch (err) {
      alert(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Candidates</h1>
          <p className="text-muted-foreground">Upload resumes and view applicants for a specific role.</p>
        </div>
        
        <div className="flex items-center gap-2">
          <select 
            value={selectedJob} 
            onChange={(e) => setSelectedJob(e.target.value)}
            className="flex h-10 w-[250px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            <option value="" disabled>Select a Job...</option>
            {jobs.map(j => <option key={j.id} value={j.id}>{j.role_title}</option>)}
          </select>
        </div>
      </div>

      <Card className="border-dashed border-2 bg-muted/20">
        <CardContent className="p-6 flex flex-col items-center justify-center space-y-4">
          <div className="flex flex-col items-center justify-center p-4">
            <Upload className="h-10 w-10 text-muted-foreground mb-4" />
            <h3 className="font-semibold text-lg">Upload Resume</h3>
            <p className="text-sm text-muted-foreground mb-4 text-center max-w-sm">
              Upload a candidate's CV in PDF format. The AI will parse it and add the candidate to the selected job.
            </p>
            <div className="flex items-center gap-2">
              <input 
                type="file" 
                accept=".pdf" 
                className="hidden" 
                ref={fileInputRef}
                onChange={handleFileChange}
              />
              <Button variant="outline" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
                Select PDF
              </Button>
              {file && (
                <div className="flex items-center gap-2 bg-secondary px-3 py-1.5 rounded-md">
                  <FileText size={14} />
                  <span className="text-sm max-w-[150px] truncate">{file.name}</span>
                  <Button variant="ghost" size="icon" className="h-4 w-4 ml-1" onClick={() => setFile(null)}>
                    <X size={12} />
                  </Button>
                </div>
              )}
            </div>
          </div>
          {file && (
             <Button onClick={handleUpload} disabled={uploading || !selectedJob} className="w-full max-w-xs">
                {uploading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin"/> Parsing CV...</> : 'Upload & Parse CV'}
             </Button>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Candidate ID (Temporary View)</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Applied At</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-muted-foreground" />
                  </TableCell>
                </TableRow>
              ) : !selectedJob ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                    Please select a job to view candidates.
                  </TableCell>
                </TableRow>
              ) : applications.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center py-8 text-muted-foreground">
                    No candidates found for this job.
                  </TableCell>
                </TableRow>
              ) : (
                applications.map((app) => (
                  <TableRow key={app.id}>
                    <TableCell className="font-mono text-xs">{app.candidate_id}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">{app.status}</Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(app.applied_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="outline" size="sm" onClick={() => navigate(`/candidates/${app.candidate_id}`)}>
                        View Profile
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
