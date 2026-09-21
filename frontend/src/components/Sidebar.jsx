import React, { useState } from 'react';

const EMPLOYEES = [
  { id: 'EMP001', name: 'Rahul Sharma', dept: 'Engineering', initials: 'RS' },
  { id: 'EMP002', name: 'Priya Patel', dept: 'Product', initials: 'PP' },
  { id: 'EMP003', name: 'Arjun Mehta', dept: 'Design', initials: 'AM' },
  { id: 'EMP004', name: 'Sneha Gupta', dept: 'Engineering', initials: 'SG' },
  { id: 'EMP005', name: 'Vikram Nair', dept: 'Operations', initials: 'VN' },
];

const TOPIC_SHORTCUTS = [
  { icon: '🏠', title: 'Work From Home Rules', query: 'What is the work from home policy?' },
  { icon: '🌴', title: 'Check Leave Balance', query: 'How many leave days do I have remaining?' },
  { icon: '📅', title: 'Apply for Leave', query: 'Apply leave from 2026-10-06 to 2026-10-07 for personal work' },
  { icon: '💡', title: 'Employee Benefits', query: 'What are the employee benefits and medical insurance?' },
  { icon: '✈️', title: 'Travel & Expenses', query: 'What is our corporate travel and expense policy?' },
];

export default function Sidebar({
  isOpen,
  onToggle,
  onNewChat,
  onSelectPrompt,
  employeeId,
  onChangeEmployee,
}) {
  const [showEmployeeModal, setShowEmployeeModal] = useState(false);
  const currentEmp = EMPLOYEES.find((e) => e.id === employeeId) || EMPLOYEES[0];

  return (
    <>
      {/* Sidebar container */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-30 flex flex-col w-[260px] bg-[#171717] border-r border-white/5 transform transition-transform duration-200 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0 md:w-[260px]'
        } ${!isOpen ? 'md:hidden' : ''}`}
      >
        {/* Top Section: Brand & New Chat */}
        <div className="p-3">
          <div className="flex items-center justify-between mb-3 px-2">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md bg-white text-black flex items-center justify-center font-bold text-xs">
                EP
              </div>
              <span className="text-sm font-semibold text-white tracking-tight">
                Employee Portal
              </span>
            </div>
            {/* Close button on mobile */}
            <button
              onClick={onToggle}
              className="md:hidden text-slate-400 hover:text-white p-1"
            >
              ✕
            </button>
          </div>

          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-between px-3 py-2 text-sm text-white bg-[#212121] hover:bg-[#2f2f2f] border border-white/10 rounded-xl transition-colors shadow-sm"
          >
            <div className="flex items-center gap-2">
              <span className="text-base font-light">＋</span>
              <span className="font-medium">New chat</span>
            </div>
            <span className="text-xs text-slate-400 font-mono">⌘K</span>
          </button>
        </div>

        {/* Middle Section: Quick Policy Shortcuts */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 py-1.5">
            Quick Topics
          </div>
          {TOPIC_SHORTCUTS.map((item, idx) => (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.query)}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#212121] rounded-lg transition-colors text-left group"
            >
              <span className="text-sm opacity-80 group-hover:opacity-100">{item.icon}</span>
              <span className="truncate">{item.title}</span>
            </button>
          ))}
        </div>

        {/* Bottom Section: Active Employee Profile / Switcher */}
        <div className="p-3 border-t border-white/5 relative">
          <button
            onClick={() => setShowEmployeeModal(!showEmployeeModal)}
            className="w-full flex items-center justify-between p-2 rounded-xl hover:bg-[#212121] transition-colors text-left"
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs flex-shrink-0">
                {currentEmp.initials}
              </div>
              <div className="min-w-0">
                <div className="text-xs font-semibold text-white truncate">
                  {currentEmp.name}
                </div>
                <div className="text-[11px] text-slate-400 truncate">
                  {currentEmp.id} · {currentEmp.dept}
                </div>
              </div>
            </div>
            <span className="text-slate-400 text-xs">↕</span>
          </button>

          {/* Employee switch popup menu */}
          {showEmployeeModal && (
            <div className="absolute bottom-16 left-3 right-3 bg-[#212121] border border-white/10 rounded-xl shadow-2xl p-1.5 z-40">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 px-2.5 py-1">
                Switch Active Employee
              </div>
              {EMPLOYEES.map((emp) => (
                <button
                  key={emp.id}
                  onClick={() => {
                    onChangeEmployee(emp.id);
                    setShowEmployeeModal(false);
                  }}
                  className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-colors ${
                    emp.id === employeeId
                      ? 'bg-white/10 text-white font-medium'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-700 flex items-center justify-center text-[10px] font-bold">
                      {emp.initials}
                    </span>
                    <span>{emp.name}</span>
                  </div>
                  <span className="text-[10px] text-slate-400">{emp.id}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </aside>

      {/* Mobile backdrop */}
      {isOpen && (
        <div
          onClick={onToggle}
          className="fixed inset-0 bg-black/60 z-20 md:hidden backdrop-blur-sm"
        />
      )}
    </>
  );
}
