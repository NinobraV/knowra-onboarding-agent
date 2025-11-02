/**
 * Custom hook for chat functionality
 * Manages messages, streaming, and chat operations
 */

import { useState, useCallback } from 'react';
import { sendMessage as sendMessageAPI, clearHistory } from '../services/api.service';
import { MESSAGE_ROLES } from '../utils/constants';
import { generateId } from '../utils/helpers';

/**
 * Hook to manage chat messages and operations
 * @returns {Object} Chat state and functions
 */
export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Create a new message object
   * @param {string} role - Message role (user/assistant)
   * @param {string} content - Message content
   * @param {Object} options - Additional options
   * @returns {Object} Message object
   */
  const createMessage = (role, content, options = {}) => ({
    id: generateId(),
    role,
    content,
    timestamp: new Date().toISOString(),
    ...options,
  });

  /**
   * Add a new message to the chat
   * @param {Object} message - Message object
   */
  const addMessage = useCallback((message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  /**
   * Send a message and handle response (non-streaming)
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
      // Send message and get complete response
      const response = await sendMessageAPI(messageText);
      
      // Create assistant message with complete response
      const assistantMessage = createMessage(
        MESSAGE_ROLES.ASSISTANT,
        response.response || response.answer || response.message || 'No response',
        { isStreaming: false },
      );
      
      addMessage(assistantMessage);
      setIsLoading(false);
    } catch (err) {
      setError(`Error: ${err.message}`);
      setIsLoading(false);
    }
  }, [isLoading, addMessage, createMessage]);

  /**
   * Clear all messages and chat history
   */
  const clearMessages = useCallback(async () => {
    try {
      await clearHistory();
      setMessages([]);
      setError(null);
      return true;
    } catch (err) {
      setError(`Failed to clear history: ${err.message}`);
      return false;
    }
  }, []);

  /**
   * Reset error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // State
    messages,
    isLoading,
    error,
    
    // Actions
    sendMessage,
    clearMessages,
    clearError,
    addMessage,
  };
};

export default useChat;
