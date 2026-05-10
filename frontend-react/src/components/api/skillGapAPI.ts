import { apiRequest } from './client';

// ── Types ──────────────────────────────────────────

export interface SkillGapItem {
  skill: string;
  gap_type: 'missing' | 'superficial' | 'outdated' | 'context_mismatch' | 'needs_clarification';
  status: 'critical' | 'trainable' | 'non_critical';
  evidence_reasoning: string;
  estimated_upskill_weeks: number;
}

export interface SkillGapReport {
  id: string;
  application_id: string;
  job_id: string;
  candidate_id: string;
  gaps: SkillGapItem[];
  impact_score: number;
  summary: string | null;
  analyzed_by: string | null;
  analysis_model: string | null;
  created_at: string;
  updated_at: string;
}

export interface SkillGapTriggerResponse {
  report_id: string;
  application_id: string;
  impact_score: number;
  status: string;
}

// ── API Calls ──────────────────────────────────────

export const triggerSkillGapAnalysis = async (applicationId: string): Promise<SkillGapTriggerResponse> => {
  return apiRequest<SkillGapTriggerResponse>(`/api/skill-gap/${applicationId}`, 'POST');
};

export const getSkillGapReport = async (applicationId: string): Promise<SkillGapReport> => {
  return apiRequest<SkillGapReport>(`/api/skill-gap/${applicationId}`, 'GET');
};
