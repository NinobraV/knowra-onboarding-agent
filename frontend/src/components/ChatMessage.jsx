/**
 * ChatMessage Component
 * Displays a single chat message with role indicator, timestamp, and enhanced metadata
 */

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { formatTime } from '../utils/formatters';
import { MESSAGE_ROLES } from '../utils/constants';
import MetadataDisplay from './MetadataDisplay';

const ChatMessage = ({ message, showMetadata = false }) => {
  const [showDetails, setShowDetails] = useState(false);
  const isUser = message.role === MESSAGE_ROLES.USER;
  const roleLabel = isUser ? '👤 You' : '🤖 Assistant';
  const messageClass = `message ${isUser ? 'user-message' : 'assistant-message'}`;
  
  const hasMetadata = message.metadata && (
    message.metadata.routing_info || 
    message.metadata.safety_info || 
    message.metadata.sources?.length > 0
  );

  return (
    <div className={messageClass} role="article" aria-label={`${roleLabel} message`}>
      <div className="message-header">
        <div className="message-info">
          <span className="message-role">{roleLabel}</span>
          <span className="message-time" aria-label="Message time">
            {formatTime(message.timestamp)}
          </span>
        </div>
        
        {/* Enhanced metadata badges for assistant messages */}
        {!isUser && hasMetadata && showMetadata && (
          <div className="message-badges">
            <MetadataDisplay 
              metadata={message.metadata} 
              show={true} 
              compact={true}
            />
            {hasMetadata && (
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="details-toggle"
                aria-label={showDetails ? 'Hide details' : 'Show details'}
                title="View response details"
              >
                ℹ️
              </button>
            )}
          </div>
        )}
      </div>
      
      <div className="message-content">
        {message.content || <span className="empty-message">Thinking...</span>}
        {message.isStreaming && <span className="cursor" aria-label="Typing">▊</span>}
        {message.hasError && (
          <div className="message-error">
            ⚠️ Error occurred while generating response
          </div>
        )}
      </div>

      {/* Enhanced metadata panel */}
      {!isUser && hasMetadata && showMetadata && showDetails && (
        <MetadataDisplay 
          metadata={message.metadata} 
          show={true} 
          expanded={true}
          className="message-metadata"
        />
      )}

      {/* Sources display for assistant messages */}
      {!isUser && message.sources && message.sources.length > 0 && (
        <div className="message-sources">
          <details className="sources-details">
            <summary className="sources-summary">
              📚 Sources ({message.sources.length})
            </summary>
            <ul className="sources-list">
              {message.sources.map((source, index) => (
                <li key={index} className="source-item">
                  {source}
                </li>
              ))}
            </ul>
          </details>
        </div>
      )}
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
    hasError: PropTypes.bool,
    sources: PropTypes.arrayOf(PropTypes.string),
    metadata: PropTypes.object,
  }).isRequired,
  showMetadata: PropTypes.bool,
};

export default React.memo(ChatMessage);
