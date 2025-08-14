import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  sources?: any[];
  timestamp: string;
}

interface ChatMessage {
  role: string;
  content: string;
  timestamp: string;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const convertToConversationHistory = (messages: Message[]): ChatMessage[] => {
    return messages.map(msg => ({
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.text,
      timestamp: msg.timestamp
    }));
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newUserMessage = { sender: 'user' as const, text: input, timestamp: new Date().toISOString() };
    const updatedMessages = [...messages, newUserMessage];
    setMessages(updatedMessages);
    setInput(''); // Clear input immediately
    setLoading(true);
    
    try {
      // Convert messages to conversation history format
      const conversationHistory = convertToConversationHistory(updatedMessages);
      
      const res = await axios.post('http://localhost:8000/api/v1/chat/query', { 
        query: input,
        conversation_history: conversationHistory
      });
      
      setMessages(msgs => [
        ...msgs,
        { sender: 'assistant' as const, text: res.data.response, sources: res.data.sources, timestamp: new Date().toISOString() }
      ]);
    } catch (err: any) {
      setMessages(msgs => [
        ...msgs,
        { sender: 'assistant' as const, text: 'Sorry, there was an error processing your request.', timestamp: new Date().toISOString() }
      ]);
    }
    setLoading(false);
  };

  // Auto scroll to bottom when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="bg-white rounded-lg shadow flex flex-col h-full relative">
      <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 pb-20 flex flex-col gap-2">
        {messages.map((msg, i) => (
          <div key={i} className={`text-sm ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block px-3 py-2 rounded-lg ${msg.sender === 'user' ? 'bg-blue-100 text-blue-900' : 'bg-gray-200 text-gray-800'}`}>{msg.text}</div>
            {msg.sender === 'assistant' && msg.sources && msg.sources.length > 0 && (
              <div className="mt-1 text-xs text-gray-500">
                <div>Sources:</div>
                <ul className="list-disc ml-4">
                  {msg.sources.map((src, idx) => (
                    <li key={idx}>
                      {src.document_title || src.filename}
                      {src.section_header && `, Section: ${src.section_header}`}
                      {src.author && `, Author: ${src.author}`}
                      {src.date && `, Date: ${src.date}`}
                      {src.relevance_score && `, Score: ${src.relevance_score.toFixed(2)}`}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="absolute bottom-0 left-0 right-0 bg-white border-t p-4 flex gap-2">
        <input
          className="flex-1 border rounded p-2"
          placeholder="Ask a question..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          disabled={loading}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-60"
          onClick={sendMessage}
          disabled={loading || !input.trim()}
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
