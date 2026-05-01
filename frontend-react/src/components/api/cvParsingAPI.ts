/// <reference types="vite/client" />
import { apiRequest } from './client';

export interface CVUploadResponse {
  status: string;
  message: string;
  candidate_id: string;
  application_id?: string;
  job_id?: string;
}

export const uploadCV = async (jobId: string, file: File): Promise<CVUploadResponse> => {
  const formData = new FormData();
  formData.append('job_id', jobId);
  formData.append('file', file);

  const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/cv-parsing/upload-cv`;
  
  const response = await fetch(url, {
    method: 'POST',
    // Do NOT set Content-Type header when sending FormData; browser sets it with boundary
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.status}`);
  }

  return response.json();
};

export const deleteCandidate = async (candidateId: string): Promise<{ status: string; id: string }> => {
  return apiRequest<{ status: string; id: string }>(`/api/cv-parsing/${candidateId}`, 'DELETE');
};
