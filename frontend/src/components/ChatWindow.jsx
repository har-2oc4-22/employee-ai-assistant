import React, { useEffect } from 'react';
import ChatMessage, { TypingIndicator } from './ChatMessage';

// Quick action cards
const SUGGESTED_PROMPTS = [
  {
    icon: '🏠',
    title: 'Work From Home Policy',
    prompt: 'What is the work from home policy?',
    desc: 'Check eligibility, weekly limits & approval guidelines',
  },
  {
    icon: '🌴',
    title: 'Check Leave Balance',
    prompt: 'How many leave days do I have remaining?',
    desc: 'Autonomous lookup from employee database',
  },
  {
    icon: '📅',
    title: 'Apply for Leave',
    prompt: 'Apply leave from 2026-10-06 to 2026-10-07 for personal work',
    desc: 'Verify balance & submit leave request',
  },
  {
    icon: '💡',
    title: 'Employee Benefits',
    prompt: 'What are the health insurance and employee benefits?',
    desc: 'Medical coverage, allowances & perks',
  },
];

function EmptyState({ onSelectPrompt }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[480px] text-center px-4 py-8">
      {/* Glow aura & icon */}
      <div className="relative mb-5">
        <div className="absolute inset-0 bg-indigo-500/20 rounded-full blur-xl animate-pulse" />
        <div className="relative w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-blue-500 flex items-center justify-center text-white text-3xl shadow-xl shadow-indigo-500/30">
          🤖
        </div>
      </div>

      <h2 className="text-xl font-bold text-white tracking-tight mb-1.5">
        Employee Portal Assistant
      </h2>
      <div className="flex items-center gap-2 mb-3">
        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-indigo-300 bg-indigo-950/70 border border-indigo-800/40 rounded-full px-2.5 py-0.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 status-pulse" />
          RAG Vector Engine + Multi-Tool Agent
        </span>
      </div>

      <p className="text-xs text-slate-400 max-w-md leading-relaxed mb-6">
        Ask questions about workplace policies, verify your balance, or submit leave requests. Your assistant reasons dynamically across company policies and internal records.
      </p>

      {/* Suggested Prompt Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl text-left">
        {SUGGESTED_PROMPTS.map((item, i) => (
          <button
            key={i}
            onClick={() => onSelectPrompt && onSelectPrompt(item.prompt)}
            className="group p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/50 hover:bg-slate-800/80 transition-all duration-200 text-left shadow-lg flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xl">{item.icon}</span>
              <span className="text-[11px] font-medium text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity">
                Try ➔
              </span>
            </div>
            <div>
              <div className="text-xs font-semibold text-slate-200 group-hover:text-white transition-colors">
                {item.title}
              </div>
              <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                {item.desc}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function ChatWindow({ messages, isLoading, messagesEndRef, onSelectPrompt }) {
  // Auto-scroll on message updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, messagesEndRef]);

  return (
    <div className="flex-1 overflow-y-auto chat-scroll px-4 py-6">
      {messages.length === 0 ? (
        <EmptyState onSelectPrompt={onSelectPrompt} />
      ) : (
        <div className="max-w-3xl mx-auto">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
}
