/**
 * components/ChatWindow.jsx
 * --------------------------
 * The scrollable chat history area.
 * Shows all messages and a typing indicator when loading.
 */

import { useEffect } from 'react';
import ChatMessage, { TypingIndicator } from './ChatMessage';

// Welcome message shown when the conversation is empty
function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-6">
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600
                      flex items-center justify-center text-white text-2xl mb-4">
        🤖
      </div>
      <h2 className="text-lg font-semibold text-slate-700 mb-2">
        TechCorp Employee Assistant
      </h2>
      <p className="text-sm text-slate-500 max-w-sm leading-relaxed">
        Ask me about company policies, check your leave balance, or apply for leave.
        I use AI to find answers from company documents.
      </p>
      <div className="mt-6 grid grid-cols-1 gap-2 w-full max-w-sm">
        {[
          'What is the work from home policy?',
          'How many leaves do I have?',
          'Apply leave from 2026-10-06 to 2026-10-07 for personal work',
          'What are the employee benefits?',
        ].map((suggestion, i) => (
          <div
            key={i}
            className="text-xs text-left text-slate-500 bg-slate-100 rounded-lg px-3 py-2 italic"
          >
            "{suggestion}"
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ChatWindow({ messages, isLoading, messagesEndRef }) {
  // Auto-scroll when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto chat-scroll px-4 py-4">
      {messages.length === 0 && !isLoading ? (
        <EmptyState />
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          {isLoading && <TypingIndicator />}
          {/* Invisible element at the bottom to scroll to */}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}
