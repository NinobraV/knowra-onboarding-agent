/**
 * Application-wide constants
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  ENDPOINTS: {
    CHAT: '/api/chat',
    CLEAR: '/api/clear',
    HEALTH: '/api/health',
    REBUILD: '/api/rebuild',
  },
  TIMEOUT: 30000, // 30 seconds
};

// Message roles
export const MESSAGE_ROLES = {
  USER: 'user',
  ASSISTANT: 'assistant',
  SYSTEM: 'system',
};

// UI Constants
export const UI_CONFIG = {
  MAX_MESSAGE_LENGTH: 500,
  AUTO_SCROLL_BEHAVIOR: 'smooth',
  TEXTAREA_MIN_ROWS: 1,
  TEXTAREA_MAX_ROWS: 5,
};

// Status indicators
export const STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  STREAMING: 'streaming',
};

// Example questions for welcome screen
export const EXAMPLE_QUESTIONS = [
  'What is the onboarding process?',
  'Tell me about the system architecture',
  'What are the security requirements?',
  'How do I deploy the application?',
];

// SSE (Server-Sent Events) markers
export const SSE_MARKERS = {
  DATA_PREFIX: 'data: ',
  DONE: '[DONE]',
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Failed to connect to the server. Please check your connection.',
  API_ERROR: 'An error occurred while processing your request.',
  TIMEOUT_ERROR: 'Request timed out. Please try again.',
  STREAM_ERROR: 'Error while streaming response.',
  HEALTH_CHECK_FAILED: 'Failed to connect to backend. Please ensure the server is running.',
};

// Success messages
export const SUCCESS_MESSAGES = {
  HISTORY_CLEARED: 'Conversation history cleared successfully.',
  VECTOR_STORE_REBUILT: 'Vector store rebuilt successfully.',
};
