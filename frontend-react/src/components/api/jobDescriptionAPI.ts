import { apiRequest } from './client';

export interface JobDescriptionListResponse {
  id: string;
  role_title: string | null;
  level: string | null;
  company_name: string | null;
  location: string | null;
  employment_type: string | null;
  status: string;
  jd_intake_id: string | null;
  created_at: string | null;
}

export interface JobDescriptionDetailResponse extends JobDescriptionListResponse {
  jd_text: string;
  structured_output: any | null;
  experience_level: number | null;
  salary_range: number | null;
  source: string | null;
  confidence_score: number | null;
  updated_at: string | null;
}

export const listJobDescriptions = async (): Promise<JobDescriptionListResponse[]> => {
  return apiRequest<JobDescriptionListResponse[]>('/api/jobs/', 'GET');
};

export const getJobDescription = async (id: string): Promise<JobDescriptionDetailResponse> => {
  return apiRequest<JobDescriptionDetailResponse>(`/api/jobs/${id}`, 'GET');
};
