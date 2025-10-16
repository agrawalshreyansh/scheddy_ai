'use client';

import React from 'react';
import { useCalendar } from '../context/CalendarContext';

const CalendarView = () => {
  const { view } = useCalendar();

  if (view === 'Day') {
    return <DayView />;
  } else if (view === 'Week') {
    return <WeekView />;
  } else if (view === 'Month') {
    return <MonthView />;
  }
};

// Week View Component
const WeekView = () => {
  const { currentDate, getWeekStart, getWeekDays, isToday } = useCalendar();

  const weekStart = getWeekStart(currentDate);
  const weekDays = getWeekDays(weekStart);

  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Calculate current time position
  const getCurrentTimePosition = () => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    // Each hour is 60px (min-h-[60px]), calculate position
    const position = (hours * 60) + (minutes / 60 * 60) + 48; // 48px for header approx
    return position;
  };

  // Check if today is in current week
  const showCurrentTime = weekDays.some(day => isToday(day));
  const currentTimePosition = showCurrentTime ? getCurrentTimePosition() : 0;

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-[#101922] overflow-hidden">
      {/* Week view grid */}
      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-8 min-w-full relative">
          {/* Current time indicator */}
          {showCurrentTime && (
            <div 
              className="absolute left-0 right-0 z-20 pointer-events-none col-span-8"
              style={{ top: `${currentTimePosition}px` }}
            >
              <div className="grid grid-cols-8">
                <div className="flex items-center justify-end pr-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                </div>
                <div className="col-span-7 h-0.5 bg-red-500"></div>
              </div>
            </div>
          )}

          {/* Time column header */}
          <div className="sticky top-0 bg-white dark:bg-[#101922] border-r border-b border-gray-200 dark:border-gray-700 p-2 z-10">
            <span className="text-xs text-gray-500 dark:text-gray-400">Time</span>
          </div>

          {/* Day headers */}
          {weekDays.map((day, index) => {
            const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            const today = isToday(day);
            
            return (
              <div
                key={index}
                className={`sticky top-0 bg-white dark:bg-[#101922] border-r border-b border-gray-200 dark:border-gray-700 p-2 text-center z-10 ${
                  today ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                }`}
              >
                <div className="text-xs text-gray-500 dark:text-gray-400">{dayNames[day.getDay()]}</div>
                <div className={`text-lg font-semibold ${today ? 'text-blue-600 dark:text-blue-400' : 'text-gray-900 dark:text-white'}`}>
                  {day.getDate()}
                </div>
              </div>
            );
          })}

          {/* Time slots */}
          {hours.map((hour) => (
            <React.Fragment key={hour}>
              {/* Time label */}
              <div
                className="border-r border-b border-gray-200 dark:border-gray-700 p-2 text-right text-xs text-gray-500 dark:text-gray-400"
              >
                {hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`}
              </div>

              {/* Day cells */}
              {weekDays.map((_, dayIndex) => (
                <div
                  key={`${hour}-${dayIndex}`}
                  className="border-r border-b border-gray-200 dark:border-gray-700 p-2 min-h-[60px] hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                />
              ))}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};

// Day View Component
const DayView = () => {
  const { currentDate, isToday } = useCalendar();
  const hours = Array.from({ length: 24 }, (_, i) => i);
  const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const today = isToday(currentDate);

  // Calculate current time position
  const getCurrentTimePosition = () => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    // Each hour is 96px (h-24), calculate position
    const position = (hours * 96) + (minutes / 60 * 96) + 64; // 64px for header
    return position;
  };

  const showCurrentTime = today;
  const currentTimePosition = showCurrentTime ? getCurrentTimePosition() : 0;

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-[#101922] overflow-hidden">
      <div className="flex-1 overflow-auto">
        <div className="flex min-w-full relative">
          {/* Current time indicator */}
          {showCurrentTime && (
            <div 
              className="absolute left-0 right-0 z-20 pointer-events-none"
              style={{ top: `${currentTimePosition}px` }}
            >
              <div className="flex items-center">
                <div className="w-20 flex items-center justify-end pr-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                </div>
                <div className="flex-1 h-0.5 bg-red-500"></div>
              </div>
            </div>
          )}

          {/* Time column - narrow */}
          <div className="w-20 flex-shrink-0">
            {/* Time column header */}
            <div className="sticky top-0 bg-white dark:bg-[#101922] border-r border-b border-gray-200 dark:border-gray-700 p-2 z-10 h-16">
              <span className="text-xs text-gray-500 dark:text-gray-400">Time</span>
            </div>
            {/* Time labels */}
            {hours.map((hour) => (
              <div
                key={`time-${hour}`}
                className="border-r border-b border-gray-200 dark:border-gray-700 p-2 text-right text-xs text-gray-500 dark:text-gray-400 h-24"
              >
                {hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`}
              </div>
            ))}
          </div>

          {/* Day column - wide */}
          <div className="flex-1">
            {/* Day header */}
            <div
              className={`sticky top-0 bg-white dark:bg-[#101922] border-r border-b border-gray-200 dark:border-gray-700 p-4 z-10 h-16 ${
                today ? 'bg-blue-50 dark:bg-blue-900/20' : ''
              }`}
            >
              <div className="flex items-center gap-3">
                <div className={`text-2xl font-bold ${today ? 'text-blue-600 dark:text-blue-400' : 'text-gray-900 dark:text-white'}`}>
                  {currentDate.getDate()}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">{dayNames[currentDate.getDay()]}</div>
              </div>
            </div>

            {/* Time slots */}
            {hours.map((hour) => (
              <div
                key={hour}
                className="border-r border-b border-gray-200 dark:border-gray-700 p-4 h-24 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
              >
                {/* Events/tasks will appear here */}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Month View Component
const MonthView = () => {
  const { currentDate, isToday } = useCalendar();

  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  };

  const getLastDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0);
  };

  const firstDay = getFirstDayOfMonth(currentDate);
  const lastDay = getLastDayOfMonth(currentDate);
  const startingDayOfWeek = firstDay.getDay();
  const numberOfDays = lastDay.getDate();

  const isTodayDate = (day) => {
    const checkDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    return isToday(checkDate);
  };

  const renderCalendarDays = () => {
    const days = [];

    // Empty cells for days before 1st
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(
        <div key={`empty-${i}`} className="border border-gray-200 dark:border-gray-700 p-2 bg-gray-50 dark:bg-gray-900/20"></div>
      );
    }

    // Days of the month
    for (let day = 1; day <= numberOfDays; day++) {
      const today = isTodayDate(day);

      days.push(
        <div
          key={day}
          className="border border-gray-200 dark:border-gray-700 p-2 min-h-[100px] hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
        >
          <div className={`text-sm font-semibold mb-1 ${today ? 'text-blue-600 dark:text-blue-400' : 'text-gray-900 dark:text-white'}`}>
            {today && <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-white text-xs">{day}</span>}
            {!today && day}
          </div>
        </div>
      );
    }

    return days;
  };

  return (
    <div className="flex-1 flex flex-col bg-white dark:bg-[#101922] overflow-hidden">
      <div className="flex-1 overflow-auto">
        <div className="h-full flex flex-col">
          {/* Day headers */}
          <div className="grid grid-cols-7 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-[#101922] z-10">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day, idx) => (
              <div key={idx} className="border-r border-gray-200 dark:border-gray-700 p-2 text-center text-sm font-semibold text-gray-700 dark:text-gray-300 last:border-r-0">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7 flex-1">
            {renderCalendarDays()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarView;