/**
 * ChatMessage Component
 * Displays a single chat message with role indicator and timestamp
 */

import React from 'react';
import PropTypes from 'prop-types';
import { formatTime } from '../utils/formatters';
import { MESSAGE_ROLES } from '../utils/constants';

const ChatMessage = ({ message }) => {
  const isUser = message.role === MESSAGE_ROLES.USER;
  const roleLabel = isUser ? '👤 You' : '🤖 Assistant';
  const messageClass = `message ${isUser ? 'user-message' : 'assistant-message'}`;

  return (
    <div className={messageClass} role="article" aria-label={`${roleLabel} message`}>
      <div className="message-header">
        <span className="message-role">{roleLabel}</span>
        <span className="message-time" aria-label="Message time">
          {formatTime(message.timestamp)}
        </span>
      </div>
      <div className="message-content">
        {message.content || <span className="empty-message">Thinking...</span>}
        {message.isStreaming && <span className="cursor" aria-label="Typing">▊</span>}
      </div>
    </div>
  );
};

ChatMessage.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string.isRequired,
    role: PropTypes.oneOf([MESSAGE_ROLES.USER, MESSAGE_ROLES.ASSISTANT, MESSAGE_ROLES.SYSTEM]).isRequired,
    content: PropTypes.string.isRequired,
    timestamp: PropTypes.string.isRequired,
    isStreaming: PropTypes.bool,
  }).isRequired,
};

export default React.memo(ChatMessage);
