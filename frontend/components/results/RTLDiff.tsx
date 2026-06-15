'use client';

import React from 'react';

interface RTLDiffProps {
  original: string;
  fixed: string;
}

export default function RTLDiff({ original, fixed }: RTLDiffProps) {
  // Simple diff logic: split by line and compare
  const originalLines = original.split('\n');
  const fixedLines = fixed.split('\n');

  const renderCode = (lines: string[], otherLines: string[], title: string, color: 'red' | 'green') => (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden">
      <div className={`p-2 text-xs font-bold uppercase tracking-widest border-b ${color === 'red' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
        {title}
      </div>
      <div className="flex-1 p-3 bg-gray-900 text-gray-300 font-mono text-xs overflow-auto max-h-[600px]">
        {lines.map((line, i) => {
          const isDifferent = line !== otherLines[i];
          const highlightClass = isDifferent 
            ? color === 'red' ? 'bg-red-900/50 text-red-200' : 'bg-green-900/50 text-green-200'
            : '';
          
          return (
            <div key={i} className={`whitespace-pre ${highlightClass} px-1 -mx-1`}>
              <span className="inline-block w-8 text-gray-600 select-none text-right mr-4">{i + 1}</span>
              {line || ' '}
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-bold text-gray-900 px-1">RTL Comparison</h3>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-full">
        {renderCode(originalLines, fixedLines, 'Buggy RTL', 'red')}
        {renderCode(fixedLines, originalLines, 'Proposed Fix', 'green')}
      </div>
    </div>
  );
}
