// components/Sidebar.jsx
'use client';
import React, { useState } from 'react';
import { Plus, ChevronLeft, ChevronRight, X, Calendar, Clock, MapPin, Users, AlignLeft, Loader2 } from 'lucide-react';
import { useCalendar } from '../context/CalendarContext';
import { createEvent } from '@/lib/api';

const Sidebar = () => {
  const { currentDate, setCurrentDate, isToday, refreshEvents } = useCalendar();
  const [miniCalendarDate, setMiniCalendarDate] = useState(new Date());
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    task_title: '',
    description: '',
    event_date: '',
    start_time: '',
    end_time: '',
    priority_number: 5,
    priority_tag: 'medium',
    location: '',
    guests: '',
    calendar_type: 'Personal'
  });

  // Reset form
  const resetForm = () => {
    setFormData({
      task_title: '',
      description: '',
      event_date: '',
      start_time: '',
      end_time: '',
      priority_number: 5,
      priority_tag: 'medium',
      location: '',
      guests: '',
      calendar_type: 'Personal'
    });
    setError('');
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle create event
  const handleCreateEvent = async () => {
    try {
      setError('');
      setIsCreating(true);

      // Validation
      if (!formData.task_title.trim()) {
        setError('Event title is required');
        return;
      }
      if (!formData.event_date) {
        setError('Date is required');
        return;
      }
      if (!formData.start_time) {
        setError('Start time is required');
        return;
      }
      if (!formData.end_time) {
        setError('End time is required');
        return;
      }

      // Combine date and time to create datetime objects
      const startDateTime = new Date(`${formData.event_date}T${formData.start_time}`);
      const endDateTime = new Date(`${formData.event_date}T${formData.end_time}`);

      // Validate end time is after start time
      if (endDateTime <= startDateTime) {
        setError('End time must be after start time');
        return;
      }

      // Prepare event data
      const eventData = {
        task_title: formData.task_title.trim(),
        description: formData.description.trim() || null,
        start_time: startDateTime,
        end_time: endDateTime,
        priority_number: parseInt(formData.priority_number),
        priority_tag: formData.priority_tag
      };

      // Create event via API
      await createEvent(eventData);

      // Success - close modal and refresh events
      setIsModalOpen(false);
      resetForm();
      refreshEvents();
      
      // Show success message (optional)
      alert('Event created successfully!');
    } catch (error) {
      console.error('Error creating event:', error);
      setError(error.message || 'Failed to create event. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  // Get the first day of the month
  const getFirstDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  };

  // Get the last day of the month
  const getLastDayOfMonth = (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0);
  };

  // Navigate mini calendar
  const goToPreviousMonth = () => {
    const newDate = new Date(miniCalendarDate);
    newDate.setMonth(miniCalendarDate.getMonth() - 1);
    setMiniCalendarDate(newDate);
  };

  const goToNextMonth = () => {
    const newDate = new Date(miniCalendarDate);
    newDate.setMonth(miniCalendarDate.getMonth() + 1);
    setMiniCalendarDate(newDate);
  };

  // Handle day click
  const handleDayClick = (day) => {
    const newDate = new Date(miniCalendarDate.getFullYear(), miniCalendarDate.getMonth(), day);
    setCurrentDate(newDate);
  };

  // Check if a date is selected (in current week)
  const isSelectedDate = (day) => {
    const checkDate = new Date(miniCalendarDate.getFullYear(), miniCalendarDate.getMonth(), day);
    return checkDate.getDate() === currentDate.getDate() &&
           checkDate.getMonth() === currentDate.getMonth() &&
           checkDate.getFullYear() === currentDate.getFullYear();
  };

  // Check if a date is today
  const isTodayDate = (day) => {
    const checkDate = new Date(miniCalendarDate.getFullYear(), miniCalendarDate.getMonth(), day);
    return isToday(checkDate);
  };

  // Format month and year
  const formatMonthYear = () => {
    const months = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December'];
    return `${months[miniCalendarDate.getMonth()]} ${miniCalendarDate.getFullYear()}`;
  };

  const renderCalendarDays = () => {
    const days = [];
    const firstDay = getFirstDayOfMonth(miniCalendarDate);
    const lastDay = getLastDayOfMonth(miniCalendarDate);
    const startingDayOfWeek = firstDay.getDay(); // 0 = Sunday
    const numberOfDays = lastDay.getDate();

    // Empty cells for days before 1st
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(<div key={`empty-${i}`} className=""></div>);
    }

    // Days of the month
    for (let day = 1; day <= numberOfDays; day++) {
      const isSelected = isSelectedDate(day);
      const isCurrentDay = isTodayDate(day);

      days.push(
        <button
          key={day}
          onClick={() => handleDayClick(day)}
          className={`flex h-8 w-8 items-center justify-center rounded-full text-sm transition-colors ${
            isSelected
              ? 'bg-[#137fec] text-white font-semibold'
              : isCurrentDay
              ? 'bg-[#137fec]/20 text-[#137fec] font-semibold'
              : 'text-gray-700 dark:text-gray-300 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20'
          }`}
        >
          {day}
        </button>
      );
    }

    return days;
  };

  return (
    <>
      <aside className="hidden w-64 flex-shrink-0 flex-col border-r border-[#101922]/10 dark:border-[#f6f7f8]/10 lg:flex p-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-20">Scheddy</h1>
        
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center justify-center gap-2 rounded-lg bg-[#137fec] px-2 py-2 text-sm font-medium text-white transition-colors hover:bg-[#137fec]/90 shadow-md cursor-pointer">
          <Plus size={20} />
          <span>Create Event</span>
        </button>

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-800 dark:text-white">{formatMonthYear()}</h3>
          <div className="flex items-center gap-2">
            <button 
              onClick={goToPreviousMonth}
              className="rounded-full p-1 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20">
              <ChevronLeft size={16} />
            </button>
            <button 
              onClick={goToNextMonth}
              className="rounded-full p-1 text-gray-500 dark:text-gray-400 hover:bg-[#137fec]/10 dark:hover:bg-[#137fec]/20">
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
        <div className="mt-2 grid grid-cols-7 gap-1 text-center text-xs">
          {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day,idx) => (
            <div key={`${day}${idx}`} className="font-medium text-gray-500 dark:text-gray-400">
              {day}
            </div>
          ))}
          {renderCalendarDays()}
        </div>
      </div>

      <div className="mt-8">
        <h3 className="text-sm font-semibold text-gray-800 dark:text-white">My Calendars</h3>
        <div className="mt-4 space-y-3">
          {[
            { id: 'personal', label: 'Personal', checked: true },
            { id: 'work', label: 'Work', checked: true },
            { id: 'reminders', label: 'Reminders', checked: false },
          ].map((calendar) => (
            <label key={calendar.id} className="flex items-center gap-3">
              <input
                type="checkbox"
                defaultChecked={calendar.checked}
                className="h-5 w-5 rounded border-gray-300 dark:border-gray-600 bg-transparent text-[#137fec] focus:ring-[#137fec] dark:ring-offset-[#101922]"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">{calendar.label}</span>
            </label>
          ))}
        </div>
      </div>
    </aside>

    {/* Create Event Modal */}
    {isModalOpen && (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
          {/* Modal Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Create Event</h2>
            <button
              onClick={() => {
                setIsModalOpen(false);
                resetForm();
              }}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              disabled={isCreating}
            >
              <X size={24} className="text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mx-6 mt-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-400 rounded-lg text-sm">
              {error}
            </div>
          )}

          {/* Modal Body */}
          <div className="p-6 space-y-6">
            {/* Event Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Event Title *
              </label>
              <input
                type="text"
                name="task_title"
                value={formData.task_title}
                onChange={handleInputChange}
                placeholder="Add title"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                disabled={isCreating}
              />
            </div>

            {/* Date and Time */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  <Calendar size={16} className="inline mr-2" />
                  Date *
                </label>
                <input
                  type="date"
                  name="event_date"
                  value={formData.event_date}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                  disabled={isCreating}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Clock size={16} className="inline mr-2" />
                    Start Time *
                  </label>
                  <input
                    type="time"
                    name="start_time"
                    value={formData.start_time}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                    disabled={isCreating}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Clock size={16} className="inline mr-2" />
                    End Time *
                  </label>
                  <input
                    type="time"
                    name="end_time"
                    value={formData.end_time}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                    disabled={isCreating}
                  />
                </div>
              </div>
            </div>

            {/* Priority */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Priority Tag
                </label>
                <select
                  name="priority_tag"
                  value={formData.priority_tag}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                  disabled={isCreating}
                >
                  <option value="urgent">Urgent</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                  <option value="optional">Optional</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Priority Number (1-10)
                </label>
                <input
                  type="number"
                  name="priority_number"
                  min="1"
                  max="10"
                  value={formData.priority_number}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                  disabled={isCreating}
                />
              </div>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <MapPin size={16} className="inline mr-2" />
                Location
              </label>
              <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                placeholder="Add location"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                disabled={isCreating}
              />
            </div>

            {/* Guests */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Users size={16} className="inline mr-2" />
                Add Guests
              </label>
              <input
                type="email"
                name="guests"
                value={formData.guests}
                onChange={handleInputChange}
                placeholder="Add guest emails"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                disabled={isCreating}
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <AlignLeft size={16} className="inline mr-2" />
                Description
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Add description"
                rows="4"
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-[#137fec] focus:border-transparent resize-none"
                disabled={isCreating}
              />
            </div>

            {/* Calendar Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Calendar
              </label>
              <select
                name="calendar_type"
                value={formData.calendar_type}
                onChange={handleInputChange}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-[#137fec] focus:border-transparent"
                disabled={isCreating}
              >
                <option>Personal</option>
                <option>Work</option>
                <option>Reminders</option>
              </select>
            </div>
          </div>

          {/* Modal Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => {
                setIsModalOpen(false);
                resetForm();
              }}
              className="px-6 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isCreating}
            >
              Cancel
            </button>
            <button
              onClick={handleCreateEvent}
              className="px-6 py-2.5 rounded-lg bg-[#137fec] text-white font-medium hover:bg-[#0d5fb8] transition-colors shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              disabled={isCreating}
            >
              {isCreating && <Loader2 size={16} className="animate-spin" />}
              {isCreating ? 'Creating...' : 'Create Event'}
            </button>
          </div>
        </div>
      </div>
    )}
  </>
  );
};

export default Sidebar;