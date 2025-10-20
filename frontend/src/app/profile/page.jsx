'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Loader2, Plus, X } from 'lucide-react';
import { fetchUserPreferences, updateUserPreferences, fetchWeeklyGoals, updateWeeklyGoals } from '@/lib/api';

const Page = () => {
  const router = useRouter();
  
  // User Info (from localStorage)
  const [user, setUser] = useState(null);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  
  // Work Schedule
  const [workStartTime, setWorkStartTime] = useState('09:00');
  const [workEndTime, setWorkEndTime] = useState('17:00');
  const [lunchBreak, setLunchBreak] = useState('12:30');
  const [lunchDuration, setLunchDuration] = useState(60);
  const [minBreak, setMinBreak] = useState(15);
  const [maxTasks, setMaxTasks] = useState(8);
  const [preferMorning, setPreferMorning] = useState(true);
  const [allowAutoReschedule, setAllowAutoReschedule] = useState(false);
  
  const [workDays, setWorkDays] = useState({
    Monday: true,
    Tuesday: true,
    Wednesday: true,
    Thursday: true,
    Friday: true,
    Saturday: false,
    Sunday: false
  });

  // Weekly Goals
  const [weeklyGoals, setWeeklyGoals] = useState({});
  const [newGoalCategory, setNewGoalCategory] = useState('');
  const [newGoalHours, setNewGoalHours] = useState(5);
  
  // UI State
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Load user data from localStorage on component mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser);
        
        // Check if user has uuid/id
        if (!userData.user_id && !userData.email) {
          router.push('/auth');
          return;
        }
        
        setUser(userData);
        
        // Parse name if it's in full name format, or use separate fields
        if (userData.full_name) {
          const nameParts = userData.full_name.trim().split(' ');
          setFirstName(nameParts[0] || '');
          setLastName(nameParts.slice(1).join(' ') || '');
        }
        
        if (userData.email) {
          setEmail(userData.email);
        }

        // Load user preferences
        loadPreferences();
      } catch (error) {
        console.error('Error parsing user data from localStorage:', error);
        router.push('/auth');
      }
    } else {
      // No user found in localStorage, redirect to auth
      router.push('/auth');
    }
  }, [router]);

  // Load user preferences from API
  const loadPreferences = async () => {
    try {
      setLoading(true);
      const response = await fetchUserPreferences();
      
      if (response.success && response.preferences) {
        const prefs = response.preferences;
        
        // Set work hours
        if (prefs.work_start_time) {
          setWorkStartTime(prefs.work_start_time.substring(0, 5)); // HH:MM
        }
        if (prefs.work_end_time) {
          setWorkEndTime(prefs.work_end_time.substring(0, 5));
        }
        
        // Set work days
        if (prefs.work_days) {
          const daysMap = {
            0: 'Monday',
            1: 'Tuesday',
            2: 'Wednesday',
            3: 'Thursday',
            4: 'Friday',
            5: 'Saturday',
            6: 'Sunday'
          };
          const newWorkDays = {
            Monday: false,
            Tuesday: false,
            Wednesday: false,
            Thursday: false,
            Friday: false,
            Saturday: false,
            Sunday: false
          };
          prefs.work_days.forEach(dayNum => {
            const dayName = daysMap[dayNum];
            if (dayName) newWorkDays[dayName] = true;
          });
          setWorkDays(newWorkDays);
        }
        
        // Set lunch break
        if (prefs.lunch_break_start) {
          setLunchBreak(prefs.lunch_break_start.substring(0, 5));
        }
        if (prefs.lunch_break_duration !== undefined) {
          setLunchDuration(prefs.lunch_break_duration);
        }
        
        // Set other preferences
        if (prefs.min_break_between_tasks !== undefined) {
          setMinBreak(prefs.min_break_between_tasks);
        }
        if (prefs.max_tasks_per_day !== undefined) {
          setMaxTasks(prefs.max_tasks_per_day);
        }
        if (prefs.prefer_morning !== undefined) {
          setPreferMorning(prefs.prefer_morning);
        }
        if (prefs.allow_auto_reschedule !== undefined) {
          setAllowAutoReschedule(prefs.allow_auto_reschedule);
        }
        
        // Set weekly goals
        if (prefs.weekly_goals) {
          setWeeklyGoals(prefs.weekly_goals);
        }
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      setMessage({ type: 'error', text: 'Failed to load preferences' });
    } finally {
      setLoading(false);
    }
  };

  // Generate initials from first and last name
  const getInitials = () => {
    const firstInitial = firstName.trim().charAt(0).toUpperCase();
    const lastInitial = lastName.trim().charAt(0).toUpperCase();
    return firstInitial + lastInitial || '?';
  };

  // Generate a color based on the name
  const getAvatarColor = () => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-yellow-500',
      'bg-red-500',
      'bg-indigo-500',
      'bg-teal-500',
    ];
    const nameString = (firstName + lastName).toLowerCase();
    const index = nameString.charCodeAt(0) % colors.length;
    return colors[index] || 'bg-primary';
  };

  const handleWorkDayChange = (day) => {
    setWorkDays(prev => ({
      ...prev,
      [day]: !prev[day]
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage({ type: '', text: '' });
      
      // Parse work hours
      const [startHour, startMinute] = workStartTime.split(':').map(Number);
      const [endHour, endMinute] = workEndTime.split(':').map(Number);
      const [lunchHour, lunchMinute] = lunchBreak.split(':').map(Number);
      
      // Convert work days to array of numbers (0=Monday, 6=Sunday)
      const daysMap = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
      };
      const workDaysArray = Object.entries(workDays)
        .filter(([_, checked]) => checked)
        .map(([day, _]) => daysMap[day]);
      
      // Prepare preferences payload
      const preferences = {
        work_start_hour: startHour,
        work_start_minute: startMinute,
        work_end_hour: endHour,
        work_end_minute: endMinute,
        work_days: workDaysArray,
        lunch_break_hour: lunchHour,
        lunch_break_minute: lunchMinute,
        lunch_break_duration: lunchDuration,
        min_break_between_tasks: minBreak,
        max_tasks_per_day: maxTasks,
        prefer_morning: preferMorning,
        allow_auto_reschedule: allowAutoReschedule,
        weekly_goals: weeklyGoals
      };
      
      const response = await updateUserPreferences(preferences);
      
      if (response.success) {
        setMessage({ type: 'success', text: 'Preferences saved successfully!' });
        setTimeout(() => setMessage({ type: '', text: '' }), 3000);
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to save preferences' });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    // Reload preferences from server
    loadPreferences();
    setMessage({ type: 'info', text: 'Changes discarded' });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };

  const handleAddGoal = () => {
    if (newGoalCategory.trim() && newGoalHours > 0) {
      setWeeklyGoals(prev => ({
        ...prev,
        [newGoalCategory.toLowerCase()]: newGoalHours
      }));
      setNewGoalCategory('');
      setNewGoalHours(5);
    }
  };

  const handleRemoveGoal = (category) => {
    setWeeklyGoals(prev => {
      const newGoals = { ...prev };
      delete newGoals[category];
      return newGoals;
    });
  };

  const handleGoalHoursChange = (category, hours) => {
    setWeeklyGoals(prev => ({
      ...prev,
      [category]: parseInt(hours) || 0
    }));
  };

  return (
    <div className="relative flex h-screen w-full flex-col bg-[#101922] overflow-hidden">
      <div className="layout-container flex h-full grow flex-col">
        <div className="px-4 md:px-10 lg:px-20 flex flex-1 justify-center py-4 overflow-y-auto">
          <div className="layout-content-container flex flex-col max-w-[1200px] flex-1">
            {/* Header with Back Button */}
            <div className="flex items-center gap-4 px-4 py-3">
              <button
                onClick={() => router.push('/calendar')}
                className="flex items-center justify-center w-10 h-10 rounded-lg bg-[#192633] hover:bg-[#324d67] border border-[#324d67] transition-colors"
                aria-label="Back to Calendar"
              >
                <ArrowLeft className="w-5 h-5 text-white" />
              </button>
              <p className="text-white text-3xl font-black leading-tight tracking-[-0.033em]">
                Profile Settings
              </p>
            </div>

            {/* Status Message */}
            {message.text && (
              <div className={`mx-4 my-2 px-4 py-3 rounded-lg ${
                message.type === 'success' ? 'bg-green-500/20 border border-green-500 text-green-400' :
                message.type === 'error' ? 'bg-red-500/20 border border-red-500 text-red-400' :
                'bg-blue-500/20 border border-blue-500 text-blue-400'
              }`}>
                {message.text}
              </div>
            )}

            {/* Loading State */}
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              </div>
            ) : (
              <>
                {/* Profile Section */}
                <div className="flex flex-col gap-3 px-4 py-3">
                  <div className="flex items-center gap-4">
                    {/* Profile Picture */}
                    <div className={`w-20 h-20 rounded-full ${getAvatarColor()} flex items-center justify-center text-white text-2xl font-bold shadow-lg flex-shrink-0`}>
                      {getInitials()}
                    </div>

                    {/* Name and Email Display */}
                    <div className="flex flex-col gap-1">
                      <h2 className="text-white text-xl font-bold">
                        {firstName && lastName ? `${firstName} ${lastName}` : 'User'}
                      </h2>
                      <p className="text-gray-400 text-sm">
                        {email || 'No email available'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Divider */}
                <div className="border-t border-[#324d67] my-3"></div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 px-4">
              {/* Left Column */}
              <div className="flex flex-col gap-4">
                {/* Work Hours */}
                <h3 className="text-white text-base font-bold leading-tight tracking-[-0.015em] px-2 pb-1 pt-2">
                  Work Hours
                </h3>
                <div className="flex flex-wrap items-end gap-3 px-2 py-2">
                  <label className="flex flex-col min-w-40 flex-1">
                    <p className="text-white text-sm font-medium leading-normal pb-1.5">
                      Work Start Time
                    </p>
                    <input
                      className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border border-[#324d67] bg-[#192633] focus:border-primary h-12 placeholder:text-[#92adc9] p-3 text-sm font-normal leading-normal"
                      type="time"
                      value={workStartTime}
                      onChange={(e) => setWorkStartTime(e.target.value)}
                    />
                  </label>
                  <label className="flex flex-col min-w-40 flex-1">
                    <p className="text-white text-sm font-medium leading-normal pb-1.5">
                      Work End Time
                    </p>
                    <input
                      className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border border-[#324d67] bg-[#192633] focus:border-primary h-12 placeholder:text-[#92adc9] p-3 text-sm font-normal leading-normal"
                      type="time"
                      value={workEndTime}
                      onChange={(e) => setWorkEndTime(e.target.value)}
                    />
                  </label>
                </div>

                {/* Work Days */}
                <h3 className="text-white text-base font-bold leading-tight tracking-[-0.015em] px-2 pb-1 pt-2">
                  Work Days
                </h3>
                <div className="px-2 grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {Object.entries(workDays).map(([day, checked]) => (
                    <label key={day} className="flex items-center gap-x-2 py-2">
                      <input
                        checked={checked}
                        onChange={() => handleWorkDayChange(day)}
                        className="h-4 w-4 rounded border-[#324d67] bg-transparent text-primary focus:ring-0 focus:ring-offset-0 focus:border-primary"
                        type="checkbox"
                      />
                      <p className="text-white text-sm font-normal leading-normal">
                        {day}
                      </p>
                    </label>
                  ))}
                </div>
              </div>

              {/* Right Column */}
              <div className="flex flex-col gap-4">
                {/* Preferences */}
                <h3 className="text-white text-base font-bold leading-tight tracking-[-0.015em] px-2 pb-1 pt-2">
                  Preferences
                </h3>
                <div className="px-2 flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <p className="text-white text-sm font-medium">
                      Prefer Morning Slots
                    </p>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        checked={preferMorning}
                        onChange={(e) => setPreferMorning(e.target.checked)}
                        className="sr-only peer"
                        type="checkbox"
                      />
                      <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-focus:ring-2 peer-focus:ring-accent/50 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                    </label>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-white text-sm font-medium">
                      Allow Auto Reschedule
                    </p>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        checked={allowAutoReschedule}
                        onChange={(e) => setAllowAutoReschedule(e.target.checked)}
                        className="sr-only peer"
                        type="checkbox"
                      />
                      <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-focus:ring-2 peer-focus:ring-accent/50 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent"></div>
                    </label>
                  </div>
                </div>

                {/* Breaks */}
                <h3 className="text-white text-base font-bold leading-tight tracking-[-0.015em] px-2 pb-1 pt-2">
                  Breaks
                </h3>
                <div className="flex flex-wrap items-end gap-3 px-2 py-2">
                  <label className="flex flex-col min-w-40 flex-1">
                    <p className="text-white text-sm font-medium leading-normal pb-1.5">
                      Lunch Break
                    </p>
                    <input
                      className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border border-[#324d67] bg-[#192633] focus:border-primary h-12 placeholder:text-[#92adc9] p-3 text-sm font-normal leading-normal"
                      type="time"
                      value={lunchBreak}
                      onChange={(e) => setLunchBreak(e.target.value)}
                    />
                  </label>
                  <label className="flex flex-col min-w-40 flex-1">
                    <p className="text-white text-sm font-medium leading-normal pb-1.5">
                      Duration (mins)
                    </p>
                    <input
                      className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border border-[#324d67] bg-[#192633] focus:border-primary h-12 placeholder:text-[#92adc9] p-3 text-sm font-normal leading-normal"
                      type="number"
                      value={lunchDuration}
                      onChange={(e) => setLunchDuration(parseInt(e.target.value))}
                    />
                  </label>
                </div>
                <div className="px-2 py-2">
                  <label className="flex flex-col">
                    <p className="text-white text-sm font-medium leading-normal pb-1.5">
                      Minimum Break Between Tasks (mins)
                    </p>
                    <input
                      className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border border-[#324d67] bg-[#192633] focus:border-primary h-12 placeholder:text-[#92adc9] p-3 text-sm font-normal leading-normal"
                      type="number"
                      value={minBreak}
                      onChange={(e) => setMinBreak(parseInt(e.target.value))}
                    />
                  </label>
                </div>

                {/* Task Management */}
                <h3 className="text-white text-base font-bold leading-tight tracking-[-0.015em] px-2 pb-1 pt-2">
                  Task Management
                </h3>
                <div className="px-2 py-2">
                  <label className="flex flex-col">
                    <p className="text-white text-sm font-medium leading-normal pb-1.5">
                      Maximum Tasks Per Day
                    </p>
                    <input
                      className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border border-[#324d67] bg-[#192633] focus:border-primary h-12 placeholder:text-[#92adc9] p-3 text-sm font-normal leading-normal"
                      type="number"
                      value={maxTasks}
                      onChange={(e) => setMaxTasks(parseInt(e.target.value))}
                    />
                  </label>
                </div>
              </div>
            </div>

            {/* Weekly Goals Section */}
            <div className="flex flex-col gap-4 px-4 py-4">
              <div className="flex items-center justify-between">
                <h3 className="text-white text-base font-bold leading-tight tracking-[-0.015em]">
                  Weekly Goals (hours/week)
                </h3>
              </div>
              
              {/* Existing Goals */}
              {Object.keys(weeklyGoals).length > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(weeklyGoals).map(([category, hours]) => (
                    <div key={category} className="flex items-center gap-3 bg-[#192633] border border-[#324d67] rounded-lg p-3">
                      <div className="flex-1">
                        <p className="text-white text-sm font-medium capitalize">{category}</p>
                      </div>
                      <input
                        type="number"
                        min="1"
                        max="40"
                        value={hours}
                        onChange={(e) => handleGoalHoursChange(category, e.target.value)}
                        className="w-20 rounded-lg text-white bg-[#101922] border border-[#324d67] focus:border-primary focus:outline-0 focus:ring-0 px-3 py-2 text-sm"
                      />
                      <span className="text-gray-400 text-sm">hrs</span>
                      <button
                        onClick={() => handleRemoveGoal(category)}
                        className="text-red-400 hover:text-red-300 transition-colors"
                        aria-label={`Remove ${category} goal`}
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Add New Goal */}
              <div className="flex flex-col sm:flex-row items-end gap-3 bg-[#192633] border border-[#324d67] rounded-lg p-4">
                <label className="flex flex-col flex-1 min-w-0">
                  <p className="text-white text-sm font-medium leading-normal pb-1.5">
                    Category
                  </p>
                  <input
                    type="text"
                    value={newGoalCategory}
                    onChange={(e) => setNewGoalCategory(e.target.value)}
                    placeholder="e.g., learning, exercise, coding"
                    className="form-input flex w-full min-w-0 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border border-[#324d67] bg-[#101922] focus:border-primary h-12 placeholder:text-[#92adc9] p-3 text-sm font-normal leading-normal"
                  />
                </label>
                <label className="flex flex-col min-w-40">
                  <p className="text-white text-sm font-medium leading-normal pb-1.5">
                    Hours per Week
                  </p>
                  <input
                    type="number"
                    min="1"
                    max="40"
                    value={newGoalHours}
                    onChange={(e) => setNewGoalHours(parseInt(e.target.value) || 5)}
                    className="form-input flex w-full min-w-0 resize-none overflow-hidden rounded-lg text-white focus:outline-0 focus:ring-0 border border-[#324d67] bg-[#101922] focus:border-primary h-12 placeholder:text-[#92adc9] p-3 text-sm font-normal leading-normal"
                  />
                </label>
                <button
                  onClick={handleAddGoal}
                  className="flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold text-white bg-[#324d67] hover:bg-primary transition-colors h-12"
                >
                  <Plus className="w-4 h-4" />
                  Add Goal
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end gap-3 px-4 py-3 mb-4">
              <button
                onClick={handleCancel}
                disabled={saving}
                className="flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-semibold text-white bg-gray-700 hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex items-center justify-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold text-white bg-primary hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving && <Loader2 className="w-4 h-4 animate-spin" />}
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Page;