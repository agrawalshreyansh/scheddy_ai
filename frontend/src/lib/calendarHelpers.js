// Calendar Helper Functions

/**
 * Get priority color based on priority number
 */
export const getPriorityColor = (priority) => {
  if (priority >= 9) return 'bg-red-600 border-red-700';
  if (priority >= 7) return 'bg-orange-600 border-orange-700';
  if (priority >= 5) return 'bg-blue-600 border-blue-700';
  if (priority >= 3) return 'bg-green-600 border-green-700';
  return 'bg-gray-600 border-gray-700';
};

/**
 * Get priority label based on priority number
 */
export const getPriorityLabel = (priority) => {
  if (priority >= 9) return 'URGENT';
  if (priority >= 7) return 'HIGH';
  if (priority >= 5) return 'MEDIUM';
  if (priority >= 3) return 'LOW';
  return 'MINIMAL';
};

/**
 * Calculate duration between start and end time
 */
export const getDuration = (startTime, endTime) => {
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

/**
 * Format datetime for input field (yyyy-MM-ddTHH:mm)
 */
export const formatDateTimeForInput = (date) => {
  if (!date) return '';
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

/**
 * Generate avatar color based on name
 */
export const generateAvatarColor = (firstName, lastName) => {
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
  return colors[index] || 'bg-blue-500';
};

/**
 * Generate initials from name
 */
export const generateInitials = (firstName, lastName) => {
  const firstInitial = firstName.trim().charAt(0).toUpperCase();
  const lastInitial = lastName.trim().charAt(0).toUpperCase();
  return firstInitial + lastInitial || '?';
};

/**
 * Parse full name into first and last name
 */
export const parseFullName = (fullName) => {
  if (!fullName) return { firstName: '', lastName: '' };
  const nameParts = fullName.trim().split(' ');
  const firstName = nameParts[0] || '';
  const lastName = nameParts.slice(1).join(' ') || '';
  return { firstName, lastName };
};
