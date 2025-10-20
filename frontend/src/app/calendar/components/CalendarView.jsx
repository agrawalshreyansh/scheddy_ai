'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useCalendar } from '../context/CalendarContext';
import { formatTime, formatTimeRange, getEventTopPosition, getEventHeight, isSameDay } from '@/lib/dateUtils';
import { updateEvent, deleteEvent } from '@/lib/api';

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

// Event Detail Modal Component
const EventDetailModal = ({ event, onClose, onEventUpdated }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [editedEvent, setEditedEvent] = useState({
    task_title: event.task_title,
    description: event.description || '',
    start_time: event.start_time,
    end_time: event.end_time,
    priority_number: event.priority_number,
    priority_tag: event.priority_tag || '',
  });

  if (!event) return null;

  const priorityColor = getPriorityColor(event.priority_number);
  const priorityLabel = getPriorityLabel(event.priority_number);

  // Handle delete with confirmation
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this event? This action cannot be undone.')) {
      return;
    }

    setIsDeleting(true);
    try {
      await deleteEvent(event.id);
      alert('Event deleted successfully!');
      onEventUpdated(); // Refresh the calendar
      onClose();
    } catch (error) {
      console.error('Error deleting event:', error);
      alert('Failed to delete event. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  // Handle edit save
  const handleSaveEdit = async () => {
    try {
      const updateData = {
        task_title: editedEvent.task_title,
        description: editedEvent.description,
        start_time: editedEvent.start_time,
        end_time: editedEvent.end_time,
        priority_number: parseInt(editedEvent.priority_number),
        priority_tag: editedEvent.priority_tag,
      };

      await updateEvent(event.id, updateData);
      alert('Event updated successfully!');
      onEventUpdated(); // Refresh the calendar
      onClose();
    } catch (error) {
      console.error('Error updating event:', error);
      alert('Failed to update event. Please try again.');
    }
  };

  // Format datetime for input field
  const formatDateTimeForInput = (date) => {
    if (!date) return '';
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  // Edit Mode UI
  if (isEditing) {
    return (
      <div 
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm overflow-y-auto py-8"
        onClick={onClose}
      >
        <div 
          className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full mx-4 my-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className={`${priorityColor} p-6`}>
            <div className="flex items-start justify-between">
              <h2 className="text-2xl font-bold text-white">Edit Event</h2>
              <button
                onClick={() => setIsEditing(false)}
                className="text-white hover:bg-white/20 rounded-full p-2 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Edit Form */}
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Event Title *
              </label>
              <input
                type="text"
                value={editedEvent.task_title}
                onChange={(e) => setEditedEvent({ ...editedEvent, task_title: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Enter event title"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Start Time *
                </label>
                <input
                  type="datetime-local"
                  value={formatDateTimeForInput(editedEvent.start_time)}
                  onChange={(e) => setEditedEvent({ ...editedEvent, start_time: new Date(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  End Time *
                </label>
                <input
                  type="datetime-local"
                  value={formatDateTimeForInput(editedEvent.end_time)}
                  onChange={(e) => setEditedEvent({ ...editedEvent, end_time: new Date(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Priority (0-10) *
                </label>
                <input
                  type="number"
                  min="0"
                  max="10"
                  value={editedEvent.priority_number}
                  onChange={(e) => setEditedEvent({ ...editedEvent, priority_number: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Priority Tag
                </label>
                <select
                  value={editedEvent.priority_tag}
                  onChange={(e) => setEditedEvent({ ...editedEvent, priority_tag: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="URGENT">URGENT</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                value={editedEvent.description}
                onChange={(e) => setEditedEvent({ ...editedEvent, description: e.target.value })}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Enter event description"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setIsEditing(false)}
                className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-medium py-2.5 px-4 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // View Mode UI
  return (
    <div 
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div 
        className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-2xl w-full mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with color */}
        <div className={`${priorityColor} p-6`}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-2">{event.task_title}</h2>
              <div className="flex items-center gap-2">
                <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-white text-sm font-medium">
                  {priorityLabel}
                </span>
                <span className="bg-white/20 backdrop-blur-sm px-3 py-1 rounded-full text-white text-sm">
                  Priority: {event.priority_number}
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:bg-white/20 rounded-full p-2 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Time Information */}
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-500 dark:text-gray-400">Date & Time</p>
                <p className="font-medium text-gray-900 dark:text-white">
                  {new Date(event.start_time).toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  {formatTimeRange(event.start_time, event.end_time)}
                </p>
              </div>
            </div>

            {/* Duration */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-500 dark:text-gray-400">Duration</p>
                <p className="font-medium text-gray-900 dark:text-white">
                  {getDuration(event.start_time, event.end_time)}
                </p>
              </div>
            </div>
          </div>

          {/* Description */}
          {event.description && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">DESCRIPTION</h3>
              <p className="text-gray-900 dark:text-white whitespace-pre-wrap">{event.description}</p>
            </div>
          )}

          {/* Additional Details */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3">EVENT DETAILS</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 dark:text-gray-400">Event ID</p>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{event.id}</p>
              </div>
              {event.priority_tag && (
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Priority Tag</p>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{event.priority_tag}</p>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              onClick={() => setIsEditing(true)}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit Event
            </button>
            <button
              className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              onClick={handleDelete}
              disabled={isDeleting}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              {isDeleting ? 'Deleting...' : 'Delete Event'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to get priority label
const getPriorityLabel = (priority) => {
  if (priority >= 9) return 'URGENT';
  if (priority >= 7) return 'HIGH';
  if (priority >= 5) return 'MEDIUM';
  if (priority >= 3) return 'LOW';
  return 'MINIMAL';
};

// Helper function to calculate duration
const getDuration = (startTime, endTime) => {
  const start = new Date(startTime);
  const end = new Date(endTime);
  const diffMs = end - start;
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 60) {
    return `${diffMins} minutes`;
  }
  
  const hours = Math.floor(diffMins / 60);
  const mins = diffMins % 60;
  
  if (mins === 0) {
    return `${hours} ${hours === 1 ? 'hour' : 'hours'}`;
  }
  
  return `${hours} ${hours === 1 ? 'hour' : 'hours'} ${mins} minutes`;
};

// Priority colors
const getPriorityColor = (priority) => {
  if (priority >= 9) return 'bg-red-600 border-red-700';
  if (priority >= 7) return 'bg-orange-600 border-orange-700';
  if (priority >= 5) return 'bg-blue-600 border-blue-700';
  if (priority >= 3) return 'bg-green-600 border-green-700';
  return 'bg-gray-600 border-gray-700';
};

// Event Card Component
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

// Week View Component
const WeekView = () => {
  const { currentDate, getWeekStart, getWeekDays, isToday, events, getEventsForDate, refreshEvents } = useCalendar();
  const [selectedEvent, setSelectedEvent] = useState(null);
  const scrollContainerRef = useRef(null);

  const weekStart = getWeekStart(currentDate);
  const weekDays = getWeekDays(weekStart);

  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Calculate current time position
  const getCurrentTimePosition = () => {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    // Each hour is 60px (min-h-[60px]), calculate position
    const position = (hours * 60) + (minutes / 60 * 60) + 60; // 60px for header
    return position;
  };

  // Check if today is in current week
  const showCurrentTime = weekDays.some(day => isToday(day));
  const currentTimePosition = showCurrentTime ? getCurrentTimePosition() : 0;

  // Auto-scroll to current time on mount
  useEffect(() => {
    if (scrollContainerRef.current && showCurrentTime) {
      // Scroll to current time with some offset to center it in the view
      const offset = 200; // Offset to show some context above current time
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

// Day View Component
const DayView = () => {
  const { currentDate, isToday, events, getEventsForDate, refreshEvents } = useCalendar();
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
      const offset = 200; // Offset to show some context above current time
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

// Month View Component
const MonthView = () => {
  const { currentDate, isToday, events, getEventsForDate, refreshEvents } = useCalendar();
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

export default CalendarView;