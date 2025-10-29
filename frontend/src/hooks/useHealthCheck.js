/**
 * Custom hook for health check functionality
 */

import { useState, useEffect } from 'react';
import { checkHealth } from '../services/api.service';
import { ERROR_MESSAGES } from '../utils/constants';

/**
 * Hook to manage API health check
 * @param {boolean} autoCheck - Whether to automatically check on mount
 * @returns {Object} Health status, loading state, error, and refresh function
 */
export const useHealthCheck = (autoCheck = true) => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const performHealthCheck = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const status = await checkHealth();
      setHealthStatus(status);
      setError(null);
    } catch (err) {
      console.error('Health check failed:', err);
      setError(ERROR_MESSAGES.HEALTH_CHECK_FAILED);
      setHealthStatus(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (autoCheck) {
      performHealthCheck();
    }
  }, [autoCheck]);

  return {
    healthStatus,
    isLoading,
    error,
    refreshHealthCheck: performHealthCheck,
  };
};

export default useHealthCheck;
