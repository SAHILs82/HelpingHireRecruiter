import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listJobDescriptions } from '../components/api/jobDescriptionAPI';
import { Card, CardContent } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Loader2, ExternalLink, Users } from 'lucide-react';

export default function JobListingPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Job Listings</h1>
        <p className="text-muted-foreground">View all AI-generated job descriptions and manage candidates.</p>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Role Title</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Level</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin mx-auto text-muted-foreground" />
                  </TableCell>
                </TableRow>
              ) : jobs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                    No job descriptions found. Generate one from the JD Intake page.
                  </TableCell>
                </TableRow>
              ) : (
                jobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell className="font-medium text-primary hover:underline cursor-pointer" onClick={() => navigate(`/jobs/${job.id}`)}>
                      {job.role_title || 'Untitled Role'}
                    </TableCell>
                    <TableCell>{job.company_name || '-'}</TableCell>
                    <TableCell>{job.location || '-'}</TableCell>
                    <TableCell>
                      {job.level ? <Badge variant="outline" className="capitalize">{job.level}</Badge> : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" size="sm" onClick={() => navigate(`/jobs/${job.id}`)}>
                          <ExternalLink size={14} className="mr-1" /> View JD
                        </Button>
                        <Button variant="default" size="sm" onClick={() => navigate(`/scoring/${job.id}`)}>
                          <Users size={14} className="mr-1" /> Candidates
                        </Button>
                      </div>
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
