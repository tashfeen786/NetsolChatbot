import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';
import { useChat } from '../../context/ChatContext';

export default function Sidebar() {
  const { threads, currentThreadId, newThread, switchThread, isLoading } = useChat();

  return (
    <div className="w-72 h-screen bg-gray-900 text-white flex flex-col flex-shrink-0">
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-lg">Chat</span>
        </div>
      </div>

      <div className="p-4">
        <button
          onClick={() => newThread()}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl px-4 py-3 font-medium transition-all duration-200 shadow-lg shadow-indigo-600/20 disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
        {threads.length === 0 && (
          <div className="text-center text-gray-500 text-sm mt-8">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-30" />
            No conversations yet
          </div>
        )}
        {threads.map((thread) => (
          <div
            key={thread.id}
            onClick={() => switchThread(thread.id)}
            className={`group flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 ${
              thread.id === currentThreadId
                ? 'bg-indigo-600/20 border border-indigo-500/20'
                : 'hover:bg-white/5'
            }`}
          >
            <MessageSquare className={`w-4 h-4 flex-shrink-0 ${thread.id === currentThreadId ? 'text-indigo-400' : 'text-gray-500'}`} />
            <span className="flex-1 truncate text-sm">
              {thread.message_count > 0 ? thread.title : 'Empty Chat'}
            </span>
            {thread.message_count > 0 && (
              <span className="text-xs text-gray-500">{thread.message_count}</span>
            )}
            {thread.id === currentThreadId && (
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
            )}
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-gray-800 text-xs text-gray-500 text-center">
        NetsolChat v2.0
      </div>
    </div>
  );
}