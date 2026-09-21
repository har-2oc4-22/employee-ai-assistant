/**
 * components/SourceList.jsx
 * --------------------------
 * Displays the list of source documents cited in a RAG response.
 * Only rendered when sources array is non-empty.
 */

export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-100">
      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
        📄 Sources
      </p>
      <ul className="space-y-1">
        {sources.map((source, index) => (
          <li
            key={index}
            className="flex items-center gap-2 text-xs text-slate-600
                       bg-blue-50 rounded-md px-2 py-1.5"
          >
            <span className="text-blue-500">📋</span>
            <span className="font-medium">{source.source}</span>
            {source.page && (
              <span className="text-slate-400 ml-auto">Page {source.page}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
