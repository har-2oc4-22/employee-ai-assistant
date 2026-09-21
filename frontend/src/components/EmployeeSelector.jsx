/**
 * components/EmployeeSelector.jsx
 * ---------------------------------
 * Dropdown to select the active employee ID.
 * When changed, the conversation is reset.
 */

const EMPLOYEES = [
  { id: 'EMP001', name: 'Rahul Sharma (EMP001)' },
  { id: 'EMP002', name: 'Priya Patel (EMP002)' },
  { id: 'EMP003', name: 'Arjun Mehta (EMP003)' },
  { id: 'EMP004', name: 'Sneha Gupta (EMP004)' },
  { id: 'EMP005', name: 'Vikram Nair (EMP005)' },
];

export default function EmployeeSelector({ employeeId, onChange }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm font-medium text-slate-600">Employee:</span>
      <select
        id="employee-select"
        value={employeeId}
        onChange={(e) => onChange(e.target.value)}
        className="text-sm bg-white border border-slate-200 rounded-lg px-3 py-1.5
                   text-slate-800 font-medium shadow-sm cursor-pointer
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                   hover:border-slate-300 transition-colors"
      >
        {EMPLOYEES.map((emp) => (
          <option key={emp.id} value={emp.id}>
            {emp.name}
          </option>
        ))}
      </select>
    </div>
  );
}
