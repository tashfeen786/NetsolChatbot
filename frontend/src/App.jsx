import React from 'react';
import { ChatProvider } from './context/ChatContext';
import ChatLayout from './components/layout/ChatLayout';

function App() {
  return (
    <ChatProvider>
      <ChatLayout />
    </ChatProvider>
  );
}

export default App;