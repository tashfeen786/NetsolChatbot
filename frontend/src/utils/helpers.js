export const formatTime = (date) => {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export const generateThreadTitle = (messages) => {
  const first = messages.find(m => m.role === 'user');
  return first ? first.content.slice(0, 30) + '...' : 'New Chat';
};