import React, { useEffect, useState, useRef } from 'react';
import { listJobDescriptions, getJobDescription } from '../components/api/jobDescriptionAPI';
import { uploadCV } from '../components/api/cvParsingAPI';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Loader2, MapPin, Briefcase, Building, Upload, CheckCircle2, FileText, X } from 'lucide-react';

export default function JobSeekerDashboard() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applying, setApplying] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await listJobDescriptions();
        setJobs(data);
      } catch (err) {
        console.error("Failed to load jobs", err);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, []);

  const fetchJobDetail = async (id) => {
    try {
      const data = await getJobDescription(id);
      setSelectedJob(data);
    } catch (err) {
      console.error("Failed to load job details", err);
    }
  };

  const handleApply = async () => {
    if (!file || !selectedJob) return;
    setApplying(true);
    try {
      await uploadCV(selectedJob.id, file);
      setUploadSuccess(true);
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      setTimeout(() => {
        setUploadSuccess(false);
        setSelectedJob(null);
      }, 3000);
    } catch (err) {
      alert(`Application failed: ${err.message}`);
    } finally {
      setApplying(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-slate-50">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto" />
          <p className="text-muted-foreground animate-pulse font-medium">Finding the best roles for you...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50/50">
      <div className="max-w-6xl mx-auto py-12 px-6">
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl mb-4 bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent">
            Find Your Next Career Move
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Explore AI-generated job roles and apply with a single click. Our AI evaluates your fit instantly.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {jobs.length === 0 ? (
            <div className="col-span-full py-20 text-center bg-white rounded-2xl border border-dashed border-muted-foreground/20">
               <Briefcase size={48} className="mx-auto text-muted-foreground/30 mb-4" />
               <h3 className="text-xl font-semibold text-muted-foreground">No active job listings</h3>
               <p className="text-sm text-muted-foreground/60">Check back later for new opportunities.</p>
            </div>
          ) : (
            jobs.map((job) => (
              <Card key={job.id} className="group hover:shadow-2xl transition-all duration-500 border-primary/5 hover:border-primary/20 flex flex-col bg-white overflow-hidden">
                <CardHeader className="pb-4">
                  <div className="flex justify-between items-start mb-3">
                    <Badge variant="outline" className="capitalize bg-slate-50/50">{job.employment_type || 'Full-time'}</Badge>
                    <Badge className="bg-primary/10 text-primary hover:bg-primary/20 border-none capitalize px-3">{job.level || 'Mid'}</Badge>
                  </div>
                  <CardTitle className="text-2xl group-hover:text-primary transition-colors leading-tight">
                    {job.role_title}
                  </CardTitle>
                  <CardDescription className="flex items-center gap-1.5 mt-2 font-medium">
                    <Building size={16} /> {job.company_name}
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex-1 pb-6">
                  <div className="space-y-3 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2.5">
                      <div className="p-1.5 rounded-full bg-slate-100"><MapPin size={14} className="text-primary" /></div>
                      {job.location || 'Remote'}
                    </div>
                    <div className="flex items-center gap-2.5">
                      <div className="p-1.5 rounded-full bg-slate-100"><Briefcase size={14} className="text-primary" /></div>
                      {job.employment_type || 'Full-time'}
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="pt-0 pb-6 px-6">
                  <Button 
                    className="w-full h-11 text-base font-semibold group-hover:scale-[1.02] transition-all shadow-md hover:shadow-lg bg-primary" 
                    onClick={() => fetchJobDetail(job.id)}
                  >
                    View & Apply
                  </Button>
                </CardFooter>
              </Card>
            ))
          )}
        </div>

        {/* Detail & Apply Overlay */}
        {selectedJob && (
          <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-300">
            <Card className="w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col bg-white border-none">
              <CardHeader className="relative border-b shrink-0 py-8 px-10">
                <Button variant="ghost" size="icon" className="absolute right-6 top-6 rounded-full hover:bg-slate-100" onClick={() => setSelectedJob(null)}>
                  <X size={20} />
                </Button>
                <div className="flex items-center gap-2 mb-4">
                  <Badge className="capitalize px-4 py-1">{selectedJob.level}</Badge>
                  <Badge variant="secondary" className="capitalize px-4 py-1">{selectedJob.employment_type}</Badge>
                </div>
                <CardTitle className="text-4xl font-extrabold tracking-tight mb-2">{selectedJob.role_title}</CardTitle>
                <CardDescription className="text-xl flex items-center gap-2 font-medium text-slate-600">
                  <Building size={20} /> {selectedJob.company_name} • <MapPin size={20} /> {selectedJob.location}
                </CardDescription>
              </CardHeader>
              
              <CardContent className="flex-1 overflow-y-auto py-10 px-10 space-y-10 custom-scrollbar">
                <div className="prose prose-slate max-w-none">
                  <h3 className="text-2xl font-bold border-b-4 border-primary/20 pb-2 mb-6 text-slate-800 inline-block">Job Description</h3>
                  <div className="whitespace-pre-wrap text-slate-600 leading-relaxed text-lg">
                    {selectedJob.jd_text || "No detailed description available."}
                  </div>
                </div>

                {!uploadSuccess ? (
                  <div className="bg-primary/5 p-8 rounded-2xl border-2 border-dashed border-primary/20 space-y-6">
                    <div className="space-y-2">
                      <h3 className="text-2xl font-bold flex items-center gap-3 text-slate-800">
                        <Upload size={28} className="text-primary" /> Apply Now
                      </h3>
                      <p className="text-slate-600 font-medium">
                        Upload your resume (PDF) and our AI will automatically parse your experience and evaluate your fit for this role.
                      </p>
                    </div>
                    
                    <div className="flex flex-col items-center gap-6 pt-4">
                      <input 
                        type="file" 
                        accept=".pdf" 
                        className="hidden" 
                        ref={fileInputRef}
                        onChange={handleFileChange}
                      />
                      {!file ? (
                        <Button 
                          variant="outline" 
                          className="w-full max-w-md h-16 text-lg border-2 border-primary/20 hover:border-primary/40 hover:bg-white transition-all bg-white" 
                          onClick={() => fileInputRef.current?.click()}
                        >
                          Choose Resume (PDF)
                        </Button>
                      ) : (
                        <div className="flex items-center gap-4 bg-white p-4 rounded-xl border-2 border-primary/20 w-full max-w-md shadow-sm">
                          <div className="p-2 bg-primary/10 rounded-lg text-primary"><FileText size={24} /></div>
                          <span className="flex-1 font-bold text-slate-700 truncate">{file.name}</span>
                          <Button variant="ghost" size="icon" className="h-10 w-10 rounded-full hover:bg-red-50 hover:text-red-500" onClick={() => setFile(null)}>
                            <X size={20} />
                          </Button>
                        </div>
                      )}

                      <Button 
                        className="w-full max-w-md h-16 text-xl font-bold shadow-xl hover:shadow-2xl transition-all" 
                        disabled={!file || applying} 
                        onClick={handleApply}
                      >
                        {applying ? <><Loader2 className="mr-3 h-6 w-6 animate-spin" /> Processing...</> : 'Submit Application'}
                      </Button>
                      <p className="text-xs text-muted-foreground italic text-center">Your data is processed by our secure AI agents.</p>
                    </div>
                  </div>
                ) : (
                  <div className="bg-green-500/10 border-4 border-green-500/20 p-16 rounded-3xl text-center space-y-6 animate-in zoom-in duration-500">
                    <div className="mx-auto w-24 h-24 bg-green-500 rounded-full flex items-center justify-center text-white mb-6 shadow-lg shadow-green-500/30">
                      <CheckCircle2 size={48} />
                    </div>
                    <h3 className="text-4xl font-black text-green-700">Success!</h3>
                    <p className="text-xl text-green-800/80 font-medium max-w-md mx-auto">
                      Your application has been received. Our AI is now mapping your profile to this role.
                    </p>
                  </div>
                )}
              </CardContent>
              
              <CardFooter className="justify-center border-t py-6 bg-slate-50/50 shrink-0">
                 <p className="text-sm font-semibold text-slate-400">Powered by HelpingHire Deep Agent Technology</p>
              </CardFooter>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
