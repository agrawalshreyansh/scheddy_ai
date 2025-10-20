/**
 * DateTime Utility Functions
 * Handles datetime formatting, conversion, and display with timezone awareness
 */

/**
 * Format time in 12-hour format (e.g., "2:30 PM")
 * @param {Date} date - Date object
 * @returns {string} Formatted time
 */
export const formatTime = (date) => {
  if (!date || !(date instanceof Date)) return '';
  
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  const displayMinutes = minutes.toString().padStart(2, '0');
  
  return `${displayHours}:${displayMinutes} ${ampm}`;
};

/**
 * Format date in "Mon Oct 20" format
 * @param {Date} date - Date object
 * @returns {string} Formatted date
 */
export const formatShortDate = (date) => {
  if (!date || !(date instanceof Date)) return '';
  
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  
  return `${days[date.getDay()]} ${months[date.getMonth()]} ${date.getDate()}`;
};

/**
 * Format date in "Monday, October 20, 2025" format
 * @param {Date} date - Date object
 * @returns {string} Formatted date
 */
export const formatLongDate = (date) => {
  if (!date || !(date instanceof Date)) return '';
  
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  
  return `${days[date.getDay()]}, ${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
};

/**
 * Format datetime in "Mon Oct 20, 2:30 PM" format
 * @param {Date} date - Date object
 * @returns {string} Formatted datetime
 */
export const formatDateTime = (date) => {
  if (!date || !(date instanceof Date)) return '';
  return `${formatShortDate(date)}, ${formatTime(date)}`;
};

/**
 * Format event time range (e.g., "2:30 PM - 3:30 PM")
 * @param {Date} startTime - Start time
 * @param {Date} endTime - End time
 * @returns {string} Formatted time range
 */
export const formatTimeRange = (startTime, endTime) => {
  if (!startTime || !endTime) return '';
  return `${formatTime(startTime)} - ${formatTime(endTime)}`;
};

/**
 * Check if two dates are on the same day
 * @param {Date} date1 - First date
 * @param {Date} date2 - Second date
 * @returns {boolean} True if same day
 */
export const isSameDay = (date1, date2) => {
  if (!date1 || !date2) return false;
  return (
    date1.getDate() === date2.getDate() &&
    date1.getMonth() === date2.getMonth() &&
    date1.getFullYear() === date2.getFullYear()
  );
};

/**
 * Check if date is today
 * @param {Date} date - Date to check
 * @returns {boolean} True if today
 */
export const isToday = (date) => {
  return isSameDay(date, new Date());
};

/**
 * Check if date is tomorrow
 * @param {Date} date - Date to check
 * @returns {boolean} True if tomorrow
 */
export const isTomorrow = (date) => {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  return isSameDay(date, tomorrow);
};

/**
 * Check if date is in the past
 * @param {Date} date - Date to check
 * @returns {boolean} True if in the past
 */
export const isPast = (date) => {
  if (!date) return false;
  return date < new Date();
};

/**
 * Get duration in minutes between two dates
 * @param {Date} startTime - Start time
 * @param {Date} endTime - End time
 * @returns {number} Duration in minutes
 */
export const getDurationMinutes = (startTime, endTime) => {
  if (!startTime || !endTime) return 0;
  return Math.round((endTime - startTime) / (1000 * 60));
};

/**
 * Format duration (e.g., "1h 30m" or "30m")
 * @param {number} minutes - Duration in minutes
 * @returns {string} Formatted duration
 */
export const formatDuration = (minutes) => {
  if (!minutes || minutes < 0) return '0m';
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours > 0 && mins > 0) {
    return `${hours}h ${mins}m`;
  } else if (hours > 0) {
    return `${hours}h`;
  } else {
    return `${mins}m`;
  }
};

/**
 * Get start of day (12:00 AM)
 * @param {Date} date - Date object
 * @returns {Date} Start of day
 */
export const getStartOfDay = (date) => {
  const newDate = new Date(date);
  newDate.setHours(0, 0, 0, 0);
  return newDate;
};

/**
 * Get end of day (11:59:59 PM)
 * @param {Date} date - Date object
 * @returns {Date} End of day
 */
export const getEndOfDay = (date) => {
  const newDate = new Date(date);
  newDate.setHours(23, 59, 59, 999);
  return newDate;
};

/**
 * Get start of week (Sunday at 12:00 AM)
 * @param {Date} date - Date object
 * @returns {Date} Start of week
 */
export const getStartOfWeek = (date) => {
  const newDate = new Date(date);
  const day = newDate.getDay();
  const diff = newDate.getDate() - day;
  newDate.setDate(diff);
  newDate.setHours(0, 0, 0, 0);
  return newDate;
};

/**
 * Get end of week (Saturday at 11:59:59 PM)
 * @param {Date} date - Date object
 * @returns {Date} End of week
 */
export const getEndOfWeek = (date) => {
  const newDate = new Date(date);
  const day = newDate.getDay();
  const diff = newDate.getDate() + (6 - day);
  newDate.setDate(diff);
  newDate.setHours(23, 59, 59, 999);
  return newDate;
};

/**
 * Get start of month (1st at 12:00 AM)
 * @param {Date} date - Date object
 * @returns {Date} Start of month
 */
export const getStartOfMonth = (date) => {
  return new Date(date.getFullYear(), date.getMonth(), 1, 0, 0, 0, 0);
};

/**
 * Get end of month (last day at 11:59:59 PM)
 * @param {Date} date - Date object
 * @returns {Date} End of month
 */
export const getEndOfMonth = (date) => {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999);
};

/**
 * Calculate position of event in day grid (for calendar display)
 * @param {Date} startTime - Event start time
 * @param {number} hourHeight - Height of one hour in pixels
 * @returns {number} Top position in pixels
 */
export const getEventTopPosition = (startTime, hourHeight = 60) => {
  if (!startTime || !(startTime instanceof Date)) return 0;
  
  const hours = startTime.getHours();
  const minutes = startTime.getMinutes();
  return (hours * hourHeight) + (minutes / 60 * hourHeight);
};

/**
 * Calculate height of event in day grid
 * @param {Date} startTime - Event start time
 * @param {Date} endTime - Event end time
 * @param {number} hourHeight - Height of one hour in pixels
 * @returns {number} Height in pixels
 */
export const getEventHeight = (startTime, endTime, hourHeight = 60) => {
  const durationMins = getDurationMinutes(startTime, endTime);
  return (durationMins / 60) * hourHeight;
};

/**
 * Get relative date string (e.g., "Today", "Tomorrow", "Oct 20")
 * @param {Date} date - Date object
 * @returns {string} Relative date string
 */
export const getRelativeDateString = (date) => {
  if (!date) return '';
  
  if (isToday(date)) return 'Today';
  if (isTomorrow(date)) return 'Tomorrow';
  
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  if (isSameDay(date, yesterday)) return 'Yesterday';
  
  return formatShortDate(date);
};

/**
 * Parse ISO datetime string to Date object (handles timezone)
 * @param {string} isoString - ISO datetime string
 * @returns {Date|null} Date object or null if invalid
 */
export const parseISODate = (isoString) => {
  if (!isoString) return null;
  try {
    return new Date(isoString);
  } catch (error) {
    console.error('Error parsing date:', error);
    return null;
  }
};

/**
 * Convert Date to ISO string for API
 * @param {Date} date - Date object
 * @returns {string|null} ISO string or null
 */
export const toISOString = (date) => {
  if (!date || !(date instanceof Date)) return null;
  try {
    return date.toISOString();
  } catch (error) {
    console.error('Error converting to ISO string:', error);
    return null;
  }
};

/**
 * Get user's timezone offset string (e.g., "UTC+5:30")
 * @returns {string} Timezone offset string
 */
export const getTimezoneOffset = () => {
  const offset = -new Date().getTimezoneOffset();
  const hours = Math.floor(Math.abs(offset) / 60);
  const minutes = Math.abs(offset) % 60;
  const sign = offset >= 0 ? '+' : '-';
  return `UTC${sign}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
};

/**
 * Get user's timezone name (e.g., "Asia/Kolkata")
 * @returns {string} Timezone name
 */
export const getTimezoneName = () => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
};
