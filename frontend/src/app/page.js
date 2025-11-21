'use client';
import { useState } from 'react';
import { Send, MessageSquare, Download, FileText } from 'lucide-react';
import { chatAPI } from '@/lib/api';
import Link from 'next/link';
import { IoSparklesOutline } from "react-icons/io5";
import { BsSend } from "react-icons/bs";

export default function Home() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const exampleQueries = [
    "Find notes on Calculus",
    "What's my Math result?",
    "Show syllabus for CSE",
    "Explain machine learning concepts"
  ];

  const handleSendMessage = async (messageText) => {
    const message = messageText || input.trim();
    if (!message || loading) return;

    // Add user message
    const userMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await chatAPI.sendMessage(message);
      
      // Add assistant message
      const assistantMessage = {
        role: 'assistant',
        content: response.response || response.answer || 'I received your message.',
        sources: response.sources || [],
        pdfFiles: response.pdf_files || [],
        hasPdfs: response.has_pdfs || false,
        agent: response.agent || response.agent_used || 'notes_agent',
        resultData: response.result_data || null,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: error.message && error.message.includes('timeout') 
          ? '⏱️ Request timed out. The server is taking too long to respond. Please try again or check your connection.'
          : '❌ Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSendMessage();
  };

  const handleDownload = async (fileId, filename) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const url = `${apiUrl}/api/notes/download/${fileId}`;
      
      // Create a temporary link and trigger download
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download PDF');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-linear-to-br  from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-linear-to-r from-blue-600 to-indigo-600 p-1 rounded-lg">
                <IoSparklesOutline className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  College AI Assistant
                </h1>
                <p className="text-xs text-gray-600">Your intelligent study companion</p>
              </div>
            </div>
            <Link
              href="/admin"
              className="px-4 py-1 bg-linear-to-r from-indigo-600 to-purple-600 text-white rounded-xs hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md hover:shadow-lg"
            >
              Admin Panel
            </Link>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center space-y-4">
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-full w-20 h-20 mx-auto flex items-center justify-center">
                  <MessageSquare className="w-10 h-10 text-white" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">
                    Welcome to College AI Assistant! 👋
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Ask me about notes, results, or syllabus
                  </p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl">
                  {exampleQueries.map((query, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(query)}
                      className="px-4 py-3 bg-white rounded-xs border border-gray-200 hover:border-blue-300 hover:bg-blue-50 text-left text-sm text-gray-700 transition-all shadow-sm hover:shadow-md"
                    >
                      💡 {query}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-4`}
              >
                <div
                  className={`max-w-[90%] sm:max-w-[80%] rounded-xs px-3 py-2 shadow-xs ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                      : 'bg-white text-gray-800 border border-gray-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-1 min-w-0">
                      {/* Results Table Display */}
                      {msg.agent === 'results_agent' && msg.resultData && msg.resultData.found && !msg.resultData.multiple && msg.resultData.results && msg.resultData.results.length > 0 && (() => {
                        // Group results by semester
                        const resultsBySemester = {};
                        msg.resultData.results.forEach(result => {
                          const sem = result.semester || 'Unknown';
                          if (!resultsBySemester[sem]) {
                            resultsBySemester[sem] = [];
                          }
                          // Deduplicate subjects within each semester
                          const exists = resultsBySemester[sem].some(r => 
                            r.subject.toUpperCase() === result.subject.toUpperCase()
                          );
                          if (!exists) {
                            resultsBySemester[sem].push(result);
                          }
                        });
                        
                        // Calculate summary per semester
                        const calculateSemesterSummary = (semResults) => {
                          let totalMarks = 0;
                          let maxMarks = 0;
                          const gradePoints = {'O': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 'C': 5, 'D': 4, 'F': 0, 'P': 5};
                          let totalGradePoints = 0;
                          let totalCredits = 0;
                          let obtainedCredits = 0;
                          let totalCreditMarks = 0;
                          let maxCreditMarks = 0;
                          
                          semResults.forEach(result => {
                            const marks = result.marks || 0;
                            totalMarks += marks;
                            maxMarks += 100;
                            
                            // Extract credits from subject name pattern: "SUBJECT (Credits: X)" or "SUBJECT (X)"
                            const creditsMatch = result.subject.match(/\(Credits?[:\s]*(\d+)\)|\((\d+)\)/);
                            const credits = creditsMatch ? parseInt(creditsMatch[1] || creditsMatch[2]) : (result.subject.toUpperCase().includes('LAB') ? 1 : 4);
                            
                            totalCredits += credits;
                            totalCreditMarks += marks * credits;
                            maxCreditMarks += 100 * credits;
                            
                            const grade = (result.grade || 'F').toUpperCase();
                            if (grade in gradePoints) {
                              totalGradePoints += gradePoints[grade] * credits;
                              if (grade !== 'F') {
                                obtainedCredits += credits;
                              }
                            }
                          });
                          
                          const percentage = maxMarks > 0 ? (totalMarks / maxMarks * 100) : 0;
                          const sgpa = totalCredits > 0 ? (totalGradePoints / totalCredits) : 0;
                          const creditPercentage = maxCreditMarks > 0 ? (totalCreditMarks / maxCreditMarks * 100) : 0;
                          const equivalentPercentage = sgpa * 10;
                          
                          return {
                            marks: totalMarks,
                            maxMarks: maxMarks,
                            percentage: percentage.toFixed(3),
                            creditMarks: Math.round(totalCreditMarks),
                            maxCreditMarks: maxCreditMarks,
                            creditPercentage: creditPercentage.toFixed(3),
                            sgpa: sgpa.toFixed(3),
                            credits: `${obtainedCredits} / ${totalCredits}`,
                            equivalentPercentage: equivalentPercentage.toFixed(1)
                          };
                        };
                        
                        // Extract paper ID from subject name (format: "027302 SUBJECT" or "SUBJECT_027302")
                        const extractPaperId = (subject) => {
                          const match = subject.match(/\b(\d{5,6})\b/);
                          return match ? match[1] : 'N/A';
                        };
                        
                        // Extract credits from subject name
                        const extractCredits = (subject) => {
                          const match = subject.match(/\(Credits?[:\s]*(\d+)\)|\((\d+)\)/);
                          return match ? parseInt(match[1] || match[2]) : (subject.toUpperCase().includes('LAB') ? 1 : 4);
                        };
                        
                        // Clean subject name (remove paper ID and credits pattern)
                        const cleanSubjectName = (subject) => {
                          return subject
                            .replace(/\b\d{5,6}\b/g, '') // Remove paper IDs
                            .replace(/\(Credits?[:\s]*\d+\)/g, '') // Remove (Credits: X)
                            .replace(/\(\d+\)/g, '') // Remove standalone (X)
                            .trim()
                            .replace(/\s+/g, ' '); // Normalize spaces
                        };
                        
                        return (
                          <div className="mb-4 space-y-4">
                            {/* Student Details Section - Clean white card */}
                            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Student Details</h2>
                              <div className="space-y-0">
                                <div className="flex items-start py-3 border-b border-gray-100 last:border-b-0">
                                  <span className="font-semibold text-gray-700 w-48 flex-shrink-0">Enrollment Number:</span>
                                  <span className="text-gray-800">{msg.resultData.student?.enrollment_no || 'N/A'}</span>
                                </div>
                                <div className="flex items-start py-3 border-b border-gray-100 last:border-b-0">
                                  <span className="font-semibold text-gray-700 w-48 flex-shrink-0">Student Name:</span>
                                  <span className="text-gray-800">{msg.resultData.student?.name || 'N/A'}</span>
                                </div>
                                <div className="flex items-start py-3 border-b border-gray-100 last:border-b-0">
                                  <span className="font-semibold text-gray-700 w-48 flex-shrink-0">Programme:</span>
                                  <span className="text-gray-800">{msg.resultData.student?.programme || 'Bachelor of Technology (B. Tech.)'}</span>
                                </div>
                                <div className="flex items-start py-3 border-b border-gray-100 last:border-b-0">
                                  <span className="font-semibold text-gray-700 w-48 flex-shrink-0">Branch:</span>
                                  <span className="text-gray-800">{msg.resultData.student?.branch || 'Computer Science and Engineering'}</span>
                                </div>
                                <div className="flex items-start py-3 border-b border-gray-100 last:border-b-0">
                                  <span className="font-semibold text-gray-700 w-48 flex-shrink-0">Institute:</span>
                                  <span className="text-gray-800">{msg.resultData.student?.institute || 'N/A'}</span>
                                </div>
                              </div>
                            </div>
                            
                            {/* Results by Semester */}
                            {Object.keys(resultsBySemester).sort().map(semester => {
                              const semResults = resultsBySemester[semester];
                              const semSummary = calculateSemesterSummary(semResults);
                              
                              return (
                                <div key={semester} className="space-y-4">
                                  {/* Sem Result Summary - Two Column Layout */}
                                  <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                                    <h2 className="text-2xl font-semibold text-gray-900 mb-6">Sem {semester} Result</h2>
                                    <div className="grid grid-cols-2 gap-8">
                                      {/* Left Column */}
                                      <div className="space-y-4">
                                        <div className="flex justify-between items-center py-2">
                                          <span className="text-gray-600 font-medium">Marks:</span>
                                          <span className="text-gray-900 font-semibold">{semSummary.marks} / {semSummary.maxMarks}</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2">
                                          <span className="text-gray-600 font-medium">Credit Marks:</span>
                                          <span className="text-gray-900 font-semibold">{semSummary.creditMarks} / {semSummary.maxCreditMarks}</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2">
                                          <span className="text-gray-600 font-medium">SGPA:</span>
                                          <span className="text-gray-900 font-semibold">{semSummary.sgpa}</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2">
                                          <span className="text-gray-600 font-medium">Credits Obtained:</span>
                                          <span className="text-gray-900 font-semibold">{semSummary.credits}</span>
                                        </div>
                                      </div>
                                      
                                      {/* Right Column */}
                                      <div className="space-y-4">
                                        <div className="flex justify-between items-center py-2">
                                          <span className="text-gray-600 font-medium">Percentage:</span>
                                          <span className="text-gray-900 font-semibold">{semSummary.percentage} %</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2">
                                          <span className="text-gray-600 font-medium">Credit Percentage:</span>
                                          <span className="text-gray-900 font-semibold">{semSummary.creditPercentage} %</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2">
                                          <span className="text-gray-600 font-medium">Equivalent Percentage:</span>
                                          <span className="text-gray-900 font-semibold">{semSummary.equivalentPercentage} %</span>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                  
                                  {/* Result Breakdown Table */}
                                  <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">Result Breakdown</h2>
                                    <div className="overflow-x-auto">
                                      <table className="w-full text-sm">
                                        <thead>
                                          <tr className="bg-blue-900 text-white">
                                            <th className="px-4 py-3 text-left font-semibold">Paper ID</th>
                                            <th className="px-4 py-3 text-left font-semibold">Subject (Credits)</th>
                                            <th className="px-4 py-3 text-center font-semibold">Int.</th>
                                            <th className="px-4 py-3 text-center font-semibold">Ext.</th>
                                            <th className="px-4 py-3 text-center font-semibold">Marks</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          {semResults.map((result, idx) => {
                                            // Use database fields directly, fallback to extraction if not available
                                            const paperId = result.paper_id || extractPaperId(result.subject) || 'N/A';
                                            const credits = result.credits || extractCredits(result.subject) || 0;
                                            const subjectName = cleanSubjectName(result.subject);
                                            // Use database fields for internal/external marks
                                            const internalMarks = result.internal_marks !== undefined && result.internal_marks !== null ? result.internal_marks : 0;
                                            const externalMarks = result.external_marks !== undefined && result.external_marks !== null ? result.external_marks : 0;
                                            
                                            return (
                                              <tr key={idx} className={idx % 2 === 0 ? 'bg-white hover:bg-gray-50' : 'bg-gray-50 hover:bg-gray-100'}>
                                                <td className="px-4 py-3 text-gray-900">{paperId}</td>
                                                <td className="px-4 py-3 text-gray-900 font-medium">{subjectName} ({credits})</td>
                                                <td className="px-4 py-3 text-center text-gray-700">{internalMarks}</td>
                                                <td className="px-4 py-3 text-center text-gray-700">{externalMarks}</td>
                                                <td className="px-4 py-3 text-center text-gray-900 font-semibold">{result.marks} ({result.grade})</td>
                                              </tr>
                                            );
                                          })}
                                        </tbody>
                                      </table>
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        );
                      })()}
                      
                      {/* Text Response - Hide if results are displayed in cards */}
                      {!(msg.agent === 'results_agent' && msg.resultData && msg.resultData.found && !msg.resultData.multiple && msg.resultData.results && msg.resultData.results.length > 0) && (
                        <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                      )}
                      
                      {/* PDF Download Section */}
                      {msg.hasPdfs && msg.pdfFiles && msg.pdfFiles.length > 0 && (
                        <div className="mt-4 pt-3 border-t border-gray-200">
                          <p className="text-xs font-semibold text-gray-600 mb-2">📎 Related PDF Notes:</p>
                          <div className="space-y-2">
                            {msg.pdfFiles.map((pdf, pdfIndex) => (
                              <div
                                key={pdfIndex}
                                className="flex items-center justify-between bg-gray-50 p-2 rounded-none border border-gray-200"
                              >
                                <div className="flex items-center gap-2 flex-1 min-w-0">
                                  <FileText className="w-4 h-4 text-blue-600 flex-shrink-0" />
                                  <div className="flex-1 min-w-0">
                                    <p className="text-xs font-medium text-gray-700 truncate">
                                      {pdf.filename}
                                    </p>
                                    <p className="text-xs text-gray-500">
                                      {pdf.subject} - {pdf.topic}
                                    </p>
                                  </div>
                                </div>
                                <button
                                  onClick={() => handleDownload(pdf.file_id, pdf.filename)}
                                  className="flex items-center gap-1 px-3 py-1 bg-blue-600 text-white text-xs rounded-none hover:bg-blue-700 transition-colors flex-shrink-0"
                                >
                                  <Download className="w-3 h-3" />
                                  Download
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-300/30">
                          <p className="text-xs opacity-75">
                            Sources: {msg.sources.length} found
                          </p>
                        </div>
                      )}
                      {msg.agent && (
                        <p className="text-xs opacity-75 mt-1">
                          Agent: {msg.agent}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-xs px-3 py-2 shadow-lg border border-gray-200">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  <span className="ml-2 text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white/80 backdrop-blur-sm border-t border-gray-200 shadow-lg">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
          <form onSubmit={handleSubmit} className="flex space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about notes, results, or syllabus..."
              disabled={loading}
              className="flex-1 px-5 py-1 border text-sm border-gray-200 rounded-xs focus:outline-none  focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-800 placeholder-gray-400"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xs hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg flex items-center space-x-2"
            >
              <BsSend className="w-4 h-4" />
              <span>Send</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
