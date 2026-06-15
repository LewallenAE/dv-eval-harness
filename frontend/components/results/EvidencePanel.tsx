'use client';

import React from 'react';

interface EvidencePanelProps {
  evidence: string[];
}

export default function EvidencePanel({ evidence }: EvidencePanelProps) {
  if (!evidence || evidence.length === 0) return null;

  return (
    <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
      <div className="p-3 bg-gray-50 border-b">
        <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider">Evidence Collected</h3>
      </div>
      <div className="p-4 space-y-3">
        {evidence.map((item, idx) => (
          <div key={idx} className="p-3 bg-gray-900 rounded-md border border-gray-800">
            <pre className="text-xs text-blue-300 whitespace-pre-wrap font-mono">{item}</pre>
          </div>
        ))}
      </div>
    </div>
  );
}
