'use client';
import React, { useState, useEffect, useRef } from 'react';
import { useCalendar } from '../../context/CalendarContext';
import EventCard from '../common/EventCard';
import EventDetailModal from '../modals/EventDetailModal';

/**
 * DayView Component
 * Displays a single day view with hourly time slots
 */
const DayView = () => {
  const { currentDate, isToday, getEventsForDate, refreshEvents } = useCalendar();
  const [selectedEvent, setSelectedEvent] = useState(null);
  const scrollContainerRef = useRef(null);
  
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

  // Auto-scroll to current time on mount
  useEffect(() => {
    if (scrollContainerRef.current && showCurrentTime) {
      // Scroll to current time with some offset to center it in the view
      const offset = 200;
      scrollContainerRef.current.scrollTop = Math.max(0, currentTimePosition - offset);
    }
  }, [currentTimePosition, showCurrentTime]);

  // Get events for current day
  const dayEvents = getEventsForDate(currentDate);

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
        <div className="flex-1 overflow-auto" ref={scrollContainerRef}>
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
                  className="border-r border-b border-gray-200 dark:border-gray-700 p-4 h-24 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer relative"
                >
                  {/* Render events for this hour */}
                  {dayEvents
                    .filter(event => {
                      const eventHour = new Date(event.start_time).getHours();
                      return eventHour === hour;
                    })
                    .map((event, idx) => (
                      <div key={event.id || idx} className="mb-1">
                        <EventCard 
                          event={event} 
                          isSmall={false}
                          onClick={() => setSelectedEvent(event)}
                        />
                      </div>
                    ))
                  }
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DayView;
