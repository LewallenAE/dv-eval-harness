'use client';

import React from 'react';
import { EvaluationScores } from '@/lib/types';
import ScoreBadge from '@/components/ui/ScoreBadge';

interface ScoreCardProps {
  scores: EvaluationScores;
  rTotal: number;
  penalties: string[];
  evalMode: boolean;
}

const SCORE_LABELS: { [K in keyof EvaluationScores]: string } = {
  root_cause_correct: 'Root Cause Semantic Match Accuracy',
  evidence_quality: 'Evidence Quality',
  tool_use_correctness: 'Tool Use Correctness',
  fix_plausibility: 'Fix Plausibility',
  no_hallucinated_signals: 'Signal Integrity',
};

export default function ScoreCard({ scores, rTotal, penalties, evalMode }: ScoreCardProps) {
  return (
    <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
      <div className="p-6 text-center bg-blue-50 border-b">
        {!evalMode && (
          <div className="inline-flex items-center gap-1.5 bg-purple-100 text-purple-700 text-xs font-bold px-3 py-1 rounded-full mb-3 border border-purple-200">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Analysis Mode — no ground truth
          </div>
        )}
        <h3 className="text-sm font-bold text-blue-600 uppercase tracking-widest mb-1">
          {evalMode ? 'Overall Score (R-Total)' : 'Confidence Score (no root-cause weight)'}
        </h3>
        <div className="text-5xl font-extrabold text-blue-900">{Math.round(rTotal * 100)}%</div>
      </div>

      <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(Object.keys(scores) as Array<keyof EvaluationScores>).map((key) => {
          const value = scores[key];
          const isRootCause = key === 'root_cause_correct';
          return (
            <div key={key} className={`flex flex-col gap-1 p-3 border rounded-md ${isRootCause && value === null ? 'bg-purple-50 border-purple-200' : ''}`}>
              <span className="text-xs font-bold text-gray-500 uppercase">{SCORE_LABELS[key]}</span>
              {value === null ? (
                <span className="text-xs text-purple-600 font-medium">N/A — Analysis mode</span>
              ) : (
                <ScoreBadge score={value} />
              )}
            </div>
          );
        })}
      </div>

      {penalties.length > 0 && (
        <div className="p-4 bg-red-50 border-t border-red-100">
          <h4 className="flex items-center gap-2 text-sm font-bold text-red-700 mb-2">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Penalties Applied
          </h4>
          <ul className="list-disc list-inside space-y-1">
            {penalties.map((penalty, idx) => (
              <li key={idx} className="text-sm text-red-600">{penalty}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
