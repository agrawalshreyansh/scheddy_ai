'use client';
import React, { useState } from 'react';
import { Plus, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';
import MiniCalendar from './sidebar/MiniCalendar';
import CreateEventModal from './modals/CreateEventModal';

/**
 * Sidebar Component
 * Left sidebar with app branding, create event button, mini calendar, and calendar filters
 */
const Sidebar = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const router = useRouter();

  const handleLogout = () => {
    // Clear all localStorage data
    localStorage.clear();
    // Redirect to auth page
    router.push('/auth');
  };

  return (
    <>
      <aside className="hidden w-64 flex-shrink-0 flex-col border-r border-[#101922]/10 dark:border-[#f6f7f8]/10 lg:flex p-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-20">Scheddy</h1>
        
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center justify-center gap-2 rounded-lg bg-[#137fec] px-2 py-2 text-sm font-medium text-white transition-colors hover:bg-[#137fec]/90 shadow-md cursor-pointer"
        >
          <Plus size={20} />
          <span>Create Event</span>
        </button>

        <MiniCalendar />

        <div className="mt-8">
          <h3 className="text-sm font-semibold text-gray-800 dark:text-white">My Calendars</h3>
          <div className="mt-4 space-y-3">
            {[
              { id: 'personal', label: 'Personal', checked: true },
              { id: 'work', label: 'Work', checked: true },
              { id: 'reminders', label: 'Reminders', checked: false },
            ].map((calendar) => (
              <label key={calendar.id} className="flex items-center gap-3">
                <input
                  type="checkbox"
                  defaultChecked={calendar.checked}
                  className="h-5 w-5 rounded border-gray-300 dark:border-gray-600 bg-transparent text-[#137fec] focus:ring-[#137fec] dark:ring-offset-[#101922]"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">{calendar.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Logout Button */}
        <div className="mt-auto pt-4">
          <button 
            onClick={handleLogout}
            className="flex items-center justify-center gap-2 w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-[#1a2332] px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 transition-all hover:border-[#137fec] hover:text-[#137fec] hover:bg-gray-50 dark:hover:bg-[#101922] shadow-sm"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      <CreateEventModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  );
};

export default Sidebar;
