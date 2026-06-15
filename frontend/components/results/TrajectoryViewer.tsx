'use client';

import React from 'react';
import { Trajectory, DVCase } from '@/lib/types';
import ScoreCard from './ScoreCard';
import ActionTimeline from './ActionTimeline';
import EvidencePanel from './EvidencePanel';
import RTLDiff from './RTLDiff';

interface TrajectoryViewerProps {
  trajectory: Trajectory;
  dvCase?: DVCase; // Optional, if we want to show original RTL
}

export default function TrajectoryViewer({ trajectory, dvCase }: TrajectoryViewerProps) {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h3 className="text-sm font-bold text-yellow-800 uppercase tracking-widest mb-2">Inferred Root Cause</h3>
        <p className="text-xl font-medium text-yellow-900 leading-relaxed italic">
          "{trajectory.root_cause}"
        </p>
      </div>

      <ScoreCard
        scores={trajectory.scores}
        rTotal={trajectory.r_total}
        penalties={trajectory.penalties}
        evalMode={trajectory.eval_mode ?? true}
      />

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="space-y-8">
          <ActionTimeline actions={trajectory.actions} />
          <EvidencePanel evidence={trajectory.evidence} />
        </div>
        
        <div className="space-y-8">
          {dvCase ? (
            <RTLDiff original={dvCase.rtl} fixed={trajectory.proposed_fix} />
          ) : (
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-gray-900 px-1">Proposed Fix</h3>
              <div className="p-4 bg-gray-900 rounded-lg border border-gray-800 overflow-auto max-h-[600px]">
                <pre className="text-xs text-green-400 font-mono">{trajectory.proposed_fix}</pre>
              </div>
            </div>
          )}

          {trajectory.constitutional_violations.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="text-sm font-bold text-red-800 uppercase mb-2">Policy Violations</h4>
              <ul className="list-disc list-inside space-y-1">
                {trajectory.constitutional_violations.map((v, i) => (
                  <li key={i} className="text-sm text-red-700">{v}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
