import React, { useState, useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import { Send, Paperclip, X, CheckCircle, AlertCircle, Loader2, FileText } from 'lucide-react';

const ALLOWED = ["pdf", "docx", "txt"];

export default function MessageInput() {
  const [message, setMessage] = useState('');
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const { sendUserMessage, isLoading } = useChat();
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  // Auto-clear only error toasts after 5 seconds
  useEffect(() => {
    if (uploadStatus?.state === 'error') {
      const timer = setTimeout(() => setUploadStatus(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [uploadStatus]);

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      sendUserMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [message]);

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (!ALLOWED.includes(ext)) {
      setUploadStatus({
        state: 'error',
        text: `Unsupported type: .${ext}. Allowed: pdf, docx, txt`,
      });
      return;
    }

    setUploadStatus({ state: 'uploading', text: `Uploading ${file.name}...` });

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.error) {
        setUploadStatus({ state: 'error', text: data.error });
      } else {
        // Clear uploading toast, add to persistent file list
        setUploadStatus(null);
        setUploadedFiles((prev) => [
          ...prev,
          { name: data.filename, chunks: data.chunks_added },
        ]);
      }
    } catch {
      setUploadStatus({
        state: 'error',
        text: 'Upload failed. Is the server running?',
      });
    }
  };

  const removeFile = (index) => {
    setUploadedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3">
      <div className="max-w-4xl mx-auto">

        {/* Persistent uploaded files list */}
        {uploadedFiles.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {uploadedFiles.map((f, i) => (
              <div
                key={i}
                className="flex items-center gap-1.5 bg-green-50 border border-green-200 text-green-700 text-xs px-2.5 py-1.5 rounded-lg"
              >
                <FileText className="w-3 h-3 flex-shrink-0" />
                <span className="max-w-[180px] truncate font-medium">{f.name}</span>
                <span className="text-green-500">({f.chunks} chunks)</span>
                <button
                  onClick={() => removeFile(i)}
                  className="ml-1 text-green-400 hover:text-green-700 transition-colors"
                  title="Remove from view (file stays in knowledge base)"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Error / uploading toast */}
        {uploadStatus && (
          <div
            className={`flex items-center gap-2 mb-2 px-3 py-2 rounded-xl text-sm ${
              uploadStatus.state === 'uploading'
                ? 'bg-indigo-50 text-indigo-700'
                : 'bg-red-50 text-red-700'
            }`}
          >
            {uploadStatus.state === 'uploading' ? (
              <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
            )}
            <span className="flex-1 truncate">{uploadStatus.text}</span>
            <button onClick={() => setUploadStatus(null)}>
              <X className="w-3.5 h-3.5 opacity-60 hover:opacity-100" />
            </button>
          </div>
        )}

        <div className="flex items-end gap-2">
          {/* Hidden file input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            onChange={handleFileChange}
          />

          {/* Attach button */}
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadStatus?.state === 'uploading'}
            title="Upload PDF, Word, or TXT file"
            className={`flex items-center justify-center w-11 h-11 rounded-full flex-shrink-0 transition-all duration-200 ${
              uploadStatus?.state === 'uploading'
                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                : 'bg-gray-100 hover:bg-indigo-50 text-gray-500 hover:text-indigo-600'
            }`}
          >
            {uploadStatus?.state === 'uploading' ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Paperclip className="w-4 h-4" />
            )}
          </button>

          {/* Textarea */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              rows={1}
              className="w-full resize-none rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
              placeholder="Type a message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
          </div>

          {/* Send button */}
          <button
            onClick={handleSend}
            disabled={!message.trim() || isLoading}
            className={`flex items-center justify-center w-11 h-11 rounded-full transition-all duration-200 flex-shrink-0 ${
              message.trim() && !isLoading
                ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-500/30'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}