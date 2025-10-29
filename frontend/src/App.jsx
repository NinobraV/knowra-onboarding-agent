/**
 * Main Application Component
 * Knowledge Chatbot - AI-powered Q&A system
 */

import { useCallback } from 'react';
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
  // Custom hooks for managing state
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

  /**
   * Handle sending a new message
   */
  const handleSendMessage = useCallback((messageText) => {
    sendMessage(messageText);
  }, [sendMessage]);

  /**
   * Handle clearing chat history with confirmation
   */
  const handleClearHistory = useCallback(async () => {
    const confirmed = window.confirm(
      'Are you sure you want to clear the conversation history?',
    );
    
    if (confirmed) {
      const success = await clearMessages();
      if (success) {
        // History cleared successfully
      }
    }
  }, [clearMessages]);

  /**
   * Handle clicking on example questions
   */
  const handleExampleClick = useCallback((question) => {
    if (!isLoading) {
      sendMessage(question);
    }
  }, [sendMessage, isLoading]);

  // Combine errors from chat and health check
  const displayError = error || healthError;

  return (
    <div className="app">
      {/* Header Section */}
      <Header />

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* Status Bar */}
          <StatusBar
            healthStatus={healthStatus}
            showClearButton={messages.length > 0}
            onClearHistory={handleClearHistory}
            isLoading={isLoading}
          />

          {/* Error Display */}
          {displayError && (
            <ErrorBanner
              message={displayError}
              onDismiss={clearError}
              dismissible={!!error}
            />
          )}

          {/* Messages Container */}
          <MessageList
            messages={messages}
            onExampleClick={handleExampleClick}
          />

          {/* Input Section */}
          <div className="input-container">
            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              disabled={!!healthError}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
