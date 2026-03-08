'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { X } from 'lucide-react';
import type { AgentInfo, AgentOutput } from '@/hooks/useAgencySocket';

const STATUS_CONFIG = {
  idle:     { label: 'IDLE',     color: 'var(--text-muted)',  bg: 'rgba(75,85,99,0.15)',      border: 'rgba(75,85,99,0.25)',        pulse: false },
  thinking: { label: 'THINKING', color: 'var(--warning)',     bg: 'var(--warning-dim)',        border: 'rgba(255,184,108,0.35)',      pulse: true  },
  working:  { label: 'WORKING',  color: 'var(--primary)',     bg: 'var(--primary-dim)',        border: 'rgba(124,111,255,0.35)',      pulse: true  },
  done:     { label: 'DONE',     color: 'var(--success)',     bg: 'var(--success-dim)',        border: 'rgba(67,217,173,0.35)',       pulse: false },
  error:    { label: 'ERROR',    color: 'var(--error)',       bg: 'var(--error-dim)',          border: 'rgba(255,83,112,0.35)',       pulse: false },
} as const;

interface AgentCardProps {
  agent: AgentInfo;
  output?: AgentOutput;
}

export function AgentCard({ agent, output }: AgentCardProps) {
  const [expanded, setExpanded] = useState(false);
  const cfg = STATUS_CONFIG[agent.status] || STATUS_CONFIG.idle;

  return (
    <>
      <div
        className="glass-card"
        style={{
          padding: 16,
          cursor: output ? 'pointer' : 'default',
          position: 'relative',
          overflow: 'hidden',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          borderColor: agent.status !== 'idle' ? cfg.border : undefined,
        }}
        onClick={() => output && setExpanded(true)}
        data-agent={agent.agent_id}
        data-status={agent.status}
        onMouseEnter={e => { if (output) (e.currentTarget as HTMLDivElement).style.transform = 'translateY(-3px)'; }}
        onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.transform = 'translateY(0)'; }}
      >
        {/* Ambient glow when active */}
        {(agent.status === 'working' || agent.status === 'thinking') && (
          <div style={{
            position: 'absolute', inset: 0,
            background: `radial-gradient(ellipse at top left, ${cfg.bg} 0%, transparent 70%)`,
            pointerEvents: 'none',
          }} />
        )}

        {/* Top row */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            {/* Avatar with pulse ring */}
            <div style={{ position: 'relative', flexShrink: 0 }}>
              <div style={{
                width: 42, height: 42, borderRadius: '50%',
                background: `linear-gradient(135deg, ${cfg.bg}, rgba(255,255,255,0.05))`,
                border: `1.5px solid ${cfg.border}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 20,
              }}>
                {agent.emoji}
              </div>
              {cfg.pulse && (
                <span style={{
                  position: 'absolute', inset: -4,
                  borderRadius: '50%',
                  border: `2px solid ${cfg.color}`,
                  animation: 'pulse-ring 1.5s ease-out infinite',
                  opacity: 0.5,
                }} />
              )}
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.88rem', color: 'var(--text-primary)', marginBottom: 2 }}>
                {agent.name}
              </div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {agent.role}
              </div>
            </div>
          </div>

          {/* Status badge */}
          <span style={{
            background: cfg.bg,
            color: cfg.color,
            border: `1px solid ${cfg.border}`,
            borderRadius: 99,
            padding: '3px 8px',
            fontSize: '0.65rem',
            fontWeight: 700,
            letterSpacing: '0.05em',
          }}>
            {cfg.label}
          </span>
        </div>

        {/* Current task */}
        {agent.current_task && (
          <div style={{
            fontSize: '0.75rem',
            color: 'var(--text-secondary)',
            background: 'rgba(0,0,0,0.2)',
            border: '1px solid rgba(255,255,255,0.05)',
            borderRadius: 6,
            padding: '6px 10px',
            marginBottom: 8,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            📌 {agent.current_task.slice(0, 70)}{agent.current_task.length > 70 ? '...' : ''}
          </div>
        )}

        {/* Output preview */}
        {output && (
          <div style={{
            fontSize: '0.72rem',
            fontFamily: 'var(--font-mono)',
            color: 'var(--success)',
            background: 'rgba(0,0,0,0.3)',
            border: '1px solid rgba(67,217,173,0.15)',
            borderRadius: 6,
            padding: '6px 10px',
            maxHeight: 52,
            overflow: 'hidden',
            lineHeight: 1.4,
          }}>
            {output.content.slice(0, 100)}...
          </div>
        )}

        {/* Footer */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          marginTop: 10,
        }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            ✅ {agent.tasks_completed} tasks done
          </div>
          {output && (
            <div style={{ fontSize: '0.7rem', color: 'var(--primary)', fontWeight: 500 }}>
              View output →
            </div>
          )}
        </div>
      </div>

      {/* Output Modal */}
      {expanded && output && (
        <OutputModal output={output} agentName={agent.name} agentEmoji={agent.emoji} onClose={() => setExpanded(false)} />
      )}
    </>
  );
}

function OutputModal({ output, agentName, agentEmoji, onClose }: {
  output: AgentOutput;
  agentName: string;
  agentEmoji: string;
  onClose: () => void;
}) {
  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        padding: 24, animation: 'fade-in 0.2s ease',
      }}
      onClick={onClose}
    >
      <div
        className="glass-card"
        style={{
          maxWidth: 720, width: '100%', maxHeight: '80vh',
          display: 'flex', flexDirection: 'column',
          animation: 'slide-up 0.25s ease',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 22 }}>{agentEmoji}</span>
            <div>
              <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{agentName} — Output</div>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                {output.output_type.replace(/_/g, ' ')}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'var(--bg-glass)', border: '1px solid var(--border)',
              borderRadius: 8, padding: 6, cursor: 'pointer', color: 'var(--text-secondary)',
              display: 'flex',
            }}
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>
        <div style={{ padding: 20, overflowY: 'auto', flex: 1 }} className="prose-dark">
          <ReactMarkdown>{output.content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
