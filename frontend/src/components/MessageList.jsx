/**
 * MessageList Component
 * Container for displaying chat messages with auto-scroll and enhanced features
 */

import PropTypes from 'prop-types';
import ChatMessage from './ChatMessage';
import WelcomeScreen from './WelcomeScreen';
import { useAutoScroll } from '../hooks/useAutoScroll';

const MessageList = ({ 
  messages, 
  onExampleClick, 
  showMetadata = false,
  currentSession = null,
  lastMetadata = null
}) => {
  const scrollRef = useAutoScroll([messages]);

  return (
    <div className="messages-container" role="log" aria-live="polite" aria-label="Chat messages">
      {messages.length === 0 ? (
        <WelcomeScreen 
          onQuestionClick={onExampleClick}
          currentSession={currentSession}
          projectId={currentSession?.project_id}
        />
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage 
              key={message.id} 
              message={message} 
              showMetadata={showMetadata}
            />
          ))}
          
          {/* Enhanced session info */}
          {showMetadata && lastMetadata && (
            <div className="session-status">
              <div className="session-info-card">
                <h4>Session Status</h4>
                <div className="status-grid">
                  {lastMetadata.session_id && (
                    <div className="status-item">
                      <span className="status-label">Session ID:</span>
                      <span className="status-value" title={lastMetadata.session_id}>
                        {lastMetadata.session_id.slice(0, 8)}...
                      </span>
                    </div>
                  )}
                  {lastMetadata.project_id && (
                    <div className="status-item">
                      <span className="status-label">Project:</span>
                      <span className="status-value">{lastMetadata.project_id}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          <div ref={scrollRef} aria-hidden="true" />
        </>
      )}
    </div>
  );
};

MessageList.propTypes = {
  messages: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      role: PropTypes.string.isRequired,
      content: PropTypes.string.isRequired,
      timestamp: PropTypes.string.isRequired,
    }),
  ),
  onExampleClick: PropTypes.func,
  showMetadata: PropTypes.bool,
  currentSession: PropTypes.object,
  lastMetadata: PropTypes.object,
};

MessageList.defaultProps = {
  messages: [],
  onExampleClick: null,
  showMetadata: false,
  currentSession: null,
  lastMetadata: null,
};

export default MessageList;
