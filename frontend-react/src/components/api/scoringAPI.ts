import { apiRequest } from './client';

export interface ScoreApplicationResponse {
  application_id: string;
  status: string;
  message: string;
}

export interface ApplicationScoreDetail {
  application_id: string;
  score_id: string;
  candidate_name: string;
  job_title: string;
  score: number;
  breakdown: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  missing_requirements: string[];
  recommendation: string;
  agent_summary: string;
  status: string;
  created_at: string;
}

export const scoreApplication = async (applicationId: string): Promise<ScoreApplicationResponse> => {
  return apiRequest<ScoreApplicationResponse>(`/api/scoring/${applicationId}/evaluate`, 'POST');
};

export const getLeaderboard = async (jobId: string): Promise<any[]> => {
  return apiRequest<any[]>(`/api/scoring/job/${jobId}/leaderboard`, 'GET');
};

export const getApplicationScoreDetail = async (applicationId: string): Promise<ApplicationScoreDetail> => {
  return apiRequest<ApplicationScoreDetail>(`/api/scoring/application/${applicationId}/score-detail`, 'GET');
};
