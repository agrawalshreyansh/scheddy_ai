'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';

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
      } catch (error) {
        console.error('Error parsing user data from localStorage:', error);
        router.push('/auth');
      }
    } else {
      // No user found in localStorage, redirect to auth
      router.push('/auth');
    }
  }, [router]);

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

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving preferences...', {
      userId: user?.uuid,
      workStartTime,
      workEndTime,
      workDays,
      preferMorning,
      allowAutoReschedule,
      lunchBreak,
      lunchDuration,
      minBreak,
      maxTasks
    });
  };

  const handleCancel = () => {
    // TODO: Implement cancel/reset functionality
    console.log('Canceling changes...');
  };

  return (
    <div className="relative flex h-screen w-full flex-col bg-[#101922] overflow-hidden">
      <div className="layout-container flex h-full grow flex-col">
        <div className="px-4 md:px-10 lg:px-20 flex flex-1 justify-center py-4">
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

            {/* Action Buttons */}
            <div className="flex justify-end gap-3 px-4 py-3">
              <button
                onClick={handleCancel}
                className="flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-semibold text-white bg-gray-700 hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-semibold text-white bg-primary hover:bg-primary/90 transition-colors"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Page;