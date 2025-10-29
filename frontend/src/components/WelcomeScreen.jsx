/**
 * WelcomeScreen Component
 * Displays a welcome message and example questions when chat is empty
 */

import PropTypes from 'prop-types';
import { EXAMPLE_QUESTIONS } from '../utils/constants';

const WelcomeScreen = ({ onQuestionClick, exampleQuestions }) => {
  return (
    <div className="welcome-message" role="region" aria-label="Welcome">
      <h2>👋 Welcome!</h2>
      <p>Ask me anything about the knowledge base.</p>
      
      <div className="example-questions">
        <p>Try asking:</p>
        <ul role="list">
          {exampleQuestions.map((question, index) => (
            <li
              key={index}
              onClick={() => onQuestionClick?.(question)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  onQuestionClick?.(question);
                }
              }}
              role="button"
              tabIndex={0}
              aria-label={`Example question: ${question}`}
            >
              {question}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

WelcomeScreen.propTypes = {
  onQuestionClick: PropTypes.func,
  exampleQuestions: PropTypes.arrayOf(PropTypes.string),
};

WelcomeScreen.defaultProps = {
  onQuestionClick: null,
  exampleQuestions: EXAMPLE_QUESTIONS,
};

export default WelcomeScreen;
