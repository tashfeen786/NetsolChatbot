import React, { useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import Sidebar from './Sidebar';
import ChatWindow from '../chat/ChatWindow';

export default function ChatLayout() {
  const { currentThreadId, newThread } = useChat();

  useEffect(() => {
    if (!currentThreadId) {
      newThread();
    }
  }, []);

  return (
    <div className="flex h-screen bg-gray-100 overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 min-h-0">
        <ChatWindow />
      </div>
    </div>
  );
}