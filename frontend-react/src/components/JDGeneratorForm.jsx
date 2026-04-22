import { useState } from 'react';
import { createJDIntake, updateJDIntake } from './api/jdIntakeAPI';

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

export default function JDGeneratorForm({ onSubmit }) {
  const [isEditing, setIsEditing] = useState(true);
  const [formData, setFormData] = useState(DEFAULT_FORM_STATE);
  const [intakeId, setIntakeId] = useState(null);
  const [localLoading, setLocalLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleReset = () => {
    setFormData(DEFAULT_FORM_STATE);
    setIntakeId(null);
    setIsEditing(true);
    setError(null);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLocalLoading(true);
    setError(null);

    // Convert numeric fields from string to Number before sending
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
        // Update existing
        result = await updateJDIntake(intakeId, payload);
      } else {
        // Create new
        result = await createJDIntake(payload);
        if (result.id) {
          setIntakeId(result.id);
        }
      }
      
      setIsEditing(false);
      
      if (onSubmit) {
        onSubmit(result);
      }
    } catch (err) {
      console.error("Failed to save intake:", err);
      setError(err.message || "Failed to save data. Please try again.");
    } finally {
      setLocalLoading(false);
    }
  };

  return (
    <article className="panel" style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Create a Job Description</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button style={{ backgroundColor: '#4b5563', color: 'white' }} onClick={handleReset}>Create New Job Intake</button>
          {!isEditing && (
            <button onClick={() => setIsEditing(true)}>Edit Draft</button>
          )}
        </div>
      </div>
      
      <p>Fill out the basic details to save an intake form.</p>

      {isEditing ? (
        <form onSubmit={handleSave} style={{ marginTop: '14px' }}>
          
          <div className="panel-grid">
            <label>
              Company Name
              <input 
                type="text" name="company_name" 
                value={formData.company_name} onChange={handleChange} 
                placeholder="e.g. Acme Corp" 
              />
            </label>
            <label>
              Location
              <input 
                type="text" name="location" 
                value={formData.location} onChange={handleChange} 
                placeholder="e.g. Bangalore, India or Remote" 
              />
            </label>
          </div>

          <div className="panel-grid">
            <label>
              Domain / Industry
              <input 
                type="text" name="domain" 
                value={formData.domain} onChange={handleChange} 
                placeholder="e.g. Engineering, Marketing, Data..." 
              />
            </label>
            <label>
              Role Type
              <select name="role_type" value={formData.role_type} onChange={handleChange}>
                {ROLE_TYPES.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
            </label>
          </div>

          <div className="panel-grid">
            <label>
              Salary Range (INR)
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input 
                  type="number" name="salary_min" 
                  value={formData.salary_min} onChange={handleChange} 
                  placeholder="Min" min="0" style={{ width: '100%' }}
                />
                <span>-</span>
                <input 
                  type="number" name="salary_max" 
                  value={formData.salary_max} onChange={handleChange} 
                  placeholder="Max" min="0" style={{ width: '100%' }}
                />
              </div>
            </label>
            <label>
              Experience Range (Years)
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input 
                  type="number" name="experience_min" 
                  value={formData.experience_min} onChange={handleChange} 
                  placeholder="Min" min="0" max="30" style={{ width: '100%' }}
                />
                <span>-</span>
                <input 
                  type="number" name="experience_max" 
                  value={formData.experience_max} onChange={handleChange} 
                  placeholder="Max" min="0" max="30" style={{ width: '100%' }}
                />
              </div>
            </label>
          </div>

          <div className="panel-grid" style={{ gridTemplateColumns: '1fr' }}>
             <label>
              Preferred Education
              <select name="preferred_education" value={formData.preferred_education} onChange={handleChange}>
                {EDU_LEVELS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
              </select>
            </label>
          </div>

          <label>
            Job Description / Context <span style={{color: '#b91c1c'}}>*</span>
            <span className="hint">Describe what the person will do, key skills needed, and the team context. (Min 20 characters)</span>
            <textarea 
              name="description" required minLength={20}
              value={formData.description} onChange={handleChange} 
              rows={5}
              placeholder="We are looking for a backend engineer to join our core payments team..." 
            />
          </label>

          {error && <p className="error" style={{ marginBottom: '10px' }}>{error}</p>}

          <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
            <button type="submit" disabled={localLoading} style={{ background: '#1d4ed8', width: '100%' }}>
              {localLoading ? 'Saving...' : (intakeId ? 'Update Draft' : 'Save Draft')}
            </button>
          </div>
        </form>
      ) : (
        <div style={{ background: '#f9fafb', border: '1px solid #e5e7eb', padding: '16px', borderRadius: '8px', marginTop: '14px' }}>
          <h4>Review your inputs</h4>
          <p><strong>Company:</strong> {formData.company_name || 'N/A'}</p>
          <p><strong>Location:</strong> {formData.location || 'N/A'}</p>
          <p><strong>Salary (INR):</strong> {formData.salary_min} - {formData.salary_max}</p>
          <p><strong>Experience:</strong> {formData.experience_min} - {formData.experience_max} years</p>
          <p><strong>Role Type:</strong> {formData.role_type}</p>
          <div style={{ marginTop: '10px' }}>
            <strong>Description:</strong>
            <p style={{ whiteSpace: 'pre-wrap', color: '#4b5563', fontSize: '14px' }}>{formData.description}</p>
          </div>
          <button style={{ marginTop: '14px' }} onClick={() => setIsEditing(true)}>Edit Details</button>
        </div>
      )}
    </article>
  );
}
