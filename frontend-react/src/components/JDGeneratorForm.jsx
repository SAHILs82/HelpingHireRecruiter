import { useState, useEffect } from 'react';
import { createJDIntake, updateJDIntake } from './api/jdIntakeAPI';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Loader2 } from 'lucide-react';

const ROLE_TYPES = [
  { value: 'full-time', label: 'Full-time' },
  { value: 'part-time', label: 'Part-time' },
  { value: 'contract', label: 'Contract' },
  { value: 'intern', label: 'Intern' },
  { value: 'freelance', label: 'Freelance' }
];

const EDU_LEVELS = [
  { value: 'any', label: 'Any' },
  { value: 'diploma', label: 'Diploma' },
  { value: 'bachelors', label: 'Bachelors' },
  { value: 'masters', label: 'Masters' },
  { value: 'phd', label: 'PhD' }
];

const DEFAULT_FORM_STATE = {
  company_name: '',
  salary_min: '',
  salary_max: '',
  experience_min: '',
  experience_max: '',
  domain: '',
  role_type: 'full-time',
  preferred_education: 'bachelors',
  location: '',
  description: ''
};

export default function JDGeneratorForm({ initialData, onSaved }) {
  const [formData, setFormData] = useState(DEFAULT_FORM_STATE);
  const [intakeId, setIntakeId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initialData) {
      setFormData({
        company_name: initialData.company_name || '',
        salary_min: initialData.salary_min || '',
        salary_max: initialData.salary_max || '',
        experience_min: initialData.experience_min || '',
        experience_max: initialData.experience_max || '',
        domain: initialData.domain || '',
        role_type: initialData.role_type || 'full-time',
        preferred_education: initialData.preferred_education || 'bachelors',
        location: initialData.location || '',
        description: initialData.description || ''
      });
      setIntakeId(initialData.id);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const payload = {
      ...formData,
      salary_min: formData.salary_min ? Number(formData.salary_min) : null,
      salary_max: formData.salary_max ? Number(formData.salary_max) : null,
      experience_min: formData.experience_min ? Number(formData.experience_min) : null,
      experience_max: formData.experience_max ? Number(formData.experience_max) : null,
    };
    
    try {
      let result;
      if (intakeId) {
        result = await updateJDIntake(intakeId, payload);
      } else {
        result = await createJDIntake(payload);
      }
      
      if (onSaved) {
        onSaved(result);
      }
    } catch (err) {
      console.error("Failed to save intake:", err);
      setError(err.message || "Failed to save data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="max-w-4xl mx-auto shadow-sm">
      <CardHeader>
        <CardTitle>{intakeId ? 'Edit Draft' : 'Basic Details'}</CardTitle>
        <CardDescription>Fill out the role constraints to guide the AI generation process.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSave}>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label>Company Name</Label>
              <Input type="text" name="company_name" value={formData.company_name} onChange={handleChange} placeholder="e.g. Acme Corp" />
            </div>
            <div className="space-y-2">
              <Label>Location</Label>
              <Input type="text" name="location" value={formData.location} onChange={handleChange} placeholder="e.g. Bangalore, India or Remote" />
            </div>
            
            <div className="space-y-2">
              <Label>Domain / Industry</Label>
              <Input type="text" name="domain" value={formData.domain} onChange={handleChange} placeholder="e.g. Engineering, Marketing..." />
            </div>
            <div className="space-y-2">
              <Label>Role Type</Label>
              <select name="role_type" value={formData.role_type} onChange={handleChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
                {ROLE_TYPES.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
            </div>

            <div className="space-y-2">
              <Label>Salary Range (INR)</Label>
              <div className="flex gap-2 items-center">
                <Input type="number" name="salary_min" value={formData.salary_min} onChange={handleChange} placeholder="Min" min="0" />
                <span className="text-muted-foreground">-</span>
                <Input type="number" name="salary_max" value={formData.salary_max} onChange={handleChange} placeholder="Max" min="0" />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Experience Range (Years)</Label>
              <div className="flex gap-2 items-center">
                <Input type="number" name="experience_min" value={formData.experience_min} onChange={handleChange} placeholder="Min" min="0" max="30" />
                <span className="text-muted-foreground">-</span>
                <Input type="number" name="experience_max" value={formData.experience_max} onChange={handleChange} placeholder="Max" min="0" max="30" />
              </div>
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label>Preferred Education</Label>
              <select name="preferred_education" value={formData.preferred_education} onChange={handleChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
                {EDU_LEVELS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between items-baseline">
              <Label>Job Context & Description <span className="text-destructive">*</span></Label>
              <span className="text-xs text-muted-foreground">Min 20 chars</span>
            </div>
            <Textarea 
              name="description" required minLength={20}
              value={formData.description} onChange={handleChange} 
              rows={6}
              placeholder="We are looking for a backend engineer to join our core payments team. They will work primarily with Python and AWS..." 
              className="resize-y"
            />
          </div>

          {error && <p className="text-sm font-medium text-destructive">{error}</p>}
        </CardContent>
        <CardFooter className="bg-muted/50 py-4 flex justify-end gap-3 border-t">
          <Button type="submit" disabled={loading} className="w-full sm:w-auto">
            {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</> : (intakeId ? 'Update Draft' : 'Save Draft')}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
