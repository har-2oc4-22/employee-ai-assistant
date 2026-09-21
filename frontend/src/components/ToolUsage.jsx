/**
 * components/ToolUsage.jsx
 * -------------------------
 * Shows which tools the agent used to answer the question.
 * Helps the user understand how the AI reasoned about their query.
 */

const TOOL_LABELS = {
  search_company_documents: '🔍 search_company_documents',
  get_employee_info: '👤 get_employee_info',
  apply_leave: '📅 apply_leave',
};

export default function ToolUsage({ tools }) {
  if (!tools || tools.length === 0) return null;

  return (
    <div className="mt-2 pt-2 border-t border-slate-100">
      <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1.5">
        Tools Used
      </p>
      <div className="flex flex-wrap gap-1.5">
        {tools.map((tool, index) => (
          <span
            key={index}
            className="inline-flex items-center gap-1 text-xs font-medium
                       bg-emerald-50 text-emerald-700 border border-emerald-200
                       rounded-full px-2.5 py-1"
          >
            ✓ {TOOL_LABELS[tool] || tool}
          </span>
        ))}
      </div>
    </div>
  );
}
