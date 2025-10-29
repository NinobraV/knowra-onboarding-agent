/**
 * Custom hook for chat functionality
 * Manages messages, streaming, and chat operations
 */

import { useState, useCallback } from 'react';
import { sendMessageStream, clearHistory } from '../services/api.service';
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
  const [streamingMessageId, setStreamingMessageId] = useState(null);

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
   * Update a specific message by ID
   * @param {string} messageId - ID of message to update
   * @param {Object} updates - Properties to update
   */
  const updateMessage = useCallback((messageId, updates) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId ? { ...msg, ...updates } : msg,
      ),
    );
  }, []);

  /**
   * Remove a message by ID
   * @param {string} messageId - ID of message to remove
   */
  const removeMessage = useCallback((messageId) => {
    setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
  }, []);

  /**
   * Append content to a streaming message
   * @param {string} messageId - ID of message to update
   * @param {string} chunk - Content chunk to append
   */
  const appendToMessage = useCallback((messageId, chunk) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId
          ? { ...msg, content: msg.content + chunk }
          : msg,
      ),
    );
  }, []);

  /**
   * Send a message and handle streaming response
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

    // Create assistant message placeholder
    const assistantMessageId = generateId();
    const assistantMessage = createMessage(
      MESSAGE_ROLES.ASSISTANT,
      '',
      { isStreaming: true },
    );
    assistantMessage.id = assistantMessageId; // Use specific ID for updates
    
    addMessage(assistantMessage);
    setStreamingMessageId(assistantMessageId);

    // Stream response
    await sendMessageStream(
      messageText,
      // onChunk - append each chunk to the assistant message
      (chunk) => {
        appendToMessage(assistantMessageId, chunk);
      },
      // onComplete - mark streaming as complete
      () => {
        updateMessage(assistantMessageId, { isStreaming: false });
        setIsLoading(false);
        setStreamingMessageId(null);
      },
      // onError - handle error
      (err) => {
        setError(`Error: ${err.message}`);
        setIsLoading(false);
        setStreamingMessageId(null);
        // Remove the incomplete assistant message
        removeMessage(assistantMessageId);
      },
    );
  }, [isLoading, addMessage, appendToMessage, updateMessage, removeMessage]);

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
    streamingMessageId,
    
    // Actions
    sendMessage,
    clearMessages,
    clearError,
    addMessage,
    updateMessage,
    removeMessage,
  };
};

export default useChat;
