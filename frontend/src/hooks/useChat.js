/**
 * Custom hook for chat functionality
 * Manages messages, streaming, and chat operations with session support
 */

import { useState, useCallback } from 'react';
import { sendMessage as sendMessageAPI, clearHistory, sendMessageStream } from '../services/api.service';
import { MESSAGE_ROLES } from '../utils/constants';
import { generateId } from '../utils/helpers';

/**
 * Hook to manage chat messages and operations
 * @param {Object} options - Configuration options
 * @param {string} options.sessionId - Current session ID
 * @param {string} options.projectId - Current project ID
 * @param {boolean} options.useStreaming - Whether to use streaming responses
 * @returns {Object} Chat state and functions
 */
export const useChat = (options = {}) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastResponseMetadata, setLastResponseMetadata] = useState(null);

  const { sessionId, projectId, useStreaming = true } = options;

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
   * Update the last message (for streaming)
   * @param {string} messageId - Message ID to update
   * @param {string} content - New content
   * @param {Object} updates - Additional updates
   */
  const updateMessage = useCallback((messageId, content, updates = {}) => {
    setMessages((prev) => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, content, ...updates }
        : msg
    ));
  }, []);

  /**
   * Send a message with streaming or non-streaming response
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

    if (useStreaming) {
      // Streaming response
      const assistantMessage = createMessage(
        MESSAGE_ROLES.ASSISTANT,
        '',
        { isStreaming: true }
      );
      addMessage(assistantMessage);

      try {
        await sendMessageStream(
          messageText,
          { sessionId, projectId },
          // onChunk
          (chunk) => {
            const content = typeof chunk === 'string' ? chunk : chunk.content || '';
            updateMessage(assistantMessage.id, (prev) => prev + content);
          },
          // onComplete
          () => {
            updateMessage(assistantMessage.id, null, { isStreaming: false });
            setIsLoading(false);
          },
          // onError
          (err) => {
            setError(`Streaming error: ${err.message}`);
            updateMessage(assistantMessage.id, null, { 
              isStreaming: false, 
              hasError: true 
            });
            setIsLoading(false);
          },
          // onMetadata
          (metadata) => {
            setLastResponseMetadata(metadata);
            updateMessage(assistantMessage.id, null, { metadata });
          }
        );
      } catch (err) {
        setError(`Error: ${err.message}`);
        setIsLoading(false);
      }
    } else {
      // Non-streaming response
      try {
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
    }
  }, [isLoading, addMessage, createMessage, updateMessage, useStreaming, sessionId, projectId]);

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

  return {
    // State
    messages,
    isLoading,
    error,
    lastResponseMetadata,
    
    // Actions
    sendMessage,
    clearMessages,
    clearError,
    addMessage,
    updateMessage,
    createMessage,
  };
};

export default useChat;
