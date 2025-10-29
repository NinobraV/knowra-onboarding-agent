/**
 * ChatInput Component
 * Provides a textarea input for user messages with auto-resize and keyboard shortcuts
 */

import { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { UI_CONFIG } from '../utils/constants';

const ChatInput = ({ onSendMessage, isLoading, disabled, placeholder }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(
        textareaRef.current.scrollHeight,
        UI_CONFIG.TEXTAREA_MAX_ROWS * 24, // Approximate line height
      );
      textareaRef.current.style.height = `${newHeight}px`;
    }
  }, [input]);

  // Focus textarea on mount
  useEffect(() => {
    if (textareaRef.current && !disabled) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  /**
   * Handle form submission
   */
  const handleSubmit = (e) => {
    e.preventDefault();
    
    const trimmedInput = input.trim();
    
    // Validate input
    if (!trimmedInput || isLoading || disabled) {
      return;
    }

    // Check max length
    if (trimmedInput.length > UI_CONFIG.MAX_MESSAGE_LENGTH) {
      alert(`Message is too long. Maximum ${UI_CONFIG.MAX_MESSAGE_LENGTH} characters allowed.`);
      return;
    }

    onSendMessage(trimmedInput);
    setInput('');
  };

  /**
   * Handle keyboard shortcuts
   * Enter - Submit message
   * Shift+Enter - New line
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isDisabled = disabled || isLoading;
  const canSubmit = input.trim() && !isDisabled;

  return (
    <form onSubmit={handleSubmit} className="chat-input-form" role="search">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isDisabled}
          rows={UI_CONFIG.TEXTAREA_MIN_ROWS}
          className="chat-textarea"
          aria-label="Message input"
          maxLength={UI_CONFIG.MAX_MESSAGE_LENGTH}
        />
        <button
          type="submit"
          disabled={!canSubmit}
          className="send-button"
          title={isLoading ? 'Sending...' : 'Send message (Enter)'}
          aria-label="Send message"
        >
          {isLoading ? (
            <span className="loading-spinner" aria-hidden="true">⏳</span>
          ) : (
            <span aria-hidden="true">➤</span>
          )}
        </button>
      </div>
      {input.length > UI_CONFIG.MAX_MESSAGE_LENGTH * 0.9 && (
        <div className="character-count" aria-live="polite">
          {input.length} / {UI_CONFIG.MAX_MESSAGE_LENGTH}
        </div>
      )}
    </form>
  );
};

ChatInput.propTypes = {
  onSendMessage: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
  placeholder: PropTypes.string,
};

ChatInput.defaultProps = {
  isLoading: false,
  disabled: false,
  placeholder: 'Ask a question... (Press Enter to send, Shift+Enter for new line)',
};

export default ChatInput;
