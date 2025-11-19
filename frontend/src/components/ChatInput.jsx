/**
 * ChatInput Component (updated)
 * - Auto-resize textarea
 * - Allow typing/paste beyond max limit (no truncation)
 * - Show character-over indicator only when over limit
 * - Disable submit when over limit
 * - Support IME composition and Shift+Enter for newline
 */

import { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';
import { UI_CONFIG } from '../utils/constants';

const DEFAULTS = {
  MAX_MESSAGE_LENGTH: 500,
  TEXTAREA_MIN_ROWS: 2,
  TEXTAREA_MAX_ROWS: 8,
};

const ChatInput = ({ onSendMessage, isLoading, disabled, placeholder }) => {
  const cfg = {
    MAX_MESSAGE_LENGTH: UI_CONFIG?.MAX_MESSAGE_LENGTH ?? DEFAULTS.MAX_MESSAGE_LENGTH,
    TEXTAREA_MIN_ROWS: UI_CONFIG?.TEXTAREA_MIN_ROWS ?? DEFAULTS.TEXTAREA_MIN_ROWS,
    TEXTAREA_MAX_ROWS: UI_CONFIG?.TEXTAREA_MAX_ROWS ?? DEFAULTS.TEXTAREA_MAX_ROWS,
  };

  const [input, setInput] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef(null);

  // Auto-resize textarea based on content (rows approximation)
  useEffect(() => {
    if (!textareaRef.current) return;
    const ta = textareaRef.current;

    // reset height then set to scrollHeight capped by max rows
    ta.style.height = 'auto';
    const lineHeight = parseFloat(getComputedStyle(ta).lineHeight) || 20;
    const maxHeight = cfg.TEXTAREA_MAX_ROWS * lineHeight;
    const newHeight = Math.min(ta.scrollHeight, maxHeight);
    ta.style.height = `${newHeight}px`;
  }, [input, cfg.TEXTAREA_MAX_ROWS]);

  // Focus on mount if not disabled
  useEffect(() => {
    if (textareaRef.current && !disabled) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const overLimit = input.length > cfg.MAX_MESSAGE_LENGTH;
  const trimmed = input.trim();
  const isDisabled = disabled || isLoading;
  const canSubmit = Boolean(trimmed) && !isDisabled && !overLimit;

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!canSubmit) return;
    onSendMessage(trimmed);
    setInput('');
  };

  const handleKeyDown = (e) => {
    // Handle IME composition properly
    if (isComposing) return;

    // Enter to submit, Shift+Enter for newline
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleChange = (e) => {
    setInput(e.target.value);
  };

  const handlePaste = (e) => {
    // allow full paste (no truncation)
    // optional: you can warn if paste will create huge input
    // const paste = (e.clipboardData || window.clipboardData).getData('text');
    // if (paste.length > 5000) { ... }
  };

  return (
    <form onSubmit={handleSubmit} className="chat-input-form" role="search" aria-label="Chat input form">
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          onCompositionStart={() => setIsComposing(true)}
          onCompositionEnd={() => setIsComposing(false)}
          placeholder={placeholder}
          disabled={isDisabled}
          rows={cfg.TEXTAREA_MIN_ROWS}
          className="chat-textarea"
          aria-label="Message input"
          // DO NOT set maxLength so user can exceed and see counter
        />

        <button
          type="submit"
          disabled={!canSubmit}
          className="send-button"
          title={isLoading ? 'Sending...' : 'Send message (Enter)'}
          aria-label="Send message"
          aria-disabled={!canSubmit}
        >
          {isLoading ? <span className="loading-spinner" aria-hidden="true">⏳</span> : <span aria-hidden="true">➤</span>}
        </button>
      </div>

      {/* Show character info ONLY when over limit */}
      {overLimit && (
        <div className="character-count" aria-live="polite" role="status" style={{ color: 'var(--error-color)' }}>
          {input.length} / {cfg.MAX_MESSAGE_LENGTH} ký tự — bạn đã vượt giới hạn
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
