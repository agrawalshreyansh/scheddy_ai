'use client';
import React from 'react';
import { useCalendar } from '../../context/CalendarContext';
import { ChevronLeft, ChevronRight } from 'lucide-react';

/**
 * MiniCalendar Component
 * Small calendar widget in the sidebar for quick date navigation
 */
const MiniCalendar = () => {
  const { currentDate, setCurrentDate, isToday } = useCalendar();

  // Get current month info
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  
  // Get first day of month
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  
  // Get day of week for first day (0 = Sunday)
  const startingDayOfWeek = firstDay.getDay();
  const daysInMonth = lastDay.getDate();

  // Navigate to previous month
  const previousMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  // Navigate to next month
  const nextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  // Navigate to specific date
  const selectDate = (day) => {
    setCurrentDate(new Date(year, month, day));
  };

  // Generate calendar days
  const generateCalendarDays = () => {
    const days = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className="h-8" />);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const isCurrentDay = isToday(date);
      const isSelected = currentDate.getDate() === day && 
                         currentDate.getMonth() === month && 
                         currentDate.getFullYear() === year;
      
      days.push(
        <button
          key={day}
          onClick={() => selectDate(day)}
          className={`
            h-8 w-8 rounded-full text-sm font-medium transition-colors
            ${isCurrentDay 
              ? 'bg-[#137fec] text-white hover:bg-[#137fec]/90' 
              : isSelected
                ? 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
            }
          `}
        >
          {day}
        </button>
      );
    }
    
    return days;
  };

  return (
    <div className="mt-8">
      {/* Month/Year header with navigation */}
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={previousMonth}
          className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
          aria-label="Previous month"
        >
          <ChevronLeft size={20} />
        </button>
        
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
        </h3>
        
        <button
          onClick={nextMonth}
          className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300"
          aria-label="Next month"
        >
          <ChevronRight size={20} />
        </button>
      </div>

      {/* Days of week header */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => (
          <div
            key={day}
            className="h-8 flex items-center justify-center text-xs font-medium text-gray-500 dark:text-gray-400"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-1">
        {generateCalendarDays()}
      </div>
    </div>
  );
};

export default MiniCalendar;
