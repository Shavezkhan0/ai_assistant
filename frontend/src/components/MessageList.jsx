'use client';

export default function MessageList({ messages }) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <h3 className="text-xl font-semibold mb-2">Welcome to College AI Assistant! 👋</h3>
            <p>Ask me about notes, results, or syllabus</p>
          </div>
        </div>
      ) : (
        messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800'
              }`}
            >
              <div className="flex items-start space-x-2">
                <span className="text-lg">
                  {msg.role === 'user' ? '👤' : '🤖'}
                </span>
                <div className="flex-1">
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.metadata && (
                    <div className="mt-2 text-xs opacity-75">
                      <p>Agent: {msg.metadata.agent}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}