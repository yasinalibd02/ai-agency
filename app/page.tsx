'use client';

import { useMemo } from 'react';
import { useAgencySocket } from '@/hooks/useAgencySocket';
import { ChatPanel } from '@/components/ChatPanel';
import { AgentStatusBoard } from '@/components/AgentStatusBoard';
import { SprintBoard } from '@/components/SprintBoard';
import { Loader2, Zap, Settings, Bell } from 'lucide-react';

const SESSION_ID = 'main-session';

export default function DashboardPage() {
  const {
    connectionState,
    agents,
    messages,
    sprints,
    agentOutputs,
    isTyping,
    sendMessage,
  } = useAgencySocket(SESSION_ID);

  const activeCount = useMemo(
    () => agents.filter(a => a.status === 'working' || a.status === 'thinking').length,
    [agents]
  );

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100dvh',
      overflow: 'hidden',
      position: 'relative',
      zIndex: 1,
    }}>
      {/* ── Top Navbar ─────────────────────────────────────────────── */}
      <header style={{
        height: 58,
        flexShrink: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 20px',
        background: 'rgba(7, 11, 20, 0.8)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        zIndex: 10,
      }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32, height: 32,
            background: 'linear-gradient(135deg, #7C6FFF, #FF6584)',
            borderRadius: 8,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 16, fontWeight: 900,
            boxShadow: '0 4px 15px rgba(124,111,255,0.4)',
          }}>
            ⚡
          </div>
          <span style={{
            fontFamily: 'var(--font-display)',
            fontSize: '1.05rem',
            fontWeight: 800,
            letterSpacing: '-0.02em',
          }}>
            <span className="gradient-text">Virtual</span>
            <span style={{ color: 'var(--text-primary)' }}> Agency</span>
          </span>
        </div>

        {/* Center status */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: 'var(--bg-glass)',
          border: '1px solid var(--border)',
          borderRadius: 99,
          padding: '5px 14px',
          fontSize: '0.78rem',
        }}>
          {activeCount > 0 ? (
            <>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--primary)', display: 'inline-block', animation: 'pulse-ring 1.5s infinite' }} />
              <span style={{ color: 'var(--text-secondary)' }}>
                <span style={{ color: 'var(--primary)', fontWeight: 600 }}>{activeCount}</span> agent{activeCount > 1 ? 's' : ''} working
              </span>
            </>
          ) : connectionState === 'connecting' ? (
            <>
              <Loader2 size={12} style={{ animation: 'spin 1s linear infinite', color: 'var(--warning)' }} />
              <span style={{ color: 'var(--text-muted)' }}>Connecting...</span>
            </>
          ) : (
            <>
              <span style={{ width: 7, height: 7, borderRadius: '50%', background: connectionState === 'connected' ? 'var(--success)' : 'var(--error)', display: 'inline-block' }} />
              <span style={{ color: 'var(--text-muted)' }}>
                {connectionState === 'connected' ? 'All agents idle' : 'Disconnected'}
              </span>
            </>
          )}
        </div>

        {/* Right actions */}
        <div style={{ display: 'flex', gap: 8 }}>
          {[Bell, Settings].map((Icon, i) => (
            <button key={i} style={{
              background: 'var(--bg-glass)', border: '1px solid var(--border)',
              borderRadius: 8, width: 34, height: 34,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', color: 'var(--text-muted)',
              transition: 'color 0.2s, border-color 0.2s',
            }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-primary)';
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border-hover)';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)';
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)';
              }}
              aria-label={i === 0 ? 'Notifications' : 'Settings'}
            >
              <Icon size={15} />
            </button>
          ))}
        </div>
      </header>

      {/* ── Main Content ────────────────────────────────────────────── */}
      <div style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '380px 1fr',
        overflow: 'hidden',
      }}>
        {/* LEFT — Chat Panel */}
        <div style={{
          borderRight: '1px solid rgba(255,255,255,0.06)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          background: 'rgba(13,18,32,0.5)',
        }}>
          <ChatPanel
            messages={messages}
            isTyping={isTyping}
            connectionState={connectionState}
            onSendMessage={sendMessage}
          />
        </div>

        {/* RIGHT — Live Dashboard */}
        <div style={{
          overflowY: 'auto',
          padding: 20,
          display: 'flex',
          flexDirection: 'column',
          gap: 24,
        }}>
          {/* Agent Status Board */}
          <section>
            <AgentStatusBoard agents={agents} agentOutputs={agentOutputs} />
          </section>

          {/* Divider */}
          <div style={{ height: 1, background: 'rgba(255,255,255,0.05)' }} />

          {/* Sprint Board */}
          <section style={{ paddingBottom: 20 }}>
            <SprintBoard sprints={sprints} />
          </section>
        </div>
      </div>
    </div>
  );
}
