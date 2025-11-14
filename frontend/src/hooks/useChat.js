/**
 * Custom hook for chat functionality
 * Manages messages and chat operations with session support (non-streaming)
 */

import { useState, useCallback, useEffect } from 'react';
import { sendMessage as sendMessageAPI, clearHistory, getRecentMessages } from '../services/api.service';
import { MESSAGE_ROLES } from '../utils/constants';
import { generateId } from '../utils/helpers';

/**
 * Hook to manage chat messages and operations
 * @param {Object} options - Configuration options
 * @param {string} options.sessionId - Current session ID
 * @param {string} options.projectId - Current project ID
 * @returns {Object} Chat state and functions
 */
export const useChat = (options = {}) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState(null);
  const [lastResponseMetadata, setLastResponseMetadata] = useState(null);

  const { sessionId, projectId } = options;

  /**
   * Load message history for current session
   */
  const loadMessageHistory = useCallback(async () => {
    if (!sessionId) {
      setMessages([]);
      return;
    }

    setIsLoadingHistory(true);
    setError(null);

    try {
      const historyData = await getRecentMessages(sessionId, 50); // Load last 50 messages
      
      // Backend returns array directly, not wrapped in {messages: [...]}
      const messagesArray = Array.isArray(historyData) ? historyData : (historyData.messages || []);
      
      // Convert backend message format to frontend format
      const formattedMessages = messagesArray.map(msg => ({
        id: msg.id || msg.message_id || generateId(),
        role: msg.role,
        content: msg.content,
        timestamp: msg.created_at || msg.timestamp,
        sessionId: msg.session_id,
        projectId: msg.project_id,
        metadata: {
          routing_info: msg.routing_info,
          safety_info: msg.safety_info,
          tokens: msg.tokens,
        },
        sources: msg.sources,
      }));

      setMessages(formattedMessages);
      setIsLoadingHistory(false);
    } catch (err) {
      console.error('Failed to load message history:', err);
      setError(`Failed to load history: ${err.message}`);
      setMessages([]); // Clear messages on error
      setIsLoadingHistory(false);
    }
  }, [sessionId]);

  /**
   * Auto-load messages when session changes
   */
  useEffect(() => {
    loadMessageHistory();
  }, [sessionId, loadMessageHistory]);

  /**
   * Create a new message object
   * @param {string} role - Message role (user/assistant)
   * @param {string} content - Message content
   * @param {Object} options - Additional options
   * @returns {Object} Message object
   */
  const createMessage = useCallback((role, content, options = {}) => ({
    id: generateId(),
    role,
    content,
    timestamp: new Date().toISOString(),
    sessionId,
    projectId,
    ...options,
  }), [sessionId, projectId]);

  /**
   * Add a new message to the chat
   * @param {Object} message - Message object
   */
  const addMessage = useCallback((message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  /**
   * Send a message with non-streaming response
   * @param {string} messageText - User message text
   */
  const sendMessage = useCallback(async (messageText) => {
    if (!messageText.trim() || isLoading) {
      return;
    }

    // Add user message
    const userMessage = createMessage(MESSAGE_ROLES.USER, messageText);
    addMessage(userMessage);

    // Set loading state
    setIsLoading(true);
    setError(null);

    try {
      // Non-streaming response - always return complete response
      const response = await sendMessageAPI(messageText, { sessionId, projectId });
      
      const assistantMessage = createMessage(
        MESSAGE_ROLES.ASSISTANT,
        response.response || response.answer || response.message || 'No response',
        { 
          isStreaming: false,
          sources: response.sources,
          metadata: {
            routing_info: response.routing_info,
            safety_info: response.safety_info,
            session_id: response.session_id,
            project_id: response.project_id
          }
        }
      );
      
      addMessage(assistantMessage);
      setLastResponseMetadata(assistantMessage.metadata);
      setIsLoading(false);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setIsLoading(false);
    }
  }, [isLoading, addMessage, createMessage, sessionId, projectId]);

  /**
   * Clear all messages and chat history for current session
   */
  const clearMessages = useCallback(async () => {
    try {
      await clearHistory(sessionId);
      setMessages([]);
      setError(null);
      setLastResponseMetadata(null);
      return true;
    } catch (err) {
      setError(`Failed to clear history: ${err.message}`);
      return false;
    }
  }, [sessionId]);

  /**
   * Reset error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Refresh/reload message history
   */
  const refreshMessages = useCallback(() => {
    return loadMessageHistory();
  }, [loadMessageHistory]);

  return {
    // State
    messages,
    isLoading,
    isLoadingHistory,
    error,
    lastResponseMetadata,
    
    // Actions
    sendMessage,
    clearMessages,
    clearError,
    addMessage,
    createMessage,
    loadMessageHistory,
    refreshMessages,
  };
};

export default useChat;
