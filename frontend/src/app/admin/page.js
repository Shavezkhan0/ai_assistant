'use client';
import { useState } from 'react';
import { Upload, FileText, GraduationCap, BookOpen, ArrowLeft, CheckCircle, XCircle, Loader } from 'lucide-react';
import { chatAPI } from '@/lib/api';
import Link from 'next/link';

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState('upload');
  const [status, setStatus] = useState({ type: null, message: '' });

  // Upload Notes State
  const [file, setFile] = useState(null);
  const [subject, setSubject] = useState('');
  const [topic, setTopic] = useState('');
  const [uploading, setUploading] = useState(false);

  // Add Results State
  const [resultFile, setResultFile] = useState(null);
  const [resultSemester, setResultSemester] = useState('');
  const [studentId, setStudentId] = useState('');
  const [semester, setSemester] = useState('');
  const [course, setCourse] = useState('');
  const [grade, setGrade] = useState('');
  const [credits, setCredits] = useState('');

  // Add Syllabus State
  const [courseCode, setCourseCode] = useState('');
  const [courseName, setCourseName] = useState('');
  const [department, setDepartment] = useState('');
  const [syllabusSemester, setSyllabusSemester] = useState('');
  const [syllabusCredits, setSyllabusCredits] = useState('');
  const [description, setDescription] = useState('');
  const [topics, setTopics] = useState('');
  
  // Upload Syllabus PDF State
  const [syllabusFile, setSyllabusFile] = useState(null);
  const [syllabusDepartment, setSyllabusDepartment] = useState('CSE');
  const [syllabusSemesterUpload, setSyllabusSemesterUpload] = useState('6');

  const showStatus = (type, message) => {
    setStatus({ type, message });
    // Show success messages longer (8 seconds) and error messages shorter (5 seconds)
    const timeout = type === 'success' ? 8000 : 5000;
    setTimeout(() => setStatus({ type: null, message: '' }), timeout);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        showStatus('error', 'Please select a PDF file');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
    } else {
      showStatus('error', 'Please drop a PDF file');
    }
  };

  const handleUploadNotes = async (e) => {
    e.preventDefault();
    
    if (!file || !subject || !topic) {
      showStatus('error', 'Please fill all fields and select a file');
      return;
    }

    setUploading(true);
    try {
      const result = await chatAPI.uploadNotes(file, { subject, topic });
      const filename = file.name;
      const chunksCount = result.chunks_created || result.chunk_count || 0;
      showStatus('success', `✅ Notes uploaded successfully! File: ${filename} (${chunksCount} chunks created)`);
      setFile(null);
      setSubject('');
      setTopic('');
      // Reset file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
    } catch (error) {
      showStatus('error', `❌ Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleResultFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        showStatus('error', 'Please select a PDF file');
        return;
      }
      setResultFile(selectedFile);
    }
  };

  const handleResultDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleResultDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setResultFile(droppedFile);
    } else {
      showStatus('error', 'Please drop a PDF file');
    }
  };

  const handleUploadResults = async (e) => {
    e.preventDefault();
    
    if (!resultFile) {
      showStatus('error', 'Please select a PDF file');
      return;
    }

    setUploading(true);
    try {
      const result = await chatAPI.uploadResults(resultFile, resultSemester || null);
      const studentsCount = result.students_processed || result.count || 0;
      const semInfo = resultSemester ? ` (Semester ${resultSemester})` : '';
      showStatus('success', `✅ Results uploaded successfully! Processed ${studentsCount} student(s)${semInfo}`);
      setResultFile(null);
      setResultSemester('');
      // Reset file input
      const fileInput = document.getElementById('result-file-input');
      if (fileInput) fileInput.value = '';
    } catch (error) {
      showStatus('error', `❌ Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleAddResult = async (e) => {
    e.preventDefault();
    
    if (!studentId || !semester || !course || !grade || !credits) {
      showStatus('error', 'Please fill all fields');
      return;
    }

    try {
      const result = await chatAPI.addResult({
        studentId,
        semester,
        course,
        grade,
        credits: parseInt(credits),
      });
      showStatus('success', `✅ Result added successfully! Student: ${studentId}, Course: ${course}, Grade: ${grade}`);
      setStudentId('');
      setSemester('');
      setCourse('');
      setGrade('');
      setCredits('');
    } catch (error) {
      showStatus('error', `❌ Failed to add result: ${error.message}`);
    }
  };

  const handleAddSyllabus = async (e) => {
    e.preventDefault();
    
    if (!courseCode || !courseName || !department || !syllabusSemester || !syllabusCredits) {
      showStatus('error', 'Please fill all required fields');
      return;
    }

    try {
      const result = await chatAPI.addSyllabus({
        courseCode,
        courseName,
        department,
        semester: syllabusSemester,
        credits: parseInt(syllabusCredits),
        description,
        topics: topics.split('\n').filter(t => t.trim()),
      });
      const topicsCount = topics.split('\n').filter(t => t.trim()).length;
      showStatus('success', `✅ Syllabus added successfully! Course: ${courseCode} - ${courseName} (${topicsCount} topics)`);
      setCourseCode('');
      setCourseName('');
      setDepartment('');
      setSyllabusSemester('');
      setSyllabusCredits('');
      setDescription('');
      setTopics('');
    } catch (error) {
      showStatus('error', `❌ Failed to add syllabus: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-2 sm:px-3 lg:px-4 py-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-1 rounded-none">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Admin Panel
                </h1>
                <p className="text-xs text-gray-600">Manage notes, results, and syllabus</p>
              </div>
            </div>
            <Link
              href="/"
              className="flex items-center space-x-1 px-3 py-0.5 bg-white border border-gray-300 rounded-none hover:bg-gray-50 transition-colors text-gray-700"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Chat</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Status Message */}
      {status.type && (
        <div className="max-w-7xl mx-auto px-2 sm:px-3 lg:px-4 pt-2">
          <div
            className={`flex items-center space-x-2 px-3 py-2 rounded-none shadow-md ${
              status.type === 'success'
                ? 'bg-green-50 text-green-800 border-2 border-green-400'
                : 'bg-red-50 text-red-800 border-2 border-red-400'
            }`}
          >
            {status.type === 'success' ? (
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
            )}
            <span className="font-semibold text-sm">{status.message}</span>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-2 sm:px-3 lg:px-4 py-3">
        <div className="bg-white rounded-none shadow-lg overflow-hidden">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-0.5 p-0.5">
              {[
                { id: 'upload', label: 'Upload Notes', icon: Upload },
                { id: 'results', label: 'Add Results', icon: FileText },
                { id: 'syllabus', label: 'Add Syllabus', icon: BookOpen },
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 flex items-center justify-center space-x-1 px-1 py-2 rounded-none transition-all ${
                      activeTab === tab.id
                        ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-2">
            {/* Upload Notes Tab */}
            {activeTab === 'upload' && (
              <form onSubmit={handleUploadNotes} className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Subject *
                  </label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="e.g., Mathematics"
                    required
                    className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Topic *
                  </label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., Calculus"
                    required
                    className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    PDF File *
                  </label>
                  <div
                    onDragOver={handleDragOver}
                    onDrop={handleDrop}
                    className={`border-2 border-dashed rounded-none p-4 text-center transition-colors ${
                      file
                        ? 'border-green-400 bg-green-50'
                        : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                    }`}
                  >
                    <input
                      id="file-input"
                      type="file"
                      accept=".pdf"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                    {file ? (
                      <div className="space-y-2">
                        <FileText className="w-12 h-12 text-green-600 mx-auto" />
                        <p className="text-gray-700 font-medium">{file.name}</p>
                        <p className="text-sm text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                        <button
                          type="button"
                          onClick={() => {
                            setFile(null);
                            document.getElementById('file-input').value = '';
                          }}
                          className="text-sm text-red-600 hover:text-red-700"
                        >
                          Remove file
                        </button>
                      </div>
                    ) : (
                      <label htmlFor="file-input" className="cursor-pointer">
                        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-1" />
                        <p className="text-gray-700 font-medium">
                          Click to upload or drag and drop
                        </p>
                        <p className="text-sm text-gray-500 mt-0.5">PDF files only</p>
                      </label>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={uploading || !file || !subject || !topic}
                  className="w-full px-3 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-none hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center justify-center space-x-1"
                >
                  {uploading ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin" />
                      <span>Uploading...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      <span>Upload Notes</span>
                    </>
                  )}
                </button>
              </form>
            )}

            {/* Add Results Tab */}
            {activeTab === 'results' && (
              <div className="space-y-3">
                {/* PDF Upload Section */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Upload Results PDF (Semester-wise)</h3>
                  <form onSubmit={handleUploadResults} className="space-y-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Semester (Optional)
                      </label>
                      <input
                        type="text"
                        value={resultSemester}
                        onChange={(e) => setResultSemester(e.target.value)}
                        placeholder="e.g., 1, 2, 3... (Leave empty for auto-detect)"
                        className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                      />
                      <p className="text-xs text-gray-500 mt-0.5">
                        Specify semester number if not detected automatically from PDF
                      </p>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Results PDF File *
                      </label>
                      <div
                        onDragOver={handleResultDragOver}
                        onDrop={handleResultDrop}
                        className={`border-2 border-dashed rounded-none p-4 text-center transition-colors ${
                          resultFile
                            ? 'border-green-400 bg-green-50'
                            : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                        }`}
                      >
                        <input
                          id="result-file-input"
                          type="file"
                          accept=".pdf"
                          onChange={handleResultFileChange}
                          className="hidden"
                        />
                        {resultFile ? (
                          <div className="space-y-1">
                            <FileText className="w-12 h-12 text-green-600 mx-auto" />
                            <p className="text-gray-700 font-medium">{resultFile.name}</p>
                            <p className="text-sm text-gray-500">
                              {(resultFile.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                            <button
                              type="button"
                              onClick={() => {
                                setResultFile(null);
                                document.getElementById('result-file-input').value = '';
                              }}
                              className="text-sm text-red-600 hover:text-red-700"
                            >
                              Remove file
                            </button>
                          </div>
                        ) : (
                          <label htmlFor="result-file-input" className="cursor-pointer">
                            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-1" />
                            <p className="text-gray-700 font-medium">
                              Click to upload or drag and drop results PDF
                            </p>
                            <p className="text-sm text-gray-500 mt-0.5">PDF files only</p>
                          </label>
                        )}
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={uploading || !resultFile}
                      className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-none hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center justify-center space-x-2"
                    >
                      {uploading ? (
                        <>
                          <Loader className="w-5 h-5 animate-spin" />
                          <span>Processing PDF...</span>
                        </>
                      ) : (
                        <>
                          <Upload className="w-5 h-5" />
                          <span>Upload Results PDF</span>
                        </>
                      )}
                    </button>
                  </form>
                </div>

                {/* Divider */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">OR</span>
                  </div>
                </div>

                {/* Manual Entry Section */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Add Result Manually</h3>
                  <form onSubmit={handleAddResult} className="space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Student ID *
                    </label>
                    <input
                      type="text"
                      value={studentId}
                      onChange={(e) => setStudentId(e.target.value)}
                      placeholder="e.g., STU001"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Semester *
                    </label>
                    <input
                      type="text"
                      value={semester}
                      onChange={(e) => setSemester(e.target.value)}
                      placeholder="e.g., Fall 2024"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Course Name *
                    </label>
                    <input
                      type="text"
                      value={course}
                      onChange={(e) => setCourse(e.target.value)}
                      placeholder="e.g., Mathematics"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Grade *
                    </label>
                    <select
                      value={grade}
                      onChange={(e) => setGrade(e.target.value)}
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    >
                      <option value="">Select grade</option>
                      <option value="A+">A+</option>
                      <option value="A">A</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>
                      <option value="B">B</option>
                      <option value="B-">B-</option>
                      <option value="C+">C+</option>
                      <option value="C">C</option>
                      <option value="C-">C-</option>
                      <option value="D">D</option>
                      <option value="F">F</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Credits *
                    </label>
                    <input
                      type="number"
                      value={credits}
                      onChange={(e) => setCredits(e.target.value)}
                      placeholder="e.g., 3"
                      min="1"
                      max="6"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full px-3 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-none hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg flex items-center justify-center space-x-1"
                >
                  <FileText className="w-5 h-5" />
                  <span>Add Result</span>
                </button>
                  </form>
                </div>
              </div>
            )}

            {/* Add Syllabus Tab */}
            {activeTab === 'syllabus' && (
              <div className="space-y-3">
                {/* PDF Upload Section */}
                <div className="border-2 border-dashed border-gray-300 rounded-none p-3 bg-gray-50">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Upload Syllabus PDF</h3>
                  <p className="text-sm text-gray-600 mb-2">
                    Upload a PDF syllabus file. The system will automatically extract course codes, names, and content.
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Department *
                      </label>
                      <select
                        value={syllabusDepartment}
                        onChange={(e) => setSyllabusDepartment(e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                      >
                        <option value="CSE">Computer Science & Engineering</option>
                        <option value="IT">Information Technology</option>
                        <option value="CST">Computer Science Technology</option>
                        <option value="ITE">Information Technology Engineering</option>
                        <option value="ECE">Electronics & Communication</option>
                        <option value="EE">Electrical Engineering</option>
                        <option value="ME">Mechanical Engineering</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Semester *
                      </label>
                      <select
                        value={syllabusSemesterUpload}
                        onChange={(e) => setSyllabusSemesterUpload(e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                      >
                        {[1, 2, 3, 4, 5, 6, 7, 8].map((sem) => (
                          <option key={sem} value={sem.toString()}>
                            Semester {sem}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                    onDrop={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      const droppedFile = e.dataTransfer.files[0];
                      if (droppedFile && droppedFile.type === 'application/pdf') {
                        setSyllabusFile(droppedFile);
                      } else {
                        showStatus('error', 'Please drop a PDF file');
                      }
                    }}
                    className={`border-2 border-dashed rounded-none p-4 text-center transition-colors ${
                      syllabusFile
                        ? 'border-green-400 bg-green-50'
                        : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                    }`}
                  >
                    <input
                      id="syllabus-file-input"
                      type="file"
                      accept=".pdf"
                      onChange={(e) => {
                        const selectedFile = e.target.files[0];
                        if (selectedFile) {
                          if (selectedFile.type !== 'application/pdf') {
                            showStatus('error', 'Please select a PDF file');
                            return;
                          }
                          setSyllabusFile(selectedFile);
                        }
                      }}
                      className="hidden"
                    />
                    {syllabusFile ? (
                      <div className="space-y-2">
                        <FileText className="w-12 h-12 text-green-600 mx-auto" />
                        <p className="text-gray-700 font-medium">{syllabusFile.name}</p>
                        <p className="text-sm text-gray-500">
                          {(syllabusFile.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                        <button
                          type="button"
                          onClick={() => {
                            setSyllabusFile(null);
                            document.getElementById('syllabus-file-input').value = '';
                          }}
                          className="text-sm text-red-600 hover:text-red-800"
                        >
                          Remove
                        </button>
                      </div>
                    ) : (
                      <div>
                        <label htmlFor="syllabus-file-input" className="cursor-pointer">
                          <div className="space-y-1">
                            <Upload className="w-12 h-12 text-gray-400 mx-auto" />
                            <p className="text-gray-600 font-medium">
                              Click to upload or drag and drop
                            </p>
                            <p className="text-sm text-gray-500">PDF files only</p>
                          </div>
                        </label>
                      </div>
                    )}
                  </div>
                  
                  <button
                    type="button"
                    onClick={async () => {
                      if (!syllabusFile) {
                        showStatus('error', 'Please select a PDF file');
                        return;
                      }
                      
                      setUploading(true);
                      try {
                        const result = await chatAPI.uploadSyllabus(
                          syllabusFile,
                          syllabusDepartment,
                          syllabusSemesterUpload
                        );
                        const coursesCount = result.courses_stored || result.count || 0;
                        const coursesList = result.courses || [];
                        const coursesText = coursesList.length > 0 
                          ? `\nCourses: ${coursesList.map(c => c.course_name || c.course_code).join(', ')}`
                          : '';
                        showStatus('success', `✅ Syllabus uploaded successfully! Processed ${coursesCount} course(s)${coursesText}`);
                        setSyllabusFile(null);
                        document.getElementById('syllabus-file-input').value = '';
                      } catch (error) {
                        showStatus('error', `❌ Upload failed: ${error.message}`);
                      } finally {
                        setUploading(false);
                      }
                    }}
                    disabled={!syllabusFile || uploading}
                    className="w-full mt-2 px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-none hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center justify-center space-x-1"
                  >
                    {uploading ? (
                      <>
                        <Loader className="w-5 h-5 animate-spin" />
                        <span>Uploading...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        <span>Upload Syllabus PDF</span>
                      </>
                    )}
                  </button>
                </div>
                
                {/* Divider */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">OR</span>
                  </div>
                </div>
                
                {/* Manual Entry Section */}
                <form onSubmit={handleAddSyllabus} className="space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Course Code *
                    </label>
                    <input
                      type="text"
                      value={courseCode}
                      onChange={(e) => setCourseCode(e.target.value)}
                      placeholder="e.g., CSE101"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Course Name *
                    </label>
                    <input
                      type="text"
                      value={courseName}
                      onChange={(e) => setCourseName(e.target.value)}
                      placeholder="e.g., Introduction to Computer Science"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Department *
                    </label>
                    <input
                      type="text"
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      placeholder="e.g., Computer Science"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Semester *
                    </label>
                    <input
                      type="text"
                      value={syllabusSemester}
                      onChange={(e) => setSyllabusSemester(e.target.value)}
                      placeholder="e.g., Fall 2024"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Credits *
                    </label>
                    <input
                      type="number"
                      value={syllabusCredits}
                      onChange={(e) => setSyllabusCredits(e.target.value)}
                      placeholder="e.g., 3"
                      min="1"
                      max="6"
                      required
                      className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Course description..."
                    rows="3"
                    className="w-full px-2 py-2 border border-gray-300 rounded-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Topics (one per line)
                  </label>
                  <textarea
                    value={topics}
                    onChange={(e) => setTopics(e.target.value)}
                    placeholder="Topic 1&#10;Topic 2&#10;Topic 3"
                    rows="6"
                    className="w-full px-4 py-3 border border-gray-300 rounded-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800 font-mono text-sm"
                  />
                </div>

                <button
                  type="submit"
                  className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-none hover:from-purple-700 hover:to-pink-700 transition-all shadow-md hover:shadow-lg flex items-center justify-center space-x-2"
                >
                  <BookOpen className="w-5 h-5" />
                  <span>Add Syllabus Manually</span>
                </button>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
