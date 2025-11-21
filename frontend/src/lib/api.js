// API service for backend communication
// Remove trailing slash if present to avoid double slashes in URLs
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

export const chatAPI = {
  // Send a chat message
  sendMessage: async (message) => {
    try {
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message }),
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
          throw new Error('Failed to send message');
        }
        
        return await response.json();
      } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
          throw new Error('Request timed out. Please try again.');
        }
        throw error;
      }
    } catch (error) {
      console.error('Chat API Error:', error);
      throw error;
    }
  },

  // Search notes
  searchNotes: async (query) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/notes/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to search notes');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Notes Search Error:', error);
      throw error;
    }
  },

  // Upload notes (PDF)
  uploadNotes: async (file, metadata) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('subject', metadata.subject);
      formData.append('topic', metadata.topic);
      
      const response = await fetch(`${API_BASE_URL}/api/notes/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || 'Failed to upload notes');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Upload Error:', error);
      throw error;
    }
  },

  // Upload results PDF
  uploadResults: async (file, semester = null) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (semester) {
        formData.append('semester', semester);
      }
      
      const response = await fetch(`${API_BASE_URL}/api/results/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || 'Failed to upload results');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Upload Results Error:', error);
      throw error;
    }
  },

  // Add student result
  addResult: async (resultData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(resultData),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || 'Failed to add result');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Add Result Error:', error);
      throw error;
    }
  },

  // Upload syllabus PDF
  uploadSyllabus: async (file, department, semester) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('department', department);
      formData.append('semester', semester);
      
      const response = await fetch(`${API_BASE_URL}/api/syllabus/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || 'Failed to upload syllabus');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Upload Syllabus Error:', error);
      throw error;
    }
  },

  // Add course syllabus (manual entry)
  addSyllabus: async (syllabusData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/syllabus`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(syllabusData),
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to add syllabus');
      }
      
      return await response.json();
    } catch (error) {
      console.error('Add Syllabus Error:', error);
      throw error;
    }
  },
};
