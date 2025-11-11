import React, { useCallback, useState } from 'react';
import {
  Header,
  StatusBar,
  ErrorBanner,
  MessageList,
  SessionManager,
} from './components';
import ChatInput from './components/ChatInput';
import { useChat } from './hooks/useChat';
import { useHealthCheck } from './hooks/useHealthCheck';
import useSessionManager from './hooks/useSessionManager';
import './index.css';

function App() {
  const [showMetadata, setShowMetadata] = useState(false);
  const [useStreaming, setUseStreaming] = useState(false);

  // Session management
  const {
    sessions,
    currentSession,
    currentProject,
    userId,
    isLoading: sessionLoading,
    error: sessionError,
    createNewSession,
    loadSessions,
    switchToSession,
    removeSession,
    switchProject,
    clearError: clearSessionError,
  } = useSessionManager();

  // Chat functionality with session support
  const {
    messages,
    isLoading: chatLoading,
    error: chatError,
    lastResponseMetadata,
    sendMessage,
    clearMessages,
    clearError: clearChatError,
  } = useChat({
    sessionId: currentSession?.session_id,
    projectId: currentProject,
    useStreaming,
  });

  // Health monitoring
  const {
    healthStatus,
    error: healthError,
  } = useHealthCheck(true);

  const handleSendMessage = useCallback((messageText) => {
    sendMessage(messageText);
  }, [sendMessage]);

  const handleClearHistory = useCallback(async () => {
    const confirmed = window.confirm(`Clear history for session "${currentSession?.session_name || 'current session'}"?`);
    if (confirmed) {
      await clearMessages();
    }
  }, [clearMessages, currentSession]);

  const handleExampleClick = useCallback((question) => {
    if (!chatLoading) sendMessage(question);
  }, [sendMessage, chatLoading]);

  const displayError = chatError || sessionError || healthError;
  const isLoading = chatLoading || sessionLoading;

  return (
    <div className="app">
      <Header />

      <main className="main-content">
        <div className="container">
          {/* Enhanced Status Bar */}
          <StatusBar
            healthStatus={healthStatus}
            isLoading={isLoading}
          />

          {/* Session Management Panel */}
          <SessionManager
            sessions={sessions}
            currentSession={currentSession}
            currentProject={currentProject}
            isLoading={sessionLoading}
            error={sessionError}
            onCreateSession={createNewSession}
            onSwitchSession={switchToSession}
            onDeleteSession={removeSession}
            onSwitchProject={switchProject}
            onClearError={clearSessionError}
            className="session-manager-panel"
          />

          {/* Error Display */}
          {displayError && (
            <ErrorBanner
              message={displayError}
              onDismiss={() => {
                clearChatError();
                clearSessionError();
              }}
              dismissible={!!(chatError || sessionError)}
            />
          )}

          {/* Enhanced Controls */}
          <div className="app-controls">
            <div className="control-group">
              <label className="control-label">
                <input
                  type="checkbox"
                  checked={showMetadata}
                  onChange={(e) => setShowMetadata(e.target.checked)}
                />
                Show Response Details
              </label>
              
              <label className="control-label">
                <input
                  type="checkbox"
                  checked={useStreaming}
                  onChange={(e) => setUseStreaming(e.target.checked)}
                />
                Stream Responses
              </label>
            </div>

            {currentSession && (
              <div className="session-controls">
                <button
                  onClick={handleClearHistory}
                  className="btn btn-outline btn-sm"
                  disabled={isLoading || messages.length === 0}
                >
                  Clear History
                </button>
              </div>
            )}
          </div>

          {/* Enhanced Message List */}
          <MessageList
            messages={messages}
            onExampleClick={handleExampleClick}
            showMetadata={showMetadata}
            currentSession={currentSession}
            lastMetadata={lastResponseMetadata}
          />

          <div className="input-container">
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={chatLoading}
              disabled={!!healthError || !currentSession}
              maxChars={500}
              placeholder={
                !currentSession 
                  ? "Creating session..." 
                  : useStreaming 
                    ? "Type your message (streaming enabled)..." 
                    : "Type your message..."
              }
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
