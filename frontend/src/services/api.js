const API_URL = import.meta.env.VITE_API_URL;

export async function getThreads() {
  const response = await fetch(`${API_URL}/api/threads`);
  if (!response.ok) throw new Error('Failed to fetch threads');
  const data = await response.json();
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.threads)) return data.threads;
  console.warn('⚠️ getThreads: unexpected response shape, returning empty array:', data);
  return [];
}

export async function getMessages(threadId) {
  const response = await fetch(`${API_URL}/api/threads/${threadId}/messages`);
  if (!response.ok) throw new Error('Failed to fetch messages');
  const data = await response.json();
  if (Array.isArray(data)) return { messages: data };
  if (data && Array.isArray(data.messages)) return data;
  console.warn('⚠️ getMessages: unexpected response shape, returning empty messages:', data);
  return { messages: [] };
}

export async function createThread(title = 'New Chat') {
  const response = await fetch(`${API_URL}/api/threads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) throw new Error('Failed to create thread');
  return response.json();
}

/**
 * 🔥 ULTRA‑ROBUST sendMessage – ab kabhi bhi onChunk call nahi bhoolta.
 * 
 * - SSE (`data: ...`) -> parse JSON, extract text field, emit.
 * - Plain text -> emit raw chunk.
 * - JSON (non‑SSE) -> parse, extract response/reply/content, emit full.
 * - Empty response -> end mein force‑emit empty string (taake fallback na aaye).
 * - Agar koi bhi chunk emit nahi hua, toh accumulated full response ko
 *   ek baar emit kar deta hai.
 */
export async function sendMessage(message, threadId, onChunk) {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, thread_id: threadId }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || 'API request failed');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let fullResponse = '';
  let chunkEmitted = false;   // flag – kya humne kabhi onChunk call kiya?

  // Pehle pehle chunk ko pehchan ke decide format
  let formatDetected = false;
  let isSSE = false;
  let isJSON = false;

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const decoded = decoder.decode(value, { stream: true });
    fullResponse += decoded;
    buffer += decoded;

    // Format detect karo agar abhi tak nahi kiya
    if (!formatDetected && buffer.length > 0) {
      isSSE = buffer.includes('data:');
      // Agar SSE nahi hai aur buffer { se shuru hota hai to JSON ho sakta hai
      if (!isSSE && buffer.trim().startsWith('{')) {
        isJSON = true;
      }
      formatDetected = true;
    }

    if (isSSE) {
      // SSE lines split
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data:')) continue;
        const payload = trimmed.slice(5).trim();
        if (!payload || payload === '[DONE]') continue;
        try {
          const parsed = JSON.parse(payload);
          const text =
            parsed.content ?? parsed.delta ?? parsed.text ?? parsed.chunk ?? '';
          if (text) {
            onChunk(text);
            chunkEmitted = true;
          }
        } catch {
          // JSON parse fail – treat as raw text
          if (payload) {
            onChunk(payload);
            chunkEmitted = true;
          }
        }
      }
    } else if (isJSON) {
      // Puri response JSON ho sakti hai, lekin chunked aa sakti hai.
      // Hum puri accumulate karke end mein parse karenge.
      // Filhaal hum kuch nahi emit karte, bas accumulate karte hain.
      // (Neeche end mein handle karenge)
    } else {
      // Raw plain text stream
      if (decoded) {
        onChunk(decoded);
        chunkEmitted = true;
      }
      buffer = '';
    }
  }

  // --- Stream khatam hone ke baad ---

  // Agar SSE stream tha, to buffer mein kuch bacha ho toh flush
  if (isSSE && buffer.trim().startsWith('data:')) {
    const payload = buffer.trim().slice(5).trim();
    if (payload && payload !== '[DONE]') {
      try {
        const parsed = JSON.parse(payload);
        const text =
          parsed.content ?? parsed.delta ?? parsed.text ?? parsed.chunk ?? '';
        if (text) {
          onChunk(text);
          chunkEmitted = true;
        }
      } catch {
        if (payload) {
          onChunk(payload);
          chunkEmitted = true;
        }
      }
    }
  }

  // Agar JSON format tha (non-SSE), toh fullResponse ko parse karo
  if (isJSON && !chunkEmitted) {
    try {
      const parsed = JSON.parse(fullResponse.trim());
      const text = parsed.response ?? parsed.reply ?? parsed.content ?? parsed.answer ?? '';
      if (text) {
        onChunk(text);
        chunkEmitted = true;
      } else {
        // Agar koi relevant field nahi mila, to poora JSON string bhej do
        if (fullResponse.trim()) {
          onChunk(fullResponse.trim());
          chunkEmitted = true;
        }
      }
    } catch {
      // Parse fail – raw text bhejo
      if (fullResponse.trim()) {
        onChunk(fullResponse.trim());
        chunkEmitted = true;
      }
    }
  }

  // 🔥 FINAL SAFETY: agar ab tak koi chunk emit nahi hua, toh fullResponse
  // ko ek baar emit karo (chahe khali ho)
  if (!chunkEmitted) {
    if (fullResponse.trim()) {
      onChunk(fullResponse.trim());
    } else {
      // Agar fullResponse bhi khali hai, to kuch nahi aaya – emit empty string
      onChunk('');
    }
  }
}