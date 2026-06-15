'use client';

import React, { useState } from 'react';
import { DVCase } from '@/lib/types';

interface CasePreviewProps {
  dvCase: DVCase;
}

export default function CasePreview({ dvCase }: CasePreviewProps) {
  const [rtlExpanded, setRtlExpanded] = useState(false);

  return (
    <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
      <div className="p-4 bg-gray-50 border-b">
        <h3 className="text-lg font-bold text-gray-900">{dvCase.title}</h3>
        <p className="text-sm text-gray-500">ID: {dvCase.id}</p>
      </div>
      
      <div className="p-4 space-y-4">
        <div>
          <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Description</h4>
          <p className="text-sm text-gray-700">{dvCase.description}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Expected Root Cause</h4>
            <p className="text-sm text-gray-700 italic">{dvCase.expected_root_cause}</p>
          </div>
          <div>
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Valid Signals</h4>
            <div className="flex flex-wrap gap-1 mt-1">
              {dvCase.valid_signals.map(s => (
                <span key={s} className="px-2 py-0.5 bg-green-50 text-green-700 border border-green-100 rounded text-xs font-mono">
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider">RTL Source</h4>
            <button 
              onClick={() => setRtlExpanded(!rtlExpanded)}
              className="text-xs text-blue-600 hover:underline"
            >
              {rtlExpanded ? 'Collapse' : 'Expand'}
            </button>
          </div>
          <div className={`
            font-mono text-xs p-3 bg-gray-900 text-gray-300 rounded overflow-auto
            ${rtlExpanded ? 'max-h-[500px]' : 'max-h-32'}
          `}>
            <pre>{dvCase.rtl}</pre>
          </div>
        </div>

        {dvCase.forbidden_targets.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider mb-1">Forbidden Targets</h4>
            <div className="flex flex-wrap gap-1 mt-1">
              {dvCase.forbidden_targets.map(t => (
                <span key={t} className="px-2 py-0.5 bg-red-50 text-red-700 border border-red-100 rounded text-xs font-mono">
                  {t}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
