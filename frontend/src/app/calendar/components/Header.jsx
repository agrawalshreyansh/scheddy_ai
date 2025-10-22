// components/Header.jsx
'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useCalendar } from '../context/CalendarContext';

const Header = () => {
  const router = useRouter();
  const { goToPrevious, goToNext, goToToday, getDateRangeString, view, setView } = useCalendar();
  const [userInitials, setUserInitials] = useState('');
  const [avatarColor, setAvatarColor] = useState('bg-blue-500');

  // Load user data and generate initials
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        let firstName = '';
        let lastName = '';

        // Parse name if it's in full name format
        if (userData.full_name) {
          const nameParts = userData.full_name.trim().split(' ');
          firstName = nameParts[0] || '';
          lastName = nameParts.slice(1).join(' ') || '';
        }

        // Generate initials
        const firstInitial = firstName.trim().charAt(0).toUpperCase();
        const lastInitial = lastName.trim().charAt(0).toUpperCase();
        setUserInitials(firstInitial + lastInitial || '?');

        // Generate avatar color
        const colors = [
          'bg-blue-500',
          'bg-green-500',
          'bg-purple-500',
          'bg-pink-500',
          'bg-yellow-500',
          'bg-red-500',
          'bg-indigo-500',
          'bg-teal-500',
        ];
        const nameString = (firstName + lastName).toLowerCase();
        const index = nameString.charCodeAt(0) % colors.length;
        setAvatarColor(colors[index] || 'bg-blue-500');
      } catch (error) {
        console.error('Error parsing user data:', error);
        setUserInitials('?');
      }
    }
  }, []);

  return (
    <header className="flex items-center justify-between whitespace-nowrap border-b border-gray-200 dark:border-gray-700 px-6 py-3">
      <div className="flex items-center gap-6">
        <button 
          onClick={goToToday}
          className="hidden md:flex items-center justify-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 transition-colors hover:bg-gray-100 dark:hover:bg-gray-800">
          <span>Today</span>
        </button>
        
        <div className="flex items-center gap-1">
          <button 
            onClick={goToPrevious}
            className="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20">
            <ChevronLeft size={20} />
          </button>
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white min-w-[200px] text-center">{getDateRangeString()}</h3>
          <button 
            onClick={goToNext}
            className="rounded-full p-2 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20">
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 rounded-lg border border-gray-300 dark:border-gray-700 p-1">
          {['Day', 'Week', 'Month'].map((viewOption) => (
            <button
              key={viewOption}
              onClick={() => setView(viewOption)}
              className={`rounded-md px-3 py-1 text-sm font-medium transition-colors ${
                view === viewOption
                  ? 'text-white bg-[#137fec]'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20'
              }`}
            >
              {viewOption}
            </button>
          ))}
        </div>
        
        <button
          onClick={() => router.push('/profile')}
          className={`h-10 w-10 rounded-full ${avatarColor} flex items-center justify-center text-white text-sm font-bold hover:ring-2 hover:ring-[#137fec] transition-all cursor-pointer shadow-md`}
          aria-label="Go to profile"
        >
          {userInitials}
        </button>
      </div>
    </header>
  );
};

export default Header;