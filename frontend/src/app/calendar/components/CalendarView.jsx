'use client';
import React, { useState } from 'react';
import { useCalendar } from '../context/CalendarContext';
import { deleteEvent, updateEvent } from '@/lib/api';
import { formatTime, formatTimeRange } from '@/lib/dateUtils';
import { getPriorityColor, getPriorityLabel, getDuration } from '@/lib/calendarHelpers';
import DayView from './views/DayView';
import WeekView from './views/WeekView';
import MonthView from './views/MonthView';

/**
 * CalendarView Component
 * Main calendar view that switches between Day, Week, and Month views
 */
const CalendarView = () => {
  const { view } = useCalendar();

  if (view === 'Day') {
    return <DayView />;
  } else if (view === 'Week') {
    return <WeekView />;
  } else if (view === 'Month') {
    return <MonthView />;
  }

  // Default to Week view
  return <WeekView />;
};

export default CalendarView;
