import { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import { useChat } from './hooks/useChat';

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
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessionCopied, setSessionCopied] = useState(false);
  const inputRef = useRef(null);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Keyboard shortcut: Cmd/Ctrl + K for new chat
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        resetChat();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [resetChat]);

  const handleSend = async (overrideText) => {
    const text = (overrideText || inputText).trim();
    if (!text || isLoading) return;
    setInputText('');
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }
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
    <div className="flex h-screen w-screen bg-[#212121] text-[#ececec] overflow-hidden font-sans select-text">
      {/* ── ChatGPT Left Sidebar ────────────────────────────────────────── */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onNewChat={resetChat}
        onSelectPrompt={(prompt) => handleSend(prompt)}
        employeeId={employeeId}
        onChangeEmployee={changeEmployee}
      />

      {/* ── Main Chat Area ──────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col h-full min-w-0 relative bg-[#212121]">
        {/* ── Top Bar (ChatGPT Style) ──────────────────────────────────── */}
        <header className="h-14 flex items-center justify-between px-4 border-b border-white/5 bg-[#212121]/90 backdrop-blur-sm flex-shrink-0 z-10">
          <div className="flex items-center gap-3">
            {/* Sidebar toggle button */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors"
              title="Toggle sidebar"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            </button>

            {/* Model / Workspace Selector Pill */}
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-xl hover:bg-white/5 transition-colors cursor-default">
              <span className="text-base font-semibold text-white tracking-tight">
                Employee Portal
              </span>
              <span className="text-xs text-slate-400 font-normal">
                3.5 Flash
              </span>
              <span className="text-xs text-slate-500">⌵</span>
            </div>
          </div>

          {/* Right Header Actions */}
          <div className="flex items-center gap-2">
            {conversationId && (
              <button
                onClick={handleCopySession}
                className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-white/5 border border-white/5 transition-colors font-mono"
                title="Copy conversation session ID"
              >
                <span>{sessionCopied ? '✓' : '📋'}</span>
                <span className="truncate max-w-[120px]">
                  {sessionCopied ? 'Copied' : conversationId.slice(0, 8) + '...'}
                </span>
              </button>
            )}

            <button
              onClick={resetChat}
              className="text-xs text-slate-400 hover:text-white px-3 py-1.5 rounded-lg hover:bg-white/5 border border-white/5 transition-colors"
              title="Start a new chat session"
            >
              New chat
            </button>
          </div>
        </header>

        {/* ── Chat Messages Flow ────────────────────────────────────────── */}
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          messagesEndRef={messagesEndRef}
          onSelectPrompt={(prompt) => handleSend(prompt)}
        />

        {/* ── Floating Bottom Input Dock (ChatGPT signature) ─────────────── */}
        <div className="flex-shrink-0 px-4 pb-4 pt-2 bg-gradient-to-t from-[#212121] via-[#212121] to-transparent">
          <div className="max-w-3xl w-full mx-auto">
            {/* Error banner */}
            {error && (
              <div className="mb-3 text-xs text-rose-300 bg-rose-950/40 border border-rose-800/40 rounded-xl px-4 py-2.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span>⚠️</span>
                  <span>{error}</span>
                </div>
                <button
                  onClick={() => resetChat()}
                  className="underline hover:text-white text-xs ml-2"
                >
                  Start New Session
                </button>
              </div>
            )}

            {/* Input Pill Box */}
            <div className="relative flex items-end gap-2 bg-[#2f2f2f] border border-white/10 rounded-[28px] px-4 py-3 shadow-xl focus-within:border-white/20 transition-colors">
              <textarea
                id="chat-input"
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Message Employee Portal..."
                rows={1}
                disabled={isLoading}
                className="flex-1 bg-transparent resize-none text-[15px] text-slate-100 placeholder-slate-400 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed leading-relaxed"
                style={{ maxHeight: '160px' }}
                onInput={(e) => {
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px';
                }}
              />

              {/* Up-arrow Send Button (ChatGPT style) */}
              <button
                id="send-btn"
                onClick={() => handleSend()}
                disabled={!inputText.trim() || isLoading}
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                  inputText.trim() && !isLoading
                    ? 'bg-white text-black hover:bg-slate-200 active:scale-95 shadow-md'
                    : 'bg-[#424242] text-slate-500 cursor-not-allowed opacity-60'
                }`}
                title="Send prompt"
              >
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4 font-bold">
                  <path fillRule="evenodd" d="M11.47 2.47a.75.75 0 011.06 0l7.5 7.5a.75.75 0 11-1.06 1.06l-6.22-6.22V21a.75.75 0 01-1.5 0V4.81l-6.22 6.22a.75.75 0 11-1.06-1.06l7.5-7.5z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            {/* Disclaimer subtitle */}
            <p className="text-[11px] text-slate-500 text-center mt-2 font-normal">
              Employee Portal can make mistakes. Verify critical leave and HR policy decisions with HR.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
