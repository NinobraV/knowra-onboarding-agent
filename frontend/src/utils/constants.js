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
    // Enhanced session management endpoints
    SESSIONS: '/api/sessions',
    SESSION_BY_ID: (sessionId) => `/api/sessions/${sessionId}`,
    SESSION_STATS: (sessionId) => `/api/sessions/${sessionId}/stats`,
    // Message history endpoints
    SESSION_MESSAGES: (sessionId) => `/api/sessions/${sessionId}/messages`,
    SESSION_MESSAGES_RECENT: (sessionId) => `/api/sessions/${sessionId}/messages/recent`,
    SESSION_HISTORY_STATS: (sessionId) => `/api/sessions/${sessionId}/history-stats`,
    GLOBAL_STATS: '/api/stats/global',
  },
  TIMEOUT: 450000, // 45 seconds
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

// Enhanced example questions by project type
export const PROJECT_EXAMPLES = {
  'onboarding': [
    'What is the employee onboarding checklist?',
    'How long does the onboarding process take?',
    'What documents do new employees need?',
  ],
  'development': [
    'What is the system architecture?',
    'How do I set up the development environment?',
    'What are the coding standards?',
  ],
  'deployment': [
    'How do I deploy to production?',
    'What are the security requirements?',
    'How do I monitor the application?',
  ],
};

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
  SESSION_CREATE_FAILED: 'Failed to create new session.',
  SESSION_LOAD_FAILED: 'Failed to load session.',
  SESSION_DELETE_FAILED: 'Failed to delete session.',
};

// Success messages
export const SUCCESS_MESSAGES = {
  HISTORY_CLEARED: 'Conversation history cleared successfully.',
  VECTOR_STORE_REBUILT: 'Vector store rebuilt successfully.',
  SESSION_CREATED: 'New session created successfully.',
  SESSION_DELETED: 'Session deleted successfully.',
  SESSION_SWITCHED: 'Switched to session successfully.',
};

// Session and project constants
export const SESSION_CONFIG = {
  DEFAULT_PROJECT_ID: 'default',
  MAX_SESSIONS: 50,
  SESSION_NAME_MAX_LENGTH: 100,
  AUTO_GENERATE_NAMES: true,
};

// Enhanced metadata display
export const METADATA_LABELS = {
  ROUTING: {
    'kb_only': 'Knowledge Base',
    'memory_only': 'Conversation Memory', 
    'kb_and_memory': 'Knowledge + Memory',
    'sensitive_handling': 'Sensitive Content',
    'default': 'Standard Processing',
  },
  SAFETY: {
    'safe': '✅ Safe',
    'potentially_sensitive': '⚠️ Sensitive',
    'sensitive': '🔒 Restricted',
    'harmful': '❌ Blocked',
  },
};
