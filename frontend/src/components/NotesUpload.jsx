'use client';
import { useState } from 'react';
import { chatAPI } from '@/lib/api';

export default function NotesUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [subject, setSubject] = useState('');
  const [topic, setTopic] = useState('');
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!file || !subject || !topic) {
      alert('Please fill all fields');
      return;
    }

    setUploading(true);
    try {
      const result = await chatAPI.uploadNotes(file, { subject, topic });
      alert('✅ Notes uploaded successfully!');
      
      // Reset form
      setFile(null);
      setSubject('');
      setTopic('');
      
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (error) {
      alert('❌ Upload failed: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-lg text-black font-semibold mb-4">📤 Upload Notes</h3>
      <form onSubmit={handleUpload} className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Subject
          </label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="e.g., Mathematics"
            className="w-full px-3 py-2 border text-black border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Topic
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Calculus"
            className="w-full px-3 py-2 border text-black border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            PDF File
          </label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full px-3 py-2 border text-black border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <button
          type="submit"
          disabled={uploading}
          className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors"
        >
          {uploading ? 'Uploading...' : 'Upload Notes'}
        </button>
      </form>
    </div>
  );
}