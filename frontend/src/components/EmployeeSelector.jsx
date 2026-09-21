import React from 'react';

const EMPLOYEES = [
  { id: 'EMP001', name: 'Rahul Sharma', dept: 'Engineering', initials: 'RS' },
  { id: 'EMP002', name: 'Priya Patel', dept: 'Product', initials: 'PP' },
  { id: 'EMP003', name: 'Arjun Mehta', dept: 'Design', initials: 'AM' },
  { id: 'EMP004', name: 'Sneha Gupta', dept: 'Engineering', initials: 'SG' },
  { id: 'EMP005', name: 'Vikram Nair', dept: 'Operations', initials: 'VN' },
];

export default function EmployeeSelector({ employeeId, onChange }) {
  const current = EMPLOYEES.find((e) => e.id === employeeId) || EMPLOYEES[0];

  return (
    <div className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 rounded-xl px-2.5 py-1.5 shadow-sm">
      {/* Employee initials avatar */}
      <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center text-[10px] font-bold text-white shadow-inner">
        {current.initials}
      </div>

      <div className="flex flex-col text-left pr-1">
        <select
          id="employee-select"
          value={employeeId}
          onChange={(e) => onChange(e.target.value)}
          className="text-xs bg-transparent text-slate-200 font-semibold cursor-pointer focus:outline-none hover:text-white transition-colors"
        >
          {EMPLOYEES.map((emp) => (
            <option key={emp.id} value={emp.id} className="bg-slate-900 text-slate-200">
              {emp.name} ({emp.id}) · {emp.dept}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
