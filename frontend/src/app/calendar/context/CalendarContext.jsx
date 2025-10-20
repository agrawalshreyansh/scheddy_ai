'use client';

import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { fetchEventsByDateRange, fetchAllEvents } from '@/lib/api';
import { getStartOfWeek, getEndOfWeek, getStartOfMonth, getEndOfMonth } from '@/lib/dateUtils';

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
  const [events, setEvents] = useState([]);
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [eventsError, setEventsError] = useState(null);

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

  // Fetch events based on current view and date
  const fetchEvents = useCallback(async () => {
    setIsLoadingEvents(true);
    setEventsError(null);
    
    try {
      let startDate, endDate;
      
      if (view === 'Day') {
        startDate = new Date(currentDate);
        startDate.setHours(0, 0, 0, 0);
        endDate = new Date(currentDate);
        endDate.setHours(23, 59, 59, 999);
      } else if (view === 'Week') {
        startDate = getStartOfWeek(currentDate);
        endDate = getEndOfWeek(currentDate);
      } else if (view === 'Month') {
        startDate = getStartOfMonth(currentDate);
        endDate = getEndOfMonth(currentDate);
      }
      
      const fetchedEvents = await fetchEventsByDateRange(startDate, endDate);
      setEvents(fetchedEvents);
    } catch (error) {
      console.error('Error fetching events:', error);
      setEventsError(error.message);
      setEvents([]);
    } finally {
      setIsLoadingEvents(false);
    }
  }, [currentDate, view]);

  // Fetch events when view or date changes
  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  // Refresh events (call this after creating/updating/deleting events)
  const refreshEvents = () => {
    fetchEvents();
  };

  // Get events for a specific date
  const getEventsForDate = (date) => {
    return events.filter(event => {
      const eventDate = new Date(event.start_time);
      return (
        eventDate.getDate() === date.getDate() &&
        eventDate.getMonth() === date.getMonth() &&
        eventDate.getFullYear() === date.getFullYear()
      );
    });
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
    events,
    isLoadingEvents,
    eventsError,
    refreshEvents,
    getEventsForDate,
  };

  return (
    <CalendarContext.Provider value={value}>
      {children}
    </CalendarContext.Provider>
  );
};
