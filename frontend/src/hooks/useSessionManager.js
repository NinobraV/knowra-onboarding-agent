/**
 * Custom hook for session management
 * Handles session creation, switching, and lifecycle management
 */

import { useState, useCallback, useEffect } from 'react';
import { 
  createSession, 
  listSessions, 
  getSession, 
  deleteSession, 
  getSessionStats 
} from '../services/api.service';
import { SESSION_CONFIG, ERROR_MESSAGES } from '../utils/constants';
import { generateId } from '../utils/helpers';

/**
 * Hook to manage conversation sessions
 * @returns {Object} Session state and functions
 */
export const useSessionManager = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [currentProject, setCurrentProject] = useState(SESSION_CONFIG.DEFAULT_PROJECT_ID);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Generate a default user ID if not provided
  const [userId] = useState(() => {
    const stored = localStorage.getItem('knowra_user_id');
    if (stored) return stored;
    
    const newId = `user-${generateId()}`;
    localStorage.setItem('knowra_user_id', newId);
    return newId;
  });

  /**
   * Create a new session
   * @param {string} sessionName - Optional session name
   * @param {string} projectId - Optional project ID
   */
  const createNewSession = useCallback(async (sessionName = null, projectId = null) => {
    setIsLoading(true);
    setError(null);

    try {
      const sessionData = {
        userId,
        projectId: projectId || currentProject,
        sessionName: sessionName || `Session ${new Date().toLocaleTimeString()}`,
      };

      const newSession = await createSession(sessionData);
      
      // Add to sessions list
      setSessions(prev => [newSession, ...prev]);
      
      // Switch to new session
      setCurrentSession(newSession);
      
      setIsLoading(false);
      return newSession;
    } catch (err) {
      setError(`${ERROR_MESSAGES.SESSION_CREATE_FAILED}: ${err.message}`);
      setIsLoading(false);
      throw err;
    }
  }, [userId, currentProject]);

  /**
   * Load sessions for current user/project
   */
  const loadSessions = useCallback(async (projectId = null) => {
    setIsLoading(true);
    setError(null);

    try {
      const filters = {
        userId,
        projectId: projectId || currentProject,
        limit: SESSION_CONFIG.MAX_SESSIONS,
      };

      const response = await listSessions(filters);
      setSessions(response.sessions || []);
      
      setIsLoading(false);
      return response.sessions;
    } catch (err) {
      setError(`${ERROR_MESSAGES.SESSION_LOAD_FAILED}: ${err.message}`);
      setIsLoading(false);
      throw err;
    }
  }, [userId, currentProject]);

  /**
   * Switch to a specific session
   * @param {string} sessionId - Session ID to switch to
   */
  const switchToSession = useCallback(async (sessionId) => {
    setIsLoading(true);
    setError(null);

    try {
      const sessionInfo = await getSession(sessionId);
      setCurrentSession(sessionInfo);
      
      // Update current project if session has different project
      if (sessionInfo.project_id !== currentProject) {
        setCurrentProject(sessionInfo.project_id);
      }
      
      setIsLoading(false);
      return sessionInfo;
    } catch (err) {
      setError(`Failed to switch session: ${err.message}`);
      setIsLoading(false);
      throw err;
    }
  }, [currentProject]);

  /**
   * Delete a session
   * @param {string} sessionId - Session ID to delete
   */
  const removeSession = useCallback(async (sessionId) => {
    setIsLoading(true);
    setError(null);

    try {
      await deleteSession(sessionId);
      
      // Remove from sessions list
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      
      // If current session was deleted, clear it
      if (currentSession?.session_id === sessionId) {
        setCurrentSession(null);
      }
      
      setIsLoading(false);
      return true;
    } catch (err) {
      setError(`${ERROR_MESSAGES.SESSION_DELETE_FAILED}: ${err.message}`);
      setIsLoading(false);
      throw err;
    }
  }, [currentSession]);

  /**
   * Get statistics for a session
   * @param {string} sessionId - Session ID
   */
  const getStats = useCallback(async (sessionId) => {
    try {
      return await getSessionStats(sessionId);
    } catch (err) {
      console.error('Failed to get session stats:', err);
      return null;
    }
  }, []);

  /**
   * Switch project context
   * @param {string} projectId - Project ID to switch to
   */
  const switchProject = useCallback(async (projectId) => {
    if (projectId === currentProject) return;
    
    setCurrentProject(projectId);
    setCurrentSession(null); // Clear current session when switching projects
    
    // Load sessions for new project
    await loadSessions(projectId);
  }, [currentProject, loadSessions]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Auto-load sessions on mount and project change
  useEffect(() => {
    loadSessions();
  }, [currentProject]);

  // Create a default session if none exist and we're not in a session
  useEffect(() => {
    if (!isLoading && sessions.length === 0 && !currentSession && !error) {
      createNewSession('Welcome Session');
    }
  }, [isLoading, sessions.length, currentSession, error, createNewSession]);

  return {
    // State
    sessions,
    currentSession,
    currentProject,
    userId,
    isLoading,
    error,
    
    // Actions
    createNewSession,
    loadSessions,
    switchToSession,
    removeSession,
    switchProject,
    getStats,
    clearError,
  };
};

export default useSessionManager;