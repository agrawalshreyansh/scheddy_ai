'use client';

import { createContext, useContext, useState } from 'react';

const CalendarContext = createContext();

export const useCalendar = () => {
  const context = useContext(CalendarContext);
  if (!context) {
    throw new Error('useCalendar must be used within CalendarProvider');
  }
  return context;
};

export const CalendarProvider = ({ children }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState('Week'); // 'Day', 'Week', or 'Month'

  // Get the start of the week (Sunday)
  const getWeekStart = (date) => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day;
    return new Date(d.setDate(diff));
  };

  // Generate week days array
  const getWeekDays = (startDate) => {
    const days = [];
    for (let i = 0; i < 7; i++) {
      const day = new Date(startDate);
      day.setDate(startDate.getDate() + i);
      days.push(day);
    }
    return days;
  };

  // Navigation functions based on view
  const goToPrevious = () => {
    const newDate = new Date(currentDate);
    if (view === 'Day') {
      newDate.setDate(currentDate.getDate() - 1);
    } else if (view === 'Week') {
      newDate.setDate(currentDate.getDate() - 7);
    } else if (view === 'Month') {
      newDate.setMonth(currentDate.getMonth() - 1);
    }
    setCurrentDate(newDate);
  };

  const goToNext = () => {
    const newDate = new Date(currentDate);
    if (view === 'Day') {
      newDate.setDate(currentDate.getDate() + 1);
    } else if (view === 'Week') {
      newDate.setDate(currentDate.getDate() + 7);
    } else if (view === 'Month') {
      newDate.setMonth(currentDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  // Legacy functions for backward compatibility
  const goToPreviousWeek = () => {
    const newDate = new Date(currentDate);
    newDate.setDate(currentDate.getDate() - 7);
    setCurrentDate(newDate);
  };

  const goToNextWeek = () => {
    const newDate = new Date(currentDate);
    newDate.setDate(currentDate.getDate() + 7);
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Format date range for header display
  const getDateRangeString = () => {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const monthsFull = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];

    if (view === 'Day') {
      const month = months[currentDate.getMonth()];
      const day = currentDate.getDate();
      const year = currentDate.getFullYear();
      return `${month} ${day}, ${year}`;
    } else if (view === 'Week') {
      const weekStart = getWeekStart(currentDate);
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);
      
      const startMonth = months[weekStart.getMonth()];
      const endMonth = months[weekEnd.getMonth()];
      const startDay = weekStart.getDate();
      const endDay = weekEnd.getDate();
      const year = weekEnd.getFullYear();

      if (weekStart.getMonth() === weekEnd.getMonth()) {
        return `${startMonth} ${startDay} - ${endDay}, ${year}`;
      } else {
        return `${startMonth} ${startDay} - ${endMonth} ${endDay}, ${year}`;
      }
    } else if (view === 'Month') {
      const month = monthsFull[currentDate.getMonth()];
      const year = currentDate.getFullYear();
      return `${month} ${year}`;
    }
  };

  // Check if date is today
  const isToday = (date) => {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
  };

  const value = {
    currentDate,
    setCurrentDate,
    view,
    setView,
    getWeekStart,
    getWeekDays,
    goToPrevious,
    goToNext,
    goToPreviousWeek,
    goToNextWeek,
    goToToday,
    getDateRangeString,
    isToday,
  };

  return (
    <CalendarContext.Provider value={value}>
      {children}
    </CalendarContext.Provider>
  );
};
