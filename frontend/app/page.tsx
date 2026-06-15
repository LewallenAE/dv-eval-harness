'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { fetchHealth } from '@/lib/api';

export default function HomePage() {
  const [health, setHealth] = useState<{ status: string; service: string } | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function checkHealth() {
      try {
        const data = await fetchHealth();
        setHealth(data);
      } catch (err) {
        setError(true);
      }
    }
    checkHealth();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-20 space-y-12 text-center">
      <div className="space-y-4">
        <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight">
          DV Eval Harness
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Automated evaluation framework for Design Verification agents. 
          Benchmark root cause analysis, fix generation, and tool use accuracy.
        </p>
        
        <div className="flex items-center justify-center gap-2 mt-6">
          <div className={`w-3 h-3 rounded-full ${error ? 'bg-red-500 animate-pulse' : health ? 'bg-green-500' : 'bg-gray-300'}`}></div>
          <span className="text-sm font-medium text-gray-500">
            API Status: {error ? 'Offline' : health ? 'Online' : 'Checking...'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <Link 
          href="/run"
          className="group p-8 bg-white border rounded-2xl shadow-sm hover:shadow-md hover:border-blue-300 transition-all text-left"
        >
          <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Run a Case</h2>
          <p className="text-gray-600">
            Select a mock case or upload your own JSON to evaluate agent performance.
          </p>
        </Link>

        <Link 
          href="/traces"
          className="group p-8 bg-white border rounded-2xl shadow-sm hover:shadow-md hover:border-blue-300 transition-all text-left"
        >
          <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mb-6 group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">View Traces</h2>
          <p className="text-gray-600">
            Review history of past evaluation runs, detailed trajectories, and scores.
          </p>
        </Link>
      </div>
    </div>
  );
}
