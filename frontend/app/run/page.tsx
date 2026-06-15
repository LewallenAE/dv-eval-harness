'use client';

import React, { useState } from 'react';
import { DVCase, IngestResponse, Trajectory } from '@/lib/types';
import { runCase, runCaseJson } from '@/lib/api';
import CaseSelector from '@/components/cases/CaseSelector';
import CaseUploader from '@/components/cases/CaseUploader';
import CasePreview from '@/components/cases/CasePreview';
import RunButton from '@/components/ui/RunButton';
import TrajectoryViewer from '@/components/results/TrajectoryViewer';

export default function RunPage() {
  const [mode, setMode] = useState<'select' | 'upload'>('select');
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [uploadedCase, setUploadedCase] = useState<DVCase | null>(null);
  const [inferredFields, setInferredFields] = useState<string[]>([]);
  const [trajectory, setTrajectory] = useState<Trajectory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    setTrajectory(null);
    try {
      let result: Trajectory;
      if (mode === 'select' && selectedCaseId) {
        result = await runCase(selectedCaseId);
      } else if (mode === 'upload' && uploadedCase) {
        result = await runCaseJson(uploadedCase);
      } else {
        throw new Error('No case selected or uploaded');
      }
      setTrajectory(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Run failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCaseSelect = (id: string) => {
    setSelectedCaseId(id);
    setTrajectory(null);
    setError(null);
  };

  const handleNormalize = (result: IngestResponse) => {
    setUploadedCase(result.case);
    setInferredFields(result.inferred_fields);
    setTrajectory(null);
    setError(null);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-4 flex-1">
          <h1 className="text-3xl font-extrabold text-gray-900">Run Evaluation</h1>
          <div className="flex p-1 bg-gray-100 rounded-lg w-fit">
            <button
              onClick={() => setMode('select')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${mode === 'select' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Select Existing
            </button>
            <button
              onClick={() => setMode('upload')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${mode === 'upload' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              Upload JSON
            </button>
          </div>

          {mode === 'select' ? (
            <CaseSelector onSelect={handleCaseSelect} selected={selectedCaseId} />
          ) : (
            <CaseUploader onNormalize={handleNormalize} onError={setError} />
          )}
        </div>

        <div className="shrink-0">
          <RunButton
            onClick={handleRun}
            loading={loading}
            disabled={mode === 'select' ? !selectedCaseId : !uploadedCase}
          />
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 font-medium">
          {error}
        </div>
      )}

      {/* Normalization preview with inferred-field badges */}
      {!trajectory && mode === 'upload' && uploadedCase && (
        <div className="space-y-4">
          <div className="flex items-center gap-4 flex-wrap">
            <h2 className="text-xl font-bold text-gray-800">Case Preview</h2>
            {inferredFields.length > 0 && (
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs text-amber-600 font-medium">AI-filled:</span>
                {inferredFields.map(f => (
                  <span key={f} className="bg-amber-100 text-amber-700 border border-amber-300 text-xs font-mono rounded px-2 py-0.5">
                    {f}
                  </span>
                ))}
              </div>
            )}
          </div>
          <CasePreview dvCase={uploadedCase} />
        </div>
      )}

      {trajectory && (
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 border-b pb-2">Evaluation Results</h2>
          <TrajectoryViewer trajectory={trajectory} dvCase={mode === 'upload' ? uploadedCase! : undefined} />
        </div>
      )}
    </div>
  );
}
