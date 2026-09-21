import { useState, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import EmployeeSelector from './components/EmployeeSelector';
import { useChat } from './hooks/useChat';

function SendIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
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
  const [sessionCopied, setSessionCopied] = useState(false);
  const inputRef = useRef(null);

  const handleSend = async (overrideText) => {
    const text = (overrideText || inputText).trim();
    if (!text || isLoading) return;
    setInputText('');
    await sendMessage(text);
    inputRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopySession = () => {
    if (!conversationId) return;
    navigator.clipboard.writeText(conversationId);
    setSessionCopied(true);
    setTimeout(() => setSessionCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-screen bg-[#0B0F19] text-slate-100 relative overflow-hidden font-sans">
      {/* Background ambient lighting */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header className="glass-header px-4 py-3 flex-shrink-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          {/* Logo & Branding */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-600 to-blue-500
                            flex items-center justify-center text-white text-lg shadow-lg shadow-indigo-500/20">
              🤖
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-bold text-white leading-tight tracking-tight">
                  Employee AI Assistant
                </h1>
                <span className="hidden sm:inline-flex items-center gap-1 text-[10px] font-medium text-emerald-400 bg-emerald-950/60 border border-emerald-800/40 rounded-full px-2 py-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 status-pulse" />
                  Online
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Employee Portal</p>
            </div>
          </div>

          {/* Right Controls: Employee Switcher & Reset */}
          <div className="flex items-center gap-2 sm:gap-3">
            <EmployeeSelector
              employeeId={employeeId}
              onChange={changeEmployee}
            />
            <button
              id="reset-conversation-btn"
              onClick={resetChat}
              title="Reset conversation and start new session"
              className="text-xs font-medium text-slate-400 hover:text-rose-300
                         bg-slate-900/80 hover:bg-rose-950/40 border border-slate-800 hover:border-rose-800/50
                         rounded-xl px-3 py-2 transition-all flex items-center gap-1.5 shadow-sm"
            >
              <span>↺</span>
              <span className="hidden sm:inline">New Chat</span>
            </button>
          </div>
        </div>
      </header>

      {/* ── Session ID Banner ────────────────────────────────────────────── */}
      {conversationId && (
        <div className="bg-slate-900/50 border-b border-slate-800/60 px-4 py-1 flex-shrink-0 z-10">
          <div className="max-w-4xl mx-auto flex items-center justify-between text-[11px] text-slate-400">
            <span className="font-mono truncate">
              Session: <span className="text-indigo-300">{conversationId}</span>
            </span>
            <button
              onClick={handleCopySession}
              className="hover:text-indigo-300 transition-colors ml-2 flex-shrink-0"
              title="Copy session ID"
            >
              {sessionCopied ? '✓ Copied' : '📋 Copy ID'}
            </button>
          </div>
        </div>
      )}

      {/* ── Chat Window ──────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-hidden max-w-4xl w-full mx-auto flex flex-col z-10">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          messagesEndRef={messagesEndRef}
          onSelectPrompt={(prompt) => handleSend(prompt)}
        />

        {/* ── Input Dock ───────────────────────────────────────────────── */}
        <div className="flex-shrink-0 glass-dock px-4 py-3">
          {/* Error banner */}
          {error && (
            <div className="max-w-3xl mx-auto mb-2 text-xs text-rose-300 bg-rose-950/50 border border-rose-800/60 rounded-xl px-3 py-2 flex items-center gap-2">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="max-w-3xl mx-auto">
            <div className="relative flex items-end gap-2 bg-slate-900/90 border border-slate-800 rounded-2xl p-1.5 shadow-xl focus-within:border-indigo-500/50 focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all">
              <textarea
                id="chat-input"
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about company policies, check leave balance, or apply for leave…"
                rows={1}
                disabled={isLoading}
                className="flex-1 bg-transparent resize-none px-3.5 py-2
                           text-sm text-slate-100 placeholder-slate-500
                           focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed
                           transition-colors leading-relaxed"
                style={{ maxHeight: '120px' }}
                onInput={(e) => {
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                }}
              />
              <button
                id="send-btn"
                onClick={() => handleSend()}
                disabled={!inputText.trim() || isLoading}
                className="flex-shrink-0 w-9 h-9 rounded-xl
                           bg-gradient-to-r from-indigo-600 to-blue-600 text-white
                           flex items-center justify-center
                           hover:from-indigo-500 hover:to-blue-500 active:scale-95
                           disabled:opacity-30 disabled:cursor-not-allowed
                           transition-all shadow-md shadow-indigo-600/20"
                title="Send message"
              >
                <SendIcon />
              </button>
            </div>

            <div className="flex items-center justify-between px-1.5 mt-2 text-[11px] text-slate-500">
              <span>Press <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">Enter</kbd> to send · <kbd className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">Shift+Enter</kbd> for new line</span>
              <span className="hidden sm:inline">RAG ChromaDB · Gemini 3.6 Flash</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
