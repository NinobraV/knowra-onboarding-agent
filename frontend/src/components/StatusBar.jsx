/**
 * StatusBar Component
 * Displays health status and action indicators
 */

import PropTypes from 'prop-types';

const StatusBar = ({ healthStatus, isLoading }) => {
  const isHealthy = Boolean(healthStatus && healthStatus.status === 'healthy');

  return (
    <div className="status-bar" role="status" aria-live="polite">
      {/* Health Status Indicator */}
      <div className="health-status" title={isHealthy ? 'Connected' : 'Disconnected'}>
        <span
          className={`status-indicator ${isHealthy ? 'healthy' : 'unhealthy'}`}
          aria-hidden="true"
        >
          ●
        </span>
        <span className="small-muted" style={{ marginLeft: 8 }}>
          {isHealthy ? 'Connected' : 'Disconnected'}
        </span>

        {isLoading && (
          <span className="small-muted" style={{ marginLeft: 12 }}>
            Processing…
          </span>
        )}
      </div>

      {/* Right-side placeholder kept minimal for layout consistency */}
      <div aria-hidden="true" style={{ width: 1 }} />
    </div>
  );
};

StatusBar.propTypes = {
  healthStatus: PropTypes.shape({
    status: PropTypes.string,
    stats: PropTypes.object,
  }),
  isLoading: PropTypes.bool,
};

StatusBar.defaultProps = {
  healthStatus: null,
  isLoading: false,
};

export default StatusBar;
