import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface PipelineStage {
  name: string;
  status: 'complete' | 'pending' | 'error';
  duration: number;
  details?: any;
}

export const RAGInspector: React.FC<{ visible: boolean }> = ({ visible }) => {
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set(['query']));

  const toggleStage = (stageName: string) => {
    const newSet = new Set(expandedStages);
    if (newSet.has(stageName)) {
      newSet.delete(stageName);
    } else {
      newSet.add(stageName);
    }
    setExpandedStages(newSet);
  };

  const stages: PipelineStage[] = [
    {
      name: 'Query Processing',
      status: 'complete',
      duration: 12,
      details: {
        original: 'Where is authentication implemented?',
        processed: 'authentication implementation flow login credentials',
        type: 'code_search',
        keywords: ['authentication', 'implementation', 'flow', 'login'],
        entities: ['AuthService', 'AuthController'],
        subqueries: [
          'Where is login handled?',
          'Where are credentials validated?',
          'Where is JWT generated?',
        ],
      },
    },
    {
      name: 'Vector Search',
      status: 'complete',
      duration: 45,
      details: {
        query_embedding_dim: 768,
        results: [
          { chunk_id: 'c001', file: 'AuthService.java', score: 0.93, lines: '42-67' },
          { chunk_id: 'c002', file: 'AuthController.java', score: 0.89, lines: '24-48' },
          { chunk_id: 'c003', file: 'JwtService.java', score: 0.87, lines: '12-39' },
          { chunk_id: 'c004', file: 'SecurityConfig.java', score: 0.82, lines: '15-31' },
          { chunk_id: 'c005', file: 'LoginRequest.java', score: 0.79, lines: '1-20' },
        ],
      },
    },
    {
      name: 'BM25 Search',
      status: 'complete',
      duration: 8,
      details: {
        results: [
          { chunk_id: 'c001', file: 'AuthService.java', score: 12.4 },
          { chunk_id: 'c002', file: 'AuthController.java', score: 11.8 },
          { chunk_id: 'c006', file: 'SecurityConfig.java', score: 9.2 },
          { chunk_id: 'c003', file: 'JwtService.java', score: 8.1 },
          { chunk_id: 'c007', file: 'LoginValidator.java', score: 7.9 },
        ],
      },
    },
    {
      name: 'Result Fusion (RRF)',
      status: 'complete',
      duration: 3,
      details: {
        k_parameter: 60,
        results: [
          { chunk_id: 'c001', fusion_score: 0.0321, rank: 1 },
          { chunk_id: 'c002', fusion_score: 0.0298, rank: 2 },
          { chunk_id: 'c003', fusion_score: 0.0287, rank: 3 },
          { chunk_id: 'c004', fusion_score: 0.0276, rank: 4 },
          { chunk_id: 'c006', fusion_score: 0.0265, rank: 5 },
        ],
      },
    },
    {
      name: 'Reranking',
      status: 'complete',
      duration: 31,
      details: {
        model: 'cross-encoder/ms-marco-MiniLM-L-12-v2',
        top_k_input: 5,
        results: [
          { chunk_id: 'c001', rerank_score: 0.96, file: 'AuthService.java', lines: '42-67' },
          { chunk_id: 'c002', rerank_score: 0.94, file: 'AuthController.java', lines: '24-48' },
          { chunk_id: 'c004', rerank_score: 0.91, file: 'SecurityConfig.java', lines: '15-31' },
        ],
      },
    },
    {
      name: 'Context Assembly',
      status: 'complete',
      duration: 18,
      details: {
        chunks_selected: 3,
        tokens_used: 2134,
        max_tokens: 6000,
        formatting: 'enhanced',
        includes_hierarchy: true,
      },
    },
    {
      name: 'Prompt Building',
      status: 'complete',
      duration: 5,
      details: {
        system_prompt_tokens: 340,
        context_tokens: 2134,
        query_tokens: 45,
        total_tokens: 2519,
      },
    },
    {
      name: 'LLM Generation',
      status: 'complete',
      duration: 228,
      details: {
        model: 'gpt-4-turbo',
        temperature: 0.3,
        max_tokens: 1000,
        output_tokens: 187,
        latency_ms: 228,
      },
    },
  ];

  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-[#0d0d0f] border border-[#1a1a1f] rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 border-b border-[#1a1a1f] p-6 bg-[#050505] flex items-center justify-between">
          <h2 className="text-2xl font-bold text-[#F5F7FA]">RAG Pipeline Inspector</h2>
          <button className="text-[#8B949E] hover:text-[#F5F7FA] text-2xl">✕</button>
        </div>

        {/* Summary */}
        <div className="p-6 border-b border-[#1a1a1f] grid grid-cols-4 gap-4">
          {[
            { label: 'Total Latency', value: '350ms', icon: '⏱️' },
            { label: 'Chunks Retrieved', value: '3', icon: '📄' },
            { label: 'Tokens Used', value: '2,706', icon: '📊' },
            { label: 'Hallucination Rate', value: '0%', icon: '✓' },
          ].map((stat, i) => (
            <div key={i} className="bg-[#101114] rounded-lg p-4">
              <div className="text-2xl mb-2">{stat.icon}</div>
              <div className="text-xs text-[#8B949E] mb-1">{stat.label}</div>
              <div className="text-lg font-bold text-[#00C8FF]">{stat.value}</div>
            </div>
          ))}
        </div>

        {/* Pipeline Stages */}
        <div className="p-6 space-y-4">
          {stages.map((stage, i) => (
            <div key={i} className="border border-[#1a1a1f] rounded-lg overflow-hidden bg-[#101114]">
              {/* Stage Header */}
              <button
                onClick={() => toggleStage(stage.name)}
                className="w-full px-6 py-4 flex items-center justify-between hover:bg-[#1a1a1f] transition"
              >
                <div className="flex items-center gap-4 text-left">
                  {/* Status Icon */}
                  <div
                    className={`w-3 h-3 rounded-full ${
                      stage.status === 'complete'
                        ? 'bg-green-500'
                        : stage.status === 'error'
                        ? 'bg-red-500'
                        : 'bg-yellow-500'
                    }`}
                  />

                  {/* Stage Info */}
                  <div>
                    <div className="font-bold text-[#F5F7FA]">{stage.name}</div>
                    <div className="text-xs text-[#8B949E]">{stage.duration}ms</div>
                  </div>
                </div>

                {/* Expand Icon */}
                {expandedStages.has(stage.name) ? (
                  <ChevronUp className="w-5 h-5 text-[#00C8FF]" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-[#8B949E]" />
                )}
              </button>

              {/* Stage Details */}
              {expandedStages.has(stage.name) && stage.details && (
                <div className="border-t border-[#1a1a1f] px-6 py-4 bg-[#0d0d0f] space-y-3">
                  {stage.name === 'Query Processing' && (
                    <>
                      <DetailRow label="Original Query" value={stage.details.original} mono />
                      <DetailRow label="Processed Query" value={stage.details.processed} mono />
                      <DetailRow label="Query Type" value={stage.details.type} />
                      <DetailRow label="Keywords" value={stage.details.keywords.join(', ')} />
                      <DetailRow label="Entities" value={stage.details.entities.join(', ')} />
                      <div>
                        <div className="text-xs text-[#8B949E] mb-2">Subqueries</div>
                        <ul className="space-y-1 ml-4">
                          {stage.details.subqueries.map((sq: string, j: number) => (
                            <li key={j} className="text-sm text-[#F5F7FA]">• {sq}</li>
                          ))}
                        </ul>
                      </div>
                    </>
                  )}

                  {(stage.name === 'Vector Search' || stage.name === 'BM25 Search') && (
                    <>
                      {stage.details.query_embedding_dim && (
                        <DetailRow label="Embedding Dimension" value={stage.details.query_embedding_dim} />
                      )}
                      {stage.details.model && <DetailRow label="Model" value={stage.details.model} mono />}
                      <div>
                        <div className="text-xs text-[#8B949E] mb-2">Top Results</div>
                        <div className="space-y-1 text-xs ml-4">
                          {stage.details.results.map((r: any, j: number) => (
                            <div key={j} className="text-[#8B949E]">
                              {j + 1}. {r.file} {stage.name === 'Vector Search' ? `(${r.score.toFixed(2)})` : `(score: ${r.score.toFixed(1)})`}
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}

                  {stage.name === 'Result Fusion (RRF)' && (
                    <>
                      <DetailRow label="RRF K Parameter" value={stage.details.k_parameter} />
                      <div>
                        <div className="text-xs text-[#8B949E] mb-2">Fused Ranking</div>
                        <div className="space-y-1 text-xs ml-4">
                          {stage.details.results.map((r: any, j: number) => (
                            <div key={j} className="text-[#8B949E]">
                              {r.rank}. Score: {r.fusion_score.toFixed(4)}
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}

                  {stage.name === 'Reranking' && (
                    <>
                      <DetailRow label="Model" value={stage.details.model} mono />
                      <DetailRow label="Input K" value={stage.details.top_k_input} />
                      <div>
                        <div className="text-xs text-[#8B949E] mb-2">Reranked Results</div>
                        <div className="space-y-1 text-xs ml-4">
                          {stage.details.results.map((r: any, j: number) => (
                            <div key={j} className="text-[#8B949E]">
                              {j + 1}. {r.file} ({r.rerank_score.toFixed(2)})
                            </div>
                          ))}
                        </div>
                      </div>
                    </>
                  )}

                  {stage.name === 'Context Assembly' && (
                    <>
                      <DetailRow label="Chunks Selected" value={stage.details.chunks_selected} />
                      <DetailRow
                        label="Token Usage"
                        value={`${stage.details.tokens_used} / ${stage.details.max_tokens}`}
                      />
                      <DetailRow label="Includes Hierarchy" value={stage.details.includes_hierarchy ? 'Yes' : 'No'} />
                    </>
                  )}

                  {stage.name === 'Prompt Building' && (
                    <>
                      <DetailRow label="System Prompt Tokens" value={stage.details.system_prompt_tokens} />
                      <DetailRow label="Context Tokens" value={stage.details.context_tokens} />
                      <DetailRow label="Query Tokens" value={stage.details.query_tokens} />
                      <DetailRow label="Total Prompt Tokens" value={stage.details.total_tokens} />
                    </>
                  )}

                  {stage.name === 'LLM Generation' && (
                    <>
                      <DetailRow label="Model" value={stage.details.model} mono />
                      <DetailRow label="Temperature" value={stage.details.temperature} />
                      <DetailRow label="Output Tokens" value={stage.details.output_tokens} />
                    </>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="border-t border-[#1a1a1f] p-6 text-center">
          <button className="px-6 py-2 rounded-lg bg-[#00C8FF] text-[#050505] hover:bg-[#38BDF8] font-bold transition">
            Export Trace
          </button>
        </div>
      </div>
    </div>
  );
};

interface DetailRowProps {
  label: string;
  value: any;
  mono?: boolean;
}

const DetailRow: React.FC<DetailRowProps> = ({ label, value, mono = false }) => (
  <div className="flex justify-between items-center text-sm">
    <span className="text-[#8B949E]">{label}</span>
    <span className={`text-[#F5F7FA] ${mono ? 'font-mono text-xs' : ''}`}>{value}</span>
  </div>
);
