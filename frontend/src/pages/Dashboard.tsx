import React, { useState } from 'react';
import { Plus, Search, Settings, Send, Code2, Eye, Zap, FileText, ChevronDown, Copy, Check } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  citations?: Array<{ file: string; lines: string }>;
}

interface SourceChunk {
  file: string;
  lines: string;
  language: string;
  code: string;
  relevance: number;
}

export const Dashboard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedRepo, setSelectedRepo] = useState('real_rag'); // 🔥 USE REAL_RAG!
  const [showDebug, setShowDebug] = useState(false);
  const [selectedSource, setSelectedSource] = useState<SourceChunk | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // 🔥 REAL REPOSITORIES FROM BACKEND
  const repositories = [
    { id: 'real_rag', name: 'real_rag', language: 'Python/TypeScript/JavaScript', indexed: true, chunks: 206 },
  ];

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: input,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // 🔥 REAL API CALL TO BACKEND
      console.log(`🔥 Sending query to backend for repository: ${selectedRepo}`);
      
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          repository_id: selectedRepo,
          query: input,
          conversation_id: `conv-${Date.now()}`,
          previous_messages: messages,
          debug: showDebug,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();
      
      console.log('✅ Response received:', data);

      const assistantMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: data.response,
        sources: data.citations?.map((c: any) => c.file) || [],
        citations: data.citations || [],
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('❌ Error:', error);
      
      const errorMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: `❌ Error: ${error instanceof Error ? error.message : 'Failed to get response from backend'}`,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="flex h-screen bg-[#050505]">
      {/* Sidebar */}
      <div className="w-64 border-r border-[#1a1a1f] bg-[#050505] flex flex-col overflow-y-auto">
        <div className="p-4 space-y-4">
          <div className="flex items-center gap-2 px-2">
            <Code2 className="w-6 h-6" style={{ color: '#00C8FF' }} />
            <span className="font-bold text-[#F5F7FA]">NEXUS</span>
          </div>

          <button className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-[#00C8FF] text-[#050505] font-bold hover:bg-[#38BDF8] transition">
            <Plus className="w-4 h-4" />
            New Chat
          </button>

          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-[#8B949E]" />
            <input
              type="text"
              placeholder="Search..."
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-[#101114] border border-[#1a1a1f] text-[#F5F7FA] text-sm focus:border-[#00C8FF] outline-none transition"
            />
          </div>
        </div>

        {/* Conversations */}
        <div className="flex-1 px-4 py-6 space-y-2">
          <div className="text-xs text-[#8B949E] px-2 font-semibold">Recent Chats</div>
          {['Explain the embedding generator', 'What does code parser do?', 'How does hybrid search work?'].map((chat, i) => (
            <button
              key={i}
              className="w-full text-left px-3 py-2 rounded-lg text-[#8B949E] text-sm hover:bg-[#101114] transition truncate"
            >
              {chat}
            </button>
          ))}
        </div>

        {/* Repository Selector */}
        <div className="border-t border-[#1a1a1f] p-4 space-y-2">
          <div className="text-xs text-[#8B949E] px-2 font-semibold">Repositories</div>
          {repositories.map(repo => (
            <button
              key={repo.id}
              onClick={() => setSelectedRepo(repo.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition ${
                selectedRepo === repo.id
                  ? 'bg-[#00C8FF] bg-opacity-10 border border-[#00C8FF] text-[#00C8FF]'
                  : 'text-[#8B949E] hover:bg-[#101114]'
              }`}
            >
              <div className="flex items-center justify-between">
                <span>{repo.name}</span>
                {repo.indexed ? (
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                ) : (
                  <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                )}
              </div>
              <div className="text-xs text-[#8B949E] mt-1">{repo.language} • {repo.chunks} chunks</div>
            </button>
          ))}
        </div>

        {/* Settings */}
        <div className="border-t border-[#1a1a1f] p-4">
          <button className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-[#8B949E] hover:text-[#00C8FF] hover:bg-[#101114] transition">
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col bg-[#0d0d0f]">
        {/* Top Bar */}
        <div className="border-b border-[#1a1a1f] px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-[#F5F7FA]">{selectedRepo}</h2>
            <p className="text-sm text-[#8B949E]">206 chunks • ● Indexed</p>
          </div>
          <button
            onClick={() => setShowDebug(!showDebug)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition ${
              showDebug
                ? 'border-[#00C8FF] text-[#00C8FF] bg-[#00C8FF] bg-opacity-10'
                : 'border-[#1a1a1f] text-[#8B949E] hover:border-[#00C8FF]'
            }`}
          >
            <Zap className="w-4 h-4" />
            RAG Inspector
          </button>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Code2 className="w-16 h-16 text-[#8B949E] mb-4 opacity-50" />
              <h3 className="text-xl font-bold text-[#F5F7FA] mb-2">Ask about your codebase</h3>
              <p className="text-[#8B949E] max-w-md">
                🔥 Connected to REAL_RAG with 206 indexed chunks. Ask questions about your code using BM25 + TF-IDF hybrid search!
              </p>
            </div>
          ) : (
            messages.map(msg => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-2xl ${
                    msg.role === 'user'
                      ? 'bg-[#00C8FF] text-[#050505]'
                      : 'bg-[#101114] border border-[#1a1a1f] text-[#F5F7FA]'
                  } rounded-lg px-6 py-4`}
                >
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>

                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-current border-opacity-20 space-y-2">
                      <div className="text-xs font-semibold opacity-75">📚 Sources</div>
                      {msg.citations.map((citation, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            // Fetch source code from backend
                            console.log(`Fetching source: ${citation.file}`);
                          }}
                          className="block text-left text-xs opacity-75 hover:opacity-100 transition"
                        >
                          📄 {citation.file} (lines {citation.lines})
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-[#101114] border border-[#1a1a1f] rounded-lg px-6 py-4">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-[#00C8FF] rounded-full animate-pulse"></div>
                  <span className="text-sm text-[#8B949E]">Searching 206 chunks with BM25 + TF-IDF...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-[#1a1a1f] p-6">
          <div className="flex gap-4">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask about your code... (using REAL RAG with 206 chunks)"
              className="flex-1 px-4 py-3 rounded-lg bg-[#101114] border border-[#1a1a1f] text-[#F5F7FA] focus:border-[#00C8FF] outline-none transition"
              disabled={loading}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading}
              className="px-6 py-3 rounded-lg bg-[#00C8FF] text-[#050505] hover:bg-[#38BDF8] transition font-bold flex items-center gap-2 disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};