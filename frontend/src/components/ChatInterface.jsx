'use client';
import { useState } from 'react';
import MessageList from './MessageList';
import InputBox from './InputBox';
import NotesUpload from './NotesUpload';
import { chatAPI } from '@/lib/api';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  const handleSendMessage = async (message) => {
    // Add user message
    const userMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const response = await chatAPI.sendMessage(message);
      
      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        metadata: response.metadata,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r p-4 space-y-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-blue-600">🎓 College AI</h2>
          <p className="text-sm text-gray-600">Your Study Assistant</p>
        </div>
        
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {showUpload ? 'Hide Upload' : 'Upload Notes'}
        </button>
        
        {showUpload && (
          <NotesUpload onUploadSuccess={() => setShowUpload(false)} />
        )}
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-semibold mb-2">💡 Try asking:</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• "Find notes on Calculus"</li>
            <li>• "What's my Math result?"</li>
            <li>• "Show syllabus for CSE"</li>
          </ul>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        <MessageList messages={messages} />
        <InputBox onSendMessage={handleSendMessage} disabled={loading} />
      </div>
    </div>
  );
}