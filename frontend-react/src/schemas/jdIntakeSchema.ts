export interface JDIntakeCreate {
  company_name?: string | null;
  salary_min?: number | null;
  salary_max?: number | null;
  experience_min?: number | null;
  experience_max?: number | null;
  domain?: string | null;
  role_type?: 'full-time' | 'part-time' | 'contract' | 'intern' | 'freelance' | null;
  preferred_education?: 'any' | 'diploma' | 'bachelors' | 'masters' | 'phd' | null;
  location?: string | null;
  description: string;
}

export interface JDIntakeUpdate {
  company_name?: string | null;
  salary_min?: number | null;
  salary_max?: number | null;
  experience_min?: number | null;
  experience_max?: number | null;
  domain?: string | null;
  role_type?: 'full-time' | 'part-time' | 'contract' | 'intern' | 'freelance' | null;
  preferred_education?: 'any' | 'diploma' | 'bachelors' | 'masters' | 'phd' | null;
  location?: string | null;
  description?: string | null;
}

export interface JDIntakeResponse {
  id: string; // UUID
  company_name: string | null;
  salary_min: number | null;
  salary_max: number | null;
  experience_min: number | null;
  experience_max: number | null;
  domain: string | null;
  role_type: string | null;
  preferred_education: string | null;
  location: string | null;
  description: string;
}
