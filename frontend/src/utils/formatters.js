/**
 * Utility functions for formatting data
 */

/**
 * Format a date/time to a localized time string
 * @param {string|Date} timestamp - The timestamp to format
 * @returns {string} Formatted time string (e.g., "2:30 PM")
 */
export const formatTime = (timestamp) => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit', 
    });
  } catch (error) {
    console.error('Error formatting time:', error);
    return '';
  }
};

/**
 * Format a date to a localized date string
 * @param {string|Date} timestamp - The timestamp to format
 * @returns {string} Formatted date string
 */
export const formatDate = (timestamp) => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleDateString();
  } catch (error) {
    console.error('Error formatting date:', error);
    return '';
  }
};

/**
 * Format a date to a full localized date-time string
 * @param {string|Date} timestamp - The timestamp to format
 * @returns {string} Formatted date-time string
 */
export const formatDateTime = (timestamp) => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString();
  } catch (error) {
    console.error('Error formatting date-time:', error);
    return '';
  }
};

/**
 * Format a relative time (e.g., "2 minutes ago")
 * @param {string|Date} timestamp - The timestamp to format
 * @returns {string} Relative time string
 */
export const formatRelativeTime = (timestamp) => {
  try {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffSecs < 60) {return 'just now';}
    if (diffMins < 60) {return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;}
    if (diffHours < 24) {return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;}
    if (diffDays < 7) {return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;}
    
    return formatDate(timestamp);
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return '';
  }
};

/**
 * Truncate text to a maximum length
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length
 * @param {string} suffix - Suffix to add when truncated (default: '...')
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength, suffix = '...') => {
  if (!text || text.length <= maxLength) {return text;}
  return text.substring(0, maxLength - suffix.length) + suffix;
};

/**
 * Format number with thousands separator
 * @param {number} num - The number to format
 * @returns {string} Formatted number string
 */
export const formatNumber = (num) => {
  return num.toLocaleString();
};
