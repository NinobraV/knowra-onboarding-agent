/**
 * ErrorBanner Component
 * Displays error messages with optional dismiss functionality
 */

import PropTypes from 'prop-types';

const ErrorBanner = ({ message, onDismiss, dismissible }) => {
  if (!message) {
    return null;
  }

  return (
    <div className="error-banner" role="alert" aria-live="assertive">
      <span className="error-message">⚠️ {message}</span>
      {dismissible && onDismiss && (
        <button
          onClick={onDismiss}
          className="dismiss-button"
          aria-label="Dismiss error"
          title="Dismiss"
        >
          ✕
        </button>
      )}
    </div>
  );
};

ErrorBanner.propTypes = {
  message: PropTypes.string,
  onDismiss: PropTypes.func,
  dismissible: PropTypes.bool,
};

ErrorBanner.defaultProps = {
  message: null,
  onDismiss: null,
  dismissible: false,
};

export default ErrorBanner;
