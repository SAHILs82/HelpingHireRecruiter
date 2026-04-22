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
