'use client';
import React from 'react';
import { formatTime, formatTimeRange } from '@/lib/dateUtils';
import { getPriorityColor } from '@/lib/calendarHelpers';

/**
 * EventCard Component
 * Displays a single event card with title, time, and priority color
 */
const EventCard = ({ event, isSmall = false, onClick }) => {
  const priorityColor = getPriorityColor(event.priority_number);
  
  return (
    <div
      className={`${priorityColor} text-white rounded-md px-3 py-2 text-sm font-medium overflow-hidden cursor-pointer hover:opacity-90 hover:shadow-lg transition-all border-l-4 shadow-md w-full h-full`}
      title={`${event.task_title}\n${formatTimeRange(event.start_time, event.end_time)}\n${event.description || ''}`}
      onClick={onClick}
    >
      <div className="font-bold truncate text-white">{event.task_title}</div>
      {!isSmall && (
        <div className="text-white/95 text-xs mt-1 font-normal">
          {formatTime(event.start_time)}
        </div>
      )}
    </div>
  );
};

export default EventCard;
