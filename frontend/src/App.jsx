/**
 * App.jsx
 * --------
 * Root application component.
 * Assembles the header, employee selector, chat window, and input bar.
 * All state logic lives in the useChat hook — this file is pure UI.
 */

import { useState, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import EmployeeSelector from './components/EmployeeSelector';
import { useChat } from './hooks/useChat';

/**
 * Send button icon
 */
function SendIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
      <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
    </svg>
  );
}

export default function App() {
  const {
    messages,
    isLoading,
    error,
    conversationId,
    employeeId,
    messagesEndRef,
    sendMessage,
    resetChat,
    changeEmployee,
  } = useChat();

  const [inputText, setInputText] = useState('');
  const inputRef = useRef(null);

  const handleSend = async () => {
    const text = inputText.trim();
    if (!text || isLoading) return;
    setInputText('');
    await sendMessage(text);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    // Send on Enter (but not Shift+Enter, which inserts a newline)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50">

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header className="bg-white border-b border-slate-200 shadow-sm px-4 py-3 flex-shrink-0">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600
                            flex items-center justify-center text-white text-lg">
              🤖
            </div>
            <div>
              <h1 className="text-base font-bold text-slate-900 leading-tight">
                Employee AI Assistant
              </h1>
              <p className="text-xs text-slate-500">TechCorp Internal Tool</p>
            </div>
          </div>

          {/* Right side: employee selector + reset button */}
          <div className="flex items-center gap-3">
            <EmployeeSelector
              employeeId={employeeId}
              onChange={changeEmployee}
            />
            <button
              id="reset-conversation-btn"
              onClick={resetChat}
              title="Reset conversation"
              className="text-xs font-medium text-slate-500 hover:text-red-500
                         bg-slate-100 hover:bg-red-50 border border-slate-200 hover:border-red-200
                         rounded-lg px-3 py-1.5 transition-colors"
            >
              ↺ Reset
            </button>
          </div>
        </div>
      </header>

      {/* ── Conversation ID badge (useful for debugging) ─────────────────── */}
      {conversationId && (
        <div className="bg-slate-100 border-b border-slate-200 px-4 py-1 flex-shrink-0">
          <p className="max-w-4xl mx-auto text-xs text-slate-400 font-mono">
            Session: {conversationId}
          </p>
        </div>
      )}

      {/* ── Chat Window ──────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-hidden max-w-4xl w-full mx-auto flex flex-col">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          messagesEndRef={messagesEndRef}
        />

        {/* ── Input Bar ───────────────────────────────────────────────── */}
        <div className="flex-shrink-0 border-t border-slate-200 bg-white px-4 py-3">
          {/* Error banner */}
          {error && (
            <div className="mb-2 text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              ⚠️ {error}
            </div>
          )}

          <div className="flex items-end gap-2">
            <textarea
              id="chat-input"
              ref={inputRef}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask something about company policy, your leave, or apply for leave…"
              rows={1}
              disabled={isLoading}
              className="flex-1 resize-none border border-slate-200 rounded-xl px-4 py-2.5
                         text-sm text-slate-900 placeholder-slate-400
                         focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                         disabled:opacity-50 disabled:cursor-not-allowed
                         transition-colors leading-relaxed"
              style={{ maxHeight: '120px' }}
              onInput={(e) => {
                // Auto-grow the textarea
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
            />
            <button
              id="send-btn"
              onClick={handleSend}
              disabled={!inputText.trim() || isLoading}
              className="flex-shrink-0 w-10 h-10 rounded-xl
                         bg-gradient-to-br from-blue-600 to-indigo-600 text-white
                         flex items-center justify-center
                         hover:from-blue-700 hover:to-indigo-700
                         disabled:opacity-40 disabled:cursor-not-allowed
                         transition-all shadow-sm"
            >
              <SendIcon />
            </button>
          </div>

          <p className="text-xs text-slate-400 mt-1.5 text-center">
            Press Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
