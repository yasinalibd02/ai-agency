'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

export interface AgentInfo {
  agent_id: string;
  name: string;
  emoji: string;
  role: string;
  status: 'idle' | 'thinking' | 'working' | 'done' | 'error';
  current_task: string | null;
  last_output: string | null;
  tasks_completed: number;
}

export interface ChatMsg {
  id: string;
  role: 'user' | 'pm' | 'system';
  content: string;
  timestamp: string;
  agent_id?: string;
}

export interface SprintTask {
  id: string;
  title: string;
  description: string;
  assigned_to: string;
  status: 'todo' | 'in_progress' | 'review' | 'done';
  priority: string;
  result?: string;
}

export interface Sprint {
  id: number;
  name: string;
  goal: string;
  status: string;
  tasks: SprintTask[];
}

export interface AgentOutput {
  agent_id: string;
  output_type: string;
  content: string;
  task_id?: string;
}

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export function useAgencySocket(sessionId: string) {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected');
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [sprints, setSprints] = useState<Sprint[]>([]);
  const [agentOutputs, setAgentOutputs] = useState<Record<string, AgentOutput>>({});
  const [isTyping, setIsTyping] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const MAX_RECONNECT = 5;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setConnectionState('connecting');
    const ws = new WebSocket(`${WS_URL}/ws/${sessionId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionState('connected');
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (ev) => {
      try {
        const event = JSON.parse(ev.data);
        handleEvent(event);
      } catch (e) {
        console.error('[WS] Parse error:', e);
      }
    };

    ws.onerror = () => setConnectionState('error');

    ws.onclose = () => {
      setConnectionState('disconnected');
      wsRef.current = null;
      // Exponential backoff reconnect
      if (reconnectAttempts.current < MAX_RECONNECT) {
        const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 15000);
        reconnectAttempts.current++;
        reconnectTimeout.current = setTimeout(connect, delay);
      }
    };
  }, [sessionId]);

  const handleEvent = (event: { event_type: string; payload: Record<string, unknown> }) => {
    const { event_type, payload } = event;

    switch (event_type) {
      case 'init': {
        if (payload.agents) setAgents(payload.agents as AgentInfo[]);
        if (payload.sprints) setSprints(payload.sprints as Sprint[]);
        break;
      }

      case 'agent_status': {
        setAgents(prev =>
          prev.map(a =>
            a.agent_id === payload.agent_id
              ? {
                  ...a,
                  status: payload.status as AgentInfo['status'],
                  current_task: (payload.current_task as string) || a.current_task,
                  last_output: (payload.last_output as string) || a.last_output,
                  tasks_completed: (payload.tasks_completed as number) ?? a.tasks_completed,
                }
              : a
          )
        );
        break;
      }

      case 'chat_message': {
        const msg: ChatMsg = {
          id: `${Date.now()}-${Math.random()}`,
          role: payload.role as ChatMsg['role'],
          content: payload.content as string,
          timestamp: (payload.timestamp as string) || new Date().toISOString(),
          agent_id: payload.agent_id as string | undefined,
        };
        setMessages(prev => [...prev, msg]);
        setIsTyping(false);

        // Show typing indicator for pm responses
        if (payload.role === 'user') {
          setIsTyping(true);
        }
        break;
      }

      case 'sprint_update': {
        setSprints((payload.sprints as Sprint[]) || []);
        break;
      }

      case 'agent_output': {
        const out: AgentOutput = {
          agent_id: payload.agent_id as string,
          output_type: payload.output_type as string,
          content: payload.content as string,
          task_id: payload.task_id as string | undefined,
        };
        setAgentOutputs(prev => ({ ...prev, [out.agent_id]: out }));
        break;
      }

      case 'pong':
        break;

      default:
        console.log('[WS] Unknown event:', event_type, payload);
    }
  };

  const sendMessage = useCallback((content: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'chat', content }));
    } else {
      console.warn('[WS] Not connected — cannot send message');
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimeout.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return {
    connectionState,
    agents,
    messages,
    sprints,
    agentOutputs,
    isTyping,
    sendMessage,
  };
}
