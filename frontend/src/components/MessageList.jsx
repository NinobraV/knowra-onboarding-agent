/**
 * MessageList Component
 * Container for displaying chat messages with auto-scroll
 */

import PropTypes from 'prop-types';
import ChatMessage from './ChatMessage';
import WelcomeScreen from './WelcomeScreen';
import { useAutoScroll } from '../hooks/useAutoScroll';

const MessageList = ({ messages, onExampleClick }) => {
  const scrollRef = useAutoScroll([messages]);

  return (
    <div className="messages-container" role="log" aria-live="polite" aria-label="Chat messages">
      {messages.length === 0 ? (
        <WelcomeScreen onQuestionClick={onExampleClick} />
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
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
};

MessageList.defaultProps = {
  messages: [],
  onExampleClick: null,
};

export default MessageList;
