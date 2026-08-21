import React, { useState } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';
import { TrendingUp, Download, RefreshCw } from 'lucide-react';

export const EvaluationDashboard: React.FC = () => {
  const [selectedMetric, setSelectedMetric] = useState('recall');

  const overallMetrics = [
    { label: 'Recall@5', value: '91%', change: '+4%', bg: 'from-[#00C8FF] to-[#0d7a8f]' },
    { label: 'Precision@5', value: '87%', change: '+2%', bg: 'from-[#00AF80] to-[#0d5f47]' },
    { label: 'MRR', value: '0.84', change: '+0.05', bg: 'from-[#6366f1] to-[#3d3d8a]' },
    { label: 'Hit Rate', value: '96%', change: '+1%', bg: 'from-[#f59e0b] to-[#a86c0d]' },
  ];

  const strategyComparison = [
    { strategy: 'Vector Only', recall5: 72, recall10: 81, precision5: 79 },
    { strategy: 'BM25 Only', recall5: 68, recall10: 76, precision5: 74 },
    { strategy: 'Hybrid', recall5: 84, recall10: 90, precision5: 85 },
    { strategy: 'Hybrid + Reranker', recall5: 91, recall10: 95, precision5: 87 },
  ];

  const queryTypeMetrics = [
    { type: 'Code Search', recall: 94, precision: 91, count: 24 },
    { type: 'Architecture', recall: 87, precision: 84, count: 18 },
    { type: 'Implementation', recall: 89, precision: 86, count: 22 },
    { type: 'Debugging', recall: 82, precision: 79, count: 15 },
    { type: 'Dependency', recall: 91, precision: 88, count: 19 },
  ];

  const generationQuality = [
    { query: 'Auth Implementation', faithfulness: 98, citations: 95, hallucination: 2 },
    { query: 'Payment Flow', faithfulness: 96, citations: 92, hallucination: 4 },
    { query: 'Database Schema', faithfulness: 99, citations: 97, hallucination: 1 },
    { query: 'Cache Strategy', faithfulness: 94, citations: 89, hallucination: 6 },
    { query: 'API Design', faithfulness: 95, citations: 91, hallucination: 5 },
  ];

  const latencyData = [
    { component: 'Query', latency: 12 },
    { component: 'Vector Search', latency: 45 },
    { component: 'BM25 Search', latency: 8 },
    { component: 'Fusion', latency: 3 },
    { component: 'Reranking', latency: 31 },
    { component: 'Context', latency: 18 },
    { component: 'Prompt', latency: 5 },
    { component: 'LLM Gen', latency: 228 },
  ];

  return (
    <div className="min-h-screen bg-[#050505] p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-[#F5F7FA]">RAG Evaluation Dashboard</h1>
            <p className="text-[#8B949E] mt-2">Measure retrieval quality and generation fidelity</p>
          </div>
          <div className="flex gap-4">
            <button className="px-4 py-2 rounded-lg border border-[#1a1a1f] text-[#8B949E] hover:text-[#00C8FF] transition flex items-center gap-2">
              <RefreshCw className="w-4 h-4" />
              Re-evaluate
            </button>
            <button className="px-4 py-2 rounded-lg bg-[#00C8FF] text-[#050505] hover:bg-[#38BDF8] font-bold flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Overall Metrics */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {overallMetrics.map((metric, i) => (
            <div key={i} className="rounded-lg p-6 border border-[#1a1a1f] bg-[#0d0d0f] overflow-hidden relative">
              <div className={`absolute inset-0 bg-gradient-to-br ${metric.bg} opacity-10`} />
              <div className="relative z-10">
                <div className="text-[#8B949E] text-sm font-semibold">{metric.label}</div>
                <div className="text-3xl font-bold text-[#F5F7FA] mt-2">{metric.value}</div>
                <div className="text-xs text-green-400 mt-1 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  {metric.change} from previous
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Strategy Comparison */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          <div className="rounded-lg border border-[#1a1a1f] bg-[#0d0d0f] p-6">
            <h2 className="text-lg font-bold text-[#F5F7FA] mb-4">Retrieval Strategy Comparison</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={strategyComparison} margin={{ bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1f" />
                <XAxis dataKey="strategy" stroke="#8B949E" angle={-15} textAnchor="end" height={80} tick={{ fontSize: 12 }} />
                <YAxis stroke="#8B949E" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#101114', border: '1px solid #1a1a1f', borderRadius: '8px' }}
                  labelStyle={{ color: '#F5F7FA' }}
                  formatter={(value) => `${value}%`}
                />
                <Legend />
                <Bar dataKey="recall5" name="Recall@5" fill="#00C8FF" />
                <Bar dataKey="precision5" name="Precision@5" fill="#00AF80" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-lg border border-[#1a1a1f] bg-[#0d0d0f] p-6">
            <h2 className="text-lg font-bold text-[#F5F7FA] mb-4">Query Type Performance</h2>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart margin={{ bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1f" />
                <XAxis dataKey="recall" name="Recall" stroke="#8B949E" />
                <YAxis dataKey="precision" name="Precision" stroke="#8B949E" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#101114', border: '1px solid #1a1a1f', borderRadius: '8px' }}
                  labelStyle={{ color: '#F5F7FA' }}
                />
                <Scatter name="Query Types" data={queryTypeMetrics} fill="#00C8FF" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Query Type Metrics Table */}
        <div className="rounded-lg border border-[#1a1a1f] bg-[#0d0d0f] p-6 mb-8">
          <h2 className="text-lg font-bold text-[#F5F7FA] mb-4">Query Type Breakdown</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#1a1a1f]">
                  <th className="text-left px-4 py-3 text-[#8B949E] text-sm font-semibold">Query Type</th>
                  <th className="text-right px-4 py-3 text-[#8B949E] text-sm font-semibold">Recall</th>
                  <th className="text-right px-4 py-3 text-[#8B949E] text-sm font-semibold">Precision</th>
                  <th className="text-right px-4 py-3 text-[#8B949E] text-sm font-semibold">Count</th>
                </tr>
              </thead>
              <tbody>
                {queryTypeMetrics.map((row, i) => (
                  <tr key={i} className="border-b border-[#1a1a1f] hover:bg-[#101114] transition">
                    <td className="px-4 py-3 text-[#F5F7FA]">{row.type}</td>
                    <td className="text-right px-4 py-3 text-[#00C8FF] font-semibold">{row.recall}%</td>
                    <td className="text-right px-4 py-3 text-[#00AF80] font-semibold">{row.precision}%</td>
                    <td className="text-right px-4 py-3 text-[#8B949E]">{row.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Generation Quality */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          <div className="rounded-lg border border-[#1a1a1f] bg-[#0d0d0f] p-6">
            <h2 className="text-lg font-bold text-[#F5F7FA] mb-4">Generation Quality</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={generationQuality}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1f" />
                <XAxis dataKey="query" stroke="#8B949E" tick={{ fontSize: 11 }} angle={-15} textAnchor="end" height={60} />
                <YAxis stroke="#8B949E" domain={[85, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#101114', border: '1px solid #1a1a1f', borderRadius: '8px' }}
                  labelStyle={{ color: '#F5F7FA' }}
                  formatter={(value) => `${value}%`}
                />
                <Legend />
                <Line type="monotone" dataKey="faithfulness" stroke="#00C8FF" name="Faithfulness" />
                <Line type="monotone" dataKey="citations" stroke="#00AF80" name="Citation Accuracy" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="rounded-lg border border-[#1a1a1f] bg-[#0d0d0f] p-6">
            <h2 className="text-lg font-bold text-[#F5F7FA] mb-4">Latency Breakdown</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={latencyData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1f" />
                <XAxis type="number" stroke="#8B949E" />
                <YAxis type="category" dataKey="component" stroke="#8B949E" width={100} tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#101114', border: '1px solid #1a1a1f', borderRadius: '8px' }}
                  labelStyle={{ color: '#F5F7FA' }}
                  formatter={(value) => `${value}ms`}
                />
                <Bar dataKey="latency" fill="#00C8FF" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Detailed Generation Quality Table */}
        <div className="rounded-lg border border-[#1a1a1f] bg-[#0d0d0f] p-6">
          <h2 className="text-lg font-bold text-[#F5F7FA] mb-4">Sample Generation Quality</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[#1a1a1f]">
                  <th className="text-left px-4 py-3 text-[#8B949E] text-sm font-semibold">Query</th>
                  <th className="text-right px-4 py-3 text-[#8B949E] text-sm font-semibold">Faithfulness</th>
                  <th className="text-right px-4 py-3 text-[#8B949E] text-sm font-semibold">Citation Accuracy</th>
                  <th className="text-right px-4 py-3 text-[#8B949E] text-sm font-semibold">Hallucination</th>
                </tr>
              </thead>
              <tbody>
                {generationQuality.map((row, i) => (
                  <tr key={i} className="border-b border-[#1a1a1f] hover:bg-[#101114] transition">
                    <td className="px-4 py-3 text-[#F5F7FA]">{row.query}</td>
                    <td className="text-right px-4 py-3">
                      <span className="text-[#00C8FF] font-semibold">{row.faithfulness}%</span>
                    </td>
                    <td className="text-right px-4 py-3">
                      <span className="text-[#00AF80] font-semibold">{row.citations}%</span>
                    </td>
                    <td className="text-right px-4 py-3">
                      <span className="text-red-400 font-semibold">{row.hallucination}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
