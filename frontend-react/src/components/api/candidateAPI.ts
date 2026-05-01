import { apiRequest } from './client';

// Simple interface matching what we need to display
export interface CandidateResponse {
  id: string;
  full_name: string | null;
  email: string | null;
  phone: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  cv_text: string;
  education: any[] | null;
  skills: Record<string, string[]> | null;
  work_experience: any[] | null;
  projects: any[] | null;
  certifications: any[] | null;
  highlights: string[] | null;
  total_experience: number | null;
  primary_domain: string | null;
  seniority_level: string | null;
  confidence_score: number | null;
}

export const getCandidate = async (candidateId: string): Promise<CandidateResponse> => {
  return apiRequest<CandidateResponse>(`/api/cv-parsing/candidate/${candidateId}`, 'GET');
};
