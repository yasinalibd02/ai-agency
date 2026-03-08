'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Wifi, WifiOff, Loader2, Bot, User } from 'lucide-react';
import type { ChatMsg, ConnectionState } from '@/hooks/useAgencySocket';

interface ChatPanelProps {
  messages: ChatMsg[];
  isTyping: boolean;
  connectionState: ConnectionState;
  onSendMessage: (content: string) => void;
}

export function ChatPanel({ messages, isTyping, connectionState, onSendMessage }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = () => {
    const content = input.trim();
    if (!content || isSending || connectionState !== 'connected') return;
    onSendMessage(content);
    setInput('');
    setIsSending(true);
    setTimeout(() => setIsSending(false), 500);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-grow textarea
    e.target.style.height = 'auto';
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px';
  };

  const connColors: Record<ConnectionState, string> = {
    connected:    'text-green-400',
    connecting:   'text-yellow-400',
    disconnected: 'text-red-400',
    error:        'text-red-500',
  };

  const SUGGESTIONS = [
    'Build me a SaaS task manager',
    'Create an e-commerce platform',
    'Design a social media app',
    'Build a real-time analytics dashboard',
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 0 }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 38, height: 38, borderRadius: '50%',
            background: 'linear-gradient(135deg, #7C6FFF, #FF6584)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 18,
          }}>🎯</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-primary)' }}>
              Project Manager
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Lead Orchestrator
            </div>
          </div>
        </div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 6,
          fontSize: '0.75rem', fontWeight: 500,
        }} className={connColors[connectionState]}>
          {connectionState === 'connected'
            ? <Wifi size={13} />
            : connectionState === 'connecting'
            ? <Loader2 size={13} style={{ animation: 'spin 1s linear infinite' }} />
            : <WifiOff size={13} />}
          {connectionState}
        </div>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', margin: 'auto' }}>
            <div style={{ fontSize: 48, marginBottom: 14 }}>🎯</div>
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.3rem', marginBottom: 8, color: 'var(--text-primary)' }}>
              Meet Your Project Manager
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: 20, maxWidth: 280, margin: '0 auto 20px' }}>
              Describe your project idea and watch your AI team spring into action.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 300, margin: '0 auto' }}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => { setInput(s); textareaRef.current?.focus(); }}
                  style={{
                    background: 'var(--bg-glass)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-secondary)',
                    padding: '8px 12px',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.2s ease',
                  }}
                  onMouseEnter={e => {
                    (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(124,111,255,0.4)';
                    (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-primary)';
                  }}
                  onMouseLeave={e => {
                    (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)';
                    (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-secondary)';
                  }}
                >
                  💡 {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <MessageBubble key={msg.id || i} message={msg} />
        ))}

        {isTyping && (
          <div style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
            <div style={{
              width: 32, height: 32, borderRadius: '50%',
              background: 'linear-gradient(135deg, #7C6FFF22, #7C6FFF44)',
              border: '1px solid rgba(124,111,255,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 14, flexShrink: 0,
            }}>🎯</div>
            <div style={{
              background: 'var(--bg-glass)',
              border: '1px solid var(--border)',
              borderRadius: '12px 12px 12px 2px',
              padding: '10px 14px',
              display: 'flex', gap: 5, alignItems: 'center',
            }}>
              {[0,1,2].map(i => <span key={i} className="typing-dot" style={{ animationDelay: `${i*0.2}s` }} />)}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '14px 16px',
        borderTop: '1px solid rgba(255,255,255,0.06)',
        display: 'flex',
        gap: 10,
        alignItems: 'flex-end',
        flexShrink: 0,
      }}>
        <textarea
          ref={textareaRef}
          id="chat-input"
          className="input-field"
          value={input}
          onChange={handleTextareaChange}
          onKeyDown={handleKeyDown}
          placeholder="Describe your project... (Enter to send)"
          rows={1}
          style={{ flex: 1, padding: '10px 14px', minHeight: 44, maxHeight: 140 }}
        />
        <button
          id="send-btn"
          className="btn-primary"
          onClick={handleSend}
          disabled={!input.trim() || connectionState !== 'connected'}
          style={{ height: 44, padding: '0 16px', flexShrink: 0 }}
          aria-label="Send message"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMsg }) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

  if (isSystem) {
    return (
      <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.75rem', padding: '4px 0' }}>
        {message.content}
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: isUser ? 'row-reverse' : 'row',
      gap: 10,
      alignItems: 'flex-end',
      animation: 'slide-up 0.3s ease forwards',
    }}>
      {/* Avatar */}
      <div style={{
        width: 32, height: 32, borderRadius: '50%',
        background: isUser
          ? 'linear-gradient(135deg, rgba(255,101,132,0.3), rgba(255,101,132,0.5))'
          : 'linear-gradient(135deg, rgba(124,111,255,0.25), rgba(124,111,255,0.45))',
        border: `1px solid ${isUser ? 'rgba(255,101,132,0.3)' : 'rgba(124,111,255,0.25)'}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: 14, flexShrink: 0,
      }}>
        {isUser ? <User size={14} /> : '🎯'}
      </div>

      {/* Bubble */}
      <div style={{
        maxWidth: '80%',
        background: isUser
          ? 'linear-gradient(135deg, rgba(124,111,255,0.25), rgba(90,80,200,0.3))'
          : 'var(--bg-glass)',
        border: `1px solid ${isUser ? 'rgba(124,111,255,0.3)' : 'var(--border)'}`,
        borderRadius: isUser ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
        padding: '10px 14px',
        fontSize: '0.875rem',
        lineHeight: 1.55,
      }}>
        <div className="prose-dark">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        <div style={{
          color: 'var(--text-muted)',
          fontSize: '0.7rem',
          marginTop: 6,
          textAlign: isUser ? 'left' : 'right',
        }}>
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}
