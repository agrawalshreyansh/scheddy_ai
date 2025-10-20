/**
 * API Service for Scheddy AI
 * Handles all backend API calls with proper datetime handling
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

/**
 * Get authorization headers from localStorage
 */
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

/**
 * Get user ID from localStorage
 */
const getUserId = () => {
  const userString = localStorage.getItem('user');
  if (userString) {
    try {
      const userObj = JSON.parse(userString);
      return userObj.user_id || null;
    } catch (error) {
      console.error('Error parsing user from localStorage:', error);
      return null;
    }
  }
  return null;
};

/**
 * Convert ISO datetime string to user's local Date object
 */
export const parseEventDateTime = (isoString) => {
  if (!isoString) return null;
  return new Date(isoString);
};

/**
 * Format date to ISO string for API
 */
export const formatDateForAPI = (date) => {
  if (!date) return null;
  if (typeof date === 'string') return date;
  return date.toISOString();
};

// ============================================================================
// EVENTS API
// ============================================================================

/**
 * Fetch events by date range
 * @param {Date|string} startDate - Start date
 * @param {Date|string} endDate - End date
 * @returns {Promise<Array>} Array of events
 */
export const fetchEventsByDateRange = async (startDate, endDate) => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const start = formatDateForAPI(startDate);
    const end = formatDateForAPI(endDate);

    const response = await fetch(
      `${API_BASE_URL}/calendar/events/range/?start_date=${start}&end_date=${end}&user_id=${userId}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch events: ${response.statusText}`);
    }

    const events = await response.json();
    
    // Parse datetime strings to Date objects
    return events.map(event => ({
      ...event,
      start_time: parseEventDateTime(event.start_time),
      end_time: parseEventDateTime(event.end_time),
      created_at: parseEventDateTime(event.created_at),
      updated_at: parseEventDateTime(event.updated_at),
    }));
  } catch (error) {
    console.error('Error fetching events by date range:', error);
    throw error;
  }
};

/**
 * Fetch all events for a user
 * @returns {Promise<Array>} Array of events
 */
export const fetchAllEvents = async () => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const response = await fetch(
      `${API_BASE_URL}/calendar/events?user_id=${userId}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch events: ${response.statusText}`);
    }

    const events = await response.json();
    
    // Parse datetime strings to Date objects
    return events.map(event => ({
      ...event,
      start_time: parseEventDateTime(event.start_time),
      end_time: parseEventDateTime(event.end_time),
      created_at: parseEventDateTime(event.created_at),
      updated_at: parseEventDateTime(event.updated_at),
    }));
  } catch (error) {
    console.error('Error fetching all events:', error);
    throw error;
  }
};

/**
 * Create a new event
 * @param {Object} eventData - Event data
 * @returns {Promise<Object>} Created event
 */
export const createEvent = async (eventData) => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const payload = {
      ...eventData,
      user_id: userId,
      start_time: formatDateForAPI(eventData.start_time),
      end_time: formatDateForAPI(eventData.end_time),
    };

    const response = await fetch(`${API_BASE_URL}/calendar/events`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to create event');
    }

    const event = await response.json();
    
    // Parse datetime strings to Date objects
    return {
      ...event,
      start_time: parseEventDateTime(event.start_time),
      end_time: parseEventDateTime(event.end_time),
      created_at: parseEventDateTime(event.created_at),
      updated_at: parseEventDateTime(event.updated_at),
    };
  } catch (error) {
    console.error('Error creating event:', error);
    throw error;
  }
};

/**
 * Update an existing event
 * @param {string} eventId - Event UUID
 * @param {Object} updateData - Data to update
 * @returns {Promise<Object>} Updated event
 */
export const updateEvent = async (eventId, updateData) => {
  try {
    const payload = {
      ...updateData,
    };

    // Convert dates if present
    if (updateData.start_time) {
      payload.start_time = formatDateForAPI(updateData.start_time);
    }
    if (updateData.end_time) {
      payload.end_time = formatDateForAPI(updateData.end_time);
    }

    const response = await fetch(`${API_BASE_URL}/calendar/events/${eventId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to update event');
    }

    const event = await response.json();
    
    // Parse datetime strings to Date objects
    return {
      ...event,
      start_time: parseEventDateTime(event.start_time),
      end_time: parseEventDateTime(event.end_time),
      created_at: parseEventDateTime(event.created_at),
      updated_at: parseEventDateTime(event.updated_at),
    };
  } catch (error) {
    console.error('Error updating event:', error);
    throw error;
  }
};

/**
 * Delete an event
 * @param {string} eventId - Event UUID
 * @returns {Promise<boolean>} Success status
 */
export const deleteEvent = async (eventId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/calendar/events/${eventId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to delete event');
    }

    return true;
  } catch (error) {
    console.error('Error deleting event:', error);
    throw error;
  }
};

// ============================================================================
// CHAT API
// ============================================================================

/**
 * Send a chat message to AI assistant
 * @param {string} message - User message
 * @param {string|null} conversationId - Optional conversation ID
 * @param {number} temperature - AI temperature (0.0-2.0)
 * @returns {Promise<Object>} AI response
 */
export const sendChatMessage = async (message, conversationId = null, temperature = 0.2) => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const payload = {
      user_id: userId,
      prompt: message,
      temperature: temperature.toString(),
      conversation_id: conversationId,
      user_datetime: new Date().toISOString(), // Send current user datetime in ISO format (includes timezone)
      user_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone, // Send user's timezone name (e.g., 'Asia/Kolkata')
    };

    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to get response from AI');
    }

    const data = await response.json();

    // Parse event datetimes if present
    if (data.event) {
      data.event = {
        ...data.event,
        start_time: parseEventDateTime(data.event.start_time),
        end_time: parseEventDateTime(data.event.end_time),
      };
    }

    if (data.events) {
      data.events = data.events.map(event => ({
        ...event,
        start_time: parseEventDateTime(event.start_time),
        end_time: parseEventDateTime(event.end_time),
      }));
    }

    if (data.rescheduled_events) {
      data.rescheduled_events = data.rescheduled_events.map(event => ({
        ...event,
        start_time: parseEventDateTime(event.start_time),
        end_time: parseEventDateTime(event.end_time),
      }));
    }

    return data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

// ============================================================================
// USER PREFERENCES API
// ============================================================================

/**
 * Fetch user preferences
 * @returns {Promise<Object>} User preferences
 */
export const fetchUserPreferences = async () => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/preferences/${userId}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user preferences');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user preferences:', error);
    throw error;
  }
};

/**
 * Update user preferences
 * @param {Object} preferences - Preferences to update
 * @returns {Promise<Object>} Updated preferences
 */
export const updateUserPreferences = async (preferences) => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/preferences/${userId}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(preferences),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to update preferences');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating user preferences:', error);
    throw error;
  }
};

/**
 * Fetch user weekly goals
 * @returns {Promise<Object>} Weekly goals with progress
 */
export const fetchWeeklyGoals = async () => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/preferences/${userId}/weekly-goals`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch weekly goals');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching weekly goals:', error);
    throw error;
  }
};

/**
 * Update user weekly goals
 * @param {Object} weeklyGoals - Weekly goals to set (e.g., { learning: 5, exercise: 3 })
 * @returns {Promise<Object>} Updated weekly goals
 */
export const updateWeeklyGoals = async (weeklyGoals) => {
  try {
    const userId = getUserId();
    if (!userId) {
      throw new Error('User not authenticated');
    }

    const response = await fetch(`${API_BASE_URL}/preferences/${userId}/weekly-goals`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({ weekly_goals: weeklyGoals }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to update weekly goals');
    }

    return await response.json();
  } catch (error) {
    console.error('Error updating weekly goals:', error);
    throw error;
  }
};
