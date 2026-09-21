/**
 * components/ChatMessage.jsx
 * ---------------------------
 * Renders a single chat message (user, assistant, or error).
 * 
 * Assistant messages include:
 *   - The answer text
 *   - Source documents (if RAG was used)
 *   - Tools used
 */

import SourceList from './SourceList';
import ToolUsage from './ToolUsage';

/**
 * Loading indicator: three bouncing dots shown while waiting for the backend.
 */
function TypingIndicator() {
  return (
    <div className="flex items-end gap-3 mb-4">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600
                      flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
        AI
      </div>
      {/* Bubble */}
      <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
        <div className="flex items-center gap-1">
          <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
          <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
          <span className="typing-dot w-2 h-2 bg-slate-400 rounded-full" />
        </div>
      </div>
    </div>
  );
}

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  const isError = message.role === 'error';
  const isAssistant = message.role === 'assistant';

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[75%] bg-gradient-to-br from-blue-600 to-indigo-600
                        text-white rounded-2xl rounded-br-sm px-4 py-3 shadow-sm">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-start gap-3 mb-4">
        <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center
                        text-red-500 text-xs font-bold flex-shrink-0">
          !
        </div>
        <div className="bg-red-50 border border-red-200 rounded-2xl rounded-bl-sm px-4 py-3 max-w-[80%]">
          <p className="text-sm text-red-700">{message.content}</p>
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex items-start gap-3 mb-4">
      {/* AI Avatar */}
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600
                      flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
        AI
      </div>

      {/* Message bubble */}
      <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm px-4 py-3
                      shadow-sm max-w-[80%]">
        {/* Answer text */}
        <p className="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>

        {/* Source documents */}
        <SourceList sources={message.sources} />

        {/* Tools used */}
        <ToolUsage tools={message.tools_used} />
      </div>
    </div>
  );
}

export { TypingIndicator };
