// src/components/Chat/MessageList.jsx
import React, { useMemo } from 'react';
import { useChat } from '../../context/ChatContext';
import ChartMessage from './ChartMessage';

// ---------- Error Boundary for Chart ----------
class ChartErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('❌ Chart render error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-red-50 border border-red-200 text-red-700 p-2 rounded text-xs mt-1">
          ⚠️ Chart could not be rendered. Check console for details.
        </div>
      );
    }
    return this.props.children;
  }
}

function parseMessage(content) {
  if (!content || typeof content !== 'string') {
    return [{ type: 'text', content: '' }];
  }

  const parts = [];
  const regex = /<chart_data>([\s\S]*?)<\/chart_data>/g;
  let match;
  let lastIndex = 0;

  while ((match = regex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: content.substring(lastIndex, match.index),
      });
    }

    try {
      const chartData = JSON.parse(match[1].trim());
      if (!chartData || !Array.isArray(chartData.data) || chartData.data.length === 0) {
        console.warn('⚠️ Chart JSON valid but data missing/empty:', chartData);
      } else {
        parts.push({ type: 'chart', data: chartData });
      }
    } catch (parseErr) {
      console.warn('⚠️ Invalid chart JSON:', parseErr);
      parts.push({ type: 'text', content: match[0] });
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < content.length) {
    parts.push({ type: 'text', content: content.substring(lastIndex) });
  }

  if (parts.length === 0) {
    parts.push({ type: 'text', content });
  }

  return parts;
}

// ---------- Assistant message renderer ----------
function AssistantMessageContent({ content }) {
  const parts = useMemo(() => parseMessage(content), [content]);

  const textParts  = parts.filter(p => p.type === 'text');
  const chartParts = parts.filter(p => p.type === 'chart');

  return (
    <div className="w-full">
      {/* Text inside bubble */}
      {textParts.map((part, i) => (
        <div key={i} className="whitespace-pre-wrap">
          {part.content}
        </div>
      ))}

      {/* Charts outside bubble — full width */}
      {chartParts.length > 0 && (
        <div className="mt-3 -mx-4 -mb-2">
          {chartParts.map((part, i) => (
            <ChartErrorBoundary key={i}>
              <ChartMessage chartData={part.data} />
            </ChartErrorBoundary>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------- Main Component ----------
function MessageList() {
  const { currentMessages: messages, isLoading } = useChat();

  if (!messages || !Array.isArray(messages)) {
    return (
      <div className="flex-1 overflow-y-auto p-4 text-gray-500">
        No messages yet.
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((msg, idx) => {
        const isUser      = msg.role === 'user';
        const isAssistant = msg.role === 'assistant';
        const hasChart    = isAssistant && msg.content?.includes('<chart_data>');

        return (
          <div
            key={idx}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`rounded-2xl px-4 py-3 ${
                isUser
                  ? 'max-w-2xl bg-indigo-600 text-white'
                  : hasChart
                    ? 'w-full max-w-4xl bg-gray-100 text-gray-800'
                    : 'max-w-2xl bg-gray-100 text-gray-800'
              }`}
            >
              {isUser ? (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              ) : isAssistant ? (
                <AssistantMessageContent content={msg.content} />
              ) : null}
            </div>
          </div>
        );
      })}

      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-gray-100 text-gray-500 rounded-2xl px-4 py-2">
            Thinking...
          </div>
        </div>
      )}
    </div>
  );
}

export default MessageList;