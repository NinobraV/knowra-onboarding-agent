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
 * @param {Function} onChunk - Callback for each chunk received
 * @param {Function} onComplete - Callback when stream completes
 * @param {Function} onError - Callback for errors
 * @returns {Promise<void>}
 */
export const sendMessageStream = async (message, onChunk, onComplete, onError) => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.CHAT, {
      method: 'POST',
      body: JSON.stringify({
        message,
        stream: true,
      }),
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
 * @returns {Promise<Object>} Response data containing answer and sources
 * @throws {Error} If request fails
 */
export const sendMessage = async (message) => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.CHAT, {
      method: 'POST',
      body: JSON.stringify({
        message,
        stream: false,
      }),
    });

    return await response.json();
  } catch (error) {
    console.error('API error:', error);
    throw error;
  }
};

/**
 * Clear conversation history
 * @returns {Promise<Object>} Response data
 * @throws {Error} If request fails
 */
export const clearHistory = async () => {
  try {
    const response = await fetchWithErrorHandling(API_CONFIG.ENDPOINTS.CLEAR, {
      method: 'POST',
    });

    return await response.json();
  } catch (error) {
    console.error('Clear history error:', error);
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
};

export default apiService;
