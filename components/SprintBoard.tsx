'use client';

import type { Sprint } from '@/hooks/useAgencySocket';

const AGENT_EMOJI: Record<string, string> = {
  project_manager: '🎯',
  designer: '🎨',
  frontend_dev: '⚛️',
  backend_dev: '🔧',
  qa_tester: '🧪',
  seo_specialist: '🔍',
  virtual_ceo: '🏢',
};

const PRIORITY_CONFIG = {
  critical: { label: 'CRITICAL', color: '#FF5370', bg: 'rgba(255,83,112,0.12)' },
  high:     { label: 'HIGH',     color: '#FF6584', bg: 'rgba(255,101,132,0.12)' },
  medium:   { label: 'MED',      color: '#FFB86C', bg: 'rgba(255,184,108,0.12)' },
  low:      { label: 'LOW',      color: '#43D9AD', bg: 'rgba(67,217,173,0.12)' },
} as const;

const TASK_STATUS_CONFIG = {
  todo:        { label: 'To Do',       color: 'var(--text-muted)' },
  in_progress: { label: 'In Progress', color: 'var(--primary)'    },
  review:      { label: 'Review',      color: 'var(--warning)'    },
  done:        { label: 'Done',        color: 'var(--success)'    },
} as const;

const COLUMNS: Array<{ key: string; label: string; emoji: string }> = [
  { key: 'todo',        label: 'To Do',       emoji: '📋' },
  { key: 'in_progress', label: 'In Progress',  emoji: '⚡' },
  { key: 'done',        label: 'Done',         emoji: '✅' },
];

interface SprintBoardProps {
  sprints: Sprint[];
}

export function SprintBoard({ sprints }: SprintBoardProps) {
  if (sprints.length === 0) {
    return (
      <div>
        <h2 style={{
          fontFamily: 'var(--font-display)', fontSize: '1rem',
          fontWeight: 700, color: 'var(--text-primary)', marginBottom: 14,
        }}>
          Sprint Board
        </h2>
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10,
        }}>
          {COLUMNS.map(col => (
            <div key={col.key} className="glass-card" style={{ padding: 14, minHeight: 120 }}>
              <div style={{
                fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)',
                marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6,
                textTransform: 'uppercase', letterSpacing: '0.07em',
              }}>
                {col.emoji} {col.label}
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textAlign: 'center', paddingTop: 16 }}>
                No tasks yet
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div>
      <h2 style={{
        fontFamily: 'var(--font-display)', fontSize: '1rem',
        fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4,
      }}>
        Sprint Board
      </h2>

      {sprints.map(sprint => {
        const tasksByStatus: Record<string, typeof sprint.tasks> = {
          todo:        sprint.tasks.filter(t => t.status === 'todo'),
          in_progress: sprint.tasks.filter(t => t.status === 'in_progress'),
          done:        sprint.tasks.filter(t => t.status === 'done'),
        };

        return (
          <div key={sprint.id} style={{ marginBottom: 20 }}>
            {/* Sprint Header */}
            <div style={{
              display: 'flex', alignItems: 'center', gap: 10,
              marginBottom: 10, padding: '8px 0',
              borderBottom: '1px solid rgba(255,255,255,0.05)',
            }}>
              <div style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'var(--primary)', flexShrink: 0,
              }} />
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                {sprint.name}
              </span>
              <span style={{
                fontSize: '0.7rem', color: 'var(--text-muted)',
                background: 'var(--bg-glass)', border: '1px solid var(--border)',
                borderRadius: 99, padding: '2px 8px',
              }}>
                {sprint.tasks.length} tasks
              </span>
            </div>

            {/* Kanban Columns */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10 }}>
              {COLUMNS.map(col => {
                const colTasks = tasksByStatus[col.key] || [];
                return (
                  <div key={col.key} style={{
                    background: 'var(--bg-glass)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-md)',
                    padding: 12, minHeight: 80,
                  }}>
                    {/* Column header */}
                    <div style={{
                      fontSize: '0.7rem', fontWeight: 700,
                      color: 'var(--text-muted)', marginBottom: 10,
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      textTransform: 'uppercase', letterSpacing: '0.07em',
                    }}>
                      <span>{col.emoji} {col.label}</span>
                      <span style={{
                        background: 'rgba(255,255,255,0.06)', borderRadius: 99,
                        padding: '1px 7px', fontSize: '0.65rem',
                      }}>
                        {colTasks.length}
                      </span>
                    </div>

                    {/* Tasks */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {colTasks.map(task => {
                        const prio = PRIORITY_CONFIG[task.priority as keyof typeof PRIORITY_CONFIG] || PRIORITY_CONFIG.medium;
                        const em = AGENT_EMOJI[task.assigned_to] || '🤖';
                        return (
                          <div key={task.id} style={{
                            background: 'rgba(0,0,0,0.25)',
                            border: '1px solid rgba(255,255,255,0.06)',
                            borderRadius: 8,
                            padding: '9px 11px',
                            animation: 'slide-up 0.3s ease',
                          }}>
                            <div style={{
                              fontSize: '0.78rem', fontWeight: 500,
                              color: 'var(--text-primary)', marginBottom: 6, lineHeight: 1.35,
                            }}>
                              {task.title}
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                {em}
                              </span>
                              <span style={{
                                background: prio.bg, color: prio.color,
                                fontSize: '0.6rem', fontWeight: 700,
                                padding: '2px 6px', borderRadius: 99,
                                letterSpacing: '0.05em',
                              }}>
                                {prio.label}
                              </span>
                            </div>
                          </div>
                        );
                      })}

                      {colTasks.length === 0 && (
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', textAlign: 'center', padding: '10px 0' }}>
                          Empty
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
