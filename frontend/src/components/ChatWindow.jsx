import React, { useEffect } from 'react';
import ChatMessage, { TypingIndicator } from './ChatMessage';

const SUGGESTED_PROMPTS = [
  {
    title: 'Work From Home Policy',
    desc: 'Check eligibility, weekly allowances & manager approval rules',
    prompt: 'What is the work from home policy?',
  },
  {
    title: 'Check Leave Balance',
    desc: 'Look up your remaining paid leave balance in the directory',
    prompt: 'How many leave days do I have remaining?',
  },
  {
    title: 'Apply for Leave',
    desc: 'Submit a new leave request and validate balance deduction',
    prompt: 'Apply leave from 2026-10-06 to 2026-10-07 for personal work',
  },
  {
    title: 'Employee Benefits',
    desc: 'Explore health insurance, learning allowance & perks',
    prompt: 'What are the health insurance and employee benefits?',
  },
];

function EmptyState({ onSelectPrompt }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-2xl mx-auto text-center px-4">
      {/* Title */}
      <h1 className="text-2xl sm:text-3xl font-semibold text-white mb-8 tracking-tight">
        What can I help with today?
      </h1>

      {/* Suggested Prompt Cards (ChatGPT style grid) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
        {SUGGESTED_PROMPTS.map((item, i) => (
          <button
            key={i}
            onClick={() => onSelectPrompt && onSelectPrompt(item.prompt)}
            className="p-4 rounded-2xl bg-[#212121] hover:bg-[#2f2f2f] border border-white/10 hover:border-white/20 transition-all duration-150 text-left group shadow-sm flex flex-col justify-between"
          >
            <div className="text-sm font-medium text-slate-100 group-hover:text-white mb-1">
              {item.title}
            </div>
            <div className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
              {item.desc}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function ChatWindow({ messages, isLoading, messagesEndRef, onSelectPrompt }) {
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading, messagesEndRef]);

  return (
    <div className="flex-1 overflow-y-auto chat-scroll px-4 md:px-8 py-6">
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
