import React from 'react';

const TOOL_CONFIG = {
  search_company_documents: {
    label: 'Document Vector Search',
    icon: '🔍',
    color: 'bg-blue-950/60 text-blue-300 border-blue-800/40',
  },
  get_employee_info: {
    label: 'Employee Directory',
    icon: '👤',
    color: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/40',
  },
  apply_leave: {
    label: 'Leave Management Engine',
    icon: '📅',
    color: 'bg-purple-950/60 text-purple-300 border-purple-800/40',
  },
};

export default function ToolUsage({ tools }) {
  if (!tools || tools.length === 0) return null;

  return (
    <div className="mt-2.5 pt-2.5 border-t border-slate-800/80">
      <div className="flex items-center gap-1.5 mb-2">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Autonomous Agent Actions
        </span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {tools.map((tool, index) => {
          const conf = TOOL_CONFIG[tool] || {
            label: tool,
            icon: '⚡',
            color: 'bg-slate-800 text-slate-300 border-slate-700',
          };
          return (
            <span
              key={index}
              className={`inline-flex items-center gap-1.5 text-xs font-medium border rounded-md px-2.5 py-1 ${conf.color}`}
            >
              <span>{conf.icon}</span>
              <span>{conf.label}</span>
            </span>
          );
        })}
      </div>
    </div>
  );
}
