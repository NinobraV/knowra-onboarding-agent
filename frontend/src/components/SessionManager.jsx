/**
 * SessionManager Component
 * Provides UI for managing conversation sessions
 */

import React, { useState } from 'react';
import { SESSION_CONFIG, METADATA_LABELS, SUCCESS_MESSAGES } from '../utils/constants';

const SessionManager = ({
  sessions = [],
  currentSession,
  currentProject,
  isLoading,
  error,
  onCreateSession,
  onSwitchSession,
  onDeleteSession,
  onSwitchProject,
  onClearError,
  className = '',
}) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');
  const [showSessionList, setShowSessionList] = useState(false);

  const handleCreateSession = async (e) => {
    e.preventDefault();
    if (!newSessionName.trim() || isCreating) return;

    try {
      setIsCreating(true);
      await onCreateSession(newSessionName.trim());
      setNewSessionName('');
      setIsCreating(false);
    } catch (err) {
      console.error('Failed to create session:', err);
      setIsCreating(false);
    }
  };

  const handleDeleteSession = async (sessionId, sessionName) => {
    if (!window.confirm(`Delete session "${sessionName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await onDeleteSession(sessionId);
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return 'Unknown';
    }
  };
  console.log("session", sessions)

  // Resolve a session's display name robustly across possible field names
  const getSessionName = (s) => {
    if (!s) return '';
    const candidates = [
      s.session_name,
      s.name,
      s.title,
      s.sessionTitle,
      s.metadata?.session_name,
      s.metadata?.name,
    ];
    const val = candidates.find(v => typeof v === 'string' && v.trim().length > 0);
    return val || '';
  };

  return (
    <div className={`session-manager ${className}`}>
      {error && (
        <div className="error-banner">
          <span className="error-text">{error}</span>
          <button 
            onClick={onClearError}
            className="error-close"
            aria-label="Close error"
          >
            ×
          </button>
        </div>
      )}

      {/* Current Session Info */}
      <div className="current-session-info">
        <div className="session-header">
          <h3>
            {currentSession 
              ? (getSessionName(currentSession) || 'Untitled Session')
              : 'No Active Session'
            }
          </h3>
          <div className="session-actions">
            <button
              onClick={() => setShowSessionList(!showSessionList)}
              className="btn btn-outline"
              disabled={isLoading}
            >
              {showSessionList ? 'Hide' : 'Manage'} Sessions ({sessions.length})
            </button>
          </div>
        </div>
        
        {currentSession && (
          <div className="session-details">
            <span className="session-id">ID: {currentSession.session_id?.slice(0, 8)}...</span>
            <span className="session-project">Project: {currentSession.project_id || currentProject}</span>
            <span className="session-date">
              Created: {formatDate(currentSession.created_at)}
            </span>
          </div>
        )}
      </div>

      {/* Session Management Panel */}
      {showSessionList && (
        <div className="session-panel">
          {/* Create New Session */}
          <div className="create-session-section">
            <h4>Create New Session</h4>
            <form onSubmit={handleCreateSession} className="create-session-form">
              <input
                type="text"
                placeholder="Enter session name..."
                value={newSessionName}
                onChange={(e) => setNewSessionName(e.target.value)}
                maxLength={SESSION_CONFIG.SESSION_NAME_MAX_LENGTH}
                disabled={isCreating}
                className="session-name-input"
              />
              <button
                type="submit"
                disabled={isCreating || !newSessionName.trim()}
                className="btn btn-primary"
              >
                {isCreating ? 'Creating...' : 'Create'}
              </button>
            </form>
          </div>

          {/* Sessions List */}
          <div className="sessions-list-section">
            <h4>Recent Sessions</h4>
            {isLoading ? (
              <div className="loading-text">Loading sessions...</div>
            ) : sessions.length === 0 ? (
              <div className="empty-state">No sessions found</div>
            ) : (
              <div className="sessions-list">
                {sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`session-item ${currentSession?.session_id === session.session_id ? 'active' : ''}`}
                  >
                    <div className="session-item-content">
                      <div className="session-item-header">
                        <span className="session-name">
                          {getSessionName(session) || 'Untitled Session'}
                        </span>
                        <span className="session-date">
                          {formatDate(session.created_at)}
                        </span>
                      </div>
                      <div className="session-item-meta">
                        <span className="session-project">
                          {session.project_id || 'default'}
                        </span>
                        <span className="session-id">
                          {session.session_id}
                        </span>
                      </div>
                    </div>
                    
                    <div className="session-item-actions">
                      {currentSession?.session_id !== session.session_id && (
                        <button
                          onClick={() => onSwitchSession(session.session_id)}
                          className="btn btn-sm btn-outline"
                          disabled={isLoading}
                        >
                          Switch
                        </button>
                      )}
                      <button
                        onClick={() => handleDeleteSession(session.session_id, getSessionName(session))}
                        className="btn btn-sm btn-danger"
                        disabled={isLoading}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SessionManager;