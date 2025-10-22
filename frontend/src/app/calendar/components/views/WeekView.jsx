'use client';
import React, { useState, useEffect, useRef } from 'react';
import { useCalendar } from '../../context/CalendarContext';
import { getEventTopPosition, getEventHeight } from '@/lib/dateUtils';
import EventCard from '../common/EventCard';
import EventDetailModal from '../modals/EventDetailModal';

/**
 * WeekView Component
 * Displays a week view with 7 days and hourly time slots
 */
const WeekView = () => {
  const { currentDate, getWeekStart, getWeekDays, isToday, getEventsForDate, refreshEvents } = useCalendar();
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showCurrentTime, setShowCurrentTime] = useState(false);
  const [currentTimePosition, setCurrentTimePosition] = useState(0);
  const scrollContainerRef = useRef(null);

  const weekStart = getWeekStart(currentDate);
  const weekDays = getWeekDays(weekStart);
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Calculate current time position (client-side only)
  useEffect(() => {
    const calculateTimePosition = () => {
      // Check if today is in current week
      const isTodayInWeek = weekDays.some(day => isToday(day));
      setShowCurrentTime(isTodayInWeek);

      if (isTodayInWeek) {
        const now = new Date();
        const hours = now.getHours();
        const minutes = now.getMinutes();
        // Each hour is 60px (min-h-[60px]), calculate position
        const position = (hours * 60) + (minutes / 60 * 60) + 60; // 60px for header
        setCurrentTimePosition(position);
      }
    };

    // Calculate on mount (client-side only)
    calculateTimePosition();

    // Update every minute
    const interval = setInterval(calculateTimePosition, 60000);
    return () => clearInterval(interval);
  }, [weekDays, isToday]);

  // Auto-scroll to current time on mount
  useEffect(() => {
    if (scrollContainerRef.current && showCurrentTime) {
      // Scroll to current time with some offset to center it in the view
      const offset = 200;
      scrollContainerRef.current.scrollTop = Math.max(0, currentTimePosition - offset);
    }
  }, [currentTimePosition, showCurrentTime]);

  // Render events for each day
  const renderEventsForDay = (day, dayIndex) => {
    const dayEvents = getEventsForDate(day);
    
    return dayEvents.map((event, idx) => {
      const topPosition = getEventTopPosition(event.start_time, 60) + 60; // 60px for header
      const height = Math.max(getEventHeight(event.start_time, event.end_time, 60), 30); // Minimum 30px
      
      return (
        <div
          key={event.id || idx}
          className="absolute z-30"
          style={{
            top: `${topPosition}px`,
            height: `${height}px`,
            left: '4px',
            right: '4px',
          }}
        >
          <EventCard 
            event={event} 
            isSmall={height < 40}
            onClick={() => setSelectedEvent(event)}
          />
        </div>
      );
    });
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
        {/* Week view grid */}
        <div className="flex-1 overflow-auto relative" ref={scrollContainerRef}>
          <div className="grid grid-cols-8 min-w-full relative">
            {/* Events overlay */}
            <div className="absolute inset-0 col-span-8 z-10">
              <div className="grid grid-cols-8 h-full">
                <div /> {/* Spacer for time column */}
                {weekDays.map((day, dayIndex) => (
                  <div key={dayIndex} className="relative">
                    {renderEventsForDay(day, dayIndex)}
                  </div>
                ))}
              </div>
            </div>

            {/* Current time indicator */}
            {showCurrentTime && (
              <div 
                className="absolute left-0 right-0 z-40 pointer-events-none col-span-8"
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
            <div className="sticky top-0 bg-white dark:bg-[#101922] border-r border-b border-gray-200 dark:border-gray-700 p-2 z-10 h-[60px] flex items-center">
              <span className="text-xs text-gray-500 dark:text-gray-400">Time</span>
            </div>

            {/* Day headers */}
            {weekDays.map((day, index) => {
              const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
              const today = isToday(day);
              
              return (
                <div
                  key={index}
                  className={`sticky top-0 bg-white dark:bg-[#101922] border-r border-b border-gray-200 dark:border-gray-700 p-2 text-center z-10 h-[60px] flex flex-col justify-center ${
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
                  className="border-r border-b border-gray-200 dark:border-gray-700 p-2 text-right text-xs text-gray-500 dark:text-gray-400 h-[60px] flex items-start"
                >
                  {hour === 0 ? '12 AM' : hour < 12 ? `${hour} AM` : hour === 12 ? '12 PM' : `${hour - 12} PM`}
                </div>

                {/* Day cells */}
                {weekDays.map((_, dayIndex) => (
                  <div
                    key={`${hour}-${dayIndex}`}
                    className="border-r border-b border-gray-200 dark:border-gray-700 p-2 h-[60px] hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
                  />
                ))}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
    </>
  );
};

export default WeekView;
