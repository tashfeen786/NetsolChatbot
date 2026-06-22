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

/**
 * Assistant message ko parse karta hai.
 * <chart_data>{...}</chart_data> -> chart component
 * Baaki text -> normal paragraphs
 *
 * Component se bahar rakha hai taaki har render pe naya function
 * na bane (closure recreation avoid karne ke liye).
 */
function parseMessage(content) {
  if (!content || typeof content !== 'string') {
    return [{ type: 'text', content: '' }];
  }

  const parts = [];
  const regex = /<chart_data>([\s\S]*?)<\/chart_data>/g;
  let match;
  let lastIndex = 0;

  while ((match = regex.exec(content)) !== null) {
    // text before chart
    if (match.index > lastIndex) {
      parts.push({
        type: 'text',
        content: content.substring(lastIndex, match.index),
      });
    }

    // chart data parse
    try {
      const chartData = JSON.parse(match[1].trim());

      // 🔒 Validation: JSON valid hone ka matlab data valid hai nahi hota.
      // Agar 'data' key missing/empty hai, ChartMessage silently null
      // return karega aur user ko khali jagah dikhegi, error boundary
      // bhi nahi pakdegi (kyunki throw nahi hota). Isliye yahin check karo.
      if (
        !chartData ||
        !Array.isArray(chartData.data) ||
        chartData.data.length === 0
      ) {
        console.warn('⚠️ Chart JSON valid but data missing/empty:', chartData);
        parts.push({
          type: 'text',
          content: '[chart data missing or empty]',
        });
      } else {
        parts.push({ type: 'chart', data: chartData });
        console.log('✅ Chart parsed:', chartData);
      }
    } catch (parseErr) {
      console.warn('⚠️ Invalid chart JSON:', parseErr);
      parts.push({ type: 'text', content: match[0] }); // fallback
    }

    lastIndex = regex.lastIndex;
  }

  // remaining text after last chart
  if (lastIndex < content.length) {
    parts.push({ type: 'text', content: content.substring(lastIndex) });
  }

  // agar koi chart nahi mila toh pura content text hai
  if (parts.length === 0) {
    parts.push({ type: 'text', content });
  }

  return parts;
}

// ---------- Assistant message renderer (memoized parse) ----------
function AssistantMessageContent({ content }) {
  // useMemo: jab tak yeh specific message ka content change nahi hota,
  // re-parse skip hoga even if parent (MessageList) kisi aur reason se
  // re-render ho (e.g. naya message aaya, isLoading toggle hua).
  const parts = useMemo(() => parseMessage(content), [content]);

  return (
    <div>
      {parts.map((part, i) => {
        if (part.type === 'chart') {
          return (
            <ChartErrorBoundary key={i}>
              <ChartMessage chartData={part.data} />
            </ChartErrorBoundary>
          );
        }
        return (
          <div key={i} className="whitespace-pre-wrap">
            {part.content}
          </div>
        );
      })}
    </div>
  );
}

// ---------- Main Component ----------
function MessageList() {
  const { currentMessages: messages, isLoading } = useChat();

  // 🔒 Safety: agar messages nahi hai toh empty state dikhao
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
        const isUser = msg.role === 'user';
        const isAssistant = msg.role === 'assistant';

        return (
          <div
            key={idx}
            className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl rounded-2xl px-4 py-2 ${
                isUser
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {isUser ? (
                // User message – plain text
                <div className="whitespace-pre-wrap">{msg.content}</div>
              ) : isAssistant ? (
                // Assistant message – parse chart + text (memoized)
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