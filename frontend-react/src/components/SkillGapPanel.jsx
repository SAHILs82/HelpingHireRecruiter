import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { 
  BookOpen, 
  CheckCircle2, 
  Clock, 
  ShieldAlert, 
  TrendingDown,
  Zap
} from 'lucide-react';
import { GAP_TYPE_CONFIG, STATUS_CONFIG, SEEKER_GAP_LABELS } from './skillGapConfig';

// ── Impact Score Ring ──────────────────────────────

function ImpactScoreRing({ score, size = 120 }) {
  const readiness = Math.round((1 - score) * 100);
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (readiness / 100) * circumference;
  const color = readiness >= 80 ? '#22c55e' : readiness >= 50 ? '#eab308' : '#ef4444';

  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size} viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" fill="none" stroke="currentColor" strokeWidth="8" className="text-muted/30" />
        <circle
          cx="50" cy="50" r="45" fill="none"
          stroke={color} strokeWidth="8" strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          transform="rotate(-90 50 50)"
          className="transition-all duration-700 ease-out"
        />
        <text x="50" y="46" textAnchor="middle" className="fill-foreground text-2xl font-black">{readiness}%</text>
        <text x="50" y="62" textAnchor="middle" className="fill-muted-foreground text-[8px] font-medium">READINESS</text>
      </svg>
    </div>
  );
}

// ── Summary Stats Cards ────────────────────────────

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className={`flex items-center gap-3 p-4 rounded-xl border ${color} transition-all hover:scale-[1.02]`}>
      <div className="p-2 rounded-lg bg-white/80 shadow-sm">
        <Icon size={18} />
      </div>
      <div>
        <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{label}</div>
        <div className="text-lg font-bold">{value}</div>
      </div>
    </div>
  );
}

// ── Main Component ─────────────────────────────────

export default function SkillGapPanel({ report, variant = 'recruiter' }) {
  if (!report || !report.gaps) return null;

  const isSeeker = variant === 'seeker';
  const gaps = report.gaps;

  const criticalCount = gaps.filter(g => g.status === 'critical').length;
  const trainableCount = gaps.filter(g => g.status === 'trainable').length;
  const niceToHaveCount = gaps.filter(g => g.status === 'non_critical').length;
  const totalUpskillWeeks = gaps.reduce((sum, g) => sum + (g.estimated_upskill_weeks || 0), 0);

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header Row: Score Ring + Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="sm:row-span-2 flex items-center justify-center p-6 bg-gradient-to-br from-slate-50 to-white border-2">
          <ImpactScoreRing score={report.impact_score} />
        </Card>

        <StatCard
          icon={ShieldAlert}
          label="Critical Gaps"
          value={criticalCount}
          color="bg-red-50 border-red-100 text-red-700"
        />
        <StatCard
          icon={BookOpen}
          label="Trainable"
          value={trainableCount}
          color="bg-amber-50 border-amber-100 text-amber-700"
        />
        <StatCard
          icon={Zap}
          label="Nice to Have"
          value={niceToHaveCount}
          color="bg-emerald-50 border-emerald-100 text-emerald-700"
        />
        <StatCard
          icon={Clock}
          label="Est. Upskill Time"
          value={`${totalUpskillWeeks} weeks`}
          color="bg-blue-50 border-blue-100 text-blue-700 sm:col-span-2"
        />
      </div>

      {/* Summary */}
      {report.summary && (
        <Card className="border-primary/10 bg-primary/[0.02]">
          <CardContent className="p-5">
            <div className="flex items-start gap-3">
              <div className="p-2 rounded-lg bg-primary/10 text-primary mt-0.5">
                <TrendingDown size={16} />
              </div>
              <div>
                <h4 className="font-semibold text-sm mb-1">
                  {isSeeker ? 'Your Readiness Summary' : 'AI Assessment Summary'}
                </h4>
                <p className="text-sm text-muted-foreground leading-relaxed">{report.summary}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Gap Cards */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider px-1">
          {isSeeker ? 'Skills to Improve' : `Identified Gaps (${gaps.length})`}
        </h3>

        {gaps.length === 0 ? (
          <Card className="border-green-200 bg-green-50">
            <CardContent className="p-6 text-center">
              <CheckCircle2 className="mx-auto text-green-500 mb-2" size={32} />
              <p className="font-semibold text-green-700">Perfect Match!</p>
              <p className="text-sm text-green-600">No skill gaps were detected.</p>
            </CardContent>
          </Card>
        ) : (
          gaps.map((gap, i) => {
            const typeConfig = GAP_TYPE_CONFIG[gap.gap_type] || GAP_TYPE_CONFIG.missing;
            const statusConfig = STATUS_CONFIG[gap.status] || STATUS_CONFIG.trainable;
            const TypeIcon = typeConfig.icon;

            return (
              <Card key={i} className="overflow-hidden hover:shadow-md transition-all duration-300 group">
                <CardContent className="p-0">
                  <div className="flex items-stretch">
                    {/* Status color strip */}
                    <div className={`w-1.5 ${gap.status === 'critical' ? 'bg-red-500' : gap.status === 'trainable' ? 'bg-amber-500' : 'bg-emerald-500'}`} />
                    
                    <div className="flex-1 p-4 sm:p-5">
                      <div className="flex flex-wrap items-center gap-2 mb-3">
                        <h4 className="font-bold text-base">{gap.skill}</h4>
                        <Badge className={`text-[10px] px-2 py-0.5 ${typeConfig.color} border`}>
                          <TypeIcon size={10} className="mr-1" />
                          {isSeeker ? SEEKER_GAP_LABELS[gap.gap_type] : typeConfig.label}
                        </Badge>
                        <Badge className={`text-[10px] px-2 py-0.5 ${statusConfig.color}`}>
                          {statusConfig.label}
                        </Badge>
                      </div>
                      
                      <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                        {gap.evidence_reasoning}
                      </p>

                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          ~{gap.estimated_upskill_weeks} {gap.estimated_upskill_weeks === 1 ? 'week' : 'weeks'} to learn
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
