/**
 * StatusBar Component
 * Displays health status and action buttons
 */

import PropTypes from 'prop-types';

const StatusBar = ({
  healthStatus,
  showClearButton,
  onClearHistory,
  isLoading,
}) => {
  return (
    <div className="status-bar" role="status">
      {/* Health Status Indicator */}
      {healthStatus && (
        <div className="health-status">
          <span 
            className="status-indicator healthy" 
            aria-label="Connected to server"
          >
            ●
          </span>
          <span>Connected</span>
          {healthStatus.stats && (
            <span className="stats-info">
              | {healthStatus.stats.documents_loaded} docs loaded
            </span>
          )}
        </div>
      )}

      {/* Clear History Button */}
      {showClearButton && (
        <button
          onClick={onClearHistory}
          className="clear-button"
          disabled={isLoading}
          aria-label="Clear conversation history"
        >
          🗑️ Clear History
        </button>
      )}
    </div>
  );
};

StatusBar.propTypes = {
  healthStatus: PropTypes.shape({
    status: PropTypes.string,
    stats: PropTypes.shape({
      documents_loaded: PropTypes.number,
    }),
  }),
  showClearButton: PropTypes.bool,
  onClearHistory: PropTypes.func,
  isLoading: PropTypes.bool,
};

StatusBar.defaultProps = {
  healthStatus: null,
  showClearButton: false,
  onClearHistory: () => {},
  isLoading: false,
};

export default StatusBar;
