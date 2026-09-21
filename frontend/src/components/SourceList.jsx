import React from 'react';

/**
 * components/SourceList.jsx
 * Displays sources cited from ChromaDB in a refined modern pill layout.
 */
export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-800/80">
      <div className="flex items-center gap-1.5 mb-2">
        <span className="text-xs">📑</span>
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Cited Policy Documents
        </span>
      </div>
      <div className="flex flex-wrap gap-2">
        {sources.map((source, index) => (
          <div
            key={index}
            className="flex items-center gap-2 text-xs bg-slate-800/60 border border-slate-700/60 hover:border-indigo-500/40 text-slate-300 rounded-lg px-2.5 py-1.5 transition-colors"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            <span className="font-mono text-indigo-300 font-medium">{source.source}</span>
            {source.page && (
              <span className="text-[11px] px-1.5 py-0.5 rounded bg-slate-700/60 text-slate-400">
                p. {source.page}
              </span>
            )}
            {source.document_type && (
              <span className="text-[10px] uppercase font-bold text-slate-400">
                {source.document_type}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
