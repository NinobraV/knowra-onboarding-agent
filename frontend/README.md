# Knowledge Chatbot - Frontend

A modern, accessible, and performant React-based frontend for the Knowledge Chatbot application. This application provides an intuitive interface for interacting with an AI-powered Q&A system.

## 🚀 Features

- **Real-time Streaming**: Server-Sent Events (SSE) for streaming AI responses
- **Responsive Design**: Mobile-first, works on all screen sizes
- **Accessibility**: WCAG compliant with ARIA labels and keyboard navigation
- **Error Handling**: Graceful error handling with user-friendly messages
- **Health Monitoring**: Real-time backend health status
- **Modern UI**: Clean, dark-themed interface with smooth animations
- **Performance Optimized**: React.memo, useCallback, and efficient rendering

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000` (or configured URL)

## 🛠️ Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
cp .env.example .env
```

## 🏃 Running the Application

### Development Mode

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatInput.jsx    # Message input component
│   │   ├── ChatMessage.jsx  # Individual message display
│   │   ├── ErrorBanner.jsx  # Error display component
│   │   ├── Header.jsx       # Application header
│   │   ├── MessageList.jsx  # Messages container
│   │   ├── StatusBar.jsx    # Health status bar
│   │   ├── WelcomeScreen.jsx # Initial welcome screen
│   │   └── index.js         # Component exports
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useAutoScroll.js # Auto-scroll behavior
│   │   ├── useChat.js       # Chat state management
│   │   └── useHealthCheck.js # API health monitoring
│   │
│   ├── services/            # External services
│   │   └── api.service.js   # Backend API client
│   │
│   ├── utils/               # Utility functions
│   │   ├── constants.js     # Application constants
│   │   ├── formatters.js    # Data formatting utilities
│   │   └── helpers.js       # Helper functions
│   │
│   ├── App.jsx              # Main application component
│   ├── main.jsx             # Application entry point
│   └── index.css            # Global styles
│
├── .eslintrc.json           # ESLint configuration
├── .env                     # Environment variables
├── vite.config.js           # Vite configuration
├── package.json             # Project dependencies
├── ARCHITECTURE.md          # Architecture documentation
└── README.md                # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### Vite Configuration

The `vite.config.js` includes:
- React plugin for Fast Refresh
- Proxy configuration for API requests
- Port configuration (default: 5173)

## 🎨 Styling

The application uses a custom CSS design system with:
- CSS custom properties (variables) for theming
- Dark mode optimized color scheme
- Responsive breakpoints for mobile/tablet/desktop
- Smooth animations and transitions

## 🧩 Key Components

### App.jsx
Main application component that orchestrates the entire UI. Uses custom hooks for state management and renders all sub-components.

### Custom Hooks

#### useChat
Manages chat state including messages, loading states, and streaming responses.

```javascript
const { messages, isLoading, error, sendMessage, clearMessages } = useChat();
```

#### useHealthCheck
Monitors backend API health status.

```javascript
const { healthStatus, error, refreshHealthCheck } = useHealthCheck();
```

#### useAutoScroll
Automatically scrolls to the bottom when new messages arrive.

```javascript
const scrollRef = useAutoScroll([messages]);
```

### API Service

Centralized service for all backend communication:
- `sendMessageStream()` - Stream chat responses
- `sendMessage()` - Send message without streaming
- `clearHistory()` - Clear conversation history
- `checkHealth()` - Check API health
- `rebuildVectorStore()` - Rebuild vector database

## 📱 Responsive Design

The application is fully responsive with breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## ♿ Accessibility Features

- Semantic HTML5 elements
- ARIA labels and roles
- Keyboard navigation support
- Focus management
- Screen reader friendly
- High contrast colors
- Sufficient color contrast ratios

## 🧪 Code Quality

### ESLint
Configured with React and React Hooks rules:

```bash
# Run linter
npm run lint
```

### Code Style
- ES6+ JavaScript
- Functional components with hooks
- PropTypes for type checking
- JSDoc comments for documentation

## 🚀 Performance Optimizations

1. **React.memo**: Memoized components to prevent unnecessary re-renders
2. **useCallback**: Memoized callbacks for stable references
3. **Code Splitting**: Dynamic imports for route-based splitting
4. **Lazy Loading**: Deferred loading of non-critical components
5. **Optimized Re-renders**: Efficient state updates and minimal re-renders

## 🐛 Debugging

### Development Tools
- React Developer Tools (browser extension)
- Redux DevTools (if using Redux)
- Network tab for API inspection
- Console logging (controlled via constants)

### Common Issues

#### Backend Connection Failed
- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration on backend
- Verify `.env` file configuration

#### Streaming Not Working
- Check browser SSE support
- Verify backend streaming endpoint
- Check network firewall/proxy settings

## 🔐 Security

- Input validation and sanitization
- XSS prevention through React's built-in escaping
- HTTPS recommended for production
- Environment variables for sensitive data
- No hardcoded credentials

## 📊 Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🤝 Contributing

1. Follow the established code style (ESLint)
2. Add PropTypes to all new components
3. Write JSDoc comments for functions
4. Test on multiple browsers
5. Update documentation for new features

## 📚 Additional Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed architecture documentation
- [Backend API Documentation](../backend/README.md) - Backend API reference

## 📝 Scripts

```json
{
  "dev": "Start development server",
  "build": "Build for production",
  "preview": "Preview production build",
  "lint": "Run ESLint"
}
```

## 🙏 Acknowledgments

- React team for the amazing framework
- Vite for blazing fast development experience
- Community for open-source contributions

## 📄 License

This project is part of the Knowra Onboarding Agent system.

---

**Note**: This is a refactored version following React best practices and modern web development standards. See `ARCHITECTURE.md` for detailed technical documentation.
