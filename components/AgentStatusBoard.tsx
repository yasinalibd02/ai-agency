'use client';

import { AgentCard } from './AgentCard';
import type { AgentInfo, AgentOutput } from '@/hooks/useAgencySocket';

interface AgentStatusBoardProps {
  agents: AgentInfo[];
  agentOutputs: Record<string, AgentOutput>;
}

export function AgentStatusBoard({ agents, agentOutputs }: AgentStatusBoardProps) {
  const activeCount = agents.filter(a => a.status === 'working' || a.status === 'thinking').length;
  const doneCount = agents.filter(a => a.status === 'done').length;

  return (
    <div>
      {/* Board Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
        <div>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            marginBottom: 2,
          }}>
            Live Agent Status
          </h2>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {agents.length} agents · {activeCount} active · {doneCount} complete
          </p>
        </div>

        {/* Status legend */}
        <div style={{ display: 'flex', gap: 10 }}>
          {[
            { label: 'Active', color: 'var(--primary)' },
            { label: 'Done', color: 'var(--success)' },
            { label: 'Idle', color: 'var(--text-muted)' },
          ].map(l => (
            <div key={l.label} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.7rem', color: 'var(--text-muted)' }}>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: l.color, display: 'inline-block' }} />
              {l.label}
            </div>
          ))}
        </div>
      </div>

      {/* Agent Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: 12,
      }}>
        {agents.map(agent => (
          <AgentCard
            key={agent.agent_id}
            agent={agent}
            output={agentOutputs[agent.agent_id]}
          />
        ))}

        {agents.length === 0 && (
          <div style={{
            gridColumn: '1/-1',
            textAlign: 'center',
            padding: '40px 20px',
            color: 'var(--text-muted)',
            fontSize: '0.875rem',
          }}>
            <div style={{ fontSize: 36, marginBottom: 10 }}>⏳</div>
            Connecting to agents...
          </div>
        )}
      </div>
    </div>
  );
}
