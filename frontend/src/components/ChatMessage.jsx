import React, { useState } from 'react';
import SourceList from './SourceList';
import ToolUsage from './ToolUsage';
import MarkdownRenderer from './MarkdownRenderer';

function TypingIndicator() {
  return (
    <div className="flex items-start gap-4 py-3">
      <div className="w-7 h-7 rounded-full bg-white text-black flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
        EP
      </div>
      <div className="flex items-center gap-1.5 pt-2">
        <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
        <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
        <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
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
      <div className="flex justify-end my-4">
        <div className="bg-[#2f2f2f] text-white rounded-3xl px-4 py-2.5 max-w-[75%] shadow-sm">
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-start gap-4 my-4 p-4 rounded-2xl bg-rose-950/30 border border-rose-800/40 text-rose-200">
        <span className="text-base">⚠️</span>
        <p className="text-sm leading-relaxed">{message.content}</p>
      </div>
    );
  }

  // Assistant message (ChatGPT layout)
  return (
    <div className="flex items-start gap-4 my-6 group">
      {/* Bot Icon */}
      <div className="w-7 h-7 rounded-full bg-white text-black flex items-center justify-center text-xs font-bold flex-shrink-0 mt-1 shadow-sm">
        EP
      </div>

      <div className="flex-1 min-w-0">
        {/* Content */}
        <div className="text-[15px] leading-relaxed text-slate-100">
          <MarkdownRenderer content={message.content} />
        </div>

        {/* Source Citations */}
        <SourceList sources={message.sources} />

        {/* Tools Used */}
        <ToolUsage tools={message.tools_used} />

        {/* Actions Row */}
        <div className="flex items-center gap-3 mt-3 opacity-60 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleCopy}
            title="Copy answer"
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white p-1 rounded transition-colors"
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
      </div>
    </div>
  );
}

export { TypingIndicator };
