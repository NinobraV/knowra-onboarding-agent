/**
 * API Service for Knowledge Chatbot Backend
 * Handles all HTTP requests to the backend API with proper error handling
 */

import { API_CONFIG, SSE_MARKERS, ERROR_MESSAGES } from '../utils/constants';

/**
 * Base fetch wrapper with error handling
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise<Response>} Fetch response
 * @throws {Error} If request fails
 */
const fetchWithErrorHandling = async (endpoint, options = {}) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
    
    const response = await fetch(url, {
      ...defaultOptions,
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || 
        errorData.message || 
        `HTTP ${response.status}: ${response.statusText}`,
      );
    }

    return response;
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error(ERROR_MESSAGES.TIMEOUT_ERROR);
    }
    
    if (error.message === 'Failed to fetch') {
      throw new Error(ERROR_MESSAGES.NETWORK_ERROR);
    }
    
    throw error;
  }
};

/**
 * Send a chat message with streaming response
 * @param {string} message - User message
 * @param {Object} options - Chat options
 * @param {string} options.sessionId - Session ID
 * @param {string} options.projectId - Project ID  
 * @param {Function} onChunk - Callback for each chunk received
 * @param {Function} onComplete - Callback when stream completes
 * @param {Function} onError - Callback for errors
 * @param {Function} onMetadata - Callback for metadata (routing, safety info)
 * @returns {Promise<void>}
 */
export const sendMessageStream = async (message, options = {}, onChunk, onComplete, onError, onMetadata) => {
  try {
    const requestBody = {
      message,
      stream: true,
      session_id: options.sessionId,
      project_id: options.projectId || 'default',
    };

    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.CHAT, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    let isDone = false;
    while (!isDone) {
      const { done, value } = await reader.read();

      if (done) {
        isDone = true;
        break;
      }

      // Decode chunk
      buffer += decoder.decode(value, { stream: true });

      // Process complete SSE messages
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith(SSE_MARKERS.DATA_PREFIX)) {
          const data = line.slice(SSE_MARKERS.DATA_PREFIX.length).trim();

          if (data === SSE_MARKERS.DONE) {
            onComplete();
            return;
          }

          // Handle metadata
          if (data.startsWith('[METADATA]')) {
            const metadataStr = data.slice('[METADATA]'.length);
            try {
              const metadata = JSON.parse(metadataStr);
              if (onMetadata) onMetadata(metadata);
            } catch (e) {
              console.warn('Failed to parse metadata:', e);
            }
            continue;
          }

          if (data) {
            // Parse JSON if the data is a JSON string
            try {
              const parsedData = JSON.parse(data);
              onChunk(parsedData);
            } catch {
              // If not JSON, send raw string data
              onChunk(data);
            }
          }
        }
      }
    }

    onComplete();
  } catch (error) {
    console.error('Stream error:', error);
    onError(error);
  }
};

/**
 * Send a chat message without streaming (JSON response)
 * @param {string} message - User message
 * @param {Object} options - Chat options
 * @param {string} options.sessionId - Session ID
 * @param {string} options.projectId - Project ID
 * @returns {Promise<Object>} Response data containing answer, sources, and metadata
 * @throws {Error} If request fails
 */
export const sendMessage = async (message, options = {}) => {
  try {
    const requestBody = {
      message,
      stream: false,
      session_id: options.sessionId,
      project_id: options.projectId || 'default',
    };

    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.CHAT, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });

    return await response.json();
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
};

/**
 * Clear conversation history
 * @param {string} sessionId - Session ID to clear (optional)
 * @returns {Promise<Object>} Response data
 * @throws {Error} If request fails
 */
export const clearHistory = async (sessionId = null) => {
  try {
    const url = sessionId 
      ? `${API_CONFIG.ENDPOINTS.CLEAR}?session_id=${sessionId}`
      : API_CONFIG.ENDPOINTS.CLEAR;
      
    const response = await fetchWithErrorHandling(url, {
      method: 'POST',
    });

    return await response.json();
  } catch (error) {
    console.error('Clear history error:', error);
    throw error;
  }
};

// Session Management Functions

/**
 * Create a new conversation session
 * @param {Object} sessionData - Session creation data
 * @param {string} sessionData.userId - User identifier
 * @param {string} sessionData.projectId - Project identifier
 * @param {string} sessionData.sessionName - Human-readable session name
 * @returns {Promise<Object>} Created session data
 * @throws {Error} If request fails
 */
export const createSession = async (sessionData) => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.SESSIONS, {
      method: 'POST',
      body: JSON.stringify({
        user_id: sessionData.userId,
        project_id: sessionData.projectId || 'default',
        session_name: sessionData.sessionName || `Session ${new Date().toLocaleString()}`,
      }),
    });

    return await response.json();
  } catch (error) {
    console.error('Create session error:', error);
    throw error;
  }
};

/**
 * Get list of sessions with optional filtering
 * @param {Object} filters - Optional filters
 * @param {string} filters.userId - Filter by user ID
 * @param {string} filters.projectId - Filter by project ID
 * @param {number} filters.limit - Maximum number of sessions
 * @returns {Promise<Object>} List of sessions
 * @throws {Error} If request fails
 */
export const listSessions = async (filters = {}) => {
  try {
    const params = new URLSearchParams();
    if (filters.userId) params.append('user_id', filters.userId);
    if (filters.projectId) params.append('project_id', filters.projectId);
    if (filters.limit) params.append('limit', filters.limit.toString());

    const url = params.toString() 
      ? `${API_CONFIG.ENDPOINTS.SESSIONS}?${params.toString()}`
      : API_CONFIG.ENDPOINTS.SESSIONS;

    const response = await fetchWithErrorHandling(url, {
      method: 'GET',
    });

    return await response.json();
  } catch (error) {
    console.error('List sessions error:', error);
    throw error;
  }
};

/**
 * Get information about a specific session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Session information
 * @throws {Error} If request fails
 */
export const getSession = async (sessionId) => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.SESSION_BY_ID(sessionId), {
      method: 'GET',
    });

    return await response.json();
  } catch (error) {
    console.error('Get session error:', error);
    throw error;
  }
};

/**
 * Delete a conversation session
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Deletion confirmation
 * @throws {Error} If request fails
 */
export const deleteSession = async (sessionId) => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.SESSION_BY_ID(sessionId), {
      method: 'DELETE',
    });

    return await response.json();
  } catch (error) {
    console.error('Delete session error:', error);
    throw error;
  }
};

/**
 * Get session statistics and memory usage
 * @param {string} sessionId - Session identifier
 * @returns {Promise<Object>} Session statistics
 * @throws {Error} If request fails
 */
export const getSessionStats = async (sessionId) => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.SESSION_STATS(sessionId), {
      method: 'GET',
    });

    return await response.json();
  } catch (error) {
    console.error('Get session stats error:', error);
    throw error;
  }
};

/**
 * Check API health status
 * @returns {Promise<Object>} Health status and stats
 * @throws {Error} If request fails
 */
export const checkHealth = async () => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.HEALTH, {
      method: 'GET',
    });

    return await response.json();
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
};

/**
 * Rebuild vector store
 * @returns {Promise<Object>} Response data with rebuild status
 * @throws {Error} If request fails
 */
export const rebuildVectorStore = async () => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.REBUILD, {
      method: 'POST',
    });

    return await response.json();
  } catch (error) {
    console.error('Rebuild error:', error);
    throw error;
  }
};

/**
 * API service object for easier imports
 */
const apiService = {
  sendMessageStream,
  sendMessage,
  clearHistory,
  checkHealth,
  rebuildVectorStore,
  // Session management
  createSession,
  listSessions,
  getSession,
  deleteSession,
  getSessionStats,
};

export default apiService;
