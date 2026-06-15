'use client';

import React, { useState } from 'react';
import { DVCase, IngestResponse } from '@/lib/types';
import { ingestCase } from '@/lib/api';

interface CaseUploaderProps {
  onNormalize: (result: IngestResponse) => void;
  onError: (msg: string) => void;
}

const REQUIRED_FIELDS = [
  { name: 'id', desc: 'Unique case ID  (e.g. "MY_BUG_001")' },
  { name: 'rtl', desc: 'SystemVerilog / Verilog snippet containing the bug' },
  { name: 'bug_signature', desc: 'Simulation error string the bug produces' },
];

const KNOWN_ROOT_CAUSE_FIELD = {
  name: 'expected_root_cause',
  desc: 'Ground-truth explanation — omit if unknown (switches to Analysis mode)',
};

const OPTIONAL_FIELDS = [
  'title', 'description', 'testbench', 'fix_replacement',
  'expected_fix_contains', 'valid_signals', 'forbidden_targets',
  'failure_log', 'success_log', 'failure_coverage', 'success_coverage',
];

const EXAMPLE_EVAL = `{
  "id": "MY_BUG_001",
  "rtl": "assign full = (wr_ptr == rd_ptr);",
  "bug_signature": "UVM_ERROR: FIFO overflow detected",
  "expected_root_cause": "Full flag ignores MSB bit used to disambiguate empty vs full."
}`;

const EXAMPLE_ANALYSIS = `{
  "id": "MY_BUG_001",
  "rtl": "assign full = (wr_ptr == rd_ptr);",
  "bug_signature": "UVM_ERROR: FIFO overflow detected"
}`;

export default function CaseUploader({ onNormalize, onError }: CaseUploaderProps) {
  const [fileName, setFileName] = useState<string | null>(null);
  const [normalizing, setNormalizing] = useState(false);
  const [schemaOpen, setSchemaOpen] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);

    const text = await file.text();
    let raw: Record<string, unknown>;
    try {
      raw = JSON.parse(text);
    } catch {
      onError('File is not valid JSON.');
      setFileName(null);
      e.target.value = '';
      return;
    }

    setNormalizing(true);
    try {
      const result = await ingestCase(raw);
      onNormalize(result);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Normalization failed');
      setFileName(null);
    } finally {
      setNormalizing(false);
      e.target.value = '';
    }
  };

  const clear = () => setFileName(null);

  return (
    <div className="w-full space-y-4">

      {/* Schema reference accordion */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setSchemaOpen(o => !o)}
          className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 text-sm font-medium text-gray-700 transition-colors"
        >
          <span>Format reference — what to include in your JSON</span>
          <svg
            className={`w-4 h-4 text-gray-500 transition-transform ${schemaOpen ? 'rotate-180' : ''}`}
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {schemaOpen && (
          <div className="px-4 py-4 space-y-4 bg-white text-sm">
            <div>
              <p className="font-semibold text-red-600 mb-2">Required (must be in your file)</p>
              <div className="space-y-1">
                {REQUIRED_FIELDS.map(f => (
                  <div key={f.name} className="flex gap-3">
                    <code className="text-red-700 font-mono w-36 shrink-0">{f.name}</code>
                    <span className="text-gray-600">{f.desc}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-l-4 border-blue-300 pl-3 bg-blue-50 py-2 rounded-r-md">
              <p className="font-semibold text-blue-700 mb-1">Controls which mode runs</p>
              <div className="flex gap-3">
                <code className="text-blue-700 font-mono w-36 shrink-0">{KNOWN_ROOT_CAUSE_FIELD.name}</code>
                <span className="text-gray-600 text-xs">{KNOWN_ROOT_CAUSE_FIELD.desc}</span>
              </div>
              <div className="mt-2 flex flex-col gap-1 text-xs">
                <span className="text-green-700 font-medium">Include it → Eval mode: agent is scored against your answer</span>
                <span className="text-purple-700 font-medium">Omit it → Analysis mode: agent diagnoses the bug for you</span>
              </div>
            </div>

            <div>
              <p className="font-semibold text-amber-600 mb-2">Auto-filled by AI (optional)</p>
              <div className="flex flex-wrap gap-2">
                {OPTIONAL_FIELDS.map(f => (
                  <code key={f} className="bg-amber-50 text-amber-700 border border-amber-200 rounded px-2 py-0.5 text-xs font-mono">
                    {f}
                  </code>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <p className="font-semibold text-green-700 mb-1 text-xs uppercase tracking-wide">Eval mode</p>
                <pre className="bg-gray-900 text-green-300 text-xs rounded-md p-3 overflow-x-auto">{EXAMPLE_EVAL}</pre>
              </div>
              <div>
                <p className="font-semibold text-purple-700 mb-1 text-xs uppercase tracking-wide">Analysis mode</p>
                <pre className="bg-gray-900 text-purple-300 text-xs rounded-md p-3 overflow-x-auto">{EXAMPLE_ANALYSIS}</pre>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Drop zone */}
      <div className="w-full max-w-xs">
        {normalizing ? (
          <div className="flex items-center gap-3 p-4 border border-blue-200 rounded-lg bg-blue-50">
            <svg className="animate-spin w-5 h-5 text-blue-500 shrink-0" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-blue-700">Normalizing with AI…</p>
              <p className="text-xs text-blue-500">Filling in missing fields</p>
            </div>
          </div>
        ) : !fileName ? (
          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <svg className="w-8 h-8 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="mb-1 text-sm text-gray-500 font-semibold text-center px-2">Click to upload case JSON</p>
              <p className="text-xs text-gray-400">AI fills in any missing fields</p>
            </div>
            <input type="file" className="hidden" accept=".json" onChange={handleFileChange} />
          </label>
        ) : (
          <div className="flex items-center justify-between p-3 border rounded-md bg-blue-50 border-blue-200">
            <div className="flex items-center gap-2 overflow-hidden">
              <svg className="w-5 h-5 text-blue-500 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium text-blue-700 truncate">{fileName}</span>
            </div>
            <button onClick={clear} className="text-blue-500 hover:text-blue-700 p-1">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
