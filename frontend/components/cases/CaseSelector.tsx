'use client';

import React, { useEffect, useState } from 'react';
import { fetchCases } from '@/lib/api';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface CaseSelectorProps {
  onSelect: (caseId: string) => void;
  selected: string | null;
}

export default function CaseSelector({ onSelect, selected }: CaseSelectorProps) {
  const [cases, setCases] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchCases();
        setCases(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch cases');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return (
    <div className="flex items-center gap-2 text-gray-500">
      <LoadingSpinner size="sm" />
      <span>Loading cases...</span>
    </div>
  );

  if (error) return (
    <div className="text-red-600 bg-red-50 p-3 rounded-md text-sm border border-red-200">
      Error: {error}
    </div>
  );

  return (
    <div className="w-full max-w-xs">
      <label htmlFor="case-select" className="block text-sm font-medium text-gray-700 mb-1">
        Select an Existing Case
      </label>
      <select
        id="case-select"
        value={selected || ''}
        onChange={(e) => onSelect(e.target.value)}
        className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
      >
        <option value="" disabled>Choose a case...</option>
        {cases.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>
    </div>
  );
}
