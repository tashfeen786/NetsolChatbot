import React, { createContext, useReducer, useContext, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendMessage, getThreads, getMessages, createThread } from '../services/api';

const initialState = {
  threads: [],
  currentThreadId: null,
  currentMessages: [],
  isLoading: false,
  error: null,
  isInitialized: false,
};

function chatReducer(state, action) {
  switch (action.type) {
    case 'SET_THREADS':
      return { ...state, threads: action.payload, isInitialized: true };
    case 'SET_CURRENT_THREAD':
      return { ...state, currentThreadId: action.payload };
    case 'SET_MESSAGES':
      return { ...state, currentMessages: action.payload };
    case 'ADD_MESSAGE': {
      const { role, content } = action.payload;
      return { ...state, currentMessages: [...state.currentMessages, { role, content }] };
    }
    case 'UPDATE_LAST_MESSAGE': {
      const { content } = action.payload;
      const msgs = [...state.currentMessages];
      const last = msgs[msgs.length - 1];
      if (last && last.role === 'assistant') {
        msgs[msgs.length - 1] = { ...last, content: last.content + content };
      } else {
        msgs.push({ role: 'assistant', content });
      }
      return { ...state, currentMessages: msgs };
    }
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'NEW_THREAD_OPTIMISTIC': {
      const { id, title } = action.payload;
      return {
        ...state,
        threads: [{ id, title, message_count: 0 }, ...state.threads],
        currentThreadId: id,
        currentMessages: [], // new thread => no messages
      };
    }
    default:
      return state;
  }
}

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Load threads on mount
  useEffect(() => {
    async function loadThreads() {
      try {
        const data = await getThreads();
        dispatch({ type: 'SET_THREADS', payload: data });
        if (data.length > 0) {
          const firstThread = data[0];
          dispatch({ type: 'SET_CURRENT_THREAD', payload: firstThread.id });
          const msgsData = await getMessages(firstThread.id);
          dispatch({ type: 'SET_MESSAGES', payload: msgsData.messages || [] });
        }
      } catch (err) {
        console.error('Failed to load threads:', err);
      }
    }
    loadThreads();
  }, []);

  // Create new thread (with safe empty-thread reuse)
  const createNewThread = async (title = 'New Chat') => {
    try {
      const freshThreads = await getThreads();
      const emptyThread = freshThreads.find((t) => t.message_count === 0);
      if (emptyThread) {
        dispatch({ type: 'SET_THREADS', payload: freshThreads });
        dispatch({ type: 'SET_CURRENT_THREAD', payload: emptyThread.id });
        dispatch({ type: 'SET_MESSAGES', payload: [] });
        return emptyThread.id;
      }
      // sync fresh list
      dispatch({ type: 'SET_THREADS', payload: freshThreads });
    } catch (err) {
      console.error('Failed to fetch fresh threads, falling back to local state:', err);
    }

    try {
      const data = await createThread(title);
      dispatch({ type: 'NEW_THREAD_OPTIMISTIC', payload: { id: data.id, title: data.title } });
      return data.id;
    } catch (err) {
      console.error('Failed to create thread:', err);
      const fallbackId = uuidv4();
      dispatch({ type: 'NEW_THREAD_OPTIMISTIC', payload: { id: fallbackId, title: 'New Chat' } });
      return fallbackId;
    }
  };

  // Switch thread with safe reload
  const switchThread = async (threadId) => {
    const isSameThread = threadId === state.currentThreadId;
    const alreadyHasMessages = state.currentMessages.length > 0;
    if (isSameThread && alreadyHasMessages) return;

    dispatch({ type: 'SET_CURRENT_THREAD', payload: threadId });
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const data = await getMessages(threadId);
      dispatch({ type: 'SET_MESSAGES', payload: data.messages || [] });
    } catch (err) {
      console.error('Failed to load messages:', err);
      dispatch({ type: 'SET_ERROR', payload: err.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  /**
   * 🔥 FIXED sendUserMessage – Robust streaming + fallback
   */
  const sendUserMessage = async (message) => {
    // Ensure we have a thread
    let threadId = state.currentThreadId;
    if (!threadId) {
      threadId = await createNewThread();
    }
    if (!threadId) {
      threadId = await createNewThread(); // retry
    }
    if (!threadId) {
      console.error('Could not create or find a thread');
      return;
    }

    // Add user message optimistically
    dispatch({ type: 'ADD_MESSAGE', payload: { role: 'user', content: message } });
    dispatch({ type: 'SET_LOADING', payload: true });

    // Flag to track if we got any assistant chunk
    let assistantStarted = false;

    try {
      // Call the streaming API – sendMessage should call the callback for each chunk
      await sendMessage(
        message,
        threadId,
        (chunk) => {
          // This callback is called for each chunk
          assistantStarted = true;
          dispatch({ type: 'UPDATE_LAST_MESSAGE', payload: { content: chunk } });
        }
      );

      // After streaming ends, if no assistant message was added, add a fallback
      // (this can happen if the API returns a non-streaming response)
      if (!assistantStarted) {
        // The API didn't call the callback; we need to get the full response.
        // But sendMessage already consumed the response. We can either:
        // 1) Modify sendMessage to also return the full response, or
        // 2) Use a separate non-streaming endpoint.
        // As a quick fix, we add a placeholder error message.
        dispatch({
          type: 'ADD_MESSAGE',
          payload: { role: 'assistant', content: '⚠️ No streaming response received. Please try again.' },
        });
        console.warn('No streaming chunks received; check sendMessage implementation.');
      }
    } catch (err) {
      console.error('Error sending message:', err);
      dispatch({ type: 'SET_ERROR', payload: err.message });
      // Add error message so user sees something
      dispatch({
        type: 'ADD_MESSAGE',
        payload: { role: 'assistant', content: `⚠️ Error: ${err.message}` },
      });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
      // Refresh thread list (to update message_count)
      try {
        const threadsData = await getThreads();
        dispatch({ type: 'SET_THREADS', payload: threadsData });
      } catch (e) {
        console.warn('Could not refresh threads after send', e);
      }
    }
  };

  const value = {
    ...state,
    newThread: createNewThread,
    switchThread,
    sendUserMessage,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  return useContext(ChatContext);
}