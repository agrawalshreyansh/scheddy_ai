'use client';
import React, { useState } from 'react';
import { useCalendar } from '../../context/CalendarContext';
import { formatTime } from '@/lib/dateUtils';
import { getPriorityColor } from '@/lib/calendarHelpers';
import EventDetailModal from '../modals/EventDetailModal';

/**
 * MonthView Component
 * Displays a monthly calendar grid with events
 */
const MonthView = () => {
  const { currentDate, isToday, getEventsForDate, refreshEvents } = useCalendar();
  const [selectedEvent, setSelectedEvent] = useState(null);

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

  const getEventsForDay = (day) => {
    const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
    return getEventsForDate(date);
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
      const dayEvents = getEventsForDay(day);

      days.push(
        <div
          key={day}
          className="border border-gray-200 dark:border-gray-700 p-2 min-h-[100px] hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer overflow-hidden"
        >
          <div className={`text-sm font-semibold mb-1 ${today ? 'text-blue-600 dark:text-blue-400' : 'text-gray-900 dark:text-white'}`}>
            {today && <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-600 text-white text-xs">{day}</span>}
            {!today && day}
          </div>
          {/* Render events for this day */}
          <div className="space-y-1">
            {dayEvents.slice(0, 3).map((event, idx) => (
              <div 
                key={event.id || idx}
                className={`${getPriorityColor(event.priority_number)} text-white text-xs px-2 py-1 rounded truncate cursor-pointer hover:opacity-80`}
                onClick={() => setSelectedEvent(event)}
              >
                {formatTime(event.start_time)} {event.task_title}
              </div>
            ))}
            {dayEvents.length > 3 && (
              <div className="text-xs text-gray-500 dark:text-gray-400 pl-2">
                +{dayEvents.length - 3} more
              </div>
            )}
          </div>
        </div>
      );
    }

    return days;
  };

  return (
    <>
      {/* Event Detail Modal */}
      {selectedEvent && (
        <EventDetailModal 
          event={selectedEvent} 
          onClose={() => setSelectedEvent(null)}
          onEventUpdated={refreshEvents}
        />
      )}
      
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
    </>
  );
};

export default MonthView;
