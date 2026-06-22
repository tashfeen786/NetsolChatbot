import React, { useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import { Bot, Menu } from 'lucide-react';

export default function ChatWindow() {
  const { currentMessages, isLoading, currentThreadId } = useChat();
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentMessages, isLoading]);

  if (!currentThreadId) {
    return (
      <div className="flex-1 flex items-center justify-center bg-gray-50 min-h-0">
        <div className="text-center">
          <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-600">Start a new conversation</h2>
          <p className="text-gray-400 mt-2">Click "New Chat" to begin</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-50 min-h-0">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 gradient-primary rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-800">Chat Assistant</h2>
            <p className="text-xs text-gray-400">Online</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-gray-400">Ready</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 min-h-0">
        {currentMessages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <Bot className="w-14 h-14 mb-4 opacity-30" />
            <p className="text-lg font-medium text-gray-300">No messages yet</p>
            <p className="text-sm">Start typing below to chat</p>
          </div>
        ) : (
          <MessageList messages={currentMessages} />
        )}
        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <MessageInput />
    </div>
  );
}