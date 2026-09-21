import React, { useState } from 'react';
import SourceList from './SourceList';
import ToolUsage from './ToolUsage';
import MarkdownRenderer from './MarkdownRenderer';

/**
 * Loading indicator: three pulsing dots with AI avatar.
 */
function TypingIndicator() {
  return (
    <div className="flex items-start gap-3.5 mb-6 animate-pulse">
      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shadow-lg shadow-indigo-500/20 flex-shrink-0">
        ✨
      </div>
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 shadow-lg flex items-center gap-1.5">
        <span className="typing-dot w-2 h-2 bg-indigo-400 rounded-full" />
        <span className="typing-dot w-2 h-2 bg-indigo-400 rounded-full" />
        <span className="typing-dot w-2 h-2 bg-indigo-400 rounded-full" />
      </div>
    </div>
  );
}

export default function ChatMessage({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const isError = message.role === 'error';

  const handleCopy = () => {
    if (!message.content) return;
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isUser) {
    return (
      <div className="flex justify-end mb-6">
        <div className="flex items-end gap-2.5 max-w-[80%]">
          <div className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-lg shadow-indigo-600/10 border border-indigo-500/30">
            <p className="text-sm leading-relaxed whitespace-pre-wrap selection:bg-indigo-300 selection:text-indigo-900">
              {message.content}
            </p>
          </div>
          <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-xs text-slate-300 font-semibold flex-shrink-0">
            👤
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-start gap-3.5 mb-6">
        <div className="w-8 h-8 rounded-xl bg-rose-950/80 border border-rose-800/60 flex items-center justify-center text-rose-400 text-sm font-bold flex-shrink-0">
          ⚠️
        </div>
        <div className="bg-rose-950/30 border border-rose-800/50 rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%]">
          <p className="text-sm text-rose-300">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex items-start gap-3.5 mb-6 group">
      {/* AI Avatar */}
      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 via-purple-600 to-pink-500 flex items-center justify-center text-white text-xs font-bold shadow-lg shadow-indigo-500/20 flex-shrink-0 mt-0.5">
        ✨
      </div>

      {/* Message bubble */}
      <div className="bg-slate-900/90 border border-slate-800/90 rounded-2xl rounded-tl-sm px-5 py-4 shadow-xl max-w-[88%] relative group">
        {/* Top Header bar with Assistant label and Copy button */}
        <div className="flex items-center justify-between mb-2 text-xs border-b border-slate-800/60 pb-1.5">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-300 text-[11px] tracking-wide">
              Employee Portal Assistant
            </span>
            <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-950/70 text-indigo-400 border border-indigo-800/40">
              Gemini 3.6 Flash
            </span>
          </div>

          <button
            onClick={handleCopy}
            title="Copy answer"
            className="text-[11px] text-slate-400 hover:text-indigo-300 transition-colors flex items-center gap-1 opacity-70 hover:opacity-100"
          >
            {copied ? (
              <>
                <span className="text-emerald-400">✓</span>
                <span className="text-emerald-400">Copied</span>
              </>
            ) : (
              <>
                <span>📋</span>
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        {/* Answer text formatted with Markdown */}
        <div className="text-sm leading-relaxed text-slate-200">
          <MarkdownRenderer content={message.content} />
        </div>

        {/* Source documents cited from ChromaDB */}
        <SourceList sources={message.sources} />

        {/* Tools used by agent */}
        <ToolUsage tools={message.tools_used} />
      </div>
    </div>
  );
}

export { TypingIndicator };
