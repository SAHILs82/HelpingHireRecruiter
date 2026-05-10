import { ShieldAlert, Eye, Clock, Target, HelpCircle } from 'lucide-react';

// ── Gap Type Visual Config ─────────────────────────

export const GAP_TYPE_CONFIG = {
  missing:              { label: 'Missing',               color: 'bg-red-500/10 text-red-700 border-red-200',       icon: ShieldAlert },
  superficial:          { label: 'Not Demonstrated',      color: 'bg-orange-500/10 text-orange-700 border-orange-200', icon: Eye },
  outdated:             { label: 'Outdated',              color: 'bg-yellow-500/10 text-yellow-700 border-yellow-200', icon: Clock },
  context_mismatch:     { label: 'Context Mismatch',      color: 'bg-purple-500/10 text-purple-700 border-purple-200', icon: Target },
  needs_clarification:  { label: 'Needs Clarification',   color: 'bg-blue-500/10 text-blue-700 border-blue-200',     icon: HelpCircle },
};

// ── Status Visual Config ───────────────────────────

export const STATUS_CONFIG = {
  critical:    { label: 'Critical',     color: 'bg-red-500 text-white',    dot: 'bg-red-400' },
  trainable:   { label: 'Trainable',    color: 'bg-amber-500 text-white',  dot: 'bg-amber-400' },
  non_critical: { label: 'Nice to Have', color: 'bg-emerald-500 text-white', dot: 'bg-emerald-400' },
};

// ── Seeker-Friendly Labels ─────────────────────────

export const SEEKER_GAP_LABELS = {
  missing:              'Not yet on your profile',
  superficial:          'Mentioned but needs project evidence',
  outdated:             'Consider updating to latest version',
  context_mismatch:     'Different context than required',
  needs_clarification:  'More details would help',
};
