import { JDIntakeCreate, JDIntakeUpdate, JDIntakeResponse } from '../../schemas/jdIntakeSchema';
import { apiRequest } from './client';

// ── JD INTAKE SERVICE ────────────────────────────────────────────────────────

export const createJDIntake = async (payload: JDIntakeCreate): Promise<JDIntakeResponse> => {
  return apiRequest<JDIntakeResponse>('/api/jd/intake/', 'POST', payload);
};

export const updateJDIntake = async (id: string, payload: JDIntakeUpdate): Promise<{ id: string; status: string }> => {
  return apiRequest<{ id: string; status: string }>(`/api/jd/intake/${id}`, 'PATCH', payload);
};

export const getJDIntake = async (id: string): Promise<JDIntakeResponse> => {
  return apiRequest<JDIntakeResponse>(`/api/jd/intake/${id}`, 'GET');
};

export const listJDIntakes = async (): Promise<JDIntakeResponse[]> => {
  return apiRequest<JDIntakeResponse[]>('/api/jd/intake/', 'GET');
};

export const deleteJDIntake = async (id: string): Promise<{ status: string; id: string }> => {
  return apiRequest<{ status: string; id: string }>(`/api/jd/intake/${id}`, 'DELETE');
};

export const generateJD = async (id: string): Promise<{ status: string; message: string; jd_intake_id: string; agent_summary: string }> => {
  return apiRequest<any>(`/api/jd/intake/${id}/generate`, 'POST');
};
