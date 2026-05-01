import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { listJDIntakes, generateJD, deleteJDIntake } from '../components/api/jdIntakeAPI';
import { Plus, Sparkles, Trash2, Edit2, Loader2, FileText } from 'lucide-react';
import JDGeneratorForm from '../components/JDGeneratorForm';

export default function JDIntakePage() {
  const [intakes, setIntakes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(null); // id of intake being generated
  const [showForm, setShowForm] = useState(false);
  const [editData, setEditData] = useState(null);
  const navigate = useNavigate();

  const fetchIntakes = async () => {
    try {
      setLoading(true);
      const data = await listJDIntakes();
      setIntakes(data);
    } catch (err) {
      console.error('Failed to load intakes', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntakes();
  }, []);

  const handleGenerate = async (id) => {
    try {
      setGenerating(id);
      const res = await generateJD(id);
      // If success, navigate to the newly created job
      if (res.agent_summary && res.agent_summary.includes('ID')) {
         // Extract ID from agent summary: "Successfully validated Pydantic output and saved JD with ID 123..."
         const match = res.agent_summary.match(/ID\s+([0-9a-fA-F-]+)/);
         if (match && match[1]) {
           navigate(`/jobs/${match[1]}`);
         } else {
           fetchIntakes(); // refresh state at least
           alert("JD Generated successfully!");
         }
      }
    } catch (err) {
      alert(`Generation failed: ${err.message}`);
    } finally {
      setGenerating(null);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this intake draft?')) return;
    try {
      await deleteJDIntake(id);
      fetchIntakes();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  if (showForm) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">JD Intake Form</h1>
            <p className="text-muted-foreground">Define role requirements to generate an AI job description.</p>
          </div>
          <Button variant="outline" onClick={() => { setShowForm(false); setEditData(null); }}>
            Cancel
          </Button>
        </div>
        <JDGeneratorForm 
          initialData={editData}
          onSaved={() => {
            setShowForm(false);
            setEditData(null);
            fetchIntakes();
          }} 
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">JD Intakes</h1>
          <p className="text-muted-foreground">Manage your job requisitions and generate Job Descriptions.</p>
        </div>
        <Button onClick={() => setShowForm(true)} className="gap-2">
          <Plus size={16} /> New Intake
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Role Title</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Type</TableHead>
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
              ) : intakes.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                    No intake drafts found. Create one to get started.
                  </TableCell>
                </TableRow>
              ) : (
                intakes.map((intake) => (
                  <TableRow key={intake.id}>
                    <TableCell className="font-medium">
                      {intake.domain || 'Unspecified Role'} 
                      {intake.experience_max ? ` (${intake.experience_min}-${intake.experience_max} yrs)` : ''}
                    </TableCell>
                    <TableCell>{intake.company_name || '-'}</TableCell>
                    <TableCell>{intake.location || '-'}</TableCell>
                    <TableCell>
                      {intake.role_type ? (
                        <Badge variant="secondary" className="capitalize">{intake.role_type.replace('-', ' ')}</Badge>
                      ) : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => { setEditData(intake); setShowForm(true); }}
                        >
                          <Edit2 size={14} className="mr-1" /> Edit
                        </Button>
                        <Button 
                          variant="default" 
                          size="sm"
                          disabled={generating === intake.id}
                          onClick={() => handleGenerate(intake.id)}
                        >
                          {generating === intake.id ? (
                            <><Loader2 size={14} className="mr-1 animate-spin" /> Generating...</>
                          ) : (
                            <><Sparkles size={14} className="mr-1 text-yellow-300" /> Generate JD</>
                          )}
                        </Button>
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="text-destructive hover:bg-destructive/10"
                          onClick={() => handleDelete(intake.id)}
                        >
                          <Trash2 size={14} />
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
