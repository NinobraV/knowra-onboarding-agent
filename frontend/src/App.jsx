import React, { useCallback } from 'react';
import {
  Header,
  StatusBar,
  ErrorBanner,
  MessageList,
  ChatInput,
} from './components';
import { useChat } from './hooks/useChat';
import { useHealthCheck } from './hooks/useHealthCheck';
import './index.css';

function App() {
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    clearError,
  } = useChat();

  const {
    healthStatus,
    error: healthError,
  } = useHealthCheck(true);

  const handleSendMessage = useCallback((messageText) => {
    sendMessage(messageText);
  }, [sendMessage]);

  // keep clear logic available but not exposed in UI
  const handleClearHistory = useCallback(async () => {
    const confirmed = window.confirm('Are you sure you want to clear the conversation history?');
    if (confirmed) {
      await clearMessages();
    }
  }, [clearMessages]);

  const handleExampleClick = useCallback((question) => {
    if (!isLoading) sendMessage(question);
  }, [sendMessage, isLoading]);

  const displayError = error || healthError;

  return (
    <div className="app">
      <Header />

      <main className="main-content">
        <div className="container">
          {/* StatusBar: no clear button, no docs count */}
          <StatusBar
            healthStatus={healthStatus}
            isLoading={isLoading}
          />

          {displayError && (
            <ErrorBanner
              message={displayError}
              onDismiss={clearError}
              dismissible={!!error}
            />
          )}

          <MessageList
            messages={messages}
            onExampleClick={handleExampleClick}
          />

          <div className="input-container">
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              disabled={!!healthError}
              maxChars={2000}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
