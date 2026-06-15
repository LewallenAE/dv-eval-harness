'use client';

import React, { useEffect, useState } from 'react';
import { Trajectory } from '@/lib/types';
import { fetchTraces } from '@/lib/api';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ScoreBadge from '@/components/ui/ScoreBadge';
import TrajectoryViewer from '@/components/results/TrajectoryViewer';

export default function TracesTable() {
  const [traces, setTraces] = useState<Trajectory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchTraces();
        // Sort by r_total descending
        const sorted = data.sort((a, b) => b.r_total - a.r_total);
        setTraces(sorted);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch traces');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <LoadingSpinner size="lg" />
      <p className="text-gray-500 font-medium">Loading evaluation history...</p>
    </div>
  );

  if (error) return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <p className="text-red-700 font-semibold mb-2">Error Loading Traces</p>
      <p className="text-red-600 text-sm">{error}</p>
    </div>
  );

  if (traces.length === 0) return (
    <div className="bg-gray-50 border border-dashed border-gray-300 rounded-lg p-12 text-center">
      <p className="text-gray-500 font-medium">No evaluation runs found yet.</p>
      <p className="text-gray-400 text-sm mt-1">Run a case to see results here.</p>
    </div>
  );

  return (
    <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Case ID</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">R-Total</th>
              <th className="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Inferred Root Cause</th>
              <th className="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {traces.map((trace, idx) => (
              <React.Fragment key={idx}>
                <tr 
                  className={`hover:bg-blue-50 cursor-pointer transition-colors ${expandedRow === idx ? 'bg-blue-50' : ''}`}
                  onClick={() => setExpandedRow(expandedRow === idx ? null : idx)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">{trace.case_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <ScoreBadge score={trace.r_total} />
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600 truncate max-w-xs">{trace.root_cause}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900">
                      {expandedRow === idx ? 'Hide Details' : 'View Details'}
                    </button>
                  </td>
                </tr>
                {expandedRow === idx && (
                  <tr>
                    <td colSpan={4} className="px-6 py-8 bg-gray-50 border-y shadow-inner">
                      <TrajectoryViewer trajectory={trace} />
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
