'use client';

import React, { useState } from 'react';
import { AgentAction } from '@/lib/types';

interface ActionTimelineProps {
  actions: AgentAction[];
}

export default function ActionTimeline({ actions }: ActionTimelineProps) {
  const [expandedStep, setExpandedStep] = useState<number | null>(null);

  const formatToolName = (name: string) => {
    return name
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (l) => l.toUpperCase())
      .replace('Run Simulator', 'Simulator');
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 px-1">Agent Action Timeline</h3>
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
        <div className="space-y-6">
          {actions.map((action) => (
            <div key={action.step} className="relative pl-10">
              <div className="absolute left-0 top-1 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm shadow-sm z-10">
                {action.step}
              </div>
              
              <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
                <button 
                  onClick={() => setExpandedStep(expandedStep === action.step ? null : action.step)}
                  className="w-full text-left p-3 hover:bg-gray-50 transition-colors flex justify-between items-center"
                >
                  <span className="font-semibold text-gray-800">{formatToolName(action.tool_name)}</span>
                  <svg 
                    className={`w-5 h-5 text-gray-400 transition-transform ${expandedStep === action.step ? 'rotate-180' : ''}`} 
                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {expandedStep === action.step && (
                  <div className="p-3 border-t bg-gray-50 space-y-3">
                    <div>
                      <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Input</h4>
                      <pre className="text-xs p-2 bg-gray-900 text-green-400 rounded overflow-auto max-h-40">{action.input}</pre>
                    </div>
                    <div>
                      <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Output</h4>
                      <pre className="text-xs p-2 bg-gray-900 text-gray-300 rounded overflow-auto max-h-60 whitespace-pre-wrap">{action.output}</pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
