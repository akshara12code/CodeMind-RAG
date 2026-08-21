import React, { useState } from 'react';
import { Code2, ArrowRight, Zap, GitBranch, Search } from 'lucide-react';

export const Landing: React.FC = () => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#050505] to-[#0d0d0f]">
      {/* Header */}
      <header className="border-b border-[#1a1a1f] backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code2 className="w-8 h-8" style={{ color: '#00C8FF' }} />
            <span className="text-xl font-bold text-[#F5F7FA]">NEXUS</span>
          </div>
          <nav className="hidden md:flex gap-8">
            <a href="#features" className="text-[#8B949E] hover:text-[#00C8FF] transition">Features</a>
            <a href="#demo" className="text-[#8B949E] hover:text-[#00C8FF] transition">Demo</a>
            <a href="#" className="text-[#8B949E] hover:text-[#00C8FF] transition">Docs</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 md:py-32">
        <div className="text-center mb-12">
          {/* Subtle glow effect behind hero */}
          <div
            className="absolute inset-0 max-w-2xl mx-auto blur-3xl opacity-20"
            style={{
              background: 'radial-gradient(circle, #00C8FF 0%, transparent 70%)',
              top: '100px',
              height: '400px',
              pointerEvents: 'none',
            }}
          />

          <h1 className="text-5xl md:text-7xl font-bold text-[#F5F7FA] mb-6 tracking-tight relative z-10">
            Understand Any Codebase.
          </h1>

          <p className="text-xl md:text-2xl text-[#8B949E] mb-8 max-w-2xl mx-auto leading-relaxed relative z-10">
            An AI-powered developer assistant that retrieves and explains your entire repository with precision.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center relative z-10">
            <button
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
              className="px-8 py-4 bg-[#00C8FF] text-[#050505] font-bold rounded-lg flex items-center justify-center gap-2 hover:bg-[#38BDF8] transition-all duration-200 shadow-lg"
              style={{
                boxShadow: isHovered ? '0 0 20px rgba(0, 200, 255, 0.3)' : '0 0 10px rgba(0, 200, 255, 0.15)',
              }}
            >
              Get Started
              <ArrowRight className="w-5 h-5" />
            </button>
            <button className="px-8 py-4 bg-[#101114] text-[#00C8FF] font-bold rounded-lg border border-[#00C8FF] border-opacity-20 hover:border-opacity-50 transition flex items-center justify-center gap-2">
              View Demo
              <Zap className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20">
          {[
            {
              icon: <Search className="w-6 h-6" />,
              title: 'Semantic Search',
              desc: 'Find relevant code using natural language queries',
            },
            {
              icon: <GitBranch className="w-6 h-6" />,
              title: 'Dependency Aware',
              desc: 'Understands code relationships and architecture',
            },
            {
              icon: <Zap className="w-6 h-6" />,
              title: 'Instant Answers',
              desc: 'Get grounded, cited answers in milliseconds',
            },
          ].map((feature, i) => (
            <div
              key={i}
              className="p-6 rounded-lg bg-[#101114] border border-[#1a1a1f] hover:border-[#00C8FF] transition-all group"
            >
              <div className="text-[#00C8FF] mb-3 group-hover:scale-110 transition transform">
                {feature.icon}
              </div>
              <h3 className="text-lg font-bold text-[#F5F7FA] mb-2">{feature.title}</h3>
              <p className="text-[#8B949E] text-sm">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Preview Section */}
      <section id="demo" className="max-w-7xl mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-[#F5F7FA] mb-8 text-center">See It In Action</h2>
        
        <div className="rounded-lg overflow-hidden border border-[#1a1a1f] bg-[#0d0d0f] shadow-2xl">
          {/* Mock UI Preview */}
          <div className="grid grid-cols-3 gap-0 min-h-[500px]">
            {/* Left Sidebar */}
            <div className="col-span-1 border-r border-[#1a1a1f] p-4 bg-[#050505]">
              <div className="space-y-4">
                <button className="w-full px-4 py-2 rounded bg-[#00C8FF] text-[#050505] text-sm font-bold">
                  + New Chat
                </button>
                <input
                  type="text"
                  placeholder="Search..."
                  className="w-full px-3 py-2 rounded bg-[#101114] border border-[#1a1a1f] text-[#F5F7FA] text-sm"
                />
                <div className="space-y-2">
                  <div className="text-xs text-[#8B949E] px-3 py-2">Recent</div>
                  {['repo-auth', 'repo-payments', 'repo-api'].map((name, i) => (
                    <div
                      key={i}
                      className="px-3 py-2 rounded text-sm text-[#8B949E] hover:bg-[#101114] cursor-pointer transition"
                    >
                      {name}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Main Chat Area */}
            <div className="col-span-2 flex flex-col bg-[#0d0d0f] p-6">
              <div className="flex-1 space-y-4 mb-6 overflow-y-auto">
                {/* User message */}
                <div className="flex justify-end">
                  <div className="bg-[#00C8FF] text-[#050505] rounded-lg px-4 py-2 max-w-xs">
                    <p className="text-sm font-medium">Where is authentication implemented?</p>
                  </div>
                </div>

                {/* AI Response */}
                <div className="flex justify-start">
                  <div className="bg-[#101114] border border-[#1a1a1f] rounded-lg px-4 py-2 max-w-xs">
                    <p className="text-sm text-[#F5F7FA] mb-2">
                      Authentication is primarily handled in the <code className="text-[#00C8FF]">AuthService</code> class...
                    </p>
                    <div className="text-xs text-[#8B949E] border-t border-[#1a1a1f] pt-2 mt-2">
                      📄 AuthService.java (lines 42-67)
                    </div>
                  </div>
                </div>
              </div>

              {/* Input Area */}
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Ask about your codebase..."
                  className="flex-1 px-4 py-2 rounded bg-[#101114] border border-[#1a1a1f] text-[#F5F7FA] text-sm focus:border-[#00C8FF] outline-none transition"
                />
                <button className="px-4 py-2 rounded bg-[#00C8FF] text-[#050505] hover:bg-[#38BDF8] transition font-bold">
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-6 py-20 text-center">
        <h2 className="text-3xl font-bold text-[#F5F7FA] mb-4">Ready to understand your codebase?</h2>
        <p className="text-[#8B949E] mb-8">Upload a repository and start asking questions</p>
        <button className="px-8 py-4 bg-[#00C8FF] text-[#050505] font-bold rounded-lg hover:bg-[#38BDF8] transition">
          Analyze Repository
        </button>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#1a1a1f] bg-[#050505] py-8 text-center text-[#8B949E] text-sm">
        <p>© 2025 NEXUS - AI Developer Assistant. Built with precision.</p>
      </footer>
    </div>
  );
};
