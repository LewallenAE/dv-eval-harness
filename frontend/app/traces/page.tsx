'use client';

import React from 'react';
import TracesTable from '@/components/traces/TracesTable';

export default function TracesPage() {
  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-extrabold text-gray-900">Evaluation History</h1>
        <button 
          onClick={handleRefresh}
          className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-gray-600 bg-white border rounded-lg hover:bg-gray-50 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
      
      <TracesTable />
    </div>
  );
}
