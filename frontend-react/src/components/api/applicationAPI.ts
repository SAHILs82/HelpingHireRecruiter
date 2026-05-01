import { apiRequest } from './client';

export interface ApplicationResponse {
  id: string;
  candidate_id: string;
  job_id: string;
  status: string;
  applied_at: string;
  updated_at: string;
}

export const getApplicationsByJob = async (jobId: string): Promise<ApplicationResponse[]> => {
  return apiRequest<ApplicationResponse[]>(`/api/applications/job/${jobId}`, 'GET');
};

export const getApplicationsByCandidate = async (candidateId: string): Promise<ApplicationResponse[]> => {
  return apiRequest<ApplicationResponse[]>(`/api/applications/candidate/${candidateId}`, 'GET');
};

export const updateApplicationStatus = async (applicationId: string, status: string): Promise<ApplicationResponse> => {
  return apiRequest<ApplicationResponse>(`/api/applications/${applicationId}`, 'PATCH', { status });
};
